#!/usr/bin/env python3
"""
Local ML pipeline script for testing and development
Runs YOLOv10 detection + MONAI segmentation on local TIFF scans using dummy models
"""

import sys
import os
import logging
import json
import time
from datetime import datetime
import numpy as np

# Local modules
from preprocess_tiff import extract_slices_from_tiff, normalize_slice, preprocess_volume
from yolo_detector import YOLODetector
from monai_segmenter import MONAISegmenter
from postprocess import quantify_segmentation, save_mask_as_nrrd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Organ label mapping
ORGAN_NAMES = {
    1: "digestive_tract",
    2: "reproductive_organs",
    3: "neural_tissue"
}

def run_pipeline(tiff_path: str, output_base_dir: str = "results"):
    """
    Run complete pipeline locally
    
    Args:
        tiff_path: Path to input TIFF file
        output_base_dir: Base directory for results
    """
    start_time = time.time()
    
    scan_name = os.path.splitext(os.path.basename(tiff_path))[0]
    results_dir = os.path.join(output_base_dir, scan_name)
    os.makedirs(results_dir, exist_ok=True)
    
    # Setup file logging
    file_handler = logging.FileHandler(os.path.join(results_dir, "processing.log"))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    logger.info(f"Starting local pipeline for {scan_name}")
    logger.info("=" * 80)
    
    try:
        # Stage 1: Preprocess - extract slices
        logger.info("Stage 1: Preprocessing TIFF")
        if not os.path.exists(tiff_path):
            raise FileNotFoundError(f"TIFF file not found: {tiff_path}")
            
        volume, slices = extract_slices_from_tiff(tiff_path)
        slices_normalized = [normalize_slice(s) for s in slices]
        
        # Stage 2: YOLOv10 detection (Dummy Mode)
        logger.info("Stage 2: Running YOLOv10 detection (DUMMY MODE)")
        detector = YOLODetector(dummy_mode=True)
        slice_detections = detector.detect_volume(slices_normalized)
        
        # Aggregate to 3D bounding box
        bbox_3d = detector.aggregate_to_3d_bbox(slice_detections, volume.shape)
        
        if bbox_3d:
            logger.info(f"Found ROI: {bbox_3d}")
            roi_volume = detector.crop_volume(volume, bbox_3d)
        else:
            logger.warning("No detections found, processing full volume")
            roi_volume = volume
            bbox_3d = {
                'x_min': 0, 'y_min': 0, 'z_min': 0,
                'x_max': volume.shape[2], 'y_max': volume.shape[1], 'z_max': volume.shape[0]
            }
        
        # Stage 3: Preprocess volume for MONAI
        logger.info("Stage 3: Preprocessing volume for MONAI")
        roi_volume_normalized = preprocess_volume(roi_volume)
        
        # Stage 4: MONAI segmentation (Dummy Mode)
        logger.info("Stage 4: Running MONAI segmentation (DUMMY MODE)")
        segmenter = MONAISegmenter(
            model_type="unet",
            out_channels=len(ORGAN_NAMES) + 1,  # +1 for background
            dummy_mode=True
        )
        
        # Determine ROI size based on volume shape
        roi_size = tuple(min(s, 96) for s in roi_volume_normalized.shape)
        
        mask, seg_metrics = segmenter.segment(
            roi_volume_normalized,
            roi_size=roi_size,
            sw_batch_size=2
        )
        
        # Post-process mask
        mask = segmenter.postprocess(mask, remove_small_objects=True)
        
        # Pad mask back to original volume size if cropped
        full_mask = np.zeros(volume.shape, dtype=np.uint8)
        full_mask[
            bbox_3d['z_min']:bbox_3d['z_max'],
            bbox_3d['y_min']:bbox_3d['y_max'],
            bbox_3d['x_min']:bbox_3d['x_max']
        ] = mask
        
        # Stage 5: Quantification
        logger.info("Stage 5: Computing quantification metrics")
        quantification_results = quantify_segmentation(
            full_mask,
            ORGAN_NAMES,
            spacing=(1.0, 1.0, 1.0)  # Placeholder spacing
        )
        
        # Stage 6: Save results locally
        logger.info("Stage 6: Saving results")
        
        # Save NRRD mask
        mask_path_nrrd = os.path.join(results_dir, "mask.nrrd")
        save_mask_as_nrrd(full_mask, mask_path_nrrd)
        
        # Save quantification as JSON
        quant_path = os.path.join(results_dir, "quantification.json")
        with open(quant_path, 'w') as f:
            json.dump(quantification_results, f, indent=2)
            
        # Save run metadata
        metadata = {
            "scan_name": scan_name,
            "timestamp": datetime.utcnow().isoformat(),
            "duration_seconds": time.time() - start_time,
            "bbox_3d": bbox_3d,
            "volume_shape": volume.shape
        }
        with open(os.path.join(results_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Results saved to {results_dir}/")
        logger.info("=" * 80)
        logger.info("Pipeline completed successfully")
        
        return results_dir
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_local_segmentation.py <path_to_tiff> [output_dir]")
        sys.exit(1)
    
    tiff_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "results"
    
    run_pipeline(tiff_path, output_dir)


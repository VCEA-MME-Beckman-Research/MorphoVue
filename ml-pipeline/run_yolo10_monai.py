#!/usr/bin/env python3
"""
Main ML pipeline script for Kamiak HPC
Runs YOLOv10 detection + MONAI segmentation on CT tick scans
"""

import sys
import os
import logging
import json
from datetime import datetime
import numpy as np

# Firebase imports
from firebase_admin import credentials, initialize_app, storage, firestore

# Local modules
from preprocess_tiff import extract_slices_from_tiff, normalize_slice, preprocess_volume
from yolo_detector import YOLODetector
from monai_segmenter import MONAISegmenter
from postprocess import quantify_segmentation, save_mask_as_nrrd, save_mask_as_nifti

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Configuration
FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-key.json')
YOLO_WEIGHTS = os.getenv('YOLO_WEIGHTS', 'weights/yolov10s.pt')
MONAI_WEIGHTS = os.getenv('MONAI_WEIGHTS', 'weights/monai_unet.pth')
TMP_DIR = 'tmp'
RESULTS_DIR = 'results'

# Organ label mapping
ORGAN_NAMES = {
    1: "digestive_tract",
    2: "reproductive_organs",
    3: "neural_tissue"
}


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        initialize_app(cred, {
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
        })
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise


def download_scan_from_firebase(scan_id: str) -> str:
    """
    Download TIFF scan from Firebase Storage
    
    Args:
        scan_id: Scan ID
    
    Returns:
        Path to downloaded file
    """
    logger.info(f"Downloading scan {scan_id} from Firebase Storage")
    
    bucket = storage.bucket()
    db = firestore.client()
    
    # Get scan metadata
    scan_doc = db.collection('scans').document(scan_id).get()
    if not scan_doc.exists:
        raise ValueError(f"Scan {scan_id} not found in Firestore")
    
    scan_data = scan_doc.to_dict()
    storage_path = scan_data['storage_path']
    
    # Download file
    blob = bucket.blob(storage_path)
    download_path = os.path.join(TMP_DIR, f"{scan_id}.tiff")
    
    os.makedirs(TMP_DIR, exist_ok=True)
    blob.download_to_filename(download_path)
    
    logger.info(f"Downloaded to {download_path}")
    
    return download_path


def upload_results_to_firebase(scan_id: str, mask_path: str, metrics: dict, quantification: list):
    """
    Upload segmentation results to Firebase
    
    Args:
        scan_id: Scan ID
        mask_path: Path to segmentation mask file
        metrics: Segmentation metrics
        quantification: Quantification results
    """
    logger.info(f"Uploading results for scan {scan_id}")
    
    bucket = storage.bucket()
    db = firestore.client()
    
    # Upload mask to Storage
    mask_blob_path = f"segmentations/{scan_id}/mask.nrrd"
    blob = bucket.blob(mask_blob_path)
    blob.upload_from_filename(mask_path)
    
    mask_url = f"gs://{bucket.name}/{mask_blob_path}"
    
    logger.info(f"Mask uploaded to {mask_url}")
    
    # Create segmentation document in Firestore
    import uuid
    segmentation_id = str(uuid.uuid4())
    
    segmentation_data = {
        "id": segmentation_id,
        "scan_id": scan_id,
        "mask_url": mask_url,
        "model_version": "yolov10s_monai_unet_v1",
        "metrics": metrics,
        "created_at": datetime.utcnow()
    }
    
    db.collection('segmentations').document(segmentation_id).set(segmentation_data)
    
    logger.info(f"Segmentation document created: {segmentation_id}")
    
    # Create quantification documents
    for quant in quantification:
        quant_id = str(uuid.uuid4())
        quant_data = {
            "id": quant_id,
            "segmentation_id": segmentation_id,
            **quant
        }
        db.collection('quantification_results').document(quant_id).set(quant_data)
    
    logger.info(f"Created {len(quantification)} quantification documents")
    
    return segmentation_id


def run_pipeline(scan_id: str):
    """
    Run complete YOLOv10 + MONAI pipeline
    
    Args:
        scan_id: Scan ID to process
    """
    logger.info(f"Starting pipeline for scan {scan_id}")
    logger.info("=" * 80)
    
    # Stage 1: Download scan
    logger.info("Stage 1: Downloading scan from Firebase")
    tiff_path = download_scan_from_firebase(scan_id)
    
    # Stage 2: Preprocess - extract slices
    logger.info("Stage 2: Preprocessing TIFF")
    volume, slices = extract_slices_from_tiff(tiff_path)
    slices_normalized = [normalize_slice(s) for s in slices]
    
    # Stage 3: YOLOv10 detection
    logger.info("Stage 3: Running YOLOv10 detection")
    detector = YOLODetector(model_path=YOLO_WEIGHTS, confidence=0.25)
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
    
    # Stage 4: Preprocess volume for MONAI
    logger.info("Stage 4: Preprocessing volume for MONAI")
    roi_volume_normalized = preprocess_volume(roi_volume)
    
    # Stage 5: MONAI segmentation
    logger.info("Stage 5: Running MONAI segmentation")
    segmenter = MONAISegmenter(
        model_type="unet",
        model_path=MONAI_WEIGHTS if os.path.exists(MONAI_WEIGHTS) else None,
        out_channels=len(ORGAN_NAMES) + 1  # +1 for background
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
    
    # Stage 6: Quantification
    logger.info("Stage 6: Computing quantification metrics")
    quantification_results = quantify_segmentation(
        mask,
        ORGAN_NAMES,
        spacing=(1.0, 1.0, 1.0)  # Update with actual spacing if available
    )
    
    # Stage 7: Save results locally
    logger.info("Stage 7: Saving results")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    mask_path_nrrd = os.path.join(RESULTS_DIR, f"{scan_id}_mask.nrrd")
    save_mask_as_nrrd(mask, mask_path_nrrd)
    
    # Save quantification as JSON
    quant_path = os.path.join(RESULTS_DIR, f"{scan_id}_quantification.json")
    with open(quant_path, 'w') as f:
        json.dump(quantification_results, f, indent=2)
    
    logger.info(f"Results saved to {RESULTS_DIR}/")
    
    # Stage 8: Upload results to Firebase
    logger.info("Stage 8: Uploading results to Firebase")
    segmentation_id = upload_results_to_firebase(
        scan_id,
        mask_path_nrrd,
        seg_metrics,
        quantification_results
    )
    
    logger.info("=" * 80)
    logger.info(f"Pipeline completed successfully for scan {scan_id}")
    logger.info(f"Segmentation ID: {segmentation_id}")
    
    return segmentation_id


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python run_yolo10_monai.py <scan_id> [job_id]")
        sys.exit(1)
    
    scan_id = sys.argv[1]
    job_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    logger.info(f"Scan ID: {scan_id}")
    if job_id:
        logger.info(f"Job ID: {job_id}")
    
    try:
        # Initialize Firebase
        initialize_firebase()
        
        # Run pipeline
        segmentation_id = run_pipeline(scan_id)
        
        # Update job status if job_id provided
        if job_id:
            db = firestore.client()
            # Note: Individual scan completion doesn't complete the whole job
            # Job status is updated by the SLURM script or researcher
            logger.info(f"Scan {scan_id} completed for job {job_id}")
        
        logger.info("Success!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


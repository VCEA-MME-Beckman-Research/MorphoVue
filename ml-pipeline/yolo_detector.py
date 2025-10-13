"""
YOLOv10 detection module for tick CT scans
Performs 2D detection on slices and aggregates to 3D bounding volume
"""

import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Dict
import logging
import torch

logger = logging.getLogger(__name__)


class YOLODetector:
    def __init__(self, model_path: str = "yolov10s.pt", confidence: float = 0.25):
        """
        Initialize YOLOv10 detector
        
        Args:
            model_path: Path to YOLOv10 weights
            confidence: Detection confidence threshold
        """
        self.model = YOLO(model_path)
        self.confidence = confidence
        logger.info(f"Loaded YOLOv10 model from {model_path}")
    
    def detect_slice(self, slice_image: np.ndarray) -> List[Dict]:
        """
        Detect objects in a single slice
        
        Args:
            slice_image: 2D numpy array
        
        Returns:
            List of detection dictionaries
        """
        # Ensure RGB format
        if slice_image.ndim == 2:
            slice_rgb = np.stack([slice_image] * 3, axis=-1)
        else:
            slice_rgb = slice_image
        
        # Run detection
        results = self.model.predict(
            source=slice_rgb,
            conf=self.confidence,
            save=False,
            verbose=False
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                
                detections.append({
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': float(conf),
                    'class': cls
                })
        
        return detections
    
    def detect_volume(self, slices: List[np.ndarray]) -> List[List[Dict]]:
        """
        Detect objects in all slices
        
        Args:
            slices: List of 2D numpy arrays
        
        Returns:
            List of detection lists (one per slice)
        """
        all_detections = []
        
        for i, slice_img in enumerate(slices):
            detections = self.detect_slice(slice_img)
            all_detections.append(detections)
            
            if detections:
                logger.info(f"Slice {i}: Found {len(detections)} detections")
        
        return all_detections
    
    def aggregate_to_3d_bbox(
        self,
        slice_detections: List[List[Dict]],
        volume_shape: Tuple[int, int, int]
    ) -> Dict:
        """
        Aggregate 2D detections into 3D bounding box
        
        Args:
            slice_detections: List of detection lists
            volume_shape: Shape of original volume (Z, Y, X)
        
        Returns:
            3D bounding box dictionary
        """
        if not any(slice_detections):
            logger.warning("No detections found in any slice")
            return None
        
        # Collect all bounding box coordinates
        all_x1, all_y1, all_x2, all_y2 = [], [], [], []
        z_indices = []
        
        for z, detections in enumerate(slice_detections):
            for det in detections:
                bbox = det['bbox']
                all_x1.append(bbox[0])
                all_y1.append(bbox[1])
                all_x2.append(bbox[2])
                all_y2.append(bbox[3])
                z_indices.append(z)
        
        if not all_x1:
            return None
        
        # Compute 3D bounding box
        x_min = int(min(all_x1))
        y_min = int(min(all_y1))
        x_max = int(max(all_x2))
        y_max = int(max(all_y2))
        z_min = int(min(z_indices))
        z_max = int(max(z_indices))
        
        # Add padding (10% of dimension)
        padding_x = int((x_max - x_min) * 0.1)
        padding_y = int((y_max - y_min) * 0.1)
        padding_z = int((z_max - z_min) * 0.1)
        
        x_min = max(0, x_min - padding_x)
        y_min = max(0, y_min - padding_y)
        z_min = max(0, z_min - padding_z)
        x_max = min(volume_shape[2], x_max + padding_x)
        y_max = min(volume_shape[1], y_max + padding_y)
        z_max = min(volume_shape[0], z_max + padding_z)
        
        bbox_3d = {
            'x_min': x_min,
            'y_min': y_min,
            'z_min': z_min,
            'x_max': x_max,
            'y_max': y_max,
            'z_max': z_max,
            'num_detections': len(all_x1)
        }
        
        logger.info(f"3D bounding box: {bbox_3d}")
        
        return bbox_3d
    
    def crop_volume(self, volume: np.ndarray, bbox_3d: Dict) -> np.ndarray:
        """
        Crop volume to 3D bounding box
        
        Args:
            volume: 3D numpy array (Z, Y, X)
            bbox_3d: 3D bounding box dictionary
        
        Returns:
            Cropped volume
        """
        if bbox_3d is None:
            logger.warning("No bounding box provided, returning full volume")
            return volume
        
        cropped = volume[
            bbox_3d['z_min']:bbox_3d['z_max'],
            bbox_3d['y_min']:bbox_3d['y_max'],
            bbox_3d['x_min']:bbox_3d['x_max']
        ]
        
        logger.info(f"Cropped volume shape: {cropped.shape}")
        
        return cropped


if __name__ == "__main__":
    # Test detector
    from preprocess_tiff import extract_slices_from_tiff, normalize_slice
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python yolo_detector.py <path_to_tiff>")
        sys.exit(1)
    
    tiff_path = sys.argv[1]
    volume, slices = extract_slices_from_tiff(tiff_path)
    
    # Normalize slices
    slices_normalized = [normalize_slice(s) for s in slices]
    
    # Initialize detector
    detector = YOLODetector()
    
    # Detect
    detections = detector.detect_volume(slices_normalized)
    
    # Aggregate to 3D bbox
    bbox_3d = detector.aggregate_to_3d_bbox(detections, volume.shape)
    
    if bbox_3d:
        # Crop volume
        cropped = detector.crop_volume(volume, bbox_3d)
        print(f"Cropped volume shape: {cropped.shape}")
    else:
        print("No detections found")


"""
MONAI segmentation module for 3D tick organ segmentation
Uses UNet/VNet for volumetric segmentation
"""

import numpy as np
import torch
from monai.networks.nets import UNet, VNet
from monai.transforms import (
    Compose, EnsureChannelFirst, ScaleIntensity, Resize,
    AsDiscrete, KeepLargestConnectedComponent
)
from monai.inferers import sliding_window_inference
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class MONAISegmenter:
    def __init__(
        self,
        model_type: str = "unet",
        model_path: str = None,
        in_channels: int = 1,
        out_channels: int = 4,
        device: str = None
    ):
        """
        Initialize MONAI segmenter
        
        Args:
            model_type: "unet" or "vnet"
            model_path: Path to trained weights
            in_channels: Number of input channels (1 for grayscale)
            out_channels: Number of output classes (background + organs)
            device: Device to use (cuda/cpu)
        """
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        logger.info(f"Using device: {self.device}")
        
        # Initialize model
        if model_type.lower() == "unet":
            self.model = UNet(
                spatial_dims=3,
                in_channels=in_channels,
                out_channels=out_channels,
                channels=(16, 32, 64, 128, 256),
                strides=(2, 2, 2, 2),
                num_res_units=2,
            )
        elif model_type.lower() == "vnet":
            self.model = VNet(
                spatial_dims=3,
                in_channels=in_channels,
                out_channels=out_channels,
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Load weights if provided
        if model_path:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            logger.info(f"Loaded weights from {model_path}")
        else:
            logger.warning("No weights provided, using random initialization")
        
        self.model.to(self.device)
        self.model.eval()
        
        self.out_channels = out_channels
    
    def preprocess(self, volume: np.ndarray, target_shape: Tuple[int, int, int] = None) -> torch.Tensor:
        """
        Preprocess volume for model input
        
        Args:
            volume: 3D numpy array (Z, Y, X)
            target_shape: Optional target shape for resizing
        
        Returns:
            Preprocessed tensor (1, 1, Z, Y, X)
        """
        transforms = [
            EnsureChannelFirst(),
            ScaleIntensity(),
        ]
        
        if target_shape:
            transforms.append(Resize(spatial_size=target_shape))
        
        transform = Compose(transforms)
        
        volume_tensor = transform(volume)
        volume_tensor = volume_tensor.unsqueeze(0)  # Add batch dimension
        
        return volume_tensor.to(self.device)
    
    def segment(
        self,
        volume: np.ndarray,
        roi_size: Tuple[int, int, int] = (64, 64, 64),
        sw_batch_size: int = 4
    ) -> Tuple[np.ndarray, Dict]:
        """
        Segment 3D volume
        
        Args:
            volume: 3D numpy array (Z, Y, X)
            roi_size: ROI size for sliding window inference
            sw_batch_size: Batch size for sliding window
        
        Returns:
            mask: Segmentation mask (Z, Y, X)
            metrics: Dictionary of metrics
        """
        original_shape = volume.shape
        
        # Preprocess
        volume_tensor = self.preprocess(volume)
        
        logger.info(f"Input shape: {volume_tensor.shape}")
        
        # Inference
        with torch.no_grad():
            # Use sliding window inference for large volumes
            output = sliding_window_inference(
                inputs=volume_tensor,
                roi_size=roi_size,
                sw_batch_size=sw_batch_size,
                predictor=self.model,
                overlap=0.5
            )
        
        # Post-process: convert logits to class predictions
        output = torch.argmax(output, dim=1)
        mask = output.cpu().numpy()[0]  # Remove batch dimension
        
        # Compute metrics
        metrics = self.compute_metrics(mask)
        
        logger.info(f"Segmentation complete. Output shape: {mask.shape}")
        logger.info(f"Unique labels: {np.unique(mask)}")
        
        return mask, metrics
    
    def compute_metrics(self, mask: np.ndarray) -> Dict:
        """
        Compute segmentation metrics
        
        Args:
            mask: Segmentation mask
        
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "num_classes": len(np.unique(mask)),
            "unique_labels": np.unique(mask).tolist(),
            "shape": mask.shape,
        }
        
        # Compute volume for each class
        for label in np.unique(mask):
            if label == 0:  # Skip background
                continue
            volume = np.sum(mask == label)
            metrics[f"class_{label}_volume"] = int(volume)
        
        return metrics
    
    def postprocess(self, mask: np.ndarray, remove_small_objects: bool = True) -> np.ndarray:
        """
        Post-process segmentation mask
        
        Args:
            mask: Raw segmentation mask
            remove_small_objects: Whether to keep only largest connected component
        
        Returns:
            Cleaned mask
        """
        if remove_small_objects:
            # Keep largest connected component for each class
            cleaned_mask = np.zeros_like(mask)
            
            for label in np.unique(mask):
                if label == 0:  # Skip background
                    continue
                
                binary_mask = (mask == label).astype(np.uint8)
                
                # Create transform to keep largest component
                keep_largest = KeepLargestConnectedComponent()
                binary_tensor = torch.from_numpy(binary_mask).unsqueeze(0).unsqueeze(0)
                largest = keep_largest(binary_tensor)
                
                cleaned_mask[largest[0, 0].numpy() > 0] = label
            
            return cleaned_mask
        
        return mask


if __name__ == "__main__":
    # Test segmenter
    import sys
    
    # Create dummy volume for testing
    volume = np.random.rand(64, 128, 128).astype(np.float32)
    
    print(f"Test volume shape: {volume.shape}")
    
    # Initialize segmenter
    segmenter = MONAISegmenter(model_type="unet", out_channels=4)
    
    # Segment
    mask, metrics = segmenter.segment(volume, roi_size=(32, 64, 64))
    
    print(f"Output mask shape: {mask.shape}")
    print(f"Metrics: {metrics}")


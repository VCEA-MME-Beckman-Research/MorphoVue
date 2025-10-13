"""
Multi-page TIFF preprocessing module
Extracts individual slices from TIFF files
"""

import numpy as np
from PIL import Image
import SimpleITK as sitk
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def extract_slices_from_tiff(tiff_path: str) -> Tuple[np.ndarray, List[np.ndarray]]:
    """
    Extract all slices from a multi-page TIFF file
    
    Args:
        tiff_path: Path to TIFF file
    
    Returns:
        volume: 3D numpy array (Z, Y, X)
        slices: List of 2D numpy arrays
    """
    try:
        # Try using SimpleITK first (better for medical images)
        image = sitk.ReadImage(tiff_path)
        volume = sitk.GetArrayFromImage(image)
        
        # If single slice, expand dimensions
        if volume.ndim == 2:
            volume = np.expand_dims(volume, axis=0)
        
        slices = [volume[i] for i in range(volume.shape[0])]
        
        logger.info(f"Extracted {len(slices)} slices from {tiff_path}")
        logger.info(f"Volume shape: {volume.shape}")
        
        return volume, slices
        
    except Exception as e:
        logger.warning(f"SimpleITK failed, trying PIL: {e}")
        
        # Fallback to PIL for multi-page TIFF
        img = Image.open(tiff_path)
        slices = []
        
        try:
            i = 0
            while True:
                img.seek(i)
                slice_array = np.array(img)
                slices.append(slice_array)
                i += 1
        except EOFError:
            pass
        
        volume = np.stack(slices, axis=0)
        
        logger.info(f"Extracted {len(slices)} slices from {tiff_path} using PIL")
        logger.info(f"Volume shape: {volume.shape}")
        
        return volume, slices


def normalize_slice(slice_array: np.ndarray) -> np.ndarray:
    """
    Normalize slice to 0-255 uint8 range
    
    Args:
        slice_array: Input slice
    
    Returns:
        Normalized slice as uint8
    """
    # Convert to float
    slice_float = slice_array.astype(np.float32)
    
    # Normalize to 0-255
    slice_min = slice_float.min()
    slice_max = slice_float.max()
    
    if slice_max > slice_min:
        normalized = ((slice_float - slice_min) / (slice_max - slice_min) * 255)
    else:
        normalized = slice_float
    
    return normalized.astype(np.uint8)


def save_slices_as_images(slices: List[np.ndarray], output_dir: str, prefix: str = "slice"):
    """
    Save slices as individual image files
    
    Args:
        slices: List of slice arrays
        output_dir: Output directory
        prefix: Filename prefix
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for i, slice_array in enumerate(slices):
        normalized = normalize_slice(slice_array)
        
        # Convert to RGB if grayscale
        if normalized.ndim == 2:
            rgb_slice = np.stack([normalized] * 3, axis=-1)
        else:
            rgb_slice = normalized
        
        # Save as PNG
        img = Image.fromarray(rgb_slice)
        output_path = os.path.join(output_dir, f"{prefix}_{i:04d}.png")
        img.save(output_path)
    
    logger.info(f"Saved {len(slices)} slices to {output_dir}")


def preprocess_volume(volume: np.ndarray) -> np.ndarray:
    """
    Preprocess 3D volume for MONAI input
    
    Args:
        volume: 3D numpy array
    
    Returns:
        Preprocessed volume
    """
    # Normalize to 0-1 range
    volume = volume.astype(np.float32)
    volume_min = volume.min()
    volume_max = volume.max()
    
    if volume_max > volume_min:
        volume = (volume - volume_min) / (volume_max - volume_min)
    
    return volume


if __name__ == "__main__":
    # Test preprocessing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python preprocess_tiff.py <path_to_tiff>")
        sys.exit(1)
    
    tiff_path = sys.argv[1]
    volume, slices = extract_slices_from_tiff(tiff_path)
    
    print(f"Volume shape: {volume.shape}")
    print(f"Number of slices: {len(slices)}")
    print(f"Slice shape: {slices[0].shape}")
    
    # Save slices
    save_slices_as_images(slices, "tmp/slices", "test_slice")
    print("Slices saved to tmp/slices/")


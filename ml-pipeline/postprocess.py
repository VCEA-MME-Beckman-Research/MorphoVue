"""
Post-processing and quantification module
Computes organ-level statistics from segmentation masks
"""

import numpy as np
import logging
from typing import Dict, List, Tuple

# Optional deps: SimpleITK and SciPy (provide fallbacks if unavailable)
try:
    import SimpleITK as sitk  # type: ignore
except Exception:  # pragma: no cover - optional
    sitk = None  # type: ignore

try:
    from scipy import ndimage as sp_ndimage  # type: ignore
except Exception:  # pragma: no cover - optional
    sp_ndimage = None  # type: ignore

logger = logging.getLogger(__name__)


def compute_organ_volume(
    mask: np.ndarray,
    label: int,
    spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
) -> float:
    """
    Compute volume of a specific organ label
    
    Args:
        mask: Segmentation mask
        label: Organ label
        spacing: Voxel spacing (z, y, x) in mm
    
    Returns:
        Volume in mm³
    """
    binary_mask = (mask == label)
    num_voxels = np.sum(binary_mask)
    
    voxel_volume = spacing[0] * spacing[1] * spacing[2]
    volume_mm3 = num_voxels * voxel_volume
    
    return float(volume_mm3)


def compute_surface_area(
    mask: np.ndarray,
    label: int,
    spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
) -> float:
    """
    Compute surface area of a specific organ label
    
    Args:
        mask: Segmentation mask
        label: Organ label
        spacing: Voxel spacing (z, y, x) in mm
    
    Returns:
        Surface area in mm²
    """
    binary_mask = (mask == label).astype(np.uint8)

    # Preferred path with SimpleITK if available
    if sitk is not None:
        try:
            sitk_mask = sitk.GetImageFromArray(binary_mask)
            sitk_mask.SetSpacing(spacing[::-1])  # SimpleITK uses (x, y, z)
            label_shape_filter = sitk.LabelShapeStatisticsImageFilter()
            label_shape_filter.Execute(sitk_mask)
            # Not all versions expose surface area directly; approximate via perimeter or fallback
            try:
                return float(label_shape_filter.GetPerimeter(1))
            except Exception:
                pass
        except Exception:
            pass

    # Fallback without SimpleITK/SciPy: count boundary faces between label and background
    z, y, x = binary_mask.shape
    sz, sy, sx = spacing

    def count_axis_faces(axis: int) -> int:
        # Compare adjacent voxels along axis; count faces where value changes
        if axis == 0:  # z
            a = binary_mask[:-1, :, :]
            b = binary_mask[1:, :, :]
        elif axis == 1:  # y
            a = binary_mask[:, :-1, :]
            b = binary_mask[:, 1:, :]
        else:  # x
            a = binary_mask[:, :, :-1]
            b = binary_mask[:, :, 1:]
        # Count faces where exactly one of the two is 1
        return int(np.count_nonzero(a != b))

    faces_z = count_axis_faces(0)
    faces_y = count_axis_faces(1)
    faces_x = count_axis_faces(2)

    area_z = faces_z * (sy * sx)
    area_y = faces_y * (sz * sx)
    area_x = faces_x * (sz * sy)
    return float(area_x + area_y + area_z)


def compute_centroid(mask: np.ndarray, label: int) -> List[float]:
    """
    Compute centroid of a specific organ label
    
    Args:
        mask: Segmentation mask
        label: Organ label
    
    Returns:
        Centroid coordinates [z, y, x]
    """
    binary_mask = (mask == label)
    if sp_ndimage is not None:
        try:
            centroid = sp_ndimage.center_of_mass(binary_mask)
            return [float(c) for c in centroid]
        except Exception:
            pass
    # Fallback: mean of coordinates
    coords = np.argwhere(binary_mask)
    if coords.size == 0:
        return [0.0, 0.0, 0.0]
    centroid = coords.mean(axis=0)
    return [float(c) for c in centroid]


def compute_bounding_box(mask: np.ndarray, label: int) -> Dict:
    """
    Compute bounding box of a specific organ label
    
    Args:
        mask: Segmentation mask
        label: Organ label
    
    Returns:
        Bounding box dictionary
    """
    binary_mask = (mask == label)
    
    # Find non-zero coordinates
    coords = np.argwhere(binary_mask)
    
    if len(coords) == 0:
        return None
    
    # Compute min and max for each dimension
    z_min, y_min, x_min = coords.min(axis=0)
    z_max, y_max, x_max = coords.max(axis=0)
    
    return {
        'z_min': int(z_min),
        'y_min': int(y_min),
        'x_min': int(x_min),
        'z_max': int(z_max),
        'y_max': int(y_max),
        'x_max': int(x_max)
    }


def quantify_segmentation(
    mask: np.ndarray,
    organ_names: Dict[int, str],
    spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
) -> List[Dict]:
    """
    Compute quantification metrics for all organs
    
    Args:
        mask: Segmentation mask
        organ_names: Dictionary mapping labels to organ names
        spacing: Voxel spacing (z, y, x) in mm
    
    Returns:
        List of quantification dictionaries
    """
    results = []
    
    unique_labels = np.unique(mask)
    
    for label in unique_labels:
        if label == 0:  # Skip background
            continue
        
        organ_name = organ_names.get(label, f"organ_{label}")
        
        logger.info(f"Quantifying {organ_name} (label {label})")
        
        # Compute metrics
        volume = compute_organ_volume(mask, label, spacing)
        surface_area = compute_surface_area(mask, label, spacing)
        centroid = compute_centroid(mask, label)
        bbox = compute_bounding_box(mask, label)
        
        result = {
            "organ_name": organ_name,
            "label": int(label),
            "volume": volume,
            "surface_area": surface_area,
            "centroid": centroid,
            "bounding_box": bbox,
            "additional_metrics": {
                "num_voxels": int(np.sum(mask == label))
            }
        }
        
        results.append(result)
        
        logger.info(f"  Volume: {volume:.2f} mm³")
        logger.info(f"  Surface area: {surface_area:.2f} mm²")
        logger.info(f"  Centroid: {centroid}")
    
    return results


def save_mask_as_nrrd(mask: np.ndarray, output_path: str, spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)):
    """
    Save segmentation mask as NRRD file
    
    Args:
        mask: Segmentation mask
        output_path: Output file path
        spacing: Voxel spacing (z, y, x) in mm
    """
    sitk_mask = sitk.GetImageFromArray(mask.astype(np.uint8))
    sitk_mask.SetSpacing(spacing[::-1])  # SimpleITK uses (x, y, z)
    
    sitk.WriteImage(sitk_mask, output_path)
    logger.info(f"Saved mask to {output_path}")


def save_mask_as_nifti(mask: np.ndarray, output_path: str, spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)):
    """
    Save segmentation mask as NIfTI file
    
    Args:
        mask: Segmentation mask
        output_path: Output file path
        spacing: Voxel spacing (z, y, x) in mm
    """
    sitk_mask = sitk.GetImageFromArray(mask.astype(np.uint8))
    sitk_mask.SetSpacing(spacing[::-1])  # SimpleITK uses (x, y, z)
    
    sitk.WriteImage(sitk_mask, output_path)
    logger.info(f"Saved mask to {output_path}")


if __name__ == "__main__":
    # Test quantification
    
    # Create dummy mask
    mask = np.zeros((64, 128, 128), dtype=np.uint8)
    
    # Add some dummy organs
    mask[20:40, 40:80, 40:80] = 1  # Organ 1
    mask[30:50, 60:100, 60:100] = 2  # Organ 2
    
    organ_names = {
        1: "digestive_tract",
        2: "reproductive_organs",
        3: "neural_tissue"
    }
    
    # Quantify
    results = quantify_segmentation(mask, organ_names, spacing=(0.1, 0.1, 0.1))
    
    print("\nQuantification Results:")
    for result in results:
        print(f"\n{result['organ_name']}:")
        print(f"  Volume: {result['volume']:.2f} mm³")
        print(f"  Surface area: {result['surface_area']:.2f} mm²")
        print(f"  Centroid: {result['centroid']}")
    
    # Save mask
    save_mask_as_nrrd(mask, "tmp/test_mask.nrrd")
    print("\nMask saved to tmp/test_mask.nrrd")


import numpy as np
from postprocess import quantify_segmentation


def test_quantify_segmentation_basic():
    mask = np.zeros((10, 10, 10), dtype=np.uint8)
    mask[2:5, 2:5, 2:5] = 1
    organ_names = {1: 'organ1'}

    results = quantify_segmentation(mask, organ_names, spacing=(1.0, 1.0, 1.0))
    assert len(results) == 1
    r = results[0]
    assert r['organ_name'] == 'organ1'
    # Volume should equal number of voxels (3*3*3)
    assert r['additional_metrics']['num_voxels'] == 27

# 3D Slicer Module - Tick Segmentation Review

3D Slicer extension for reviewing and correcting CT tick segmentations from MorphoVue.

## Features

- Load CT scans and segmentation masks from Firebase
- Review segmentations in 3D
- Manually correct segmentation masks using Slicer's tools
- Compute organ-level statistics (volume, surface area)
- Export corrected masks back to Firebase

## Installation

### Option 1: Manual Installation

1. Open 3D Slicer
2. Go to Edit → Application Settings → Modules
3. Add the path to `slicer-module/` directory under "Additional module paths"
4. Restart 3D Slicer
5. The module will appear under the "Segmentation" category

### Option 2: Extension Installation (Future)

Once packaged as an extension:
```bash
# Install via Extension Manager in 3D Slicer
```

## Usage

### Loading Data

1. Open the "Tick Segmentation Review" module
2. Enter the Scan ID from MorphoVue
3. Click "Load from Firebase"
   - Select the CT scan TIFF file
   - Select the segmentation mask NRRD file
4. The scan and mask will be displayed in 3D

### Reviewing Segmentation

1. Use 3D Slicer's built-in visualization tools:
   - Slice views (Red, Yellow, Green)
   - 3D view with volume rendering
   - Segmentation overlay controls

2. Edit segmentation if needed:
   - Use the "Segment Editor" module
   - Tools: Paint, Erase, Scissors, Level Tracing, etc.
   - Modify individual segments

### Computing Statistics

1. With both CT scan and segmentation selected
2. Click "Compute Statistics"
3. View results in the Statistics section:
   - Volume (mm³)
   - Surface area (mm²)
   - Centroid coordinates

### Exporting Results

1. **Export Mask**: Save segmentation as NRRD/NIfTI file
2. **Upload to Firebase**: Save corrected mask for upload

## Firebase Integration

The module includes placeholders for Firebase integration. To implement:

1. Install Firebase Python SDK:
```python
pip install firebase-admin
```

2. Add Firebase credentials to 3D Slicer Python environment

3. Implement download/upload functions in `TickSegmentationReview.py`

## Development

### File Structure

```
slicer-module/
├── TickSegmentationReview/
│   ├── TickSegmentationReview.py       # Main module
│   └── Resources/
│       └── UI/
│           └── TickSegmentationReview.ui  # Qt UI file
└── README.md
```

### Testing

Run tests in 3D Slicer Python console:
```python
import TickSegmentationReview
tester = TickSegmentationReview.TickSegmentationReviewTest()
tester.runTest()
```

## Keyboard Shortcuts

When in 3D Slicer:
- `Ctrl+0`: Reset 3D view
- `Shift+Mouse Drag`: Window/level adjustment
- `Ctrl+Mouse Wheel`: Zoom in slice views

## Troubleshooting

### Module doesn't appear
- Check that the module path is added correctly in Application Settings
- Restart 3D Slicer
- Check Python console for errors

### Can't load TIFF files
- 3D Slicer may require ITK or custom readers for multi-page TIFFs
- Convert to NRRD format first: `slicer --python-code "slicer.util.loadVolume('scan.tiff'); slicer.util.saveNode(slicer.util.getNode('scan'), 'scan.nrrd')"`

### Statistics computation fails
- Ensure both volume and segmentation are selected
- Check that segmentation has valid segments

## Resources

- [3D Slicer Documentation](https://slicer.readthedocs.io/)
- [Scripted Modules Guide](https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html)
- [Segment Editor](https://slicer.readthedocs.io/en/latest/user_guide/modules/segmenteditor.html)


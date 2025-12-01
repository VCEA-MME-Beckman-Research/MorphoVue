# MorphoVue Local MVP Setup Guide

This guide explains how to set up and run the MorphoVue pipeline locally using dummy models for testing and development.

## Prerequisites

- Python 3.9+
- 3D Slicer (installed locally)

## 1. Environment Setup

Create a virtual environment and install dependencies:

```bash
cd ml-pipeline

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** If you don't have GPU support, PyTorch will install the CPU version automatically.

## 2. Directory Structure

The local pipeline expects the following structure (created automatically):

```
ml-pipeline/
├── input/              # Place your TIFF files here
├── results/            # Output directory
│   └── <scan_name>/    # Results for each scan
│       ├── mask.nrrd          # Segmentation mask
│       ├── quantification.json # Computed metrics
│       ├── metadata.json       # Processing info
│       └── processing.log      # Logs
└── ...
```

## 3. Running the Pipeline

You can run the pipeline on a specific TIFF file using the provided script:

```bash
# Using the example workflow (creates a dummy TIFF if none provided)
python example_workflow.py

# OR specifying your own file
python run_local_segmentation.py path/to/your/scan.tiff
```

### What happens during execution?

Since this is the **MVP / Dummy Mode**:
1. **YOLOv10 Detector** generates random bounding boxes instead of running a real model.
2. **MONAI Segmenter** generates simple geometric shapes (spheres) as dummy organs.
3. **Pipeline** processes these dummy results exactly as it would real ones, generating valid NRRD masks and JSON metrics.

This allows you to verify the entire workflow (loading, processing, saving, visualization) without needing trained model weights.

## 4. Reviewing in 3D Slicer

1. **Install the Module:**
   - Open 3D Slicer
   - Go to **Edit -> Application Settings -> Modules**
   - Add the `slicer-module` directory path to **Additional module paths**
   - Restart Slicer

2. **Use the Module:**
   - Select **Tick Segmentation Review** from the module dropdown
   - Click **Load from Local**
   - Select your input TIFF file (e.g., from `ml-pipeline/input/`)
   - If the mask is in the standard `results/` location, it will auto-load. If not, you'll be prompted to select the `.nrrd` file.

3. **Review & Edit:**
   - Use the **Segment Editor** (built into Slicer) to modify the mask
   - Click **Compute Statistics** to see updated organ volumes
   - Click **Save to Local** to save your corrections back to disk

## Troubleshooting

- **Missing Dependencies:** Ensure all packages in `requirements.txt` are installed.
- **Slicer Module Not Found:** Verify the path added to Slicer points to the parent folder containing `TickSegmentationReview/`.
- **Mask Mismatch:** Ensure the NRRD mask dimensions match the TIFF volume. The pipeline handles this automatically.


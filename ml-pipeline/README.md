# ML Pipeline - YOLOv10 + MONAI

Machine learning pipeline for CT tick scan analysis on Kamiak HPC.

## Architecture

1. **YOLOv10 Detection**: 2D object detection on slices → 3D ROI aggregation
2. **MONAI Segmentation**: 3D UNet/VNet on cropped ROI → organ masks
3. **Quantification**: Volume, surface area, and statistics computation

## Setup on Kamiak

### First-time Setup

1. SSH to Kamiak:
```bash
ssh <username>@kamiak.wsu.edu
```

2. Clone repository:
```bash
cd ~
git clone <repository-url> MorphoVue
cd MorphoVue/ml-pipeline
```

3. Setup environment:
```bash
bash setup_env.sh
```

4. Download Firebase credentials:
```bash
# Copy firebase-key.json to ml-pipeline directory
# You can download it from Firebase Console or copy via scp
scp /local/path/firebase-key.json <username>@kamiak.wsu.edu:~/MorphoVue/ml-pipeline/
```

5. Download model weights:
```bash
mkdir -p weights
cd weights

# Download YOLOv10 pretrained weights
wget https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10s.pt

# MONAI weights will be provided after training
# For now, the pipeline will initialize with random weights (for testing)
```

6. Create directories:
```bash
cd ~/MorphoVue/ml-pipeline
mkdir -p logs tmp results
```

### Environment Variables

Create `.env` file or export:
```bash
export FIREBASE_CREDENTIALS_PATH=~/MorphoVue/ml-pipeline/firebase-key.json
export FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
export YOLO_WEIGHTS=~/MorphoVue/ml-pipeline/weights/yolov10s.pt
export MONAI_WEIGHTS=~/MorphoVue/ml-pipeline/weights/monai_unet.pth
```

## Running the Pipeline

### Single Scan

```bash
# Activate environment
source activate tickml

# Run pipeline
python3 run_yolo10_monai.py <scan_id>
```

### Batch Processing (SLURM)

1. Get job script from web interface
2. Copy to Kamiak:
```bash
scp job_<job_id>.sh <username>@kamiak.wsu.edu:~/MorphoVue/ml-pipeline/
```

3. Submit job:
```bash
cd ~/MorphoVue/ml-pipeline
sbatch job_<job_id>.sh
```

4. Monitor job:
```bash
# Check job status
squeue -u $USER

# View output logs
tail -f logs/cttick_*.out

# View error logs
tail -f logs/cttick_*.err
```

### Cancel Job

```bash
scancel <job_id>
```

## Pipeline Stages

### Stage 1: Download
Downloads TIFF scan from Firebase Storage

### Stage 2: Preprocessing
Extracts slices from multi-page TIFF

### Stage 3: YOLOv10 Detection
- Runs detection on each 2D slice
- Aggregates bounding boxes into 3D ROI
- Crops volume to ROI

### Stage 4: MONAI Preprocessing
Normalizes cropped volume

### Stage 5: MONAI Segmentation
- 3D UNet segmentation
- Sliding window inference for large volumes
- Outputs multi-class organ masks

### Stage 6: Quantification
Computes per-organ metrics:
- Volume (mm³)
- Surface area (mm²)
- Centroid
- Bounding box

### Stage 7: Save Results
Saves masks as NRRD and quantification as JSON

### Stage 8: Upload
Uploads results back to Firebase

## Testing Individual Modules

### Test TIFF Preprocessing
```bash
python3 preprocess_tiff.py sample.tiff
```

### Test YOLOv10 Detection
```bash
python3 yolo_detector.py sample.tiff
```

### Test MONAI Segmentation
```bash
python3 monai_segmenter.py
```

### Test Quantification
```bash
python3 postprocess.py
```

## Training Models

### YOLOv10 Fine-tuning

```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO('yolov10s.pt')

# Fine-tune on tick CT data
results = model.train(
    data='tick_dataset.yaml',  # Your dataset config
    epochs=100,
    imgsz=640,
    batch=16,
    device=0
)
```

### MONAI Training

See `train_monai.py` (to be created) for full training script.

## Troubleshooting

### GPU not available
```bash
# Check GPU status
sinfo -p gpu

# Request interactive GPU session
salloc --partition=gpu --gres=gpu:1 --time=1:00:00
```

### Out of memory
Reduce `sw_batch_size` in `monai_segmenter.py` or use smaller ROI size.

### Firebase connection issues
Verify `firebase-key.json` has correct permissions and project ID.

## File Outputs

- `results/<scan_id>_mask.nrrd` - Segmentation mask
- `results/<scan_id>_quantification.json` - Organ metrics
- `logs/cttick_<job>_<array>.out` - Standard output
- `logs/cttick_<job>_<array>.err` - Error output


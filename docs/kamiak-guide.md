# Kamiak HPC Guide for MorphoVue

Complete guide for running the CT Tick ML pipeline on Kamiak HPC cluster.

## Table of Contents
1. [Getting Access](#getting-access)
2. [Initial Setup](#initial-setup)
3. [Running Jobs](#running-jobs)
4. [Monitoring](#monitoring)
5. [Troubleshooting](#troubleshooting)

## Getting Access

### Request Account
1. Contact WSU HPC support: hpc@wsu.edu
2. Request access to Kamiak cluster
3. Request GPU partition access for ML workloads
4. Receive your username and initial password

### First Login
```bash
ssh <username>@kamiak.wsu.edu
# Enter your password when prompted
# Change password on first login
```

## Initial Setup

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/your-org/MorphoVue.git
cd MorphoVue/ml-pipeline
```

### 2. Setup Conda Environment

```bash
# Run the setup script
bash setup_env.sh

# This will:
# - Load Anaconda module
# - Create 'tickml' conda environment
# - Install PyTorch with CUDA support
# - Install all required packages
```

### 3. Configure Firebase

```bash
# Copy Firebase credentials to Kamiak
# Option A: From local machine
scp /path/to/firebase-key.json <username>@kamiak.wsu.edu:~/MorphoVue/ml-pipeline/

# Option B: Download directly on Kamiak
# (Transfer file via secure method)
```

### 4. Set Environment Variables

Create `~/.bashrc_morphovue`:
```bash
export FIREBASE_CREDENTIALS_PATH=~/MorphoVue/ml-pipeline/firebase-key.json
export FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
export YOLO_WEIGHTS=~/MorphoVue/ml-pipeline/weights/yolov10s.pt
export MONAI_WEIGHTS=~/MorphoVue/ml-pipeline/weights/monai_unet.pth
```

Add to your `.bashrc`:
```bash
echo "source ~/.bashrc_morphovue" >> ~/.bashrc
source ~/.bashrc
```

### 5. Download Model Weights

```bash
cd ~/MorphoVue/ml-pipeline
mkdir -p weights
cd weights

# Download YOLOv10 pretrained weights
wget https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10s.pt

# MONAI weights (after training)
# Will be provided separately or trained on Kamiak
```

### 6. Create Directories

```bash
cd ~/MorphoVue/ml-pipeline
mkdir -p logs tmp results
```

## Running Jobs

### Single Scan Test

Test the pipeline on a single scan:

```bash
# Activate environment
source activate tickml

# Run pipeline
python3 run_yolo10_monai.py <scan_id>

# Example:
python3 run_yolo10_monai.py abc123-def456-ghi789
```

### Batch Job Submission

#### From MorphoVue Web Interface

1. Go to "Batch Submit" page
2. Select project and scans
3. Click "Generate Job Script"
4. Follow the displayed instructions:

```bash
# 1. Download the job script
wget '<script_url>' -O job_<job_id>.sh

# 2. SSH to Kamiak
ssh <username>@kamiak.wsu.edu

# 3. Copy script to ml-pipeline directory
# (if downloaded locally, use scp first)
mv ~/job_<job_id>.sh ~/MorphoVue/ml-pipeline/

# 4. Navigate to directory
cd ~/MorphoVue/ml-pipeline

# 5. Submit job
sbatch job_<job_id>.sh
```

#### Example Job Script

```bash
#!/bin/bash
#SBATCH --job-name=cttick_pipeline
#SBATCH --output=logs/cttick_%A_%a.out
#SBATCH --error=logs/cttick_%A_%a.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --array=1-5

module load anaconda3
source activate tickml

SCAN_IDS=(scan_001 scan_002 scan_003 scan_004 scan_005)
SCAN_ID=${SCAN_IDS[$SLURM_ARRAY_TASK_ID-1]}
JOB_ID="your-job-id"

python3 run_yolo10_monai.py $SCAN_ID $JOB_ID
```

### SLURM Parameters

- `--job-name`: Job name (appears in queue)
- `--partition=gpu`: Use GPU partition
- `--gres=gpu:1`: Request 1 GPU
- `--time=02:00:00`: Max runtime (HH:MM:SS)
- `--array=1-N`: Array job for N scans
- `--mem=32G`: Memory (optional, default is sufficient)
- `--cpus-per-task=4`: CPU cores (optional)

## Monitoring

### Check Job Status

```bash
# View your jobs
squeue -u $USER

# Output:
# JOBID  PARTITION  NAME           USER      ST TIME  NODES NODELIST
# 123456 gpu        cttick_pipelin username  R  10:30 1     node42

# Status codes:
# PD = Pending (waiting for resources)
# R  = Running
# CG = Completing
# CD = Completed
```

### View Job Output

```bash
cd ~/MorphoVue/ml-pipeline/logs

# View output (while running)
tail -f cttick_<job_id>_<array_id>.out

# View errors
tail -f cttick_<job_id>_<array_id>.err

# View completed job output
cat cttick_<job_id>_<array_id>.out
```

### Check GPU Usage

```bash
# View GPU partition status
sinfo -p gpu

# View GPU utilization (when job is running)
srun --partition=gpu --gres=gpu:1 --pty nvidia-smi
```

### Cancel Job

```bash
# Cancel specific job
scancel <job_id>

# Cancel all your jobs
scancel -u $USER

# Cancel specific array task
scancel <job_id>_<array_task_id>
```

## File Management

### Check Disk Usage

```bash
# Your home directory
du -sh ~

# ML pipeline directory
du -sh ~/MorphoVue/ml-pipeline

# Check quota
quota -s
```

### Clean Up Temporary Files

```bash
cd ~/MorphoVue/ml-pipeline

# Remove temporary files
rm -rf tmp/*

# Remove old logs (keep last 30 days)
find logs -name "*.out" -mtime +30 -delete
find logs -name "*.err" -mtime +30 -delete

# Results are uploaded to Firebase, so can be removed locally
rm -rf results/*
```

### Transfer Files

```bash
# From Kamiak to local machine
scp <username>@kamiak.wsu.edu:~/MorphoVue/ml-pipeline/results/*.nrrd ./

# From local to Kamiak
scp local_file.tiff <username>@kamiak.wsu.edu:~/MorphoVue/ml-pipeline/tmp/
```

## Troubleshooting

### Job Fails Immediately

Check error log:
```bash
cat logs/cttick_<job_id>_<array_id>.err
```

Common issues:
- **Module not found**: Environment not activated properly
- **Firebase error**: Check credentials path
- **CUDA error**: GPU not available or out of memory
- **File not found**: Scan not downloaded from Firebase

### GPU Out of Memory

Reduce batch size in `monai_segmenter.py`:
```python
# Change sw_batch_size parameter
mask, metrics = segmenter.segment(
    roi_volume_normalized,
    roi_size=(64, 64, 64),  # Reduce if needed
    sw_batch_size=1  # Reduce from 2 to 1
)
```

### Job Pending for Long Time

```bash
# Check why job is pending
squeue -u $USER --start

# Check partition availability
sinfo -p gpu

# Consider:
# - Reduce requested time (--time)
# - Submit during off-peak hours
# - Check if GPU quota is exceeded
```

### Environment Issues

Recreate environment:
```bash
conda remove -n tickml --all
cd ~/MorphoVue/ml-pipeline
bash setup_env.sh
```

### Firebase Connection Issues

Test Firebase connection:
```bash
source activate tickml
python3 -c "
from firebase_admin import credentials, initialize_app
cred = credentials.Certificate('firebase-key.json')
app = initialize_app(cred)
print('Firebase connected successfully')
"
```

## Best Practices

1. **Test First**: Always test on single scan before batch submission
2. **Monitor Resources**: Check logs regularly
3. **Clean Up**: Remove temporary files after job completion
4. **Reasonable Time Limits**: Don't request excessive time (wastes resources)
5. **GPU Etiquette**: Don't hog GPUs - be considerate of other users
6. **Save Results**: Results auto-upload to Firebase, but verify before deletion

## Performance Tips

### Optimize Pipeline

- Use smaller ROI sizes for faster processing
- Adjust sliding window overlap (default 0.5)
- Use lower-resolution models if accuracy permits
- Process in batches of 5-10 scans

### Parallel Processing

Run multiple independent jobs:
```bash
# Submit multiple jobs (not array)
for project in proj1 proj2 proj3; do
    sbatch job_${project}.sh
done
```

## Getting Help

### Kamiak Support
- Email: hpc@wsu.edu
- Documentation: https://hpc.wsu.edu/
- Office Hours: Check HPC website

### MorphoVue Issues
- GitHub Issues: https://github.com/your-org/MorphoVue/issues
- Project Team: Contact via email

## Quick Reference

### Common Commands

```bash
# Submit job
sbatch job_script.sh

# Check status
squeue -u $USER

# View output
tail -f logs/cttick_*.out

# Cancel job
scancel <job_id>

# Interactive session
salloc --partition=gpu --gres=gpu:1 --time=1:00:00

# Check quota
quota -s

# Load environment
source activate tickml
```

### Resource Limits

- **Home Directory**: 100 GB quota
- **GPU Time**: Check with HPC support
- **Max Job Time**: 7 days (168 hours)
- **Max Array Size**: 1000 tasks

## Advanced Usage

### Interactive GPU Session

For debugging:
```bash
salloc --partition=gpu --gres=gpu:1 --time=1:00:00
source activate tickml
python3 run_yolo10_monai.py <scan_id>
```

### Custom Job Arrays

Process specific scans:
```bash
#SBATCH --array=1,3,5,7-10

# Only runs tasks 1, 3, 5, 7, 8, 9, 10
```

### Job Dependencies

Chain jobs:
```bash
# Submit job 1
job1=$(sbatch --parsable job1.sh)

# Submit job 2 after job 1 completes
sbatch --dependency=afterok:$job1 job2.sh
```


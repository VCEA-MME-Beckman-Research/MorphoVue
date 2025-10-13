#!/bin/bash
# Setup Conda environment for CT Tick ML Pipeline on Kamiak

echo "Setting up CT Tick ML environment on Kamiak..."

# Load Anaconda module
module load anaconda3

# Create conda environment
conda create -n tickml python=3.10 -y

# Activate environment
source activate tickml

# Install PyTorch with CUDA support
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y

# Install requirements
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p weights
mkdir -p tmp
mkdir -p results

echo "Environment setup complete!"
echo "To activate: source activate tickml"


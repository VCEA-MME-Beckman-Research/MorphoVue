# MorphoVue - CT Tick ML Platform

An end-to-end research platform for detecting, segmenting, and analyzing tick CT scans using YOLOv10 + MONAI hybrid ML pipeline with human-in-the-loop annotation via Label Studio.

## 🎯 Overview

MorphoVue enables researchers to:
- Upload and manage multi-page TIFF CT scans
- Annotate scans using integrated Label Studio
- Process scans with YOLOv10 detection + MONAI segmentation on Kamiak HPC
- Visualize results in 3D using VTK.js and 3D Slicer
- Track quantitative organ-level metrics

## 🏗️ Architecture

- **Frontend:** React + VTK.js + Chart.js
- **Backend:** FastAPI + Firebase (Firestore, Storage, Auth)
- **ML Pipeline:** YOLOv10 (detection) + MONAI (segmentation)
- **Compute:** Kamiak HPC Cluster (SLURM)
- **Annotation:** Label Studio (Docker)
- **Visualization:** 3D Slicer integration

## 📁 Project Structure

```
MorphoVue/
├── frontend/              # React application
├── backend/              # FastAPI server
├── ml-pipeline/          # Kamiak HPC scripts
├── slicer-module/        # 3D Slicer extension
├── docker/               # Docker Compose setup
├── firebase/             # Firebase configuration
└── docs/                 # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- Firebase CLI
- Kamiak HPC account (for ML processing)

### Local Development

1. **Setup Firebase**
```bash
cd firebase
npm install
firebase login
firebase init
```

2. **Start Backend Services**
```bash
cd docker
docker-compose up -d
```

3. **Start Frontend**
```bash
cd frontend
npm install
npm start
```

4. **Setup Kamiak Environment**
```bash
# SSH to Kamiak
ssh <username>@kamiak.wsu.edu
cd MorphoVue/ml-pipeline
bash setup_env.sh
```

## 📖 Researcher Workflow

1. **Create Project** - Login and create a new research project
2. **Upload Scans** - Drag-drop multi-page TIFF files
3. **Annotate** - Draw bounding boxes and segmentation masks in Label Studio
4. **Submit Batch** - Generate Kamiak job script for selected scans
5. **Run on Kamiak** - SSH to Kamiak and submit job via `sbatch`
6. **Review Results** - View 3D segmentations and organ metrics
7. **Iterate** - Refine annotations and retrain models

## 🔧 Configuration

See individual component READMEs:
- [Backend Configuration](backend/README.md)
- [Frontend Setup](frontend/README.md)
- [ML Pipeline Guide](ml-pipeline/README.md)
- [Kamiak Job Submission](docs/kamiak-guide.md)

## 📊 Key Features

- **Multi-page TIFF Support** - Automatic slice extraction
- **One-shot Learning** - Train on minimal annotated data
- **Batch Processing** - Submit multiple scans as array jobs
- **3D Visualization** - Web-based VTK.js and desktop 3D Slicer
- **Quantification** - Automatic organ volume, surface area, and statistics

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 📞 Support

For issues or questions, contact the VCEA MME Beckman Research team.


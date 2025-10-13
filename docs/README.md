# MorphoVue Documentation

Welcome to the MorphoVue documentation. This directory contains comprehensive guides for all aspects of the CT Tick ML Platform.

## Documentation Index

### Getting Started

- **[Main README](../README.md)** - Project overview and quick start
- **[User Guide](user-guide.md)** - Complete guide for researchers

### Setup and Deployment

- **[Deployment Guide](deployment-guide.md)** - Production deployment instructions
- **[Kamiak Guide](kamiak-guide.md)** - HPC cluster setup and usage

### Development

- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project
- **[Backend README](../backend/README.md)** - FastAPI backend documentation
- **[Frontend README](../frontend/README.md)** - React frontend documentation
- **[ML Pipeline README](../ml-pipeline/README.md)** - Machine learning pipeline
- **[3D Slicer README](../slicer-module/README.md)** - Slicer module documentation

## Quick Links

### For Researchers

Start here if you're using MorphoVue for CT tick analysis:

1. [User Guide](user-guide.md) - Complete usage instructions
2. [Kamiak Guide](kamiak-guide.md) - How to submit jobs to HPC

### For Administrators

Start here if you're deploying MorphoVue:

1. [Deployment Guide](deployment-guide.md) - Setup instructions
2. Firebase configuration in [firebase/](../firebase/)
3. Docker setup in [docker/](../docker/)

### For Developers

Start here if you're contributing to MorphoVue:

1. [Contributing Guide](../CONTRIBUTING.md) - Development workflow
2. Component-specific READMEs in each directory
3. [Main README](../README.md) - Architecture overview

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Firebase Hosting                      │
│                   (React Frontend)                       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Cloud Run)                 │
│         ┌─────────────────────────────────┐            │
│         │   Label Studio (Docker)         │            │
│         └─────────────────────────────────┘            │
└────────┬────────────────────────────┬───────────────────┘
         │                            │
         ▼                            ▼
┌─────────────────┐          ┌─────────────────┐
│   Firestore     │          │   Firebase      │
│   (Database)    │          │   Storage       │
└─────────────────┘          └─────────────────┘
         ▲                            ▲
         │                            │
         └────────────────┬───────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Kamiak HPC Cluster                          │
│         ┌─────────────────────────────────┐            │
│         │  YOLOv10 + MONAI Pipeline       │            │
│         │  (SLURM Jobs with GPU)          │            │
│         └─────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 3D Slicer (Desktop)                      │
│            Manual Review & Correction                    │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- React 18
- VTK.js (3D visualization)
- Chart.js (analytics)
- Tailwind CSS
- Firebase SDK

### Backend
- FastAPI (Python)
- Firebase Admin SDK
- Docker
- Label Studio

### ML Pipeline
- YOLOv10 (Ultralytics)
- MONAI (medical imaging)
- PyTorch
- OpenCV
- SimpleITK

### Infrastructure
- Firebase (Auth, Firestore, Storage, Hosting)
- Google Cloud Run
- Kamiak HPC (SLURM)
- Docker & Docker Compose

## Workflow Overview

### 1. Data Upload
Researchers upload multi-page TIFF CT scans via web interface.

### 2. Annotation
Using Label Studio, researchers annotate:
- Bounding boxes for tick detection (YOLOv10)
- Segmentation masks for organs (MONAI)

### 3. Job Submission
Web interface generates SLURM scripts for Kamiak HPC.

### 4. ML Processing
On Kamiak:
- YOLOv10 detects ticks on 2D slices
- Aggregates to 3D bounding volume
- MONAI performs 3D organ segmentation
- Computes quantification metrics

### 5. Review Results
Researchers review:
- 3D visualizations in web browser
- Quantification statistics
- Download for 3D Slicer

### 6. Manual Correction (Optional)
Using 3D Slicer:
- Load scan and segmentation
- Manually correct errors
- Re-upload to Firebase

## Key Features

### For Researchers
- ✅ Web-based interface - no local installation
- ✅ Multi-page TIFF support
- ✅ Integrated annotation with Label Studio
- ✅ Batch processing on HPC
- ✅ 3D visualization
- ✅ Automated quantification
- ✅ 3D Slicer integration

### For ML Pipeline
- ✅ YOLOv10 object detection
- ✅ MONAI 3D segmentation
- ✅ One-shot/few-shot learning
- ✅ GPU-accelerated on Kamiak
- ✅ Automatic result upload

### For Administration
- ✅ Firebase-based (scalable)
- ✅ User authentication
- ✅ Role-based access
- ✅ Cloud-native deployment
- ✅ Monitoring and logging

## Support

### Documentation Issues

If you find errors or have suggestions for documentation:
1. Open an issue on GitHub
2. Submit a pull request with fixes
3. Contact the team

### Technical Support

- **Users**: support@morphovue.org
- **Developers**: GitHub Issues
- **HPC**: hpc@wsu.edu (Kamiak)

## Contributing to Documentation

We welcome documentation improvements:

1. Fork the repository
2. Edit markdown files in `docs/`
3. Submit pull request
4. Follow [Contributing Guide](../CONTRIBUTING.md)

### Documentation Style

- Use clear, simple language
- Include code examples
- Add screenshots where helpful
- Keep updated with code changes
- Test all commands and examples

## Version History

### v1.0.0 (2024)
- Initial documentation release
- User guide
- Deployment guide
- Kamiak guide
- API documentation

## License

All documentation is licensed under the same MIT License as the project.

See [LICENSE](../LICENSE) for details.

---

*For questions about documentation, contact: support@morphovue.org*


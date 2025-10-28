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
├── tests/                # Test suite
│   └── slicer_api/       # 3D Slicer API connection tests
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

## 🧪 Testing

### 3D Slicer API Connection Tests

The project includes comprehensive tests for connecting to locally installed 3D Slicer:

#### Prerequisites for Testing

- **3D Slicer Installation**: Download and install 3D Slicer from [slicer.org](https://slicer.org)
- **Python Dependencies**: Install test dependencies from requirements files

#### Running Tests

1. **Install Test Dependencies**
   ```bash
   # For ML pipeline tests
   cd ml-pipeline
   pip install -r requirements.txt
   
   # For backend tests
   cd backend
   pip install -r requirements.txt
   ```

2. **Run Unit Tests** (no Slicer required)
   ```bash
   pytest tests/slicer_api/test_slicer_connection.py -v
   ```

3. **Run Integration Tests** (requires Slicer installation)
   ```bash
   pytest tests/slicer_api/test_slicer_integration.py -v
   ```

4. **Run All Slicer Tests**
   ```bash
   pytest tests/slicer_api/ -v
   ```

#### Test Configuration

Tests automatically detect Slicer installation in common Windows paths:
- `C:\ProgramData\NA-MIC\Slicer*`
- `C:\Program Files\Slicer*`
- `C:\Program Files (x86)\Slicer*`
- `C:\Users\*\AppData\Local\Slicer*`

Customize detection in `tests/slicer_api/slicer_config.json`:
```json
{
    "slicer_path": "/custom/path/to/Slicer.exe",
    "timeout_seconds": 30,
    "enable_cli_tests": true,
    "enable_direct_import_tests": true
}
```

#### Connection Methods Tested

| Method | Description | Requirements |
|--------|-------------|--------------|
| **CLI Interface** | Execute Python code via `Slicer.exe --python-code` | Slicer executable |
| **Direct Import** | Import Slicer Python modules directly | Slicer Python environment |

#### Test Results

Tests verify:
- ✅ Slicer installation detection
- ✅ CLI command execution
- ✅ Volume loading operations
- ✅ Segmentation node creation
- ✅ Scene information retrieval
- ✅ Error handling and timeouts

#### Troubleshooting Tests

**Slicer Not Found**
```
RuntimeError: 3D Slicer not available for CLI operations
```
- Ensure Slicer is installed and accessible
- Check `slicer_config.json` for custom path

**Import Errors**
```
ImportError: No module named 'slicer'
```
- Expected when running outside Slicer's Python environment
- Tests will skip direct import tests automatically

**Timeout Errors**
```
Command timed out after 30 seconds
```
- Increase timeout in `slicer_config.json`
- Check Slicer installation integrity

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 📞 Support

For issues or questions, contact the VCEA MME Beckman Research team.


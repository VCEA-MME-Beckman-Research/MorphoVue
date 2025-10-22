# Backend - FastAPI Server

FastAPI backend for the CT Tick ML Platform.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Firebase credentials
```

4. Place Firebase credentials:
   - Download service account key from Firebase Console
   - Save as `firebase-credentials.json` in the backend directory

## Running Locally

```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### Environment
Create `.env` with:

```
firebase_project_id=your-project-id
firebase_storage_bucket=your-project-id.appspot.com
firebase_credentials_path=./firebase-credentials.json
cors_origins=http://localhost:3000
```

## API Endpoints

### Projects
- `POST /api/projects` - Create project
- `GET /api/projects` - List projects
- `GET /api/projects/{id}` - Get project
- `DELETE /api/projects/{id}` - Delete project

### Scans
- `POST /api/scans/upload` - Upload TIFF scan
- `GET /api/scans/{id}` - Get scan metadata
- `GET /api/projects/{id}/scans` - List project scans
- `GET /api/scans/{id}/download-url` - Get download URL

### Annotations
- `POST /api/annotations/sync` - Sync Label Studio annotations
- `GET /api/scans/{id}/annotations` - Get scan annotations

### Jobs
- `POST /api/jobs/generate` - Generate Kamiak job script
- `GET /api/jobs/{id}` - Get job details
- `GET /api/jobs` - List all jobs
- `POST /api/jobs/{id}/update` - Update job status

### Results
- `POST /api/results/upload` - Upload MONAI results
- `GET /api/scans/{id}/segmentations` - Get scan segmentations
- `GET /api/quantification/{id}` - Get quantification results
- `GET /api/segmentations/{id}` - Get segmentation details
- `GET /api/segmentations/{id}/download-url?file_type=mask|volume` - Signed URL for mask/volume

## Docker Build

```bash
docker build -t cttick-backend .
docker run -p 8000:8000 -v $(pwd)/firebase-credentials.json:/app/firebase-credentials.json cttick-backend
```


from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from app.config import settings
from app.firebase_client import firebase_client
from app.models import (
    ProjectCreate, Project, ScanUpload, Scan, AnnotationSync, 
    JobGenerate, JobUpdate, JobInstructions, ResultUpload,
    ProcessingStatus, JobStatus
)
from app.routers import projects, scans, annotations, jobs, results

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="CT Tick ML Platform - YOLOv10 + MONAI + Firebase"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency for authentication
async def verify_auth_token(authorization: Optional[str] = Header(None)):
    """Verify Firebase ID token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.split("Bearer ")[-1]
        decoded_token = firebase_client.verify_token(token)
        if not decoded_token:
            raise HTTPException(status_code=401, detail="Invalid token")
        return decoded_token
    except Exception as e:
        logger.error(f"Auth verification failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# Include routers
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(scans.router, prefix="/api", tags=["scans"])
app.include_router(annotations.router, prefix="/api", tags=["annotations"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(results.router, prefix="/api", tags=["results"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check Firebase connection
        db = firebase_client.db
        test_doc = db.collection('_health').document('test').get()
        firebase_status = "connected"
    except Exception as e:
        logger.error(f"Firebase health check failed: {e}")
        firebase_status = "error"
    
    return {
        "status": "healthy",
        "firebase": firebase_status,
        "label_studio": settings.label_studio_url
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


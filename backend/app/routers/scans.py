from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from typing import List, Optional
from datetime import datetime
import uuid
import os

from app.firebase_client import firebase_client
from app.models import Scan, ProcessingStatus
from app.main import verify_auth_token
from PIL import Image, ImageSequence
import io

router = APIRouter()


@router.post("/scans/upload", response_model=Scan)
async def upload_scan(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    user=Depends(verify_auth_token)
):
    """Upload a multi-page TIFF scan"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.tiff', '.tif')):
            raise HTTPException(status_code=400, detail="Only TIFF files are supported")
        
        db = firebase_client.db
        bucket = firebase_client.bucket
        
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        storage_path = f"scans/{project_id}/{scan_id}.tiff"
        
        # Upload to Firebase Storage
        blob = bucket.blob(storage_path)
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Attempt to compute number of slices (pages) using PIL
        num_slices = None
        try:
            with Image.open(io.BytesIO(content)) as im:
                if getattr(im, 'is_animated', False):
                    num_slices = im.n_frames
                else:
                    # Fallback: iterate frames if available
                    num_slices = sum(1 for _ in ImageSequence.Iterator(im)) or 1
        except Exception:
            num_slices = None

        # Upload with metadata
        blob.upload_from_string(
            content,
            content_type='image/tiff'
        )
        
        # Create Firestore document
        scan_data = {
            "id": scan_id,
            "project_id": project_id,
            "filename": file.filename,
            "storage_path": storage_path,
            "upload_timestamp": datetime.utcnow(),
            "processing_status": ProcessingStatus.UPLOADED.value,
            "file_size": file_size,
            "num_slices": num_slices
        }
        
        db.collection('scans').document(scan_id).set(scan_data)
        
        return Scan(**scan_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload scan: {str(e)}")


@router.get("/scans/{scan_id}", response_model=Scan)
async def get_scan(scan_id: str, user=Depends(verify_auth_token)):
    """Get scan metadata"""
    try:
        db = firebase_client.db
        doc = db.collection('scans').document(scan_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        return Scan(**doc.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scan: {str(e)}")


@router.get("/projects/{project_id}/scans", response_model=List[Scan])
async def list_project_scans(
    project_id: str,
    user=Depends(verify_auth_token)
):
    """List all scans for a project"""
    try:
        db = firebase_client.db
        scans_ref = db.collection('scans').where('project_id', '==', project_id)
        scans_ref = scans_ref.order_by('upload_timestamp', direction='DESCENDING')
        
        scans = []
        for doc in scans_ref.stream():
            scan_data = doc.to_dict()
            scans.append(Scan(**scan_data))
        
        return scans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list scans: {str(e)}")


@router.patch("/scans/{scan_id}/status")
async def update_scan_status(
    scan_id: str,
    status: ProcessingStatus,
    user=Depends(verify_auth_token)
):
    """Update scan processing status"""
    try:
        db = firebase_client.db
        doc_ref = db.collection('scans').document(scan_id)
        
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        doc_ref.update({
            "processing_status": status.value
        })
        
        return {"message": "Status updated successfully", "status": status.value}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@router.get("/scans/{scan_id}/download-url")
async def get_scan_download_url(
    scan_id: str,
    user=Depends(verify_auth_token)
):
    """Get a signed URL for downloading the scan"""
    try:
        db = firebase_client.db
        doc = db.collection('scans').document(scan_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        scan_data = doc.to_dict()
        bucket = firebase_client.bucket
        blob = bucket.blob(scan_data['storage_path'])
        
        # Generate signed URL (valid for 1 hour)
        url = blob.generate_signed_url(
            version="v4",
            expiration=3600,
            method="GET"
        )
        
        return {"download_url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")


@router.get("/scans/{scan_id}/slices")
async def get_scan_num_slices(
    scan_id: str,
    user=Depends(verify_auth_token)
):
    """Return number of slices if available"""
    try:
        db = firebase_client.db
        doc = db.collection('scans').document(scan_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Scan not found")
        data = doc.to_dict()
        return {"num_slices": data.get("num_slices")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get slice count: {str(e)}")


from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import uuid
import json

from app.firebase_client import firebase_client
from app.models import AnnotationSync, Annotation, ProcessingStatus
from app.main import verify_auth_token

router = APIRouter()


@router.post("/annotations/sync")
async def sync_annotations(
    annotation: AnnotationSync,
    user=Depends(verify_auth_token)
):
    """Sync Label Studio annotations to Firestore"""
    try:
        db = firebase_client.db
        bucket = firebase_client.bucket
        
        annotation_id = str(uuid.uuid4())
        
        # Save annotation JSON to Firebase Storage
        annotation_path = f"annotations/{annotation.scan_id}/{annotation_id}.json"
        blob = bucket.blob(annotation_path)
        blob.upload_from_string(
            json.dumps(annotation.annotations),
            content_type='application/json'
        )
        
        # Extract bounding boxes and masks based on type
        bounding_boxes = None
        masks = None
        
        if annotation.annotation_type == "bbox":
            bounding_boxes = annotation.annotations.get("bboxes", [])
        elif annotation.annotation_type == "mask":
            masks = annotation.annotations.get("masks", {})
        
        # Create Firestore document
        annotation_data = {
            "id": annotation_id,
            "scan_id": annotation.scan_id,
            "annotation_type": annotation.annotation_type,
            "bounding_boxes": bounding_boxes,
            "masks": masks,
            "storage_path": annotation_path,
            "created_at": datetime.utcnow(),
            "annotator_id": user['uid']
        }
        
        db.collection('annotations').document(annotation_id).set(annotation_data)
        
        # Update scan status to annotated
        db.collection('scans').document(annotation.scan_id).update({
            "processing_status": ProcessingStatus.ANNOTATED.value
        })
        
        return {
            "message": "Annotations synced successfully",
            "annotation_id": annotation_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync annotations: {str(e)}")


@router.get("/scans/{scan_id}/annotations", response_model=List[Annotation])
async def get_scan_annotations(
    scan_id: str,
    user=Depends(verify_auth_token)
):
    """Get all annotations for a scan"""
    try:
        db = firebase_client.db
        annotations_ref = db.collection('annotations').where('scan_id', '==', scan_id)
        annotations_ref = annotations_ref.order_by('created_at', direction='DESCENDING')
        
        annotations = []
        for doc in annotations_ref.stream():
            annotation_data = doc.to_dict()
            annotations.append(Annotation(**annotation_data))
        
        return annotations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get annotations: {str(e)}")


@router.get("/annotations/{annotation_id}")
async def get_annotation_download_url(
    annotation_id: str,
    user=Depends(verify_auth_token)
):
    """Get signed URL for downloading annotation JSON"""
    try:
        db = firebase_client.db
        doc = db.collection('annotations').document(annotation_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Annotation not found")
        
        annotation_data = doc.to_dict()
        bucket = firebase_client.bucket
        blob = bucket.blob(annotation_data['storage_path'])
        
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


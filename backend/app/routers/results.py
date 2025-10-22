from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from datetime import datetime
import uuid

import app.firebase_client as fb
from app.models import ResultUpload, Segmentation, QuantificationResult
from app.deps import verify_auth_token

router = APIRouter()


@router.post("/results/upload")
async def upload_results(
    result: ResultUpload,
    user=Depends(verify_auth_token)
):
    """Upload MONAI segmentation results from Kamiak"""
    try:
        db = fb.firebase_client.db
        
        # Create segmentation document
        segmentation_id = str(uuid.uuid4())
        segmentation_data = {
            "id": segmentation_id,
            "scan_id": result.scan_id,
            "mask_url": result.segmentation_url,
            "volume_url": result.volume_url,
            "model_version": result.model_version,
            "metrics": result.metrics,
            "created_at": datetime.utcnow()
        }
        
        db.collection('segmentations').document(segmentation_id).set(segmentation_data)
        
        # Create quantification result documents
        quantification_ids = []
        for quant in result.quantification:
            quant_id = str(uuid.uuid4())
            quant_data = {
                "id": quant_id,
                "segmentation_id": segmentation_id,
                "organ_name": quant.get("organ_name"),
                "volume": quant.get("volume"),
                "surface_area": quant.get("surface_area"),
                "centroid": quant.get("centroid"),
                "additional_metrics": quant.get("additional_metrics", {})
            }
            
            db.collection('quantification_results').document(quant_id).set(quant_data)
            quantification_ids.append(quant_id)
        
        return {
            "message": "Results uploaded successfully",
            "segmentation_id": segmentation_id,
            "quantification_ids": quantification_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload results: {str(e)}")


@router.get("/scans/{scan_id}/segmentations", response_model=List[Segmentation])
async def get_scan_segmentations(
    scan_id: str,
    user=Depends(verify_auth_token)
):
    """Get all segmentations for a scan"""
    try:
        db = fb.firebase_client.db
        segmentations_ref = db.collection('segmentations').where('scan_id', '==', scan_id)
        segmentations_ref = segmentations_ref.order_by('created_at', direction='DESCENDING')
        
        segmentations = []
        for doc in segmentations_ref.stream():
            seg_data = doc.to_dict()
            segmentations.append(Segmentation(**seg_data))
        
        return segmentations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get segmentations: {str(e)}")


@router.get("/quantification/{segmentation_id}", response_model=List[QuantificationResult])
async def get_quantification_results(
    segmentation_id: str,
    user=Depends(verify_auth_token)
):
    """Get quantification results for a segmentation"""
    try:
        db = fb.firebase_client.db
        quant_ref = db.collection('quantification_results').where('segmentation_id', '==', segmentation_id)
        
        results = []
        for doc in quant_ref.stream():
            quant_data = doc.to_dict()
            results.append(QuantificationResult(**quant_data))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quantification results: {str(e)}")


@router.get("/segmentations/{segmentation_id}")
async def get_segmentation(
    segmentation_id: str,
    user=Depends(verify_auth_token)
):
    """Get segmentation details"""
    try:
        db = fb.firebase_client.db
        doc = db.collection('segmentations').document(segmentation_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Segmentation not found")
        
        return Segmentation(**doc.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get segmentation: {str(e)}")


@router.get("/segmentations/{segmentation_id}/download-url")
async def get_segmentation_download_url(
    segmentation_id: str,
    file_type: str = Query("mask", pattern="^(mask|volume)$"),
    user=Depends(verify_auth_token)
):
    """Get signed download URL for segmentation mask or volume"""
    try:
        db = fb.firebase_client.db
        bucket = fb.firebase_client.bucket

        doc = db.collection('segmentations').document(segmentation_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Segmentation not found")

        seg_data = doc.to_dict()

        target_url = None
        if file_type == "mask":
            target_url = seg_data.get("mask_url")
        else:
            target_url = seg_data.get("volume_url")

        if not target_url:
            raise HTTPException(status_code=404, detail=f"{file_type.capitalize()} not available for this segmentation")

        # Derive storage path from gs:// URL or take path directly
        storage_path = None
        if isinstance(target_url, str) and target_url.startswith("gs://"):
            # Expect gs://<bucket>/<path>
            without_scheme = target_url[5:]
            if '/' not in without_scheme:
                raise HTTPException(status_code=400, detail="Invalid gs:// URL")
            bucket_name, storage_path = without_scheme.split('/', 1)
            # If different bucket, try to use it
            from firebase_admin import storage as fa_storage
            bkt = fa_storage.bucket(bucket_name)
        else:
            storage_path = target_url
            bkt = bucket

        blob = bkt.blob(storage_path)
        url = blob.generate_signed_url(
            version="v4",
            expiration=3600,
            method="GET"
        )

        return {"download_url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate signed URL: {str(e)}")


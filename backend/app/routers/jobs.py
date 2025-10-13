from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import uuid

from app.firebase_client import firebase_client
from app.models import JobGenerate, JobUpdate, KamiakJob, JobInstructions, JobStatus, ProcessingStatus
from app.main import verify_auth_token
from app.config import settings

router = APIRouter()


def generate_slurm_script(job_id: str, scan_ids: List[str], job_config: JobGenerate) -> str:
    """Generate SLURM array job script"""
    num_scans = len(scan_ids)
    scan_ids_str = " ".join(scan_ids)
    
    script = f"""#!/bin/bash
#SBATCH --job-name={job_config.job_name}
#SBATCH --output=logs/cttick_%A_%a.out
#SBATCH --error=logs/cttick_%A_%a.err
#SBATCH --partition={job_config.partition}
#SBATCH --gres=gpu:1
#SBATCH --time={job_config.time_limit}
#SBATCH --array=1-{num_scans}

# Load modules
module load anaconda3

# Activate environment
source activate tickml

# Array of scan IDs
SCAN_IDS=({scan_ids_str})

# Get scan ID for this array task
SCAN_ID=${{SCAN_IDS[$SLURM_ARRAY_TASK_ID-1]}}

# Job ID for Firebase tracking
JOB_ID="{job_id}"

echo "Processing scan: $SCAN_ID"
echo "Job ID: $JOB_ID"
echo "Array task ID: $SLURM_ARRAY_TASK_ID"

# Run the ML pipeline
python3 run_yolo10_monai.py $SCAN_ID $JOB_ID

# Update job status on completion
if [ $? -eq 0 ]; then
    echo "Scan $SCAN_ID processed successfully"
else
    echo "ERROR: Scan $SCAN_ID processing failed"
    exit 1
fi
"""
    return script


@router.post("/jobs/generate", response_model=JobInstructions)
async def generate_job(
    job_config: JobGenerate,
    user=Depends(verify_auth_token)
):
    """Generate Kamiak job script for batch processing"""
    try:
        db = firebase_client.db
        bucket = firebase_client.bucket
        
        # Validate that all scans exist and are annotated
        for scan_id in job_config.scan_ids:
            scan_doc = db.collection('scans').document(scan_id).get()
            if not scan_doc.exists:
                raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
            
            scan_data = scan_doc.to_dict()
            if scan_data.get('processing_status') not in [ProcessingStatus.ANNOTATED.value, ProcessingStatus.UPLOADED.value]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Scan {scan_id} must be annotated before processing"
                )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Generate SLURM script
        script_content = generate_slurm_script(job_id, job_config.scan_ids, job_config)
        
        # Save script to Firebase Storage
        script_path = f"job_scripts/{job_id}.sh"
        blob = bucket.blob(script_path)
        blob.upload_from_string(script_content, content_type='text/plain')
        
        # Get signed URL for download
        script_url = blob.generate_signed_url(
            version="v4",
            expiration=86400,  # 24 hours
            method="GET"
        )
        
        # Create Firestore job document
        job_data = {
            "id": job_id,
            "scan_ids": job_config.scan_ids,
            "job_script": script_path,
            "status": JobStatus.PENDING.value,
            "slurm_id": None,
            "submitted_at": datetime.utcnow(),
            "completed_at": None,
            "log_output": None,
            "created_by": user['uid']
        }
        
        db.collection('kamiak_jobs').document(job_id).set(job_data)
        
        # Update scan statuses to queued
        for scan_id in job_config.scan_ids:
            db.collection('scans').document(scan_id).update({
                "processing_status": ProcessingStatus.QUEUED.value
            })
        
        # Generate instructions
        instructions = [
            f"1. Download the job script from the link below or use wget:",
            f"   wget '{script_url}' -O {job_id}.sh",
            f"",
            f"2. SSH to Kamiak:",
            f"   ssh <username>@kamiak.wsu.edu",
            f"",
            f"3. Copy the script to your Kamiak workspace:",
            f"   # If downloaded locally, use scp:",
            f"   scp {job_id}.sh <username>@kamiak.wsu.edu:~/MorphoVue/ml-pipeline/",
            f"",
            f"4. Navigate to the ml-pipeline directory:",
            f"   cd ~/MorphoVue/ml-pipeline",
            f"",
            f"5. Create logs directory if it doesn't exist:",
            f"   mkdir -p logs",
            f"",
            f"6. Submit the job:",
            f"   sbatch {job_id}.sh",
            f"",
            f"7. Note the SLURM job ID returned and update it in the web interface",
            f"",
            f"8. Monitor job status:",
            f"   squeue -u $USER",
            f"   tail -f logs/cttick_<job_id>_*.out"
        ]
        
        return JobInstructions(
            job_id=job_id,
            script_content=script_content,
            script_path=script_url,
            instructions=instructions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate job: {str(e)}")


@router.get("/jobs/{job_id}", response_model=KamiakJob)
async def get_job(job_id: str, user=Depends(verify_auth_token)):
    """Get job details"""
    try:
        db = firebase_client.db
        doc = db.collection('kamiak_jobs').document(job_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return KamiakJob(**doc.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")


@router.get("/jobs", response_model=List[KamiakJob])
async def list_jobs(user=Depends(verify_auth_token)):
    """List all jobs"""
    try:
        db = firebase_client.db
        jobs_ref = db.collection('kamiak_jobs').order_by('submitted_at', direction='DESCENDING')
        
        jobs = []
        for doc in jobs_ref.stream():
            job_data = doc.to_dict()
            jobs.append(KamiakJob(**job_data))
        
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.post("/jobs/{job_id}/update")
async def update_job_status(
    job_id: str,
    job_update: JobUpdate,
    user=Depends(verify_auth_token)
):
    """Update job status (called by researcher or Kamiak script)"""
    try:
        db = firebase_client.db
        doc_ref = db.collection('kamiak_jobs').document(job_id)
        
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Job not found")
        
        update_data = {
            "status": job_update.status.value
        }
        
        if job_update.slurm_id:
            update_data["slurm_id"] = job_update.slurm_id
        
        if job_update.log_output:
            update_data["log_output"] = job_update.log_output
        
        if job_update.status == JobStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
            
            # Update all scan statuses to completed
            job_data = doc.to_dict()
            for scan_id in job_data['scan_ids']:
                db.collection('scans').document(scan_id).update({
                    "processing_status": ProcessingStatus.COMPLETED.value
                })
        
        elif job_update.status == JobStatus.RUNNING:
            # Update scan statuses to processing
            job_data = doc.to_dict()
            for scan_id in job_data['scan_ids']:
                db.collection('scans').document(scan_id).update({
                    "processing_status": ProcessingStatus.PROCESSING.value
                })
        
        elif job_update.status == JobStatus.FAILED:
            update_data["completed_at"] = datetime.utcnow()
            
            # Update scan statuses to failed
            job_data = doc.to_dict()
            for scan_id in job_data['scan_ids']:
                db.collection('scans').document(scan_id).update({
                    "processing_status": ProcessingStatus.FAILED.value
                })
        
        doc_ref.update(update_data)
        
        return {"message": "Job status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update job: {str(e)}")


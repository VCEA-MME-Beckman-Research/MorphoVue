from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import uuid

import app.firebase_client as fb
from app.models import ProjectCreate, Project
from app.deps import verify_auth_token

router = APIRouter()


@router.post("/projects", response_model=Project)
async def create_project(
    project: ProjectCreate,
    user=Depends(verify_auth_token)
):
    """Create a new research project"""
    try:
        db = fb.firebase_client.db
        project_id = str(uuid.uuid4())
        
        project_data = {
            "id": project_id,
            "name": project.name,
            "description": project.description,
            "researcher_id": user['uid'],
            "created_at": datetime.utcnow(),
            "updated_at": None
        }
        
        db.collection('projects').document(project_id).set(project_data)
        
        return Project(**project_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@router.get("/projects", response_model=List[Project])
async def list_projects(user=Depends(verify_auth_token)):
    """List all projects for the authenticated user"""
    try:
        db = fb.firebase_client.db
        projects_ref = db.collection('projects')
        
        # Filter by researcher_id for non-admin users
        query = projects_ref.order_by('created_at', direction='DESCENDING')
        
        projects = []
        for doc in query.stream():
            project_data = doc.to_dict()
            projects.append(Project(**project_data))
        
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")


@router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, user=Depends(verify_auth_token)):
    """Get a specific project"""
    try:
        db = fb.firebase_client.db
        doc = db.collection('projects').document(project_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return Project(**doc.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, user=Depends(verify_auth_token)):
    """Delete a project"""
    try:
        db = firebase_client.db
        doc = db.collection('projects').document(project_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Delete project document
        db.collection('projects').document(project_id).delete()
        
        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")


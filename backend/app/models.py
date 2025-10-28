from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    RESEARCHER = "researcher"
    ANNOTATOR = "annotator"


class ProcessingStatus(str, Enum):
    UPLOADED = "uploaded"
    ANNOTATING = "annotating"
    ANNOTATED = "annotated"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Request Models
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ScanUpload(BaseModel):
    project_id: str
    filename: str


class AnnotationSync(BaseModel):
    scan_id: str
    annotation_type: str  # "bbox" or "mask"
    annotations: Dict[str, Any]


class JobGenerate(BaseModel):
    scan_ids: List[str]
    job_name: Optional[str] = "cttick_pipeline"
    partition: str = "gpu"
    time_limit: str = "02:00:00"


class JobUpdate(BaseModel):
    status: JobStatus
    slurm_id: Optional[str] = None
    log_output: Optional[str] = None


class ResultUpload(BaseModel):
    scan_id: str
    segmentation_url: str
    volume_url: Optional[str] = None
    model_version: str
    metrics: Dict[str, Any]
    quantification: List[Dict[str, Any]]


# Response Models
class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    researcher_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class Scan(BaseModel):
    id: str
    project_id: str
    filename: str
    storage_path: str
    upload_timestamp: datetime
    processing_status: ProcessingStatus
    file_size: Optional[int] = None
    num_slices: Optional[int] = None


class Annotation(BaseModel):
    id: str
    scan_id: str
    annotation_type: str
    bounding_boxes: Optional[List[Dict[str, Any]]] = None
    masks: Optional[Dict[str, Any]] = None
    created_at: datetime
    annotator_id: str


class Segmentation(BaseModel):
    id: str
    scan_id: str
    mask_url: str
    volume_url: Optional[str] = None
    model_version: str
    metrics: Dict[str, Any]
    created_at: datetime


class QuantificationResult(BaseModel):
    id: str
    segmentation_id: str
    organ_name: str
    volume: float
    surface_area: float
    centroid: List[float]
    additional_metrics: Optional[Dict[str, Any]] = None


class KamiakJob(BaseModel):
    id: str
    scan_ids: List[str]
    job_script: str
    status: JobStatus
    slurm_id: Optional[str] = None
    submitted_at: datetime
    completed_at: Optional[datetime] = None
    log_output: Optional[str] = None


class JobInstructions(BaseModel):
    job_id: str
    script_content: str
    script_path: str
    instructions: List[str]


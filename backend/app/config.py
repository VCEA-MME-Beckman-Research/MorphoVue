from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Firebase
    firebase_project_id: str
    firebase_storage_bucket: str
    firebase_credentials_path: str
    
    # Label Studio
    label_studio_url: str = "http://localhost:8080"
    
    # Kamiak
    kamiak_job_template_path: str = "../ml-pipeline/job_template.sh"
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    # App
    app_name: str = "CT Tick ML Platform"
    debug: bool = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


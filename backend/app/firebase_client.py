import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class FirebaseClient:
    """Singleton Firebase client"""
    _instance: Optional['FirebaseClient'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.initialize()
            self._initialized = True
    
    def initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': settings.firebase_storage_bucket
            })
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    @property
    def db(self):
        """Get Firestore client"""
        return firestore.client()
    
    @property
    def bucket(self):
        """Get Storage bucket"""
        return storage.bucket()
    
    def verify_token(self, id_token: str):
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None


# Global instance
firebase_client = FirebaseClient()


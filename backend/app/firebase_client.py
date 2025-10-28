import os
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
            # Allow disabling during tests
            if os.getenv("FIREBASE_DISABLE_INIT", "0") in ("1", "true", "True"):
                logger.info("Firebase initialization disabled via FIREBASE_DISABLE_INIT")
                return
            # If credentials file missing, keep a no-op client for tests/local
            cred_path = settings.firebase_credentials_path
            if not os.path.exists(cred_path):
                logger.warning("Firebase credentials not found; skipping initialization")
                return
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {'storageBucket': settings.firebase_storage_bucket})
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


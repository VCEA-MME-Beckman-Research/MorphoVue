from typing import Optional
from fastapi import HTTPException, Header
import logging

import app.firebase_client as firebase_module

logger = logging.getLogger(__name__)


async def verify_auth_token(authorization: Optional[str] = Header(None)):
    """Verify Firebase ID token from Authorization header.

    Extracts token from "Bearer <token>" and verifies via Firebase Admin.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        token = authorization.split("Bearer ")[-1]
        decoded_token = firebase_module.firebase_client.verify_token(token)
        if not decoded_token:
            raise HTTPException(status_code=401, detail="Invalid token")
        return decoded_token
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth verification failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

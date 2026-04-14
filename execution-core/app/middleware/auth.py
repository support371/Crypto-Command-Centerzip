"""
Supabase JWT verification middleware.
All POST/write routes require a valid Supabase-issued JWT.
"""
import logging
from fastapi import HTTPException, Header
from jose import jwt, JWTError
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


async def require_supabase_jwt(authorization: Optional[str] = Header(None)):
    if not settings.supabase_jwt_secret:
        # In development mode without JWT secret configured, log warning and pass through
        if settings.app_env == "development":
            logger.warning("Supabase JWT secret not configured — skipping JWT check in development mode")
            return
        raise HTTPException(status_code=503, detail="JWT verification not configured")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization[len("Bearer "):]
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as e:
        logger.warning("JWT verification failed: %s", e)
        raise HTTPException(status_code=401, detail="Invalid or expired token")

from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "env": settings.app_env,
        "sandbox": settings.ccxt_sandbox_mode,
    }


@router.get("/")
async def root():
    return {"service": "execution-core", "version": "1.0.0"}

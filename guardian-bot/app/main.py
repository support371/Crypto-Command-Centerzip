"""
Guardian Bot — Capital protection service with absolute override authority.
Monitors: drawdown, loss limits, position limits, risk breaches.
Triggers kill-switch automatically when thresholds are exceeded.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.guardian import GuardianService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

guardian = GuardianService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Guardian Bot starting — absolute override active")
    await guardian.start()
    yield
    await guardian.stop()
    logger.info("Guardian Bot stopped")


app = FastAPI(title="CryptoSignal Guardian Bot", version="1.0.0", lifespan=lifespan)


class KillRequest(BaseModel):
    reason: str = "manual"


@app.get("/health")
async def health():
    return {"status": "ok", "service": "guardian-bot"}


@app.get("/status")
async def status():
    return guardian.get_status()


@app.post("/kill")
async def kill(request: KillRequest):
    """Trigger kill-switch. Guardian has absolute authority."""
    await guardian.trigger_kill(request.reason)
    return {"killed": True, "reason": request.reason}


@app.post("/reset")
async def reset(secret: str):
    """Reset kill-switch after manual review. Requires secret."""
    import os
    expected = os.getenv("KILL_SWITCH_SECRET", "")
    if expected and secret != expected:
        raise HTTPException(status_code=403, detail="Invalid secret")
    await guardian.reset()
    return {"reset": True}

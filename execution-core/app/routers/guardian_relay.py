"""
Guardian relay — proxies kill-switch and status from Guardian Bot.
Also handles manual kill-switch from frontend via Supabase-authenticated request.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import httpx

from app.config import settings
from app.middleware.auth import require_supabase_jwt
from app.models.audit_log import audit

logger = logging.getLogger(__name__)
router = APIRouter()

_kill_switch_active = False


class KillRequest(BaseModel):
    reason: str = "manual_trigger"
    secret: Optional[str] = None


@router.get("/status")
async def guardian_status():
    """Check guardian bot status. Falls back gracefully if bot is offline."""
    if _kill_switch_active:
        return {"state": "killed"}
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(
                f"{settings.guardian_bot_url}/status",
                headers={"x-api-key": settings.guardian_bot_api_key or ""},
            )
            if res.status_code == 200:
                return res.json()
    except Exception:
        pass
    return {"state": "offline"}


@router.post("/kill", dependencies=[Depends(require_supabase_jwt)])
async def trigger_kill_switch(request: KillRequest):
    """
    Manual kill-switch. Requires Supabase JWT.
    Closes all positions, halts execution, emits audit event.
    """
    global _kill_switch_active
    _kill_switch_active = True

    audit("error", "kill-switch", f"KILL SWITCH TRIGGERED — reason: {request.reason}")
    logger.critical("KILL SWITCH ACTIVATED — reason: %s", request.reason)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{settings.guardian_bot_url}/kill",
                json={"reason": request.reason},
                headers={"x-api-key": settings.guardian_bot_api_key or ""},
            )
    except Exception as e:
        logger.warning("Guardian bot kill relay failed: %s", e)

    return {"killed": True, "reason": request.reason}


@router.post("/reset")
async def reset_kill_switch(secret: str):
    """Reset kill switch. Requires kill-switch secret."""
    global _kill_switch_active
    if settings.kill_switch_secret and secret != settings.kill_switch_secret:
        raise HTTPException(status_code=403, detail="Invalid kill-switch secret")
    _kill_switch_active = False
    audit("warn", "kill-switch", "Kill switch reset — trading resumed")
    return {"reset": True}

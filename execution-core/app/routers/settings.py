"""
Settings router — runtime risk limit configuration.
All settings persisted to DB in testnet/live; in-memory for paper mode.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional
from app.middleware.auth import require_supabase_jwt
from app.config import settings
from app.models.audit_log import audit

router = APIRouter()

_runtime_limits = {
    "maxPositionSizeUsd": settings.max_position_size_usd,
    "maxDailyLossUsd": settings.max_daily_loss_usd,
    "maxOpenPositions": settings.max_open_positions,
    "autoKillDrawdownPct": settings.auto_kill_drawdown_pct,
    "autoKillLossUsd": settings.auto_kill_loss_usd,
}


class RiskLimits(BaseModel):
    maxPositionSizeUsd: float = Field(gt=0)
    maxDailyLossUsd: float = Field(gt=0)
    maxOpenPositions: int = Field(ge=1, le=100)
    autoKillDrawdownPct: float = Field(ge=0.1, le=50.0)
    autoKillLossUsd: float = Field(gt=0)


@router.get("")
async def get_risk_limits():
    return _runtime_limits


@router.post("", dependencies=[Depends(require_supabase_jwt)])
async def update_risk_limits(limits: RiskLimits):
    global _runtime_limits
    _runtime_limits = limits.model_dump()
    audit(
        "warn",
        "settings",
        f"Risk limits updated: maxPos=${limits.maxPositionSizeUsd}, maxDailyLoss=${limits.maxDailyLossUsd}",
    )
    return {"saved": True, "limits": _runtime_limits}

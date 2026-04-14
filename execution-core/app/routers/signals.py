from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from app.models.signal_store import get_signal_store, Signal
from app.models.audit_log import audit
import uuid

router = APIRouter()


class IngestSignalRequest(BaseModel):
    id: Optional[str] = None
    symbol: str
    direction: Literal["long", "short"]
    strength: float = Field(ge=0.0, le=1.0)
    source: str = "prediction-bot"
    timestamp: Optional[str] = None
    status: str = "pending"


@router.get("/recent")
async def recent_signals(limit: int = Query(20, ge=1, le=200)):
    store = get_signal_store()
    return {"signals": store.recent(limit)}


@router.get("")
async def all_signals():
    store = get_signal_store()
    return {"signals": store.all()}


@router.post("/ingest")
async def ingest_signal(req: IngestSignalRequest):
    """Internal endpoint — receives signals from prediction-bot."""
    store = get_signal_store()
    signal = Signal(
        id=req.id or str(uuid.uuid4()),
        symbol=req.symbol,
        direction=req.direction,
        strength=req.strength,
        source=req.source,
        timestamp=req.timestamp or __import__("datetime").datetime.utcnow().isoformat(),
        status=req.status,
    )
    store.push(signal)
    audit("info", "signals", f"Signal ingested: {req.direction} {req.symbol} ({req.strength:.2f})", signal_source=req.source)
    return {"ingested": True, "id": signal.id}

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import Literal, Optional
from app.config import settings
from app.middleware.auth import require_supabase_jwt
from app.models.audit_log import audit
from app.models.paper_account import get_paper_account
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()


class OrderRequest(BaseModel):
    symbol: str
    side: Literal["buy", "sell"]
    order_type: Literal["market", "limit"] = "market"
    amount: float = Field(gt=0)
    price: Optional[float] = None
    exchange: Literal["btcc", "bitget", "paper"] = "paper"
    reason: str = "manual"


class CloseAllRequest(BaseModel):
    reason: str = "guardian_kill"


@router.post("", dependencies=[Depends(require_supabase_jwt)])
async def place_order(order: OrderRequest):
    """Place an order. Requires valid Supabase JWT."""
    if order.exchange != "paper" and not (settings.is_testnet or settings.is_live):
        raise HTTPException(
            status_code=400,
            detail="Live/testnet orders require app_env=testnet or app_env=production",
        )

    logger.info("Order: %s %s %.4f on %s (%s)", order.side, order.symbol, order.amount, order.exchange, order.reason)
    audit("info", "orders", f"Order placed: {order.side} {order.symbol} {order.amount}", exchange=order.exchange)

    if order.exchange == "paper":
        order_id = str(uuid.uuid4())
        account = get_paper_account()
        account.total_trades += 1
        audit("success", "orders", f"Paper order filled: {order.side} {order.symbol}", order_id=order_id)
        return {"order_id": order_id, "status": "filled", "filled_at": order.price, "message": "Paper order filled"}

    raise HTTPException(status_code=501, detail="Live exchange adapter not yet connected for this symbol")


@router.post("/close-all")
async def close_all_positions(request: CloseAllRequest):
    """
    Guardian kill-switch: close all open positions immediately.
    Called by guardian bot — no JWT required (internal service call).
    """
    account = get_paper_account()
    closed = len(account.positions)
    account.positions.clear()
    audit("error", "kill-switch", f"All positions closed by {request.reason}", positions_closed=closed)
    logger.critical("CLOSE ALL POSITIONS — reason: %s, closed: %d", request.reason, closed)
    return {"closed": closed, "reason": request.reason}

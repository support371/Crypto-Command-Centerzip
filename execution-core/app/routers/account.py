from fastapi import APIRouter, Query
from typing import Literal
from app.models.paper_account import get_paper_account
from datetime import datetime, timedelta
import random

router = APIRouter()


@router.get("/summary")
async def account_summary():
    account = get_paper_account()
    return account.summary()


@router.get("/equity-history")
async def equity_history(period: Literal["1D", "1W", "1M"] = "1D"):
    """Return synthetic equity curve for paper mode; wired to DB in testnet/live."""
    account = get_paper_account()
    now = datetime.utcnow()
    if period == "1D":
        points = 48
        delta = timedelta(minutes=30)
    elif period == "1W":
        points = 84
        delta = timedelta(hours=2)
    else:
        points = 90
        delta = timedelta(hours=8)

    base = account.initial_balance
    data = []
    equity = base
    for i in range(points, 0, -1):
        ts = (now - delta * i).isoformat()
        drift = random.gauss(0.0002, 0.001) * equity
        equity = max(equity + drift, base * 0.7)
        data.append({"timestamp": ts, "equity": round(equity, 2), "balance": round(base, 2)})

    return {"data": data, "period": period}

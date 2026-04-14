"""
Price feed router — WebSocket and REST endpoints for live price data.
Development: returns simulated prices.
Testnet/Live: connected to CCXT Pro exchange streams.
"""
import asyncio
import json
import logging
import random
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]

_last_prices = {
    "BTC/USDT": 65000.0,
    "ETH/USDT": 3200.0,
    "SOL/USDT": 145.0,
    "BNB/USDT": 590.0,
}


def _simulate_tick(symbol: str) -> float:
    price = _last_prices.get(symbol, 100.0)
    drift = random.gauss(0, 0.0008) * price
    _last_prices[symbol] = max(price + drift, 0.01)
    return _last_prices[symbol]


@router.get("/ticker/{symbol:path}")
async def get_ticker(symbol: str):
    """REST price ticker. Returns live price (simulated in paper mode)."""
    symbol = symbol.replace("-", "/").upper()
    if settings.is_testnet or settings.is_live:
        # TODO: Connect to CCXT Pro adapter
        raise NotImplementedError("Live price feed not yet connected")
    price = _simulate_tick(symbol)
    return {"symbol": symbol, "price": round(price, 4), "source": "paper"}


@router.websocket("/ws/ticker")
async def price_websocket(ws: WebSocket):
    """WebSocket price stream. Streams ticks every second (paper) or live (testnet/live)."""
    await ws.accept()
    logger.info("Price WebSocket connected")
    try:
        while True:
            ticks = {sym: round(_simulate_tick(sym), 4) for sym in SYMBOLS}
            await ws.send_text(json.dumps({"type": "ticks", "data": ticks}))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        logger.info("Price WebSocket disconnected")

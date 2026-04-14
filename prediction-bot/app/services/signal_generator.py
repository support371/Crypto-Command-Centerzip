"""
Signal generation service.
Paper mode: RSI + momentum heuristics on simulated prices.
Testnet/Live: CCXT Pro price data + configurable model pipeline.

Signals are published to Redis channel 'signals' and also
POSTed to execution core for ingestion.
"""
import asyncio
import json
import logging
import os
import random
import uuid
from datetime import datetime
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]
EXECUTION_CORE_URL = os.getenv("EXECUTION_CORE_URL", "http://localhost:8000")
SIGNAL_INTERVAL_SEC = float(os.getenv("SIGNAL_INTERVAL_SEC", "15"))

_prices: dict[str, list[float]] = {s: [random.uniform(100, 70000)] for s in SYMBOLS}


def _rsi_signal(prices: list[float], period: int = 14) -> float:
    """Simplified RSI → returns normalised signal 0–1."""
    if len(prices) < period + 1:
        return 0.5
    gains, losses = [], []
    for i in range(1, period + 1):
        delta = prices[-(period + 1 - i)] - prices[-(period + 2 - i)]
        (gains if delta > 0 else losses).append(abs(delta))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period or 1e-9
    rsi = 100 - 100 / (1 + avg_gain / avg_loss)
    # Oversold → long signal; overbought → short signal
    if rsi < 30:
        return 0.7 + random.uniform(0, 0.3)
    if rsi > 70:
        return random.uniform(0, 0.3)
    return 0.4 + random.uniform(0, 0.2)


class SignalGenerator:
    def __init__(self):
        self.running = False
        self.signals_generated = 0
        self.last_signal: Optional[dict] = None
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()

    async def _loop(self):
        while self.running:
            try:
                await self._generate_signals()
            except Exception as e:
                logger.error("Signal generation error: %s", e)
            await asyncio.sleep(SIGNAL_INTERVAL_SEC)

    async def _generate_signals(self):
        symbol = random.choice(SYMBOLS)
        # Simulate price tick
        last = _prices[symbol][-1]
        tick = last * (1 + random.gauss(0, 0.001))
        _prices[symbol].append(tick)
        if len(_prices[symbol]) > 200:
            _prices[symbol] = _prices[symbol][-200:]

        strength = _rsi_signal(_prices[symbol])
        direction = "long" if strength > 0.5 else "short"
        effective_strength = strength if direction == "long" else 1.0 - strength

        signal = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "direction": direction,
            "strength": round(effective_strength, 4),
            "source": "prediction-bot",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending",
        }
        self.last_signal = signal
        self.signals_generated += 1

        # POST to execution core
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                await client.post(f"{EXECUTION_CORE_URL}/signals/ingest", json=signal)
        except Exception:
            pass  # Execution core may not be running yet
        logger.debug("Signal generated: %s %s %.3f", direction, symbol, effective_strength)

"""
Guardian service — autonomous risk monitoring.
Runs independently. Kill-switch cannot be overridden by execution core.
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

EXECUTION_CORE_URL = os.getenv("EXECUTION_CORE_URL", "http://localhost:8000")
CHECK_INTERVAL_SEC = float(os.getenv("GUARDIAN_CHECK_INTERVAL_SEC", "5"))
AUTO_KILL_DRAWDOWN_PCT = float(os.getenv("AUTO_KILL_DRAWDOWN_PCT", "5.0"))
AUTO_KILL_LOSS_USD = float(os.getenv("AUTO_KILL_LOSS_USD", "1000.0"))
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "10"))


class GuardianService:
    def __init__(self):
        self.state: str = "active"  # active | triggered | killed
        self.kill_reason: Optional[str] = None
        self.triggered_at: Optional[str] = None
        self.checks_run: int = 0
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("Guardian monitoring loop started")

    async def stop(self):
        if self._task:
            self._task.cancel()

    async def trigger_kill(self, reason: str):
        if self.state == "killed":
            return
        self.state = "killed"
        self.kill_reason = reason
        self.triggered_at = datetime.utcnow().isoformat()
        logger.critical("GUARDIAN KILL-SWITCH TRIGGERED — reason: %s", reason)
        await self._close_all_positions()

    async def reset(self):
        self.state = "active"
        self.kill_reason = None
        self.triggered_at = None
        logger.warning("Guardian reset — monitoring resumed")

    def get_status(self) -> dict:
        return {
            "state": self.state,
            "kill_reason": self.kill_reason,
            "triggered_at": self.triggered_at,
            "checks_run": self.checks_run,
            "thresholds": {
                "drawdown_pct": AUTO_KILL_DRAWDOWN_PCT,
                "loss_usd": AUTO_KILL_LOSS_USD,
                "max_positions": MAX_OPEN_POSITIONS,
            },
        }

    async def _monitor_loop(self):
        while True:
            if self.state == "active":
                try:
                    await self._check_risk()
                except Exception as e:
                    logger.error("Guardian monitor error: %s", e)
            self.checks_run += 1
            await asyncio.sleep(CHECK_INTERVAL_SEC)

    async def _check_risk(self):
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{EXECUTION_CORE_URL}/account/summary")
                if res.status_code != 200:
                    return
                data = res.json()

            daily_pnl = data.get("dailyPnL", 0)
            open_positions = data.get("openPositions", 0)
            equity = data.get("equity", 0)
            balance = data.get("balance", 1)

            # Drawdown check
            drawdown_pct = ((balance - equity) / balance * 100) if balance > 0 else 0

            if daily_pnl < -abs(AUTO_KILL_LOSS_USD):
                await self.trigger_kill(f"daily_loss_limit: ${daily_pnl:.2f}")
            elif drawdown_pct > AUTO_KILL_DRAWDOWN_PCT:
                await self.trigger_kill(f"drawdown_limit: {drawdown_pct:.2f}%")
            elif open_positions > MAX_OPEN_POSITIONS:
                await self.trigger_kill(f"position_limit: {open_positions} positions")
        except Exception:
            pass  # Execution core unavailable — fail safe (don't kill on comms failure)

    async def _close_all_positions(self):
        """Sends close-all command to execution core."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{EXECUTION_CORE_URL}/orders/close-all",
                    json={"reason": self.kill_reason},
                )
        except Exception as e:
            logger.error("Failed to close all positions: %s", e)

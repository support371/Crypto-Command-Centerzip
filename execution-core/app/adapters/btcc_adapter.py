"""
BTCC Exchange Adapter — CCXT Pro implementation.
IMPORTANT: testnet=True is enforced until testnet validation passes.
"""
import logging
from typing import Optional
from app.adapters.base import BaseExchangeAdapter
from app.config import settings

logger = logging.getLogger(__name__)


class BTCCAdapter(BaseExchangeAdapter):
    def __init__(self):
        if not settings.btcc_api_key or not settings.btcc_api_secret:
            raise ValueError("BTCC_API_KEY and BTCC_API_SECRET must be set in environment")
        super().__init__(
            api_key=settings.btcc_api_key,
            api_secret=settings.btcc_api_secret,
            testnet=settings.btcc_testnet,
        )
        self._exchange = None

    async def connect(self) -> None:
        try:
            import ccxt.async_support as ccxt
            self._exchange = ccxt.btcc({
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "sandbox": self.testnet,
                "enableRateLimit": True,
            })
            if self.testnet:
                self._exchange.set_sandbox_mode(True)
                logger.info("BTCC adapter connected in TESTNET/sandbox mode")
            else:
                logger.warning("BTCC adapter connected in LIVE mode — verify testnet validation complete")
            self._connected = True
        except ImportError:
            raise RuntimeError("ccxt package not installed — run: pip install ccxt")

    async def disconnect(self) -> None:
        if self._exchange:
            await self._exchange.close()
            self._connected = False
            logger.info("BTCC adapter disconnected")

    async def fetch_balance(self) -> dict:
        if not self._connected or not self._exchange:
            raise RuntimeError("BTCC adapter not connected")
        balance = await self._exchange.fetch_balance()
        return balance

    async def fetch_positions(self) -> list:
        if not self._connected or not self._exchange:
            raise RuntimeError("BTCC adapter not connected")
        positions = await self._exchange.fetch_positions()
        return positions

    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: float,
        price: Optional[float] = None,
    ) -> dict:
        if not self._connected or not self._exchange:
            raise RuntimeError("BTCC adapter not connected")
        if not self.testnet and not settings.is_live:
            self._assert_not_mainnet_without_validation()

        logger.info("BTCC placing %s %s order: %s %.4f", side, order_type, symbol, amount)
        order = await self._exchange.create_order(symbol, order_type, side, amount, price)
        return order

    async def cancel_order(self, order_id: str, symbol: str) -> dict:
        if not self._connected or not self._exchange:
            raise RuntimeError("BTCC adapter not connected")
        return await self._exchange.cancel_order(order_id, symbol)

    async def close_all_positions(self) -> list:
        """Guardian kill-switch — closes every open position."""
        positions = await self.fetch_positions()
        results = []
        for pos in positions:
            try:
                symbol = pos["symbol"]
                size = abs(pos.get("contracts", 0) or pos.get("amount", 0))
                side = "sell" if pos.get("side", "long") == "long" else "buy"
                if size > 0:
                    result = await self.place_order(symbol, side, "market", size)
                    results.append({"symbol": symbol, "status": "closed", "order": result})
            except Exception as e:
                results.append({"symbol": pos.get("symbol"), "status": "error", "error": str(e)})
        return results

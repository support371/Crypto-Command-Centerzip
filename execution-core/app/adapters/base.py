"""
Abstract exchange adapter interface.
All live exchange adapters must implement this interface.
Guardian has override authority over all adapters.
"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseExchangeAdapter(ABC):
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self._connected = False

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to exchange."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Cleanly disconnect."""
        ...

    @abstractmethod
    async def fetch_balance(self) -> dict:
        """Fetch current account balance. MUST return real data — no synthetic values."""
        ...

    @abstractmethod
    async def fetch_positions(self) -> list:
        """Fetch open positions. MUST return real data."""
        ...

    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: float,
        price: Optional[float] = None,
    ) -> dict:
        """Place an order. Testnet flag must be verified before calling."""
        ...

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> dict:
        ...

    @abstractmethod
    async def close_all_positions(self) -> list:
        """Close all open positions. Called by guardian kill-switch."""
        ...

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _assert_not_mainnet_without_validation(self) -> None:
        """Safety check — never allow mainnet operations without explicit flag."""
        if not self.testnet:
            raise RuntimeError(
                "SAFETY VIOLATION: Attempted live trade on non-testnet adapter without explicit override. "
                "Set testnet=False only after testnet validation has passed."
            )

"""
In-memory paper trading account for development / pre-testnet validation.
Real balances are fetched from exchange adapters in testnet/live mode.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List
import uuid


@dataclass
class PaperPosition:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    side: str = "long"  # long | short
    size: float = 0.0
    entry_price: float = 0.0
    current_price: float = 0.0
    exchange: str = "paper"
    opened_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def unrealized_pnl(self) -> float:
        if self.side == "long":
            return (self.current_price - self.entry_price) * self.size
        return (self.entry_price - self.current_price) * self.size

    @property
    def unrealized_pnl_pct(self) -> float:
        if self.entry_price == 0:
            return 0.0
        return (self.unrealized_pnl / (self.entry_price * self.size)) * 100

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "side": self.side,
            "size": self.size,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "unrealized_pnl": round(self.unrealized_pnl, 4),
            "unrealized_pnl_pct": round(self.unrealized_pnl_pct, 4),
            "exchange": self.exchange,
            "opened_at": self.opened_at,
        }


class PaperAccount:
    def __init__(self, initial_balance: float = 100_000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions: Dict[str, PaperPosition] = {}
        self.closed_pnl = 0.0
        self.daily_pnl: Dict[date, float] = {}
        self.total_trades = 0
        self.mode = "paper"

    @property
    def unrealized_pnl(self) -> float:
        return sum(p.unrealized_pnl for p in self.positions.values())

    @property
    def equity(self) -> float:
        return self.balance + self.unrealized_pnl

    @property
    def today_pnl(self) -> float:
        return self.daily_pnl.get(date.today(), 0.0)

    def summary(self) -> dict:
        return {
            "balance": round(self.balance, 2),
            "equity": round(self.equity, 2),
            "unrealizedPnL": round(self.unrealized_pnl, 2),
            "dailyPnL": round(self.today_pnl, 2),
            "openPositions": len(self.positions),
            "totalTrades": self.total_trades,
            "mode": self.mode,
        }

    def get_positions(self) -> List[dict]:
        return [p.to_dict() for p in self.positions.values()]


# Singleton
_paper_account = PaperAccount()


def get_paper_account() -> PaperAccount:
    return _paper_account

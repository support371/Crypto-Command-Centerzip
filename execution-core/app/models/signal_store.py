"""
In-memory signal store — replaced by Redis pub/sub + DB in testnet/live.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Deque
from collections import deque
import uuid


@dataclass
class Signal:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    direction: str = "long"  # long | short
    strength: float = 0.5    # 0.0 – 1.0
    source: str = "prediction-bot"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "pending"  # pending | executed | rejected | expired

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "direction": self.direction,
            "strength": self.strength,
            "source": self.source,
            "timestamp": self.timestamp,
            "status": self.status,
        }


class SignalStore:
    def __init__(self, max_size: int = 500):
        self._signals: Deque[Signal] = deque(maxlen=max_size)

    def push(self, signal: Signal) -> None:
        self._signals.appendleft(signal)

    def recent(self, limit: int = 20) -> List[dict]:
        return [s.to_dict() for s in list(self._signals)[:limit]]

    def all(self) -> List[dict]:
        return [s.to_dict() for s in self._signals]


_store = SignalStore()


def get_signal_store() -> SignalStore:
    return _store

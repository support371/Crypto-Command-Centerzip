"""
Audit log — in-memory for development; wired to PostgreSQL/TimescaleDB in testnet/live.
ALL material actions must produce an audit event.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Deque, Literal
from collections import deque
import uuid


AuditLevel = Literal["info", "warn", "error", "success"]


@dataclass
class AuditEvent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    level: AuditLevel = "info"
    source: str = "system"
    message: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "level": self.level,
            "source": self.source,
            "message": self.message,
            "metadata": self.metadata,
        }


class AuditLog:
    def __init__(self, max_size: int = 1000):
        self._events: Deque[AuditEvent] = deque(maxlen=max_size)

    def log(self, level: AuditLevel, source: str, message: str, **metadata) -> AuditEvent:
        event = AuditEvent(level=level, source=source, message=message, metadata=metadata)
        self._events.appendleft(event)
        return event

    def recent(self, limit: int = 50) -> List[dict]:
        return [e.to_dict() for e in list(self._events)[:limit]]


_audit_log = AuditLog()


def get_audit_log() -> AuditLog:
    return _audit_log


def audit(level: AuditLevel, source: str, message: str, **metadata) -> None:
    get_audit_log().log(level, source, message, **metadata)

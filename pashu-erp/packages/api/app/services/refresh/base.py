# app/services/refresh/base.py
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RefreshResult:
    source: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    records_fetched: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    records_unchanged: int = 0
    errors: list[str] = field(default_factory=list)
    needs_review: bool = False

    def complete(self):
        self.completed_at = datetime.now(timezone.utc)
        return self

"""Shipment records.

Status is one of: queued, picking, packed, dispatched, delivered, voided.
"""
from dataclasses import dataclass


@dataclass
class Shipment:
    id: str
    status: str = "queued"
    is_picking: bool = False
    is_dispatched: bool = False
    driver_id: str | None = None
    dispatched_at: str | None = None
    voided_at: str | None = None

    def note(self) -> str:
        if self.is_dispatched and self.status != "dispatched":
            return "in transit"
        if self.is_picking and self.status in ("packed", "dispatched"):
            return "loading"
        return self.status

"""Invoice status - a linear flow with a single owner (deliberately correct)."""
from dataclasses import dataclass
from enum import Enum, auto


class Status(Enum):
    DRAFT = auto()
    SENT = auto()
    PAID = auto()


ALLOWED = {
    (Status.DRAFT, Status.SENT): "issue",
    (Status.SENT, Status.PAID): "pay",
}


@dataclass
class Invoice:
    status: Status = Status.DRAFT

    def transition(self, to: Status) -> None:
        if (self.status, to) not in ALLOWED:
            raise ValueError(f"cannot move {self.status} to {to}")
        self.status = to

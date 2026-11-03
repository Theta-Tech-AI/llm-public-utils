"""Subscription records - three flags stand in for the lifecycle."""
from dataclasses import dataclass


@dataclass
class Subscription:
    account_id: str
    is_trial: bool = True
    is_past_due: bool = False
    is_cancelled: bool = False


def start_trial(sub: Subscription) -> None:
    sub.is_trial = True
    sub.is_past_due = False


def charge_failed(sub: Subscription) -> None:
    sub.is_past_due = True


def cancel(sub: Subscription) -> None:
    sub.is_cancelled = True


def can_access(sub: Subscription) -> bool:
    if sub.is_cancelled:
        return False
    if sub.is_past_due and not sub.is_trial:
        return False
    return True

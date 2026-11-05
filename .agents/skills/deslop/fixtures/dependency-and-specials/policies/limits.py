"""Per-customer limits. NEGATIVE CONTROL: the per-customer difference has an owner."""
from dataclasses import dataclass

LIMITS = {
    "acme": {"daily_orders": 5000, "review_required": True},
    "default": {"daily_orders": 500, "review_required": False},
}


@dataclass(frozen=True)
class Limits:
    daily_orders: int
    review_required: bool


def limits_for(tenant: str) -> Limits:
    return Limits(**LIMITS.get(tenant, LIMITS["default"]))

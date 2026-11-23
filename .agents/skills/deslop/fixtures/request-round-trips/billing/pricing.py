COUPONS: dict[str, int] = {"EARLY": 20, "TEAM": 35}


def quote(price_cents: int, coupon: str | None) -> int:
    """The price after the coupon's percentage, never below zero."""
    return max(0, price_cents * (100 - COUPONS.get(coupon or "", 0)) // 100)

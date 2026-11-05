"""Adapter for the exchange-rate vendor. Volatile by nature: the vendor ships monthly."""
from decimal import Decimal

import requests

BASE = "https://rates.example-vendor.test/v3"


class RateUnavailable(RuntimeError):
    pass


def fetch_rate(currency: str, on: str) -> Decimal:
    resp = requests.get(f"{BASE}/rate", params={"ccy": currency, "on": on}, timeout=5)
    if resp.status_code != 200:
        raise RateUnavailable(resp.text[:120])
    return Decimal(resp.json()["rate"])

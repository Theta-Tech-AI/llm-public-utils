"""Pricing policy. Changes when the CFO changes a rule — roughly twice a year."""
from decimal import Decimal

from integrations.rates import fetch_rate          # PLANTED: stable rule -> volatile vendor client
from integrations.rates import RateUnavailable     # ...and the vendor's error type leaks inward


def convert(amount: Decimal, currency: str, on: str) -> Decimal:
    try:
        return amount * fetch_rate(currency, on)
    except RateUnavailable:                        # vendor taxonomy now shapes this file
        return amount

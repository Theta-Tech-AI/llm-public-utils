"""Application settings, read at import time."""
import os

LEGACY_MODE = os.environ.get("LEGACY_MODE", "off")        # PLANTED: set in no deployment
REGION_NOTIFY = os.environ.get("REGION_NOTIFY", "eu")     # PLANTED: 'eu' merged into default path
CURRENCY_DEFAULT = os.environ.get("CURRENCY_DEFAULT", "USD")   # live: set in every deploy manifest

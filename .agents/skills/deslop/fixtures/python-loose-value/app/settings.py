"""Planted: a loose string setting turned into a decision at every read site."""
import os


def _truthy(value: str | None) -> bool:              # PLANTED: the helper that must not need to exist
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def use_cache() -> bool:
    return _truthy(os.environ.get("USE_CACHE"))


def strict_mode() -> bool:                            # PLANTED: second interpretation, same value
    raw = os.environ.get("USE_CACHE")
    return raw == "1" or raw == "true"


def cache_ttl() -> int:                               # PLANTED: a third interpretation
    return 60 if use_cache() else 0

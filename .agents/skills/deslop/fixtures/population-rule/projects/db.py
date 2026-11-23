from contextlib import contextmanager

LEASES: dict[str, str] = {}
ROWS: dict[str, dict[str, object]] = {}


@contextmanager
def row_lock(key: str):
    # SELECT ... FOR UPDATE in the real store
    yield ROWS.setdefault(key, {})

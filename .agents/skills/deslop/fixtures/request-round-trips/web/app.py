from dataclasses import dataclass

ROUTES: list[tuple[str, str, object]] = []


@dataclass(frozen=True)
class User:
    id: str


class Forbidden(Exception):
    pass


def route(method: str, path: str):
    """Register a handler. The framework authenticates the caller and hands the handler a pooled connection."""
    def wrap(fn):
        ROUTES.append((method, path, fn))
        return fn
    return wrap

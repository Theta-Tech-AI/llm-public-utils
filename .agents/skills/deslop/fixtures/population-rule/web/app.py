from dataclasses import dataclass

ROUTES: list[tuple[str, str, str, object]] = []


@dataclass(frozen=True)
class User:
    id: str
    roles: frozenset[str]


class Conflict(Exception):
    pass


class Forbidden(Exception):
    pass


def route(method: str, path: str, role: str):
    """Register a handler; the router refuses a caller without `role` before the handler runs."""
    def wrap(fn):
        ROUTES.append((method, path, role, fn))
        return fn
    return wrap

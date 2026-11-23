from profile import store
from profile.checks import field_problem


class Rejected(Exception):
    pass


def save_profile(user_id: str, body: dict[str, object]) -> dict[str, object]:
    for name, value in body.items():
        problem = field_problem(name, value)
        if problem:
            raise Rejected(f"{name}: {problem}")
    store.put(user_id, body)
    return {"saved": True}

import json

_ROWS: dict[str, str] = {}


def put(user_id: str, profile: dict[str, object]) -> None:
    _ROWS[user_id] = json.dumps(profile)


def get(user_id: str) -> dict[str, object]:
    return json.loads(_ROWS[user_id])

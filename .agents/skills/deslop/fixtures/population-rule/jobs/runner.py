import uuid

QUEUE: list[dict[str, str]] = []


def start(kind: str, **args: str) -> str:
    run_id = str(uuid.uuid4())
    QUEUE.append({"kind": kind, "run_id": run_id, **args})
    return run_id

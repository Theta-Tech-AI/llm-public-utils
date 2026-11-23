from typing import Any

from courses import store


def completion(conn: Any, course_id: str, learner_id: str) -> dict[str, int]:
    """How far the learner is through the course."""
    enrolment = store.get_enrolment(conn, course_id, learner_id)
    done = len(store.results(conn, enrolment["id"]))
    total = len(store.lessons(conn, course_id))
    return {"done": done, "total": total, "percent": 100 * done // total if total else 0}

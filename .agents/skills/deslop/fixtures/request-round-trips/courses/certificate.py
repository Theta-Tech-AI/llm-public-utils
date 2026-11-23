from typing import Any

from courses import store


def eligibility(conn: Any, course_id: str, learner_id: str) -> dict[str, object]:
    """A certificate needs every lesson finished at or above the course's pass mark."""
    enrolment = store.get_enrolment(conn, course_id, learner_id)
    course = store.get_course(conn, course_id)
    scores = [r["score"] for r in store.results(conn, enrolment["id"])]
    finished_all = len(scores) == len(store.lessons(conn, course_id)) and bool(scores)
    return {"eligible": finished_all and min(scores) >= course["pass_mark"], "pass_mark": course["pass_mark"]}

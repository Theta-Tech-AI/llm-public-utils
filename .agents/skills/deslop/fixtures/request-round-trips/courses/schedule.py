from typing import Any

from courses import store
from web.db import Row


def next_lesson(conn: Any, course_id: str, learner_id: str) -> Row | None:
    """The first lesson, in course order, that the learner has not finished."""
    enrolment = store.get_enrolment(conn, course_id, learner_id)
    finished = {r["lesson_id"] for r in store.results(conn, enrolment["id"])}
    for lesson in store.lessons(conn, course_id):
        if lesson["id"] not in finished:
            return lesson
    return None

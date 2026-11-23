"""The tutor's weekly report, built by a scheduled job once per course."""
from typing import Any

from web import db


def course_report(conn: Any, course_id: str) -> dict[str, object]:
    lessons = db.rows(conn, "SELECT id, position, title FROM lesson WHERE course_id = %s ORDER BY position", (course_id,))
    learners = db.rows(
        conn,
        """SELECT e.id, l.email, e.status
             FROM enrolment e JOIN learner l ON l.id = e.learner_id
            WHERE e.course_id = %s AND e.role = 'learner'""",
        (course_id,),
    )
    results = db.rows(
        conn,
        "SELECT enrolment_id, lesson_id, score FROM lesson_result WHERE enrolment_id = ANY(%s)",
        ([learner["id"] for learner in learners],),
    )
    scores: dict[str, dict[str, int]] = {}
    for result in results:
        scores.setdefault(result["enrolment_id"], {})[result["lesson_id"]] = result["score"]
    return {
        "lessons": lessons,
        "learners": [{**learner, "scores": scores.get(learner["id"], {})} for learner in learners],
    }

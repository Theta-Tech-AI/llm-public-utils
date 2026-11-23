"""The single owner of course and enrolment reads: every module asks here, and none writes its own SQL for them."""
from typing import Any

from web import db
from web.db import Row


def get_course(conn: Any, course_id: str) -> Row | None:
    return db.one(conn, "SELECT id, title, pass_mark, archived_at FROM course WHERE id = %s", (course_id,))


def get_enrolment(conn: Any, course_id: str, learner_id: str) -> Row | None:
    return db.one(
        conn,
        "SELECT id, role, status, expires_at FROM enrolment WHERE course_id = %s AND learner_id = %s",
        (course_id, learner_id),
    )


def lessons(conn: Any, course_id: str) -> list[Row]:
    return db.rows(conn, "SELECT id, position, title FROM lesson WHERE course_id = %s ORDER BY position", (course_id,))


def results(conn: Any, enrolment_id: str) -> list[Row]:
    return db.rows(conn, "SELECT lesson_id, score FROM lesson_result WHERE enrolment_id = %s", (enrolment_id,))

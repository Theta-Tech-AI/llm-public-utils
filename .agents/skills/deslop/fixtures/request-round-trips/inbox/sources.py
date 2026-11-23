"""One reader per inbox section. Each returns rows shaped (id, body, posted_at), newest first."""
from typing import Any

from web import db
from web.db import Row


def announcements(conn: Any, learner_id: str) -> list[Row]:
    return db.rows(
        conn,
        """SELECT a.id, a.body, a.posted_at
             FROM enrolment e JOIN announcement a ON a.course_id = e.course_id
            WHERE e.learner_id = %s AND e.status = 'active'
            ORDER BY a.posted_at DESC LIMIT 10""",
        (learner_id,),
    )


def replies(conn: Any, learner_id: str) -> list[Row]:
    return db.rows(
        conn,
        "SELECT id, body, posted_at FROM reply WHERE learner_id = %s AND read_at IS NULL ORDER BY posted_at DESC LIMIT 10",
        (learner_id,),
    )


def grade_notices(conn: Any, learner_id: str) -> list[Row]:
    return db.rows(
        conn,
        "SELECT id, body, posted_at FROM grade_notice WHERE learner_id = %s AND read_at IS NULL ORDER BY posted_at DESC LIMIT 10",
        (learner_id,),
    )


def reminders(conn: Any, learner_id: str) -> list[Row]:
    return db.rows(
        conn,
        "SELECT id, body, posted_at FROM reminder WHERE learner_id = %s AND dismissed_at IS NULL ORDER BY posted_at DESC LIMIT 10",
        (learner_id,),
    )

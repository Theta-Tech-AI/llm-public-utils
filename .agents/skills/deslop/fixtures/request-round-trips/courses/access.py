from datetime import datetime, timezone
from typing import Any

from web import db
from web.app import Forbidden, User


def require_enrolled(conn: Any, course_id: str, user: User) -> None:
    """Refuse a caller who has no live enrolment in this course."""
    row = db.one(
        conn,
        """SELECT e.role, e.status, e.expires_at, c.archived_at
             FROM enrolment e JOIN course c ON c.id = e.course_id
            WHERE e.course_id = %s AND e.learner_id = %s""",
        (course_id, user.id),
    )
    if row is None or row["status"] == "paused":
        raise Forbidden("not enrolled")
    if row["expires_at"] is not None and row["expires_at"] < datetime.now(timezone.utc):
        raise Forbidden("enrolment expired")
    if row["archived_at"] is not None and row["role"] != "tutor":
        raise Forbidden("course archived")

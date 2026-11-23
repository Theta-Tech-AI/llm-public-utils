from typing import Any

from inbox import sources
from web import db
from web.app import User, route


@route("GET", "/me/inbox")
def inbox(conn: Any, user: User) -> dict[str, object]:
    """The bell in the page header. Each open browser tab asks for it every 30 seconds."""
    items = (
        sources.announcements(conn, user.id)
        + sources.replies(conn, user.id)
        + sources.grade_notices(conn, user.id)
        + sources.reminders(conn, user.id)
    )
    with_certificate = []
    completed = db.rows(
        conn, "SELECT id, course_id FROM enrolment WHERE learner_id = %s AND status = 'completed'", (user.id,)
    )
    for enrolment in completed:
        if db.one(conn, "SELECT * FROM certificate WHERE enrolment_id = %s", (enrolment["id"],)):
            with_certificate.append(enrolment["course_id"])
    newest = sorted(items, key=lambda item: item["posted_at"], reverse=True)[:10]
    return {"items": newest, "certificates": with_certificate}

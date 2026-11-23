from typing import Any

from billing import pricing
from web import db
from web.app import User, route


@route("POST", "/courses/{course_id}/purchase")
def buy_seat(conn: Any, course_id: str, user: User, coupon: str | None = None) -> dict[str, str]:
    """Take one seat, or join the waiting list when the course is full."""
    with conn.transaction():
        course = db.one(
            conn, "SELECT seats_left, price_cents, archived_at FROM course WHERE id = %s FOR UPDATE", (course_id,)
        )
        if course is None or course["archived_at"] is not None:
            return {"outcome": "closed"}
        if course["seats_left"] == 0:
            db.execute(
                conn,
                "INSERT INTO waitlist (course_id, learner_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (course_id, user.id),
            )
            return {"outcome": "waitlisted"}
        db.execute(conn, "UPDATE course SET seats_left = seats_left - 1 WHERE id = %s", (course_id,))
        db.execute(
            conn,
            "INSERT INTO enrolment (course_id, learner_id, role, status) VALUES (%s, %s, 'learner', 'active')",
            (course_id, user.id),
        )
        db.execute(
            conn,
            "INSERT INTO purchase (course_id, learner_id, paid_cents) VALUES (%s, %s, %s)",
            (course_id, user.id, pricing.quote(course["price_cents"], coupon)),
        )
        return {"outcome": "enrolled"}

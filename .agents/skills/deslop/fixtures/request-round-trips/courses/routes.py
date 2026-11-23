from typing import Any

from courses import actions, certificate, progress, schedule, store
from courses.access import require_enrolled
from web.app import User, route


@route("GET", "/courses/{course_id}/overview")
def overview(conn: Any, course_id: str, user: User) -> dict[str, object]:
    """The course page. Every tab of the page loads it, and the page reloads it after each action."""
    require_enrolled(conn, course_id, user)
    enrolment = store.get_enrolment(conn, course_id, user.id)
    return {
        "role": enrolment["role"],
        "progress": progress.completion(conn, course_id, user.id),
        "certificate": certificate.eligibility(conn, course_id, user.id),
        "next_lesson": schedule.next_lesson(conn, course_id, user.id),
        "actions": actions.available(conn, course_id, user.id),
    }

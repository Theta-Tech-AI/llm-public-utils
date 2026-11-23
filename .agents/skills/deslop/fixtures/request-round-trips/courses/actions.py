from dataclasses import dataclass
from typing import Any, Callable

from courses import certificate, progress, store


@dataclass(frozen=True)
class ActionContext:
    role: str
    status: str
    archived: bool
    percent: int
    eligible: bool


def build_context(conn: Any, course_id: str, learner_id: str) -> ActionContext:
    enrolment = store.get_enrolment(conn, course_id, learner_id)
    course = store.get_course(conn, course_id)
    return ActionContext(
        role=enrolment["role"],
        status=enrolment["status"],
        archived=course["archived_at"] is not None,
        percent=progress.completion(conn, course_id, learner_id)["percent"],
        eligible=bool(certificate.eligibility(conn, course_id, learner_id)["eligible"]),
    )


RULES: dict[str, Callable[[ActionContext], bool]] = {
    "resume": lambda c: c.status == "active" and c.percent < 100,
    "pause": lambda c: c.status == "active" and not c.archived,
    "request_certificate": lambda c: c.eligible,
    "post_announcement": lambda c: c.role == "tutor" and not c.archived,
    "leave": lambda c: c.status != "completed",
}


def allowed(conn: Any, course_id: str, learner_id: str, action: str) -> bool:
    """Whether the learner may take this action now. The action routes call this before they act."""
    return RULES[action](build_context(conn, course_id, learner_id))


def available(conn: Any, course_id: str, learner_id: str) -> list[str]:
    """The actions the course page offers as buttons."""
    return [action for action in RULES if allowed(conn, course_id, learner_id, action)]

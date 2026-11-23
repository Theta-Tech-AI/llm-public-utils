from projects import db
from web.app import Conflict, User


def require_lease(project_id: str, user: User) -> None:
    """Refuse the caller unless they hold the project's edit lease."""
    if db.LEASES.get(project_id) != user.id:
        raise Conflict("another editor holds this project")


def take_lease(project_id: str, user: User) -> None:
    """Take the edit lease when it is free; refuse when another editor holds it."""
    holder = db.LEASES.setdefault(project_id, user.id)
    if holder != user.id:
        raise Conflict("another editor holds this project")


def release(project_id: str, user: User) -> None:
    if db.LEASES.get(project_id) == user.id:
        del db.LEASES[project_id]

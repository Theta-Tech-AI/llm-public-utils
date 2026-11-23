from contextlib import contextmanager

from projects import db
from web.app import Conflict, User


@contextmanager
def editing_session(project_id: str, user: User):
    """Document edits run inside an editing session so two editors never write one document."""
    if db.LEASES.get(project_id, user.id) != user.id:
        raise Conflict("another editor holds this project")
    db.LEASES[project_id] = user.id
    yield

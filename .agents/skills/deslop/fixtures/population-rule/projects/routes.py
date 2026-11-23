from projects import db, lease
from web.app import User, route


@route("PATCH", "/projects/{id}", role="edit")
def rename_project(project_id: str, name: str, user: User) -> dict:
    lease.take_lease(project_id, user)
    db.ROWS.setdefault(project_id, {})["name"] = name
    return {"ok": True}


@route("PUT", "/projects/{id}/settings", role="edit")
def update_settings(project_id: str, settings: dict, user: User) -> dict:
    lease.require_lease(project_id, user)
    db.ROWS.setdefault(project_id, {})["settings"] = settings
    return {"ok": True}


@route("POST", "/projects/{id}/comments", role="comment")
def add_comment(project_id: str, text: str, user: User) -> dict:
    db.ROWS.setdefault(project_id, {}).setdefault("comments", []).append((user.id, text))
    return {"ok": True}


@route("GET", "/projects/{id}/export", role="view")
def export_pdf(project_id: str, user: User) -> bytes:
    return repr(db.ROWS.get(project_id, {})).encode()


@route("DELETE", "/projects/{id}/lease", role="edit")
def release_lease(project_id: str, user: User) -> dict:
    lease.release(project_id, user)
    return {"ok": True}

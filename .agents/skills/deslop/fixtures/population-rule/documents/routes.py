from documents.session import editing_session
from projects import db
from web.app import User, route


@route("PUT", "/projects/{id}/documents/{doc}", role="edit")
def edit_document(project_id: str, doc: str, body: str, user: User) -> dict:
    with editing_session(project_id, user):
        db.ROWS.setdefault(doc, {})["body"] = body
    return {"ok": True}


@route("POST", "/projects/{id}/documents/{doc}/lock", role="edit")
def lock_document(project_id: str, doc: str, user: User) -> dict:
    db.ROWS.setdefault(doc, {})["locked_by"] = user.id
    return {"ok": True}


@route("POST", "/projects/{id}/documents/{doc}/sign-off", role="edit")
def sign_off(project_id: str, doc: str, user: User) -> dict:
    db.ROWS.setdefault(doc, {})["stale_accepted_by"] = user.id
    return {"ok": True}

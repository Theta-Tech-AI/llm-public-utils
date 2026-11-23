from projects import db, lease
from web.app import User, route


def _render(text: str) -> str:
    return text.strip()


@route("PUT", "/projects/{id}/sections/{section}", role="edit")
def save_section(project_id: str, section: str, text: str, user: User) -> dict:
    lease.require_lease(project_id, user)
    rendered = _render(text)
    with db.row_lock(section) as row:
        row["text"] = rendered
        row["version"] = int(row.get("version", 0)) + 1
    return {"version": row["version"]}

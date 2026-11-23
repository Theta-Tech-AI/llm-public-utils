from jobs import runner
from web.app import User, route


@route("POST", "/projects/{id}/summary", role="edit")
def start_summary(project_id: str, user: User) -> dict:
    # Calls a paid model for every document in the project.
    run_id = runner.start("summary", project_id=project_id, requested_by=user.id)
    return {"run_id": run_id}

from profile import store


def welcome_message(user_id: str) -> dict[str, str]:
    profile = store.get(user_id)
    to = str(profile["email"]).strip()
    return {"to": to, "subject": "Welcome"}

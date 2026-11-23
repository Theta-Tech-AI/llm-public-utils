from profile import store


def vcard(user_id: str) -> str:
    profile = store.get(user_id)
    email = str(profile["email"]).strip().lower()
    phone = str(profile.get("phone") or "").strip()
    return f"BEGIN:VCARD\nEMAIL:{email}\nTEL:{phone}\nEND:VCARD"

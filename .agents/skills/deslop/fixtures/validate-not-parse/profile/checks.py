import re

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.IGNORECASE)
PHONE = re.compile(r"^\+?[0-9 ()-]{7,20}$")
INTEREST_OPTIONS = {"hiking", "cooking", "chess", "music"}


def field_problem(name: str, value: object) -> str | None:
    """Why a profile field cannot be saved, or None."""
    if name == "email":
        if not isinstance(value, str):
            return "email must be text"
        text = value.strip()
        return None if EMAIL.match(text) else "must be an email like name@example.com"
    if name == "phone":
        if not isinstance(value, str):
            return "phone must be text"
        text = value.strip()
        return None if PHONE.match(text) else "must be a phone number"
    if name == "interests":
        if not isinstance(value, list):
            return "interests must be a list"
        unknown = [item for item in value if item not in INTEREST_OPTIONS]
        return f"unknown interests: {unknown}" if unknown else None
    return f"unknown field {name!r}"

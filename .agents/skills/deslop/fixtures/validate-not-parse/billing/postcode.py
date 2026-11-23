import re
from typing import NewType

Postcode = NewType("Postcode", str)
_SHAPE = re.compile(r"^[A-Z0-9]{5,7}$")


def parse_postcode(raw: str) -> Postcode:
    """The one place a typed postcode becomes the stored form: no spaces, upper case."""
    text = raw.replace(" ", "").upper()
    if not _SHAPE.match(text):
        raise ValueError("must be a postcode")
    return Postcode(text)

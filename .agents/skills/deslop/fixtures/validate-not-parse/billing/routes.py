from billing.postcode import Postcode, parse_postcode

_BILLING: dict[str, Postcode] = {}


def save_billing(user_id: str, body: dict[str, str]) -> dict[str, str]:
    postcode = parse_postcode(body["postcode"])
    _BILLING[user_id] = postcode
    return {"postcode": postcode}


def billing_postcode(user_id: str) -> Postcode:
    return _BILLING[user_id]

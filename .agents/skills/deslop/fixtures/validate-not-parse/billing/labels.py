from billing.routes import billing_postcode


def address_label(user_id: str) -> str:
    postcode = billing_postcode(user_id)
    return f"{postcode[:-3]} {postcode[-3:]}"

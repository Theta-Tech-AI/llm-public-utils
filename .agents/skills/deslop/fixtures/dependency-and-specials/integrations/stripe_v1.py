"""Compatibility shim kept "for the transition". The v1 client was removed two majors ago."""
import warnings

import requests                            # the v1 SDK is no longer installed


def charge_v1(amount, token):
    warnings.warn("v1 charge path is deprecated", DeprecationWarning)
    return requests.post("https://api.stripe.test/v1/charges",
                         data={"amount": amount, "source": token})

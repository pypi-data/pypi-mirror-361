"""Set of utilities implementing a set of openid connect specs related actions"""

import base64
import json

SETTINGS_KEYS = (
    "oidc.client_secret",
    "oidc.scope",
    "oidc.client_id",
    "oidc.auth_endpoint_url",
    "oidc.token_endpoint_url",
    "oidc.logout_endpoint_url",
)


def check_settings(pyramid_settings):
    """Check that the app is correctly configured

    :raises Exception: _description_
    """
    for key in SETTINGS_KEYS:
        if key not in pyramid_settings:
            raise Exception(
                "Erreur de configuration, les clés {} "
                "sont requises, il manque {}".format(SETTINGS_KEYS, key)
            )


def parse_id_token(token: str) -> dict:
    """
    Parse an openid JWT token and returns the json loaded data

    :param token: The token to parse id_token or logout_token
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise Exception("Incorrect id token format")

    payload = parts[1]
    padded = payload + "=" * (4 - len(payload) % 4)
    decoded = base64.urlsafe_b64decode(padded)
    return json.loads(decoded)

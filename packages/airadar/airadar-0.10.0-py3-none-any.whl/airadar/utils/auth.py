import requests
import logging
import jwt
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def get_ccf_access_token(
    auth_tenant_url: str,
    auth_client_id: str,
    auth_client_secret: str,
    auth_client_scope: str,
) -> Optional[str]:
    """
    Retrieves a JWT access token using client credentials flow.

    Arguments:
        auth_tenant_url: The URL for your auth provider
        auth_client_id: The client ID
        auth_client_secret: The client secret
        auth_client_scope: [Optional] The permissions scope for the access token
    """

    payload = {
        "grant_type": "client_credentials",
        "client_id": auth_client_id,
        "client_secret": auth_client_secret,
        "roles": "api://radar-api/sdk",  # This adds the correct role that the api will verify
    }

    return _get_access_token(auth_tenant_url, payload)


def get_private_key_access_token(
    tenant_url: str,
    client_id: str,
    private_key: str,
    key_id: str,
    client_scope: str,
) -> Optional[str]:
    """
    Retrieves an API Access token based on a JWT signed with a user-provided private key.

    Arguments:
        tenant_url: The URL for your auth provider
        client_id: The client ID
        private_key: The client private key to sign the JWT
        key_id: The key ID to identify the private key
        client_scope: The permissions scope for the access token
    """

    # Set JWT expiration time (e.g., 1 hour from now)
    expiration_time = datetime.utcnow() + timedelta(hours=1)

    # Prepare JWT payload
    jwt_payload = {
        "iss": client_id,  # Client ID
        "sub": client_id,  # Client ID
        "aud": tenant_url,  # Token URL
        "exp": expiration_time,  # Expiration time
    }

    # Generate JWT token signed with private key
    jwt_token = jwt.encode(
        jwt_payload,
        private_key,
        algorithm="RS256",
        headers={"kid": key_id},
    )

    # Make a POST request with JWT token
    payload = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt_token,
        "scope": client_scope,
        "roles": "api://radar-api/sdk",
    }
    return _get_access_token(tenant_url, payload)


def _get_access_token(tenant_url: str, payload: dict[str, str]) -> Optional[str]:
    try:
        response = requests.post(
            tenant_url,
            data=payload,
            timeout=2,
        )

        resp = response.json().get("access_token")
        if resp and type(resp) is str:
            return resp
    except requests.exceptions.HTTPError as e:
        if e.response is not None:
            logger.error("Error with request: %s", e.response.status_code)
            logger.error(e.response.text)
        else:
            logger.error("Unknown HTTPError with request to %s", tenant_url)
    except requests.exceptions.JSONDecodeError as e:
        logger.error(
            "Response was not valid JSON for request to %s: %s", tenant_url, str(e)
        )
    except requests.exceptions.Timeout as e:
        logger.error("Request timed out for request to %s: %s", tenant_url, str(e))
    except Exception as e:
        logger.error("Unexpected error during request to %s: %s", tenant_url, str(e))

    return None

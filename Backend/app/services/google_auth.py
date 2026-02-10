"""
Google OAuth service for verifying Google ID tokens.
"""

from dataclasses import dataclass
from typing import Optional

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class GoogleAuthError(Exception):
    """Custom exception for Google authentication errors."""

    pass


@dataclass
class GoogleUserInfo:
    """User information extracted from a Google ID token."""

    google_id: str
    email: str
    email_verified: bool
    name: Optional[str] = None
    picture: Optional[str] = None


def verify_google_token(token: str) -> GoogleUserInfo:
    """
    Verify a Google ID token and extract user information.

    Args:
        token: The Google ID token (JWT credential) from the frontend.

    Returns:
        GoogleUserInfo with the user's Google profile data.

    Raises:
        GoogleAuthError: If the token is invalid, expired, or not issued for our client.
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise GoogleAuthError("Google OAuth is not configured on the server")

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        if idinfo["iss"] not in ("accounts.google.com", "https://accounts.google.com"):
            raise GoogleAuthError("Invalid token issuer")

        return GoogleUserInfo(
            google_id=idinfo["sub"],
            email=idinfo["email"],
            email_verified=idinfo.get("email_verified", False),
            name=idinfo.get("name"),
            picture=idinfo.get("picture"),
        )

    except ValueError as e:
        logger.warning(f"Google token verification failed: {e}")
        raise GoogleAuthError(f"Invalid Google token: {e}")
    except KeyError as e:
        logger.warning(f"Google token missing required field: {e}")
        raise GoogleAuthError(f"Google token missing required field: {e}")

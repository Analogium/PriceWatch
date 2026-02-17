from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.base import get_db
from app.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, t
from app.models.user import User
from app.models.user_preferences import UserPreferences

security = HTTPBearer()


def parse_accept_language(request: Request) -> str:
    """Parse Accept-Language header and return best supported language."""
    accept_lang = request.headers.get("Accept-Language", "")
    if not accept_lang:
        return DEFAULT_LANGUAGE
    # Parse first language tag (e.g. "en-US,en;q=0.9,fr;q=0.8" -> "en")
    primary = accept_lang.split(",")[0].split(";")[0].strip().split("-")[0].lower()
    if primary in SUPPORTED_LANGUAGES:
        return primary
    return DEFAULT_LANGUAGE


def get_language(request: Request, db: Session = Depends(get_db)) -> str:
    """Detect language from authenticated user preferences or Accept-Language header."""
    # Try to get language from authenticated user
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = decode_access_token(token)
        if payload:
            email = payload.get("sub")
            if email:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
                    if prefs and prefs.language in SUPPORTED_LANGUAGES:
                        return prefs.language

    # Fall back to Accept-Language header
    return parse_accept_language(request)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.
    Validates the JWT token and returns the user from the database.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("invalid_or_expired_token"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: Optional[str] = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("invalid_token_payload"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("user_not_found"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to verify the current user is an admin.
    Raises 403 Forbidden if user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("admin_required"))
    return current_user

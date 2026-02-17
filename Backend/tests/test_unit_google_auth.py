"""
Unit tests for Google OAuth authentication.
Tests the Google token verification service and the /auth/google endpoint.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.google_auth import GoogleAuthError, GoogleUserInfo, verify_google_token


@pytest.mark.unit
class TestGoogleAuthService:
    """Test suite for Google OAuth token verification service."""

    @patch("app.services.google_auth.settings")
    @patch("app.services.google_auth.id_token.verify_oauth2_token")
    def test_verify_google_token_success(self, mock_verify, mock_settings):
        """Test successful Google token verification."""
        mock_settings.GOOGLE_CLIENT_ID = "test-client-id.apps.googleusercontent.com"
        mock_verify.return_value = {
            "iss": "accounts.google.com",
            "sub": "google_user_123",
            "email": "test@gmail.com",
            "email_verified": True,
            "name": "Test User",
            "picture": "https://lh3.googleusercontent.com/photo.jpg",
        }

        result = verify_google_token("valid_google_token")

        assert isinstance(result, GoogleUserInfo)
        assert result.google_id == "google_user_123"
        assert result.email == "test@gmail.com"
        assert result.email_verified is True
        assert result.name == "Test User"
        assert result.picture == "https://lh3.googleusercontent.com/photo.jpg"

    @patch("app.services.google_auth.settings")
    @patch("app.services.google_auth.id_token.verify_oauth2_token")
    def test_verify_google_token_https_issuer(self, mock_verify, mock_settings):
        """Test token verification with https issuer variant."""
        mock_settings.GOOGLE_CLIENT_ID = "test-client-id.apps.googleusercontent.com"
        mock_verify.return_value = {
            "iss": "https://accounts.google.com",
            "sub": "google_user_123",
            "email": "test@gmail.com",
            "email_verified": True,
        }

        result = verify_google_token("valid_google_token")

        assert result.google_id == "google_user_123"

    @patch("app.services.google_auth.settings")
    @patch("app.services.google_auth.id_token.verify_oauth2_token")
    def test_verify_google_token_invalid(self, mock_verify, mock_settings):
        """Test that invalid tokens raise GoogleAuthError."""
        mock_settings.GOOGLE_CLIENT_ID = "test-client-id.apps.googleusercontent.com"
        mock_verify.side_effect = ValueError("Token expired or invalid")

        with pytest.raises(GoogleAuthError, match="Invalid Google token"):
            verify_google_token("invalid_token")

    @patch("app.services.google_auth.settings")
    @patch("app.services.google_auth.id_token.verify_oauth2_token")
    def test_verify_google_token_wrong_issuer(self, mock_verify, mock_settings):
        """Test that tokens from wrong issuer are rejected."""
        mock_settings.GOOGLE_CLIENT_ID = "test-client-id.apps.googleusercontent.com"
        mock_verify.return_value = {
            "iss": "evil.com",
            "sub": "google_user_123",
            "email": "test@gmail.com",
            "email_verified": True,
        }

        with pytest.raises(GoogleAuthError, match="Invalid token issuer"):
            verify_google_token("token_wrong_issuer")

    @patch("app.services.google_auth.settings")
    def test_verify_google_token_not_configured(self, mock_settings):
        """Test error when GOOGLE_CLIENT_ID is not set."""
        mock_settings.GOOGLE_CLIENT_ID = None

        with pytest.raises(GoogleAuthError, match="not configured"):
            verify_google_token("any_token")

    @patch("app.services.google_auth.settings")
    @patch("app.services.google_auth.id_token.verify_oauth2_token")
    def test_verify_google_token_missing_email(self, mock_verify, mock_settings):
        """Test that tokens missing required fields raise GoogleAuthError."""
        mock_settings.GOOGLE_CLIENT_ID = "test-client-id.apps.googleusercontent.com"
        mock_verify.return_value = {
            "iss": "accounts.google.com",
            "sub": "google_user_123",
            # Missing "email" field
        }

        with pytest.raises(GoogleAuthError, match="missing required field"):
            verify_google_token("token_missing_email")


@pytest.mark.unit
class TestGoogleAuthEndpoint:
    """Test suite for POST /auth/google endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.verify_google_token")
    @patch("app.api.endpoints.auth.create_access_token")
    @patch("app.api.endpoints.auth.create_refresh_token")
    async def test_google_auth_new_user(self, mock_refresh_token, mock_access_token, mock_verify, mock_rate_limit):
        """Test Google auth creates new user when no account exists."""
        mock_rate_limit.return_value = None
        mock_verify.return_value = GoogleUserInfo(
            google_id="google_123",
            email="newuser@gmail.com",
            email_verified=True,
            name="New User",
        )
        mock_access_token.return_value = "access_token_123"
        mock_refresh_token.return_value = "refresh_token_456"

        mock_db = Mock(spec=Session)
        # Both queries (by google_id, by email) return None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Accept-Language": "en"}

        from app.api.endpoints.auth import google_auth
        from app.schemas.user import GoogleAuthRequest

        google_data = GoogleAuthRequest(credential="google_id_token")

        with (
            patch.object(mock_db, "add") as mock_add,
            patch.object(mock_db, "commit") as mock_commit,
            patch.object(mock_db, "refresh") as mock_refresh_db,
        ):

            def refresh_user(user):
                user.id = 1

            mock_refresh_db.side_effect = refresh_user

            result = await google_auth(mock_request, google_data, mock_db)

            assert result["access_token"] == "access_token_123"
            assert result["refresh_token"] == "refresh_token_456"
            assert result["token_type"] == "bearer"
            # User + UserPreferences = 2 adds
            assert mock_add.call_count == 2
            # User commit + preferences commit = 2
            assert mock_commit.call_count == 2

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.verify_google_token")
    @patch("app.api.endpoints.auth.create_access_token")
    @patch("app.api.endpoints.auth.create_refresh_token")
    async def test_google_auth_existing_google_user(
        self, mock_refresh_token, mock_access_token, mock_verify, mock_rate_limit
    ):
        """Test Google auth logs in existing Google user."""
        mock_rate_limit.return_value = None
        mock_verify.return_value = GoogleUserInfo(
            google_id="google_123",
            email="existing@gmail.com",
            email_verified=True,
        )
        mock_access_token.return_value = "access_token_123"
        mock_refresh_token.return_value = "refresh_token_456"

        mock_user = Mock(spec=User)
        mock_user.email = "existing@gmail.com"
        mock_user.google_id = "google_123"

        mock_db = Mock(spec=Session)
        # First query (by google_id) returns user
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Accept-Language": "en"}

        from app.api.endpoints.auth import google_auth
        from app.schemas.user import GoogleAuthRequest

        google_data = GoogleAuthRequest(credential="google_id_token")
        result = await google_auth(mock_request, google_data, mock_db)

        assert result["access_token"] == "access_token_123"
        assert result["token_type"] == "bearer"
        # No new user created, no add/commit for user creation
        mock_db.add.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.verify_google_token")
    @patch("app.api.endpoints.auth.create_access_token")
    @patch("app.api.endpoints.auth.create_refresh_token")
    async def test_google_auth_link_existing_local_user(
        self, mock_refresh_token, mock_access_token, mock_verify, mock_rate_limit
    ):
        """Test Google auth links to existing local account with matching email."""
        mock_rate_limit.return_value = None
        mock_verify.return_value = GoogleUserInfo(
            google_id="google_123",
            email="local@example.com",
            email_verified=True,
        )
        mock_access_token.return_value = "access_token_123"
        mock_refresh_token.return_value = "refresh_token_456"

        mock_user = Mock(spec=User)
        mock_user.email = "local@example.com"
        mock_user.google_id = None
        mock_user.auth_provider = "local"
        mock_user.is_verified = False

        mock_db = Mock(spec=Session)
        # First query (by google_id) returns None, second (by email) returns user
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, mock_user]
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Accept-Language": "en"}

        from app.api.endpoints.auth import google_auth
        from app.schemas.user import GoogleAuthRequest

        google_data = GoogleAuthRequest(credential="google_id_token")
        result = await google_auth(mock_request, google_data, mock_db)

        assert result["access_token"] == "access_token_123"
        assert result["token_type"] == "bearer"
        # Account linked
        assert mock_user.google_id == "google_123"
        assert mock_user.auth_provider == "both"
        assert mock_user.is_verified is True
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.verify_google_token")
    async def test_google_auth_invalid_token(self, mock_verify, mock_rate_limit):
        """Test Google auth with invalid credential returns 401."""
        mock_rate_limit.return_value = None
        mock_verify.side_effect = GoogleAuthError("Invalid Google token: Token expired")

        mock_db = Mock(spec=Session)
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Accept-Language": "en"}

        from app.api.endpoints.auth import google_auth
        from app.schemas.user import GoogleAuthRequest

        google_data = GoogleAuthRequest(credential="invalid_token")

        with pytest.raises(HTTPException) as exc_info:
            await google_auth(mock_request, google_data, mock_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.verify_google_token")
    async def test_google_auth_unverified_email(self, mock_verify, mock_rate_limit):
        """Test Google auth rejects unverified Google emails."""
        mock_rate_limit.return_value = None
        mock_verify.return_value = GoogleUserInfo(
            google_id="google_123",
            email="unverified@gmail.com",
            email_verified=False,
        )

        mock_db = Mock(spec=Session)
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Accept-Language": "en"}

        from app.api.endpoints.auth import google_auth
        from app.schemas.user import GoogleAuthRequest

        google_data = GoogleAuthRequest(credential="google_id_token")

        with pytest.raises(HTTPException) as exc_info:
            await google_auth(mock_request, google_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "not verified" in exc_info.value.detail


@pytest.mark.unit
class TestLoginGoogleOnlyUser:
    """Test that Google-only users cannot log in with password."""

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    async def test_login_google_only_user_rejected(self, mock_rate_limit):
        """Test that Google-only users get a helpful error on password login."""
        mock_rate_limit.return_value = None

        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.email = "google@gmail.com"
        mock_user.password_hash = None  # Google-only user
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_request = Mock(spec=Request)
        mock_request.headers = {"Accept-Language": "en"}
        mock_form_data = Mock()
        mock_form_data.username = "google@gmail.com"
        mock_form_data.password = "SomePassword123!"

        from app.api.endpoints.auth import login

        with pytest.raises(HTTPException) as exc_info:
            await login(mock_request, mock_form_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "Google" in exc_info.value.detail

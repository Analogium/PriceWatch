"""
Unit tests for authentication endpoints.
Tests registration, login, token refresh, password reset, and verification endpoints.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin


@pytest.mark.unit
class TestRegisterEndpoint:
    """Test suite for user registration endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.validate_password_strength")
    @patch("app.api.endpoints.auth.generate_verification_token")
    @patch("app.api.endpoints.auth.get_password_hash")
    @patch("app.api.endpoints.auth.email_service.send_verification_email")
    async def test_register_success(
        self, mock_send_email, mock_hash, mock_gen_token, mock_validate_pwd, mock_rate_limit
    ):
        """Test successful user registration."""
        # Setup mocks
        mock_rate_limit.return_value = None
        mock_validate_pwd.return_value = (True, None)
        mock_gen_token.return_value = "verification_token_123"
        mock_hash.return_value = "hashed_password"
        mock_send_email.return_value = None

        # Mock database
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user

        # Mock request
        mock_request = Mock(spec=Request)

        # User data
        user_data = UserCreate(email="test@example.com", password="SecurePass123!")

        # Import and call the endpoint
        from app.api.endpoints.auth import register

        # Mock the database operations
        with (
            patch.object(mock_db, "add") as mock_add,
            patch.object(mock_db, "commit") as mock_commit,
            patch.object(mock_db, "refresh") as mock_refresh,
        ):

            def refresh_user(user):
                user.id = 1

            mock_refresh.side_effect = refresh_user

            result = await register(mock_request, user_data, mock_db)

            # Assertions
            mock_validate_pwd.assert_called_once_with("SecurePass123!")
            mock_gen_token.assert_called_once()
            mock_hash.assert_called_once_with("SecurePass123!")
            mock_commit.assert_called_once()
            mock_send_email.assert_called_once_with("test@example.com", "verification_token_123")

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.validate_password_strength")
    async def test_register_weak_password(self, mock_validate_pwd, mock_rate_limit):
        """Test registration with weak password."""
        mock_rate_limit.return_value = None
        mock_validate_pwd.return_value = (False, "Password is too weak")

        mock_db = Mock(spec=Session)
        mock_request = Mock(spec=Request)
        user_data = UserCreate(email="test@example.com", password="weak")

        from app.api.endpoints.auth import register

        with pytest.raises(HTTPException) as exc_info:
            await register(mock_request, user_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "Password is too weak" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.validate_password_strength")
    async def test_register_existing_email(self, mock_validate_pwd, mock_rate_limit):
        """Test registration with already registered email."""
        mock_rate_limit.return_value = None
        mock_validate_pwd.return_value = (True, None)

        # Mock existing user
        mock_db = Mock(spec=Session)
        existing_user = Mock(spec=User)
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user

        mock_request = Mock(spec=Request)
        user_data = UserCreate(email="existing@example.com", password="SecurePass123!")

        from app.api.endpoints.auth import register

        with pytest.raises(HTTPException) as exc_info:
            await register(mock_request, user_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "Email already registered" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.validate_password_strength")
    @patch("app.api.endpoints.auth.generate_verification_token")
    @patch("app.api.endpoints.auth.get_password_hash")
    @patch("app.api.endpoints.auth.email_service.send_verification_email")
    async def test_register_email_send_failure(
        self, mock_send_email, mock_hash, mock_gen_token, mock_validate_pwd, mock_rate_limit
    ):
        """Test registration when email sending fails (should still succeed)."""
        mock_rate_limit.return_value = None
        mock_validate_pwd.return_value = (True, None)
        mock_gen_token.return_value = "verification_token_123"
        mock_hash.return_value = "hashed_password"
        mock_send_email.side_effect = Exception("SMTP connection failed")

        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        mock_request = Mock(spec=Request)
        user_data = UserCreate(email="test@example.com", password="SecurePass123!")

        from app.api.endpoints.auth import register

        with (
            patch.object(mock_db, "add") as mock_add,
            patch.object(mock_db, "commit") as mock_commit,
            patch.object(mock_db, "refresh") as mock_refresh,
        ):

            def refresh_user(user):
                user.id = 1

            mock_refresh.side_effect = refresh_user

            # Should still succeed even if email fails
            result = await register(mock_request, user_data, mock_db)

            mock_commit.assert_called_once()
            assert mock_send_email.called


@pytest.mark.unit
class TestLoginEndpoint:
    """Test suite for login endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.verify_password")
    @patch("app.api.endpoints.auth.create_access_token")
    @patch("app.api.endpoints.auth.create_refresh_token")
    async def test_login_success(self, mock_refresh_token, mock_access_token, mock_verify_pwd, mock_rate_limit):
        """Test successful login."""
        mock_rate_limit.return_value = None
        mock_verify_pwd.return_value = True
        mock_access_token.return_value = "access_token_123"
        mock_refresh_token.return_value = "refresh_token_456"

        # Mock user
        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_user.password_hash = "hashed_password"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_request = Mock(spec=Request)
        credentials = UserLogin(email="test@example.com", password="SecurePass123!")

        from app.api.endpoints.auth import login

        result = await login(mock_request, credentials, mock_db)

        assert result["access_token"] == "access_token_123"
        assert result["refresh_token"] == "refresh_token_456"
        assert result["token_type"] == "bearer"
        mock_verify_pwd.assert_called_once_with("SecurePass123!", "hashed_password")

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    async def test_login_user_not_found(self, mock_rate_limit):
        """Test login with non-existent user."""
        mock_rate_limit.return_value = None

        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        mock_request = Mock(spec=Request)
        credentials = UserLogin(email="nonexistent@example.com", password="SecurePass123!")

        from app.api.endpoints.auth import login

        with pytest.raises(HTTPException) as exc_info:
            await login(mock_request, credentials, mock_db)

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.verify_password")
    async def test_login_wrong_password(self, mock_verify_pwd, mock_rate_limit):
        """Test login with incorrect password."""
        mock_rate_limit.return_value = None
        mock_verify_pwd.return_value = False

        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.password_hash = "hashed_password"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_request = Mock(spec=Request)
        credentials = UserLogin(email="test@example.com", password="WrongPassword123!")

        from app.api.endpoints.auth import login

        with pytest.raises(HTTPException) as exc_info:
            await login(mock_request, credentials, mock_db)

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in exc_info.value.detail


@pytest.mark.unit
class TestGetMeEndpoint:
    """Test suite for /me endpoint."""

    def test_get_me_success(self):
        """Test getting current user information."""
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"

        from app.api.endpoints.auth import get_me

        result = get_me(current_user=mock_user)

        assert result == mock_user


@pytest.mark.unit
class TestRefreshTokenEndpoint:
    """Test suite for token refresh endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.decode_access_token")
    @patch("app.api.endpoints.auth.create_access_token")
    async def test_refresh_token_success(self, mock_create_access, mock_decode, mock_rate_limit):
        """Test successful token refresh."""
        mock_rate_limit.return_value = None
        mock_decode.return_value = {"sub": "test@example.com", "type": "refresh"}
        mock_create_access.return_value = "new_access_token"

        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import refresh_token
        from app.schemas.user import RefreshTokenRequest

        token_request = RefreshTokenRequest(refresh_token="old_refresh_token")

        result = await refresh_token(mock_request, token_request, mock_db)

        assert result["access_token"] == "new_access_token"
        assert result["token_type"] == "bearer"

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.decode_access_token")
    async def test_refresh_token_invalid_token(self, mock_decode, mock_rate_limit):
        """Test refresh with invalid token."""
        mock_rate_limit.return_value = None
        mock_decode.return_value = None

        mock_db = Mock(spec=Session)
        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import refresh_token
        from app.schemas.user import RefreshTokenRequest

        token_request = RefreshTokenRequest(refresh_token="invalid_token")

        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(mock_request, token_request, mock_db)

        assert exc_info.value.status_code == 401
        assert "Invalid refresh token" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.decode_access_token")
    async def test_refresh_token_wrong_type(self, mock_decode, mock_rate_limit):
        """Test refresh with access token instead of refresh token."""
        mock_rate_limit.return_value = None
        mock_decode.return_value = {"sub": "test@example.com", "type": "access"}  # Wrong type

        mock_db = Mock(spec=Session)
        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import refresh_token
        from app.schemas.user import RefreshTokenRequest

        token_request = RefreshTokenRequest(refresh_token="access_token")

        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(mock_request, token_request, mock_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.decode_access_token")
    async def test_refresh_token_missing_sub(self, mock_decode, mock_rate_limit):
        """Test refresh token with missing subject."""
        mock_rate_limit.return_value = None
        mock_decode.return_value = {"type": "refresh"}  # No sub field

        mock_db = Mock(spec=Session)
        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import refresh_token
        from app.schemas.user import RefreshTokenRequest

        token_request = RefreshTokenRequest(refresh_token="token_without_sub")

        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(mock_request, token_request, mock_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.decode_access_token")
    async def test_refresh_token_user_not_found(self, mock_decode, mock_rate_limit):
        """Test refresh token when user no longer exists."""
        mock_rate_limit.return_value = None
        mock_decode.return_value = {"sub": "deleted@example.com", "type": "refresh"}

        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None  # User not found

        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import refresh_token
        from app.schemas.user import RefreshTokenRequest

        token_request = RefreshTokenRequest(refresh_token="valid_token")

        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(mock_request, token_request, mock_db)

        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail


@pytest.mark.unit
class TestVerifyEmailEndpoint:
    """Test suite for email verification endpoint."""

    @pytest.mark.asyncio
    async def test_verify_email_success(self):
        """Test successful email verification."""
        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.is_verified = False
        mock_user.verification_token = "valid_token"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        from app.api.endpoints.auth import verify_email
        from app.schemas.user import EmailVerification

        verification_data = EmailVerification(token="valid_token")

        result = await verify_email(verification_data, mock_db)

        assert result["message"] == "Email verified successfully"
        assert mock_user.is_verified is True
        assert mock_user.verification_token is None
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self):
        """Test email verification with invalid token."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        from app.api.endpoints.auth import verify_email
        from app.schemas.user import EmailVerification

        verification_data = EmailVerification(token="invalid_token")

        with pytest.raises(HTTPException) as exc_info:
            await verify_email(verification_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "Invalid verification token" in exc_info.value.detail


@pytest.mark.unit
class TestForgotPasswordEndpoint:
    """Test suite for forgot password endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.generate_reset_token")
    @patch("app.api.endpoints.auth.email_service.send_password_reset_email")
    async def test_forgot_password_success(self, mock_send_email, mock_gen_token, mock_rate_limit):
        """Test successful password reset request."""
        mock_rate_limit.return_value = None
        mock_gen_token.return_value = "reset_token_123"
        mock_send_email.return_value = None

        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import forgot_password
        from app.schemas.user import PasswordResetRequest

        reset_data = PasswordResetRequest(email="test@example.com")

        result = await forgot_password(mock_request, reset_data, mock_db)

        assert "message" in result
        mock_gen_token.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_send_email.assert_called_once_with("test@example.com", "reset_token_123")

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    async def test_forgot_password_user_not_found(self, mock_rate_limit):
        """Test password reset for non-existent user (should still return success for security)."""
        mock_rate_limit.return_value = None

        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import forgot_password
        from app.schemas.user import PasswordResetRequest

        reset_data = PasswordResetRequest(email="nonexistent@example.com")

        result = await forgot_password(mock_request, reset_data, mock_db)

        # Should return success message even if user doesn't exist (security best practice)
        assert "message" in result

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.generate_reset_token")
    @patch("app.api.endpoints.auth.email_service.send_password_reset_email")
    async def test_forgot_password_email_failure(self, mock_send_email, mock_gen_token, mock_rate_limit):
        """Test password reset when email sending fails (should still succeed)."""
        mock_rate_limit.return_value = None
        mock_gen_token.return_value = "reset_token_123"
        mock_send_email.side_effect = Exception("SMTP error")

        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import forgot_password
        from app.schemas.user import PasswordResetRequest

        reset_data = PasswordResetRequest(email="test@example.com")

        # Should still succeed even if email fails
        result = await forgot_password(mock_request, reset_data, mock_db)

        assert "message" in result
        mock_db.commit.assert_called_once()


@pytest.mark.unit
class TestResetPasswordEndpoint:
    """Test suite for password reset confirmation endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.validate_password_strength")
    @patch("app.api.endpoints.auth.get_password_hash")
    async def test_reset_password_success(self, mock_hash, mock_validate_pwd, mock_rate_limit):
        """Test successful password reset."""
        mock_rate_limit.return_value = None
        mock_validate_pwd.return_value = (True, None)
        mock_hash.return_value = "new_hashed_password"

        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.reset_token = "valid_reset_token"
        mock_user.password_hash = "old_hash"
        mock_user.reset_token_expires = datetime(2099, 12, 31)  # Far future
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import reset_password
        from app.schemas.user import PasswordResetConfirm

        reset_data = PasswordResetConfirm(token="valid_reset_token", new_password="NewSecurePass123!")

        result = await reset_password(mock_request, reset_data, mock_db)

        assert result["message"] == "Password reset successfully"
        assert mock_user.password_hash == "new_hashed_password"
        assert mock_user.reset_token is None
        assert mock_user.reset_token_expires is None
        mock_validate_pwd.assert_called_once_with("NewSecurePass123!")
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.validate_password_strength")
    async def test_reset_password_invalid_token(self, mock_validate_pwd, mock_rate_limit):
        """Test password reset with invalid token."""
        mock_rate_limit.return_value = None
        mock_validate_pwd.return_value = (True, None)

        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import reset_password
        from app.schemas.user import PasswordResetConfirm

        reset_data = PasswordResetConfirm(token="invalid_token", new_password="NewSecurePass123!")

        with pytest.raises(HTTPException) as exc_info:
            await reset_password(mock_request, reset_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "Invalid reset token" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.validate_password_strength")
    async def test_reset_password_weak_password(self, mock_validate_pwd, mock_rate_limit):
        """Test password reset with weak password."""
        mock_rate_limit.return_value = None
        mock_validate_pwd.return_value = (False, "Password is too weak")

        mock_db = Mock(spec=Session)
        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import reset_password
        from app.schemas.user import PasswordResetConfirm

        reset_data = PasswordResetConfirm(token="valid_token", new_password="weak")

        with pytest.raises(HTTPException) as exc_info:
            await reset_password(mock_request, reset_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "Password is too weak" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("app.api.endpoints.auth.rate_limiter.check_rate_limit")
    @patch("app.api.endpoints.auth.validate_password_strength")
    async def test_reset_password_expired_token(self, mock_validate_pwd, mock_rate_limit):
        """Test password reset with expired token."""
        mock_rate_limit.return_value = None
        mock_validate_pwd.return_value = (True, None)

        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.reset_token = "valid_token"
        mock_user.reset_token_expires = datetime(2020, 1, 1)  # Expired
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_request = Mock(spec=Request)

        from app.api.endpoints.auth import reset_password
        from app.schemas.user import PasswordResetConfirm

        reset_data = PasswordResetConfirm(token="valid_token", new_password="NewSecurePass123!")

        with pytest.raises(HTTPException) as exc_info:
            await reset_password(mock_request, reset_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "expired" in exc_info.value.detail.lower()

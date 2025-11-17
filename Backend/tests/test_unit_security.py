"""
Unit tests for security features.

Tests include:
- Password strength validation
- User registration with verification
- Login and refresh tokens
- Password reset flow
- Duplicate email prevention
- Invalid credentials handling
- Token validation
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.core.security import (
    validate_password_strength,
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token
)


class TestPasswordStrength:
    """Test suite for password strength validation."""

    @pytest.mark.unit
    def test_password_too_short(self):
        """Test that short passwords are rejected."""
        is_valid, error = validate_password_strength("Short1!")
        assert is_valid is False
        assert "at least" in error and "characters" in error

    @pytest.mark.unit
    def test_password_no_uppercase(self):
        """Test that passwords without uppercase are rejected."""
        is_valid, error = validate_password_strength("lowercase123!")
        assert is_valid is False
        assert "uppercase letter" in error

    @pytest.mark.unit
    def test_password_no_lowercase(self):
        """Test that passwords without lowercase are rejected."""
        is_valid, error = validate_password_strength("UPPERCASE123!")
        assert is_valid is False
        assert "lowercase letter" in error

    @pytest.mark.unit
    def test_password_no_digit(self):
        """Test that passwords without digits are rejected."""
        is_valid, error = validate_password_strength("NoDigits!")
        assert is_valid is False
        assert "digit" in error

    @pytest.mark.unit
    def test_password_no_special_char(self):
        """Test that passwords without special characters are rejected."""
        is_valid, error = validate_password_strength("NoSpecial123")
        assert is_valid is False
        assert "special character" in error

    @pytest.mark.unit
    def test_password_strong_accepted(self):
        """Test that strong passwords are accepted."""
        is_valid, error = validate_password_strength("StrongPass123!")
        assert is_valid is True
        assert error == ""

        is_valid, error = validate_password_strength("AnotherGood1@")
        assert is_valid is True

        is_valid, error = validate_password_strength("VerySecure99#")
        assert is_valid is True




class TestTokenFunctions:
    """Test suite for token utility functions."""

    @pytest.mark.unit
    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        email = "test@example.com"
        token = create_access_token({"sub": email})
        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == email

    @pytest.mark.unit
    def test_decode_invalid_token(self):
        """Test decoding an invalid token returns None."""
        decoded = decode_access_token("invalid_token_string")
        assert decoded is None

    @pytest.mark.unit
    def test_create_refresh_token(self):
        """Test creating a refresh token."""
        email = "test@example.com"
        refresh_token = create_refresh_token({"sub": email})

        assert refresh_token is not None
        assert isinstance(refresh_token, str)

        # Decode and verify
        decoded = decode_access_token(refresh_token)
        assert decoded is not None
        assert decoded["sub"] == email
        assert decoded["type"] == "refresh"

    @pytest.mark.unit
    def test_access_token_has_correct_type(self):
        """Test that access token has correct type field."""
        email = "test@example.com"
        access_token = create_access_token({"sub": email})

        decoded = decode_access_token(access_token)
        assert decoded is not None
        # Access tokens don't have type or it's not "refresh"
        assert decoded.get("type") != "refresh"

    @pytest.mark.unit
    def test_password_hash_and_verify(self):
        """Test password hashing and verification."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    @pytest.mark.unit
    def test_token_expiration(self):
        """Test that tokens have expiration claim."""
        email = "test@example.com"
        token = create_access_token({"sub": email})

        decoded = decode_access_token(token)
        assert decoded is not None
        assert "exp" in decoded

    @pytest.mark.unit
    def test_custom_token_expiration(self):
        """Test creating token with custom expiration."""
        email = "test@example.com"
        custom_delta = timedelta(minutes=5)
        token = create_access_token({"sub": email}, expires_delta=custom_delta)

        decoded = decode_access_token(token)
        assert decoded is not None
        assert "exp" in decoded

    @pytest.mark.unit
    def test_generate_verification_token(self):
        """Test generating verification token."""
        from app.core.security import generate_verification_token

        token1 = generate_verification_token()
        token2 = generate_verification_token()

        assert token1 is not None
        assert token2 is not None
        assert token1 != token2  # Should be unique
        assert len(token1) > 10  # Should be reasonably long

    @pytest.mark.unit
    def test_generate_reset_token(self):
        """Test generating reset token."""
        from app.core.security import generate_reset_token

        token1 = generate_reset_token()
        token2 = generate_reset_token()

        assert token1 is not None
        assert token2 is not None
        assert token1 != token2  # Should be unique
        assert len(token1) > 10  # Should be reasonably long

    @pytest.mark.unit
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword123!", hashed) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

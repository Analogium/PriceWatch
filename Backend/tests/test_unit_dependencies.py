"""
Unit tests for API dependencies.
Tests authentication and database dependencies.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.models.user import User


@pytest.mark.unit
class TestGetCurrentUser:
    """Test suite for get_current_user dependency."""

    def test_get_current_user_success(self):
        """Test successful user retrieval with valid token."""
        # Mock credentials
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "valid_token"

        # Mock database session
        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_user.id = 1

        # Mock query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        # Mock token decoding
        with patch("app.api.dependencies.decode_access_token") as mock_decode:
            mock_decode.return_value = {"sub": "test@example.com"}

            result = get_current_user(mock_credentials, mock_db)

            assert result == mock_user
            mock_decode.assert_called_once_with("valid_token")
            mock_db.query.assert_called_once()

    def test_get_current_user_invalid_token(self):
        """Test with invalid token returns None from decode."""
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "invalid_token"
        mock_db = Mock(spec=Session)

        with patch("app.api.dependencies.decode_access_token") as mock_decode:
            mock_decode.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_credentials, mock_db)

            assert exc_info.value.status_code == 401
            assert "Invalid or expired token" in exc_info.value.detail

    def test_get_current_user_missing_sub_in_payload(self):
        """Test with token payload missing 'sub' field."""
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "token_without_sub"
        mock_db = Mock(spec=Session)

        with patch("app.api.dependencies.decode_access_token") as mock_decode:
            mock_decode.return_value = {"exp": 1234567890}  # No 'sub' field

            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_credentials, mock_db)

            assert exc_info.value.status_code == 401
            assert "Invalid token payload" in exc_info.value.detail

    def test_get_current_user_user_not_found(self):
        """Test when user email from token doesn't exist in database."""
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "valid_token"
        mock_db = Mock(spec=Session)

        # Mock query chain returning None
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None  # User not found
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        with patch("app.api.dependencies.decode_access_token") as mock_decode:
            mock_decode.return_value = {"sub": "nonexistent@example.com"}

            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_credentials, mock_db)

            assert exc_info.value.status_code == 401
            assert "User not found" in exc_info.value.detail

    def test_get_current_user_token_extraction(self):
        """Test that token is correctly extracted from credentials."""
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        mock_credentials.credentials = test_token

        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_user
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        with patch("app.api.dependencies.decode_access_token") as mock_decode:
            mock_decode.return_value = {"sub": "user@example.com"}

            get_current_user(mock_credentials, mock_db)

            # Verify the exact token was passed
            mock_decode.assert_called_once_with(test_token)

    def test_get_current_user_www_authenticate_header(self):
        """Test that WWW-Authenticate header is included in error responses."""
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "invalid"
        mock_db = Mock(spec=Session)

        with patch("app.api.dependencies.decode_access_token") as mock_decode:
            mock_decode.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_credentials, mock_db)

            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

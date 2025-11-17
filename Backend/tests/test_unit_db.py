"""
Unit tests for database configuration and session management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.db.base import get_db, Base


@pytest.mark.unit
class TestDatabaseSession:
    """Test suite for database session management."""

    @patch("app.db.base.SessionLocal")
    def test_get_db_yields_session(self, mock_session_local):
        """Test that get_db yields a database session."""
        mock_session = Mock(spec=Session)
        mock_session_local.return_value = mock_session

        # Use the generator
        db_generator = get_db()
        db = next(db_generator)

        assert db == mock_session
        mock_session_local.assert_called_once()

    @patch("app.db.base.SessionLocal")
    def test_get_db_closes_session(self, mock_session_local):
        """Test that get_db closes session after use."""
        mock_session = Mock(spec=Session)
        mock_session_local.return_value = mock_session

        # Simulate using the generator in a try-finally
        db_generator = get_db()
        db = next(db_generator)

        try:
            db_generator.close()
        except StopIteration:
            pass

        mock_session.close.assert_called_once()

    @patch("app.db.base.SessionLocal")
    def test_get_db_closes_on_exception(self, mock_session_local):
        """Test that get_db closes session even if exception occurs."""
        mock_session = Mock(spec=Session)
        mock_session_local.return_value = mock_session

        db_generator = get_db()
        db = next(db_generator)

        # Simulate exception
        try:
            db_generator.throw(Exception("Test error"))
        except Exception:
            pass

        mock_session.close.assert_called_once()

    def test_base_metadata_exists(self):
        """Test that Base has metadata attribute."""
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None

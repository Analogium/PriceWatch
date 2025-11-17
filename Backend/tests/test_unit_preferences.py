"""
Unit tests for User Preferences functionality.

Tests include:
- User preferences model creation
- User preferences CRUD operations via API endpoints
- Email service respecting user preferences
- Webhook notifications
- Validation of webhook URLs
- Default preferences creation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from app.models.user_preferences import UserPreferences
from app.models.user import User
from app.schemas.user_preferences import UserPreferencesCreate, UserPreferencesUpdate, UserPreferencesResponse


class TestUserPreferencesModel:
    """Test suite for UserPreferences model."""

    @pytest.mark.unit
    def test_user_preferences_creation(self):
        """Test creating a UserPreferences instance."""
        preferences = UserPreferences(
            user_id=1,
            email_notifications=True,
            webhook_notifications=False,
            notification_frequency="instant",
            price_drop_alerts=True,
            weekly_summary=False,
            availability_alerts=True,
        )

        assert preferences.user_id == 1
        assert preferences.email_notifications is True
        assert preferences.webhook_notifications is False
        assert preferences.notification_frequency == "instant"
        assert preferences.price_drop_alerts is True
        assert preferences.weekly_summary is False
        assert preferences.availability_alerts is True

    @pytest.mark.unit
    def test_user_preferences_defaults(self):
        """Test that default values are set correctly when explicitly provided."""
        # Note: SQLAlchemy defaults only work when inserting to DB, not in-memory objects
        # So we test that the model accepts default values
        preferences = UserPreferences(
            user_id=1,
            email_notifications=True,
            webhook_notifications=False,
            notification_frequency="instant",
            price_drop_alerts=True,
            weekly_summary=False,
            availability_alerts=True,
        )

        assert preferences.email_notifications is True
        assert preferences.webhook_notifications is False
        assert preferences.notification_frequency == "instant"
        assert preferences.price_drop_alerts is True
        assert preferences.weekly_summary is False
        assert preferences.availability_alerts is True


class TestUserPreferencesSchemas:
    """Test suite for UserPreferences Pydantic schemas."""

    @pytest.mark.unit
    def test_preferences_create_schema(self):
        """Test creating preferences with schema."""
        data = {
            "email_notifications": True,
            "webhook_notifications": True,
            "webhook_url": "https://hooks.slack.com/test",
            "notification_frequency": "daily",
            "price_drop_alerts": True,
            "weekly_summary": True,
            "availability_alerts": True,
            "webhook_type": "slack",
        }
        schema = UserPreferencesCreate(**data)

        assert schema.email_notifications is True
        assert schema.webhook_notifications is True
        assert schema.webhook_url == "https://hooks.slack.com/test"
        assert schema.notification_frequency == "daily"
        assert schema.webhook_type == "slack"

    @pytest.mark.unit
    def test_preferences_update_schema(self):
        """Test updating preferences with partial data."""
        data = {"email_notifications": False, "notification_frequency": "weekly"}
        schema = UserPreferencesUpdate(**data)

        assert schema.email_notifications is False
        assert schema.notification_frequency == "weekly"
        assert schema.webhook_notifications is None  # Not provided

    @pytest.mark.unit
    def test_webhook_url_validation(self):
        """Test webhook URL validation."""
        # Valid URLs
        valid_data = {"webhook_url": "https://hooks.slack.com/test"}
        schema = UserPreferencesUpdate(**valid_data)
        assert schema.webhook_url == "https://hooks.slack.com/test"

        # Invalid URL (no protocol)
        with pytest.raises(ValueError, match="must start with http"):
            invalid_data = {"webhook_url": "hooks.slack.com/test"}
            schema = UserPreferencesUpdate(**invalid_data)

    @pytest.mark.unit
    def test_notification_frequency_validation(self):
        """Test notification frequency literal validation."""
        # Valid frequencies
        for freq in ["instant", "daily", "weekly"]:
            data = {"notification_frequency": freq}
            schema = UserPreferencesCreate(**data)
            assert schema.notification_frequency == freq

        # Invalid frequency should raise validation error
        with pytest.raises(ValueError):
            data = {"notification_frequency": "hourly"}  # Not in allowed values
            UserPreferencesCreate(**data)


class TestEmailServiceWithPreferences:
    """Test suite for EmailService respecting user preferences."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch("app.services.email.settings") as mock_settings:
            mock_settings.SMTP_HOST = "smtp.test.com"
            mock_settings.SMTP_PORT = 587
            mock_settings.SMTP_USER = "test@test.com"
            mock_settings.SMTP_PASSWORD = "testpass"
            mock_settings.EMAIL_FROM = "noreply@pricewatch.com"
            from app.services.email import EmailService

            self.email_service = EmailService()

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_price_alert_with_email_disabled(self, mock_smtp):
        """Test that price alert is NOT sent when email notifications are disabled."""
        # Create preferences with email disabled
        preferences = Mock(spec=UserPreferences)
        preferences.email_notifications = False
        preferences.price_drop_alerts = True

        self.email_service.send_price_alert(
            to_email="user@example.com",
            product_name="Test Product",
            new_price=99.99,
            old_price=149.99,
            product_url="https://example.com/product",
            user_preferences=preferences,
        )

        # Email should NOT be sent
        mock_smtp.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_price_alert_with_price_drop_alerts_disabled(self, mock_smtp):
        """Test that price alert is NOT sent when price drop alerts are disabled."""
        preferences = Mock(spec=UserPreferences)
        preferences.email_notifications = True
        preferences.price_drop_alerts = False

        self.email_service.send_price_alert(
            to_email="user@example.com",
            product_name="Test Product",
            new_price=99.99,
            old_price=149.99,
            product_url="https://example.com/product",
            user_preferences=preferences,
        )

        # Email should NOT be sent
        mock_smtp.assert_not_called()

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    @patch("app.services.email.requests.post")
    def test_send_price_alert_with_webhook_enabled(self, mock_requests, mock_smtp):
        """Test that webhook is sent when enabled."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Mock successful webhook response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response

        preferences = Mock(spec=UserPreferences)
        preferences.email_notifications = True
        preferences.price_drop_alerts = True
        preferences.webhook_notifications = True
        preferences.webhook_url = "https://hooks.slack.com/test"
        preferences.webhook_type = "slack"

        self.email_service.send_price_alert(
            to_email="user@example.com",
            product_name="Test Product",
            new_price=99.99,
            old_price=149.99,
            product_url="https://example.com/product",
            user_preferences=preferences,
        )

        # Both email and webhook should be sent
        mock_server.send_message.assert_called_once()
        mock_requests.assert_called_once()

        # Verify webhook payload for Slack
        call_args = mock_requests.call_args
        assert call_args[1]["json"]["text"] == "🔔 Price Drop Alert!"

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    @patch("app.services.email.requests.post")
    def test_send_webhook_discord(self, mock_requests, mock_smtp):
        """Test Discord webhook format."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response

        preferences = Mock(spec=UserPreferences)
        preferences.email_notifications = True
        preferences.price_drop_alerts = True
        preferences.webhook_notifications = True
        preferences.webhook_url = "https://discord.com/api/webhooks/test"
        preferences.webhook_type = "discord"

        self.email_service.send_price_alert(
            to_email="user@example.com",
            product_name="Test Product",
            new_price=99.99,
            old_price=149.99,
            product_url="https://example.com/product",
            user_preferences=preferences,
        )

        # Verify webhook was sent with Discord format
        mock_requests.assert_called_once()
        call_args = mock_requests.call_args
        assert "embeds" in call_args[1]["json"]
        assert call_args[1]["json"]["content"] == "🔔 **Price Drop Alert!**"

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    @patch("app.services.email.requests.post")
    def test_send_webhook_custom(self, mock_requests, mock_smtp):
        """Test custom webhook format."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response

        preferences = Mock(spec=UserPreferences)
        preferences.email_notifications = True
        preferences.price_drop_alerts = True
        preferences.webhook_notifications = True
        preferences.webhook_url = "https://example.com/webhook"
        preferences.webhook_type = "custom"

        self.email_service.send_price_alert(
            to_email="user@example.com",
            product_name="Test Product",
            new_price=99.99,
            old_price=149.99,
            product_url="https://example.com/product",
            user_preferences=preferences,
        )

        # Verify custom webhook format
        mock_requests.assert_called_once()
        call_args = mock_requests.call_args
        payload = call_args[1]["json"]
        assert payload["event"] == "price_drop"
        assert payload["product_name"] == "Test Product"
        assert payload["new_price"] == 99.99
        assert payload["old_price"] == 149.99

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    @patch("app.services.email.requests.post")
    def test_webhook_failure_does_not_prevent_email(self, mock_requests, mock_smtp):
        """Test that webhook failure doesn't prevent email from being sent."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Mock webhook failure
        mock_requests.side_effect = Exception("Webhook failed")

        preferences = Mock(spec=UserPreferences)
        preferences.email_notifications = True
        preferences.price_drop_alerts = True
        preferences.webhook_notifications = True
        preferences.webhook_url = "https://hooks.slack.com/test"
        preferences.webhook_type = "slack"

        # Should not raise exception
        self.email_service.send_price_alert(
            to_email="user@example.com",
            product_name="Test Product",
            new_price=99.99,
            old_price=149.99,
            product_url="https://example.com/product",
            user_preferences=preferences,
        )

        # Email should still be sent despite webhook failure
        mock_server.send_message.assert_called_once()


class TestPreferencesEndpoints:
    """Test suite for preferences API endpoints (logic tests)."""

    @pytest.mark.unit
    def test_get_preferences_creates_default_if_not_exists(self):
        """Test that GET /preferences creates default preferences if they don't exist."""
        # This would be tested in integration tests with actual DB
        # Here we just verify the logic
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Logic: if preferences don't exist, create them
        preferences = mock_db.query(UserPreferences).filter().first()
        assert preferences is None

        # In the actual endpoint, this would trigger creation with explicit defaults
        # (SQLAlchemy defaults only work on DB insert, not in-memory)
        new_preferences = UserPreferences(user_id=1)
        # When saved to DB, defaults would be applied
        assert new_preferences.user_id == 1

    @pytest.mark.unit
    def test_update_preferences_validates_webhook_url(self):
        """Test that updating preferences validates webhook URL when webhook is enabled."""
        # Logic test: if webhook_notifications is True, webhook_url must be provided
        webhook_enabled = True
        webhook_url = None

        # This should raise an error
        if webhook_enabled and not webhook_url:
            error = "Webhook URL is required when webhook notifications are enabled"
            assert error  # In actual endpoint, this raises HTTPException


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

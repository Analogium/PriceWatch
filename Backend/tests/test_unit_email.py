"""
Unit tests for the EmailService.

Tests include:
- Price alert email generation
- Email verification email generation
- Password reset email generation
- Email sending functionality
- Error handling
- SMTP connection handling
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.email import EmailService, email_service


class TestEmailService:
    """Test suite for EmailService class."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch("app.services.email.settings") as mock_settings:
            mock_settings.SMTP_HOST = "smtp.test.com"
            mock_settings.SMTP_PORT = 587
            mock_settings.SMTP_USER = "test@test.com"
            mock_settings.SMTP_PASSWORD = "testpass"
            mock_settings.EMAIL_FROM = "noreply@pricewatch.com"
            self.email_service = EmailService()

    @pytest.mark.unit
    @pytest.mark.email
    def test_email_service_initialization(self):
        """Test that email service initializes with correct config."""
        assert self.email_service is not None
        assert self.email_service.smtp_host == "smtp.test.com"
        assert self.email_service.smtp_port == 587
        assert self.email_service.smtp_user == "test@test.com"
        assert self.email_service.from_email == "noreply@pricewatch.com"

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_price_alert_success(self, mock_smtp):
        """Test successful price alert email sending."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        self.email_service.send_price_alert(
            to_email="user@example.com",
            product_name="Test Product",
            new_price=99.99,
            old_price=149.99,
            product_url="https://example.com/product",
        )

        # Verify SMTP methods were called
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@test.com", "testpass")
        mock_server.send_message.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_price_alert_content(self, mock_smtp):
        """Test price alert email content generation."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        self.email_service.send_price_alert(
            to_email="user@example.com",
            product_name="Amazing Laptop",
            new_price=799.99,
            old_price=999.99,
            product_url="https://example.com/laptop",
        )

        # Get the message that was sent
        call_args = mock_server.send_message.call_args
        message = call_args[0][0]

        # Verify email headers
        assert message["Subject"] == "🔔 Baisse de prix détectée sur Amazing Laptop"
        assert message["From"] == "noreply@pricewatch.com"
        assert message["To"] == "user@example.com"

        # Verify content contains key information
        # Get payload and decode if needed
        payload = message.get_payload()
        if isinstance(payload, list):
            # Get the HTML part and decode it
            html_part = payload[0]
            html_content = html_part.get_payload(decode=True).decode("utf-8")
        else:
            html_content = str(payload)

        assert "Amazing Laptop" in html_content
        assert "799.99" in html_content
        assert "999.99" in html_content
        assert "example.com/laptop" in html_content

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_price_alert_calculates_savings(self, mock_smtp):
        """Test that price alert includes savings calculation."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        self.email_service.send_price_alert(
            to_email="user@example.com",
            product_name="Product",
            new_price=80.00,
            old_price=100.00,
            product_url="https://example.com/product",
        )

        call_args = mock_server.send_message.call_args
        message = call_args[0][0]

        # Get payload and decode if needed
        payload = message.get_payload()
        if isinstance(payload, list):
            html_part = payload[0]
            html_content = html_part.get_payload(decode=True).decode("utf-8")
        else:
            html_content = str(payload)

        # Should show 20 euros savings (20%)
        assert "20.00" in html_content

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_verification_email_success(self, mock_smtp):
        """Test successful verification email sending."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        self.email_service.send_verification_email(to_email="newuser@example.com", token="test-verification-token-123")

        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_verification_email_content(self, mock_smtp):
        """Test verification email content."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        token = "verification-token-xyz"
        self.email_service.send_verification_email(to_email="newuser@example.com", token=token)

        call_args = mock_server.send_message.call_args
        message = call_args[0][0]

        assert message["Subject"] == "Vérifiez votre email - PriceWatch"
        assert message["To"] == "newuser@example.com"

        # Get payload and decode if needed
        payload = message.get_payload()
        if isinstance(payload, list):
            html_part = payload[0]
            html_content = html_part.get_payload(decode=True).decode("utf-8")
        else:
            html_content = str(payload)

        assert f"verify-email?token={token}" in html_content

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_password_reset_email_success(self, mock_smtp):
        """Test successful password reset email sending."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        self.email_service.send_password_reset_email(to_email="user@example.com", token="reset-token-abc")

        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_password_reset_email_content(self, mock_smtp):
        """Test password reset email content."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        token = "reset-token-123"
        self.email_service.send_password_reset_email(to_email="user@example.com", token=token)

        call_args = mock_server.send_message.call_args
        message = call_args[0][0]

        assert message["Subject"] == "Réinitialisation de mot de passe - PriceWatch"
        assert message["To"] == "user@example.com"

        # Get payload and decode if needed
        payload = message.get_payload()
        if isinstance(payload, list):
            html_part = payload[0]
            html_content = html_part.get_payload(decode=True).decode("utf-8")
        else:
            html_content = str(payload)

        assert f"reset-password?token={token}" in html_content
        assert "expire" in html_content.lower()

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_email_smtp_error(self, mock_smtp):
        """Test email sending with SMTP error."""
        mock_smtp.return_value.__enter__.side_effect = Exception("SMTP connection failed")

        with pytest.raises(Exception) as exc_info:
            self.email_service.send_price_alert(
                to_email="user@example.com",
                product_name="Product",
                new_price=99.99,
                old_price=149.99,
                product_url="https://example.com/product",
            )

        assert "SMTP connection failed" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_email_authentication_error(self, mock_smtp):
        """Test email sending with authentication error."""
        mock_server = MagicMock()
        mock_server.login.side_effect = Exception("Authentication failed")
        mock_smtp.return_value.__enter__.return_value = mock_server

        with pytest.raises(Exception):
            self.email_service.send_price_alert(
                to_email="user@example.com",
                product_name="Product",
                new_price=99.99,
                old_price=149.99,
                product_url="https://example.com/product",
            )

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_email_starttls_called(self, mock_smtp):
        """Test that STARTTLS is called for secure connection."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        self.email_service.send_price_alert(
            to_email="user@example.com",
            product_name="Product",
            new_price=99.99,
            old_price=149.99,
            product_url="https://example.com/product",
        )

        # Verify STARTTLS is called before login
        mock_server.starttls.assert_called_once()
        assert mock_server.starttls.call_count == 1

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_multiple_emails_sent(self, mock_smtp):
        """Test sending multiple emails in sequence."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Send price alert
        self.email_service.send_price_alert(
            to_email="user1@example.com",
            product_name="Product 1",
            new_price=50.00,
            old_price=60.00,
            product_url="https://example.com/product1",
        )

        # Send verification email
        self.email_service.send_verification_email(to_email="user2@example.com", token="token123")

        # Send password reset
        self.email_service.send_password_reset_email(to_email="user3@example.com", token="reset123")

        # All three should have been sent
        assert mock_server.send_message.call_count == 3

    @pytest.mark.unit
    def test_singleton_email_service_instance(self):
        """Test that email_service singleton is correctly instantiated."""
        assert email_service is not None
        assert isinstance(email_service, EmailService)

    @pytest.mark.unit
    @pytest.mark.email
    @patch("app.services.email.smtplib.SMTP")
    def test_send_email_generic_exception(self, mock_smtp):
        """Test handling of generic exceptions during email send."""
        mock_smtp.side_effect = Exception("Unexpected error")

        with pytest.raises(Exception):
            self.email_service.send_price_alert(
                to_email="user@example.com",
                product_name="Test Product",
                current_price=99.99,
                target_price=89.99,
                product_url="https://example.com/product",
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

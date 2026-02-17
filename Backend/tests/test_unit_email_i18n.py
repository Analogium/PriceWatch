"""
Unit tests for bilingual email templates.

Tests include:
- Price alert templates in FR and EN
- Verification email templates in FR and EN
- Password reset templates in FR and EN
- Weekly summary templates in FR and EN
- Subject lines are correctly translated
- Template content uses correct language
"""

import pytest

from app.services.email_templates import (
    password_reset_template,
    price_alert_template,
    verification_email_template,
    weekly_summary_template,
)


class TestPriceAlertTemplate:
    """Test price alert email template in both languages."""

    PARAMS = {
        "product_name": "MacBook Pro",
        "new_price": 1299.99,
        "old_price": 1499.99,
        "product_url": "https://amazon.fr/macbook",
        "preferences_url": "https://pricewatch.com/settings",
    }

    @pytest.mark.unit
    @pytest.mark.email
    def test_french_subject(self):
        subject, _ = price_alert_template(lang="fr", **self.PARAMS)
        assert "Baisse de prix" in subject
        assert "MacBook Pro" in subject

    @pytest.mark.unit
    @pytest.mark.email
    def test_english_subject(self):
        subject, _ = price_alert_template(lang="en", **self.PARAMS)
        assert "Price drop" in subject
        assert "MacBook Pro" in subject

    @pytest.mark.unit
    @pytest.mark.email
    def test_french_body_content(self):
        _, body = price_alert_template(lang="fr", **self.PARAMS)
        assert "Bonne nouvelle" in body
        assert "Bonjour" in body
        assert "Nouveau prix" in body
        assert "Ancien prix" in body
        assert "1299.99" in body
        assert "1499.99" in body

    @pytest.mark.unit
    @pytest.mark.email
    def test_english_body_content(self):
        _, body = price_alert_template(lang="en", **self.PARAMS)
        assert "Great news" in body
        assert "Hello" in body
        assert "New price" in body
        assert "Old price" in body
        assert "1299.99" in body
        assert "1499.99" in body

    @pytest.mark.unit
    @pytest.mark.email
    def test_savings_calculation(self):
        _, body = price_alert_template(lang="en", **self.PARAMS)
        assert "200.00" in body  # savings = 1499.99 - 1299.99

    @pytest.mark.unit
    @pytest.mark.email
    def test_defaults_to_french(self):
        subject, body = price_alert_template(lang="de", **self.PARAMS)
        assert "Baisse de prix" in subject
        assert "Bonjour" in body


class TestVerificationEmailTemplate:
    """Test verification email template in both languages."""

    URL = "https://pricewatch.com/verify?token=abc123"

    @pytest.mark.unit
    @pytest.mark.email
    def test_french_subject(self):
        subject, _ = verification_email_template(lang="fr", verification_url=self.URL)
        assert "Vérifiez votre email" in subject

    @pytest.mark.unit
    @pytest.mark.email
    def test_english_subject(self):
        subject, _ = verification_email_template(lang="en", verification_url=self.URL)
        assert "Verify your email" in subject

    @pytest.mark.unit
    @pytest.mark.email
    def test_french_body(self):
        _, body = verification_email_template(lang="fr", verification_url=self.URL)
        assert "Bienvenue sur PriceWatch" in body
        assert "Vérifier mon email" in body
        assert self.URL in body

    @pytest.mark.unit
    @pytest.mark.email
    def test_english_body(self):
        _, body = verification_email_template(lang="en", verification_url=self.URL)
        assert "Welcome to PriceWatch" in body
        assert "Verify my email" in body
        assert self.URL in body


class TestPasswordResetTemplate:
    """Test password reset email template in both languages."""

    URL = "https://pricewatch.com/reset?token=xyz789"

    @pytest.mark.unit
    @pytest.mark.email
    def test_french_subject(self):
        subject, _ = password_reset_template(lang="fr", reset_url=self.URL)
        assert "Réinitialisation" in subject

    @pytest.mark.unit
    @pytest.mark.email
    def test_english_subject(self):
        subject, _ = password_reset_template(lang="en", reset_url=self.URL)
        assert "Password reset" in subject

    @pytest.mark.unit
    @pytest.mark.email
    def test_french_body(self):
        _, body = password_reset_template(lang="fr", reset_url=self.URL)
        assert "Réinitialiser mon mot de passe" in body
        assert "1 heure" in body
        assert self.URL in body

    @pytest.mark.unit
    @pytest.mark.email
    def test_english_body(self):
        _, body = password_reset_template(lang="en", reset_url=self.URL)
        assert "Reset my password" in body
        assert "1 hour" in body
        assert self.URL in body


class TestWeeklySummaryTemplate:
    """Test weekly summary email template in both languages."""

    PARAMS = {
        "products_html": "<tr><td>Product 1</td></tr>",
        "total_products": 5,
        "total_savings": 42.50,
        "dashboard_url": "https://pricewatch.com/dashboard",
        "preferences_url": "https://pricewatch.com/settings",
    }

    @pytest.mark.unit
    @pytest.mark.email
    def test_french_subject(self):
        subject, _ = weekly_summary_template(lang="fr", **self.PARAMS)
        assert "résumé hebdomadaire" in subject

    @pytest.mark.unit
    @pytest.mark.email
    def test_english_subject(self):
        subject, _ = weekly_summary_template(lang="en", **self.PARAMS)
        assert "weekly summary" in subject

    @pytest.mark.unit
    @pytest.mark.email
    def test_french_body(self):
        _, body = weekly_summary_template(lang="fr", **self.PARAMS)
        assert "Produits surveillés" in body
        assert "Économies potentielles" in body
        assert "42.50" in body

    @pytest.mark.unit
    @pytest.mark.email
    def test_english_body(self):
        _, body = weekly_summary_template(lang="en", **self.PARAMS)
        assert "Tracked products" in body
        assert "Potential savings" in body
        assert "42.50" in body

    @pytest.mark.unit
    @pytest.mark.email
    def test_empty_products_french(self):
        _, body = weekly_summary_template(
            lang="fr",
            products_html="",
            total_products=0,
            total_savings=0,
            dashboard_url="https://pricewatch.com/dashboard",
            preferences_url="https://pricewatch.com/settings",
        )
        assert "Aucun produit surveillé" in body

    @pytest.mark.unit
    @pytest.mark.email
    def test_empty_products_english(self):
        _, body = weekly_summary_template(
            lang="en",
            products_html="",
            total_products=0,
            total_savings=0,
            dashboard_url="https://pricewatch.com/dashboard",
            preferences_url="https://pricewatch.com/settings",
        )
        assert "No tracked products" in body


class TestTemplateReturnTypes:
    """Test that all templates return (str, str) tuples."""

    @pytest.mark.unit
    @pytest.mark.email
    def test_price_alert_returns_tuple(self):
        result = price_alert_template("fr", "Prod", 10.0, 20.0, "http://url", "http://pref")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)

    @pytest.mark.unit
    @pytest.mark.email
    def test_verification_returns_tuple(self):
        result = verification_email_template("fr", "http://verify")
        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.unit
    @pytest.mark.email
    def test_password_reset_returns_tuple(self):
        result = password_reset_template("fr", "http://reset")
        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.unit
    @pytest.mark.email
    def test_weekly_summary_returns_tuple(self):
        result = weekly_summary_template("fr", "", 0, 0.0, "http://dash", "http://pref")
        assert isinstance(result, tuple)
        assert len(result) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

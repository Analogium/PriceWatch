"""
Unit tests for the i18n module.

Tests include:
- All keys exist in both FR and EN translations
- Variable interpolation works correctly
- Fallback to French for unknown languages
- parse_accept_language header parsing
- get_language dependency logic
- Language field in UserPreferences schema
"""

import pytest

from app.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, TRANSLATIONS, t
from app.i18n.locales import en, fr


class TestTranslationKeys:
    """Ensure FR and EN have identical key sets."""

    @pytest.mark.unit
    def test_supported_languages(self):
        assert SUPPORTED_LANGUAGES == ["fr", "en"]
        assert DEFAULT_LANGUAGE == "fr"

    @pytest.mark.unit
    def test_all_fr_keys_exist_in_en(self):
        missing = set(fr.MESSAGES.keys()) - set(en.MESSAGES.keys())
        assert not missing, f"Keys in FR but missing from EN: {missing}"

    @pytest.mark.unit
    def test_all_en_keys_exist_in_fr(self):
        missing = set(en.MESSAGES.keys()) - set(fr.MESSAGES.keys())
        assert not missing, f"Keys in EN but missing from FR: {missing}"

    @pytest.mark.unit
    def test_translations_dict_has_both_languages(self):
        assert "fr" in TRANSLATIONS
        assert "en" in TRANSLATIONS


class TestTranslationFunction:
    """Test the t() translation helper."""

    @pytest.mark.unit
    def test_returns_french_by_default(self):
        result = t("invalid_credentials")
        assert result == "Identifiants invalides"

    @pytest.mark.unit
    def test_returns_english_when_requested(self):
        result = t("invalid_credentials", "en")
        assert result == "Invalid credentials"

    @pytest.mark.unit
    def test_falls_back_to_french_for_unknown_language(self):
        result = t("invalid_credentials", "de")
        assert result == "Identifiants invalides"

    @pytest.mark.unit
    def test_falls_back_to_french_for_empty_language(self):
        result = t("invalid_credentials", "")
        assert result == "Identifiants invalides"

    @pytest.mark.unit
    def test_returns_key_if_missing_in_both_languages(self):
        result = t("nonexistent_key", "fr")
        assert result == "nonexistent_key"

    @pytest.mark.unit
    def test_interpolation_fr(self):
        result = t("password_min_length", "fr", length=8)
        assert "8" in result
        assert "caractères" in result

    @pytest.mark.unit
    def test_interpolation_en(self):
        result = t("password_min_length", "en", length=8)
        assert "8" in result
        assert "characters" in result

    @pytest.mark.unit
    def test_rate_limit_interpolation(self):
        result = t("rate_limit_exceeded", "en", requests=10, period=60)
        assert "10" in result
        assert "60" in result

    @pytest.mark.unit
    def test_admin_interpolation(self):
        result = t("user_promoted", "en", email="test@example.com")
        assert "test@example.com" in result

    @pytest.mark.unit
    def test_cookie_interpolation(self):
        result = t("cookies_uploaded", "fr", site="amazon")
        assert "amazon" in result


class TestParseAcceptLanguage:
    """Test Accept-Language header parsing."""

    @pytest.mark.unit
    def test_parse_simple_english(self):
        from unittest.mock import Mock

        from app.api.dependencies import parse_accept_language

        request = Mock()
        request.headers = {"Accept-Language": "en"}
        assert parse_accept_language(request) == "en"

    @pytest.mark.unit
    def test_parse_simple_french(self):
        from unittest.mock import Mock

        from app.api.dependencies import parse_accept_language

        request = Mock()
        request.headers = {"Accept-Language": "fr"}
        assert parse_accept_language(request) == "fr"

    @pytest.mark.unit
    def test_parse_with_region(self):
        from unittest.mock import Mock

        from app.api.dependencies import parse_accept_language

        request = Mock()
        request.headers = {"Accept-Language": "en-US,en;q=0.9,fr;q=0.8"}
        assert parse_accept_language(request) == "en"

    @pytest.mark.unit
    def test_parse_fr_region(self):
        from unittest.mock import Mock

        from app.api.dependencies import parse_accept_language

        request = Mock()
        request.headers = {"Accept-Language": "fr-FR,fr;q=0.9"}
        assert parse_accept_language(request) == "fr"

    @pytest.mark.unit
    def test_parse_unsupported_falls_back_to_fr(self):
        from unittest.mock import Mock

        from app.api.dependencies import parse_accept_language

        request = Mock()
        request.headers = {"Accept-Language": "de-DE,de;q=0.9"}
        assert parse_accept_language(request) == "fr"

    @pytest.mark.unit
    def test_parse_empty_header(self):
        from unittest.mock import Mock

        from app.api.dependencies import parse_accept_language

        request = Mock()
        request.headers = {}
        assert parse_accept_language(request) == "fr"

    @pytest.mark.unit
    def test_parse_missing_header(self):
        from unittest.mock import Mock

        from app.api.dependencies import parse_accept_language

        request = Mock()
        request.headers = {"Accept-Language": ""}
        assert parse_accept_language(request) == "fr"


class TestLanguageInPreferencesSchema:
    """Test language field in UserPreferences schemas."""

    @pytest.mark.unit
    def test_create_schema_default_language(self):
        from app.schemas.user_preferences import UserPreferencesCreate

        schema = UserPreferencesCreate()
        assert schema.language == "fr"

    @pytest.mark.unit
    def test_create_schema_with_language(self):
        from app.schemas.user_preferences import UserPreferencesCreate

        schema = UserPreferencesCreate(language="en")
        assert schema.language == "en"

    @pytest.mark.unit
    def test_update_schema_with_language(self):
        from app.schemas.user_preferences import UserPreferencesUpdate

        schema = UserPreferencesUpdate(language="en")
        assert schema.language == "en"

    @pytest.mark.unit
    def test_update_schema_language_optional(self):
        from app.schemas.user_preferences import UserPreferencesUpdate

        schema = UserPreferencesUpdate()
        assert schema.language is None

    @pytest.mark.unit
    def test_language_in_model(self):
        from app.models.user_preferences import UserPreferences

        prefs = UserPreferences(user_id=1, language="en")
        assert prefs.language == "en"


class TestNoEmptyTranslations:
    """Ensure no translation value is empty or whitespace-only."""

    @pytest.mark.unit
    def test_fr_no_empty_values(self):
        for key, value in fr.MESSAGES.items():
            assert value and value.strip(), f"FR key '{key}' has empty value"

    @pytest.mark.unit
    def test_en_no_empty_values(self):
        for key, value in en.MESSAGES.items():
            assert value and value.strip(), f"EN key '{key}' has empty value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

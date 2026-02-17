from app.i18n.locales import en, fr

TRANSLATIONS = {
    "fr": fr.MESSAGES,
    "en": en.MESSAGES,
}

SUPPORTED_LANGUAGES = ["fr", "en"]
DEFAULT_LANGUAGE = "fr"


def t(key: str, lang: str = "fr", **kwargs) -> str:
    """Get translated message with variable interpolation."""
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    messages = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE])
    template = messages.get(key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))
    return template.format(**kwargs) if kwargs else template

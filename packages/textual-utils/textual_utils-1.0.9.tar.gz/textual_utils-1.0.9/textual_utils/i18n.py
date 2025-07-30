"""
The i18n module provides internationalization services based on the gettext module.
"""

import gettext
from pathlib import Path

_localedir: Path

DEFAULT_LANGUAGE = "en"

_language: str = DEFAULT_LANGUAGE
_translation: gettext.GNUTranslations


def init_translation(localedir: Path) -> None:
    """
    Init translation services.
    Set locale directory.
    """
    global _localedir

    _localedir = localedir


def set_translation(language: str) -> None:
    """
    Set the current language.
    Create a Translations object based on the domain, localedir and language.
    """
    global _language
    global _translation
    global _localedir

    _language = language

    if language != DEFAULT_LANGUAGE:
        _translation = gettext.translation(
            domain="messages",
            localedir=_localedir,
            languages=[language],
        )


def _(message: str) -> str:
    """
    Return the localized translation of message based on the current language.
    """
    global _translation

    if _language == DEFAULT_LANGUAGE:
        return message
    else:
        return _translation.gettext(message)

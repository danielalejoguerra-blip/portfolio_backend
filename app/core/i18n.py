"""
Internationalization (i18n) utilities for bilingual support (ES/EN).

Spanish is the default language (source of truth in original columns).
English translations are stored in the `translations` JSONB column.
"""
from typing import Any

SUPPORTED_LANGUAGES: list[str] = ["es", "en"]
DEFAULT_LANGUAGE: str = "es"


def resolve_translation(
    fields: dict[str, Any],
    translations: dict[str, dict[str, str]],
    lang: str,
    translatable_keys: list[str],
) -> dict[str, Any]:
    """
    Merge translated values over the default (Spanish) fields.

    If lang == DEFAULT_LANGUAGE or no translation exists for the requested
    language, the original field values are returned unchanged (fallback).

    Args:
        fields: The base response dict with Spanish values.
        translations: The full translations dict, e.g. {"en": {"title": "...", ...}}.
        lang: The requested language code.
        translatable_keys: Which keys are eligible for translation.

    Returns:
        The fields dict with translated values applied where available.
    """
    if lang == DEFAULT_LANGUAGE or lang not in SUPPORTED_LANGUAGES:
        return fields

    lang_data = translations.get(lang, {})
    if not lang_data:
        return fields

    for key in translatable_keys:
        if key in lang_data and lang_data[key]:
            fields[key] = lang_data[key]

    return fields

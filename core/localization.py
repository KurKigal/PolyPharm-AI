from __future__ import annotations

from typing import Any, Literal

Language = Literal["en", "tr"]
DEFAULT_LANGUAGE: Language = "en"
SUPPORTED_LANGUAGES: tuple[Language, ...] = ("en", "tr")


def normalize_language(language: str | None) -> Language:
    return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def localize_value(
    value: str | dict[str, Any] | None,
    language: str,
    *,
    fallback: str = "",
) -> str:
    """Resolve a localized JSON value while remaining backward-compatible with strings."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        lang = normalize_language(language)
        candidate = value.get(lang) or value.get(DEFAULT_LANGUAGE) or value.get("tr")
        return candidate if isinstance(candidate, str) else fallback
    return fallback


RISK_LEVEL_LABELS = {
    "en": {
        "low": "Low Risk",
        "medium": "Moderate Risk",
        "high": "High Risk",
        "critical": "Critical Risk",
    },
    "tr": {
        "low": "Düşük Risk",
        "medium": "Orta Risk",
        "high": "Yüksek Risk",
        "critical": "Kritik Risk",
    },
}

GENDER_LABELS = {
    "en": {"female": "Female", "male": "Male", "other": "Other"},
    "tr": {"female": "Kadın", "male": "Erkek", "other": "Diğer"},
}


def risk_level_label(level: str, language: str) -> str:
    lang = normalize_language(language)
    return RISK_LEVEL_LABELS[lang].get(level, level)


def gender_label(gender: str, language: str) -> str:
    lang = normalize_language(language)
    return GENDER_LABELS[lang].get(gender, gender)

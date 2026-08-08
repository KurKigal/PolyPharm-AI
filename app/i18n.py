from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

LOCALES_DIR = Path(__file__).resolve().parent / "locales"
SUPPORTED_LANGUAGES = ("en", "tr")
DEFAULT_LANGUAGE = "en"


@lru_cache(maxsize=len(SUPPORTED_LANGUAGES))
def _load_messages(language: str) -> dict[str, Any]:
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE

    path = LOCALES_DIR / f"{language}.json"
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError(f"Locale root must be an object: {path}")

    return payload


class Translator:
    """Small JSON-backed translator for the Streamlit presentation layer."""

    def __init__(self, language: str = DEFAULT_LANGUAGE):
        self.language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        self._messages = _load_messages(self.language)
        self._fallback = _load_messages(DEFAULT_LANGUAGE)

    def __call__(self, key: str, **params: Any) -> str:
        value = self._resolve(self._messages, key)
        if value is None:
            value = self._resolve(self._fallback, key)
        if value is None:
            value = key
        if not isinstance(value, str):
            raise TypeError(f"Translation key must resolve to a string: {key}")
        return value.format(**params) if params else value

    @staticmethod
    def _resolve(messages: dict[str, Any], key: str) -> Any | None:
        current: Any = messages
        for part in key.split("."):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current


RISK_LEVEL_KEYS = {
    "Düşük Risk": "low",
    "Orta Risk": "medium",
    "Yüksek Risk": "high",
    "Kritik Risk": "critical",
    "low": "low",
    "medium": "medium",
    "high": "high",
    "critical": "critical",
}

GENDER_KEYS = {
    "Kadın": "female",
    "Erkek": "male",
    "Diğer": "other",
    "Female": "female",
    "Male": "male",
    "Other": "other",
    "female": "female",
    "male": "male",
    "other": "other",
}


def risk_level_key(value: str) -> str:
    return RISK_LEVEL_KEYS.get(value, "medium")


def risk_level_label(value: str, t: Translator) -> str:
    return t(f"risk.level.{risk_level_key(value)}")


def gender_label(value: str, t: Translator) -> str:
    key = GENDER_KEYS.get(value)
    return t(f"gender.{key}") if key else value

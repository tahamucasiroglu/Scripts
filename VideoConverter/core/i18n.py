"""JSON based localization helpers."""
import json
import os
import sys
from typing import Dict


def _resource_dir() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class I18N:
    def __init__(self, locale_dir: str = None, default_language: str = "tr"):
        app_dir = _resource_dir()
        self.locale_dir = locale_dir or os.path.join(app_dir, "locales")
        self.default_language = default_language
        self.language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_languages()

    def load_languages(self):
        if not os.path.isdir(self.locale_dir):
            return

        for name in os.listdir(self.locale_dir):
            if not name.lower().endswith(".json"):
                continue

            lang = os.path.splitext(name)[0]
            path = os.path.join(self.locale_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    self.translations[lang] = json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue

    def available_languages(self):
        return sorted(self.translations.keys()) or [self.default_language]

    def set_language(self, language: str):
        if language in self.translations:
            self.language = language

    def t(self, key: str, **kwargs) -> str:
        value = (
            self.translations.get(self.language, {}).get(key)
            or self.translations.get(self.default_language, {}).get(key)
            or key
        )
        return value.format(**kwargs) if kwargs else value

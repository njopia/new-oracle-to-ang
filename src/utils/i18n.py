#!/usr/bin/env python3
"""
Sistema de internacionalización (i18n)
Soporta cambio de idioma en runtime
"""

import json
from pathlib import Path
from typing import Any, Dict, Callable, List


class I18n:
    """Gestor de internacionalización"""

    _instance = None
    _translations: Dict[str, Dict] = {}
    _current_language: str = "es"
    _listeners: List[Callable] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18n, cls).__new__(cls)
            cls._instance._load_translations()
        return cls._instance

    def _load_translations(self):
        """Carga todas las traducciones disponibles"""
        locales_dir = Path(__file__).parent.parent / "locales"

        if not locales_dir.exists():
            print(f"Warning: Locales directory not found: {locales_dir}")
            return

        # Cargar todos los archivos de idioma
        for locale_file in locales_dir.glob("*.json"):
            lang_code = locale_file.stem
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self._translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Error loading translation {lang_code}: {e}")

    def get_available_languages(self) -> List[str]:
        """Retorna lista de idiomas disponibles"""
        return list(self._translations.keys())

    def get_current_language(self) -> str:
        """Retorna el idioma actual"""
        return self._current_language

    def set_language(self, lang_code: str):
        """
        Cambia el idioma actual

        Args:
            lang_code: Código de idioma (es, en, etc.)
        """
        if lang_code not in self._translations:
            print(f"Warning: Language {lang_code} not found, using {self._current_language}")
            return

        self._current_language = lang_code

        # Notificar a los listeners del cambio
        self._notify_listeners()

    def t(self, key: str, default: str = None) -> str:
        """
        Traduce una clave usando notación de punto

        Args:
            key: Clave en formato "section.subsection.key"
            default: Valor por defecto si no existe la traducción

        Returns:
            Texto traducido o default o la clave misma
        """
        if self._current_language not in self._translations:
            return default or key

        keys = key.split('.')
        value = self._translations[self._current_language]

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default or key

    def add_listener(self, callback: Callable):
        """
        Añade un listener que será notificado cuando cambie el idioma

        Args:
            callback: Función a llamar cuando cambie el idioma
        """
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable):
        """
        Elimina un listener

        Args:
            callback: Función a eliminar
        """
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self):
        """Notifica a todos los listeners del cambio de idioma"""
        for listener in self._listeners:
            try:
                listener(self._current_language)
            except Exception as e:
                print(f"Error notifying listener: {e}")

    def get_language_name(self, lang_code: str) -> str:
        """
        Retorna el nombre del idioma en su idioma nativo

        Args:
            lang_code: Código de idioma

        Returns:
            Nombre del idioma
        """
        language_names = {
            "es": "Español",
            "en": "English"
        }
        return language_names.get(lang_code, lang_code.upper())


# Instancia global
i18n = I18n()


# Función de atajo para traducción
def t(key: str, default: str = None) -> str:
    """
    Función de atajo para traducción

    Args:
        key: Clave de traducción
        default: Valor por defecto

    Returns:
        Texto traducido
    """
    return i18n.t(key, default)

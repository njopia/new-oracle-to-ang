#!/usr/bin/env python3
"""
Gestión de configuración de la aplicación
"""

import json
import os
from pathlib import Path
from typing import Any, Dict


class Config:
    """Gestor de configuración de la aplicación"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Carga la configuración desde el archivo"""
        self.config_path = Path("config.json")
        self.default_config_path = Path("config.default.json")

        # Si no existe config.json, crear desde default
        if not self.config_path.exists():
            if self.default_config_path.exists():
                with open(self.default_config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                self.save()
            else:
                self._config = self._get_default_config()
                self.save()
        else:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)

    def _get_default_config(self) -> Dict:
        """Retorna la configuración por defecto"""
        return {
            "app": {
                "name": "Oracle Forms to Angular Migrator",
                "version": "3.0.0",
                "language": "es"
            },
            "paths": {
                "oracle_home": "",
                "frmf2xml_path": "",
                "output_directory": "./output",
                "temp_directory": "./temp",
                "log_directory": "./logs"
            },
            "ui": {
                "theme": "blue",
                "appearance_mode": "light"
            },
            "conversion": {
                "timeout_seconds": 300,
                "batch_size": 10
            },
            "report": {
                "include_charts": True,
                "detailed_analysis": True
            },
            "recent_files": []
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración usando notación de punto

        Args:
            key: Clave en formato "section.subsection.key"
            default: Valor por defecto si no existe

        Returns:
            Valor de configuración o default
        """
        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        """
        Establece un valor de configuración usando notación de punto

        Args:
            key: Clave en formato "section.subsection.key"
            value: Valor a establecer
        """
        keys = key.split('.')
        config = self._config

        # Navegar hasta el penúltimo nivel
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Establecer el valor
        config[keys[-1]] = value

    def save(self):
        """Guarda la configuración en el archivo"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get_all(self) -> Dict:
        """Retorna toda la configuración"""
        return self._config.copy()

    def reload(self):
        """Recarga la configuración desde el archivo"""
        self._load_config()


# Instancia global
config = Config()

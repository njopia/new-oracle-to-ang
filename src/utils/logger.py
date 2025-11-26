#!/usr/bin/env python3
"""
Sistema de logging para la aplicación
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class Logger:
    """Gestor de logging de la aplicación"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        """Configura el logger"""
        # Crear directorio de logs si no existe
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Nombre del archivo de log con fecha
        log_file = log_dir / f"migrator_{datetime.now().strftime('%Y%m%d')}.log"

        # Configurar logger
        self._logger = logging.getLogger('OracleFormsToAngular')
        self._logger.setLevel(logging.DEBUG)

        # Evitar duplicar handlers
        if self._logger.handlers:
            return

        # Formato de log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para archivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

    def debug(self, message: str, *args, **kwargs):
        """Log nivel DEBUG"""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log nivel INFO"""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log nivel WARNING"""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log nivel ERROR"""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log nivel CRITICAL"""
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """Log de excepción con traceback"""
        self._logger.exception(message, *args, **kwargs)


# Instancia global
logger = Logger()

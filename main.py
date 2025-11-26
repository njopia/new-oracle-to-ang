#!/usr/bin/env python3
"""
Oracle Forms to Angular Migrator v3.0
Entry point de la aplicación

Autor: njopia
Fecha: 2024
"""

import sys
import os

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MainWindow
from src.utils.logger import logger


def main():
    """Función principal"""
    try:
        logger.info("="*60)
        logger.info("Oracle Forms to Angular Migrator v3.0 - Starting")
        logger.info("="*60)

        # Crear y ejecutar aplicación
        app = MainWindow()
        app.run()

        logger.info("Application closed")

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

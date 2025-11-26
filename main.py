#!/usr/bin/env python3
"""
Oracle Forms to Angular Migrator v3.0
Entry point de la aplicación

Autor: njopia
Fecha: 2024
"""

import sys
import os
import subprocess


def check_and_install_dependencies():
    """
    Verifica e instala automáticamente las dependencias necesarias

    Returns:
        bool: True si todas las dependencias están disponibles
    """
    print("=" * 60)
    print("Oracle Forms to Angular Migrator v3.0")
    print("=" * 60)
    print()

    required_packages = {
        'customtkinter': 'customtkinter>=5.2.0',
        'PIL': 'Pillow>=10.0.0',
        'lxml': 'lxml>=4.9.0',
        'jinja2': 'Jinja2>=3.1.2',
        'dateutil': 'python-dateutil>=2.8.2'
    }

    missing_packages = []

    print("[1/2] Verificando dependencias...")
    print()

    # Verificar cada paquete
    for package_name, package_spec in required_packages.items():
        try:
            __import__(package_name)
            print(f"  ✓ {package_spec.split('>=')[0]}")
        except ImportError:
            print(f"  ✗ {package_spec.split('>=')[0]} - NO INSTALADO")
            missing_packages.append(package_spec)

    print()

    # Si hay paquetes faltantes, instalar
    if missing_packages:
        print(f"⚠️  Faltan {len(missing_packages)} dependencia(s)")
        print()
        print("[2/2] Instalando dependencias faltantes...")
        print()

        try:
            # Intentar instalar usando pip
            cmd = [sys.executable, '-m', 'pip', 'install'] + missing_packages

            print(f"Ejecutando: pip install {' '.join(missing_packages)}")
            print()

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )

            if result.returncode == 0:
                print("✓ Dependencias instaladas correctamente")
                print()
                return True
            else:
                print("✗ Error al instalar dependencias:")
                print(result.stderr)
                print()
                print("Por favor, instala manualmente con:")
                print(f"  pip install -r requirements.txt")
                return False

        except subprocess.TimeoutExpired:
            print("✗ Timeout al instalar dependencias")
            print("Por favor, instala manualmente con:")
            print(f"  pip install -r requirements.txt")
            return False
        except Exception as e:
            print(f"✗ Error inesperado: {e}")
            print("Por favor, instala manualmente con:")
            print(f"  pip install -r requirements.txt")
            return False
    else:
        print("✓ Todas las dependencias están instaladas")
        print()
        return True


def main():
    """Función principal"""
    # Verificar e instalar dependencias
    if not check_and_install_dependencies():
        print()
        print("=" * 60)
        print("No se pudo iniciar la aplicación debido a dependencias faltantes")
        print("=" * 60)
        input("\nPresiona Enter para salir...")
        sys.exit(1)

    # Añadir el directorio src al path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    try:
        # Importar después de verificar dependencias
        from src.gui.main_window import MainWindow
        from src.utils.logger import logger

        logger.info("=" * 60)
        logger.info("Oracle Forms to Angular Migrator v3.0 - Starting")
        logger.info("=" * 60)

        print("=" * 60)
        print("Iniciando aplicación...")
        print("=" * 60)
        print()

        # Crear y ejecutar aplicación
        app = MainWindow()
        app.run()

        logger.info("Application closed")

    except KeyboardInterrupt:
        print("\n\nAplicación interrumpida por el usuario")
        sys.exit(0)
    except ImportError as e:
        print(f"\n✗ Error al importar módulos: {e}")
        print("Por favor, verifica que todas las dependencias estén instaladas:")
        print("  pip install -r requirements.txt")
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)


if __name__ == "__main__":
    main()

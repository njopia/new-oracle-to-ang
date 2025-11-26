#!/usr/bin/env python3
"""
Script para configurar variables de entorno de Oracle Forms
Ayuda a identificar las rutas correctas y genera comandos de exportación
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List


class Colors:
    """Colores ANSI para terminal"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_header(text: str) -> None:
    """Imprime encabezado"""
    print(f"\n{Colors.BLUE}=== {text} ==={Colors.NC}")


def print_success(text: str) -> None:
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")


def print_error(text: str) -> None:
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")


def print_warning(text: str) -> None:
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠  {text}{Colors.NC}")


def print_info(text: str) -> None:
    """Imprime mensaje informativo"""
    print(text)


def find_oracle_homes() -> List[Path]:
    """
    Busca posibles instalaciones de Oracle Forms en ubicaciones comunes

    Returns:
        List[Path]: Lista de rutas que podrían ser ORACLE_HOME
    """
    common_paths = [
        "/opt/oracle/middleware/forms",
        "/opt/oracle/middleware/Oracle_FRHome1",
        "/u01/app/oracle/product/12.2.1/forms",
        "/u01/app/oracle/product/11.2.0/forms",
        Path.home() / "oracle" / "middleware" / "forms",
    ]

    found = []
    for path in common_paths:
        path = Path(path)
        if path.exists() and (path / "bin" / "frmf2xml").exists():
            found.append(path)

    return found


def find_java_homes() -> List[Path]:
    """
    Busca posibles instalaciones de Java

    Returns:
        List[Path]: Lista de rutas que podrían ser JAVA_HOME
    """
    common_paths = [
        "/usr/lib/jvm/java-8-openjdk-amd64",
        "/usr/lib/jvm/java-11-openjdk-amd64",
        "/usr/lib/jvm/default-java",
        "/usr/java/latest",
    ]

    found = []
    for path in common_paths:
        path = Path(path)
        if path.exists() and (path / "bin" / "java").exists():
            found.append(path)

    # También intentar encontrar desde el comando java
    java_path = shutil.which('java')
    if java_path:
        try:
            # Resolver symlinks y obtener directorio padre
            java_real = Path(java_path).resolve()
            java_home = java_real.parent.parent
            if java_home not in found and (java_home / "bin" / "java").exists():
                found.append(java_home)
        except Exception:
            pass

    return found


def prompt_for_path(variable_name: str, current_value: Optional[str],
                   suggestions: List[Path]) -> str:
    """
    Solicita al usuario una ruta, mostrando sugerencias

    Args:
        variable_name: Nombre de la variable (ORACLE_HOME, JAVA_HOME, etc.)
        current_value: Valor actual de la variable (puede ser None)
        suggestions: Lista de sugerencias de rutas

    Returns:
        str: Ruta seleccionada por el usuario
    """
    print(f"\n{Colors.YELLOW}Configurando {variable_name}:{Colors.NC}")

    if current_value:
        print(f"Valor actual: {current_value}")

    if suggestions:
        print("\nRutas encontradas:")
        for i, path in enumerate(suggestions, 1):
            print(f"  {i}. {path}")
        print(f"  0. Ingresar ruta manualmente")

        while True:
            try:
                choice = input(f"\nSelecciona una opción [1-{len(suggestions)}, 0 para manual]: ").strip()

                if choice == "0":
                    custom_path = input(f"Ingresa la ruta completa de {variable_name}: ").strip()
                    return custom_path

                choice_num = int(choice)
                if 1 <= choice_num <= len(suggestions):
                    return str(suggestions[choice_num - 1])
                else:
                    print_error("Opción inválida")
            except ValueError:
                print_error("Por favor ingresa un número")
            except KeyboardInterrupt:
                print("\n\nCancelado por el usuario")
                sys.exit(0)
    else:
        print_warning(f"No se encontraron instalaciones automáticamente")
        custom_path = input(f"Ingresa la ruta completa de {variable_name}: ").strip()
        return custom_path


def verify_path(path: str, check_file: str) -> bool:
    """
    Verifica que una ruta existe y contiene un archivo específico

    Args:
        path: Ruta a verificar
        check_file: Archivo relativo que debe existir

    Returns:
        bool: True si la verificación es exitosa
    """
    path_obj = Path(path)

    if not path_obj.exists():
        print_error(f"La ruta no existe: {path}")
        return False

    check_path = path_obj / check_file
    if not check_path.exists():
        print_error(f"No se encuentra {check_file} en {path}")
        return False

    return True


def generate_export_commands(oracle_home: str, java_home: str) -> str:
    """
    Genera comandos de exportación para bash

    Args:
        oracle_home: Ruta de ORACLE_HOME
        java_home: Ruta de JAVA_HOME

    Returns:
        str: Comandos de exportación formateados
    """
    commands = f"""
# Oracle Forms Environment
export ORACLE_HOME="{oracle_home}"
export JAVA_HOME="{java_home}"
export FORMS_PATH="$ORACLE_HOME/forms"
export PATH="$ORACLE_HOME/bin:$JAVA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$ORACLE_HOME/lib:$LD_LIBRARY_PATH"
"""
    return commands.strip()


def main():
    """Función principal"""
    print_header("Configuración de Variables de Entorno para Oracle Forms")

    # Obtener valores actuales
    current_oracle_home = os.environ.get('ORACLE_HOME')
    current_java_home = os.environ.get('JAVA_HOME')

    # Buscar instalaciones
    print("\n🔍 Buscando instalaciones de Oracle Forms y Java...")
    oracle_suggestions = find_oracle_homes()
    java_suggestions = find_java_homes()

    # Configurar ORACLE_HOME
    oracle_home = None
    while not oracle_home:
        path = prompt_for_path('ORACLE_HOME', current_oracle_home, oracle_suggestions)
        if verify_path(path, 'bin/frmf2xml'):
            oracle_home = path
            print_success(f"ORACLE_HOME configurado: {oracle_home}")
        else:
            retry = input("\n¿Intentar con otra ruta? (s/n): ").strip().lower()
            if retry != 's':
                print("Configuración cancelada")
                sys.exit(1)

    # Configurar JAVA_HOME
    java_home = None
    while not java_home:
        path = prompt_for_path('JAVA_HOME', current_java_home, java_suggestions)
        if verify_path(path, 'bin/java'):
            java_home = path
            print_success(f"JAVA_HOME configurado: {java_home}")
        else:
            retry = input("\n¿Intentar con otra ruta? (s/n): ").strip().lower()
            if retry != 's':
                print("Configuración cancelada")
                sys.exit(1)

    # Generar comandos
    print_header("Variables de Entorno Configuradas")
    print(f"  ORACLE_HOME: {oracle_home}")
    print(f"  JAVA_HOME: {java_home}")
    print(f"  FORMS_PATH: {oracle_home}/forms")

    # Mostrar comandos para hacer permanente
    print_header("Para Hacer Permanente la Configuración")
    print("\nAñade las siguientes líneas a tu ~/.bashrc o ~/.bash_profile:\n")

    commands = generate_export_commands(oracle_home, java_home)
    print(commands)

    print("\n\nLuego ejecuta:")
    print("  source ~/.bashrc")

    # Preguntar si crear archivo .env
    print("\n")
    create_env = input("¿Deseas crear un archivo .env local con estas variables? (s/n): ").strip().lower()

    if create_env == 's':
        env_file = Path('.env')
        with open(env_file, 'w') as f:
            f.write("# Variables de entorno para Oracle Forms\n")
            f.write("# Carga con: source .env\n\n")
            f.write(commands + "\n")

        print_success(f"Archivo creado: {env_file}")
        print("Para usar: source .env")

    # Verificar instalación
    print("\n")
    verify = input("¿Deseas verificar la configuración ahora? (s/n): ").strip().lower()

    if verify == 's':
        print("\n")
        # Ejecutar verify_setup.py
        try:
            subprocess.run([sys.executable, 'verify_setup.py'], check=False)
        except Exception as e:
            print_error(f"Error al ejecutar verify_setup.py: {str(e)}")
            print("Puedes ejecutarlo manualmente: python3 verify_setup.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nConfiguración cancelada por el usuario")
        sys.exit(0)

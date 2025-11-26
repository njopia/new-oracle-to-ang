#!/usr/bin/env python3
"""
Script de verificación para Oracle Forms
Verifica que todo esté configurado correctamente antes de convertir
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Tuple


class Colors:
    """Colores ANSI para terminal"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_header(text: str) -> None:
    """Imprime encabezado"""
    print(f"\n{Colors.BLUE}{text}{Colors.NC}")


def print_check(text: str) -> None:
    """Imprime mensaje de verificación"""
    print(f"{Colors.YELLOW}{text}{Colors.NC}")


def print_success(text: str) -> None:
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")


def print_error(text: str) -> None:
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")


def print_warning(text: str) -> None:
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")


def print_info(text: str, indent: bool = True) -> None:
    """Imprime mensaje informativo"""
    prefix = "  " if indent else ""
    print(f"{prefix}{text}")


def check_oracle_home() -> Tuple[int, int]:
    """
    Verifica ORACLE_HOME
    Returns: (errores, advertencias)
    """
    print_check("[1/6] Verificando ORACLE_HOME...")

    oracle_home = os.environ.get('ORACLE_HOME')

    if not oracle_home:
        print_error("ORACLE_HOME no está configurado")
        print_info("Ejecuta: export ORACLE_HOME=/ruta/a/oracle/forms")
        return 1, 0

    if not Path(oracle_home).exists():
        print_error(f"ORACLE_HOME apunta a un directorio inexistente: {oracle_home}")
        return 1, 0

    print_success(f"ORACLE_HOME: {oracle_home}")
    return 0, 0


def check_frmf2xml() -> Tuple[int, int]:
    """
    Verifica frmf2xml
    Returns: (errores, advertencias)
    """
    print_check("\n[2/6] Verificando frmf2xml...")

    # Verificar si está en PATH
    frmf2xml_path = shutil.which('frmf2xml')

    if frmf2xml_path:
        print_success(f"frmf2xml encontrado: {frmf2xml_path}")
        return 0, 0

    # Verificar en ORACLE_HOME
    oracle_home = os.environ.get('ORACLE_HOME')
    if oracle_home:
        oracle_frmf2xml = Path(oracle_home) / "bin" / "frmf2xml"
        if oracle_frmf2xml.exists():
            print_success(f"frmf2xml encontrado: {oracle_frmf2xml}")
            print_warning("Considera añadir $ORACLE_HOME/bin al PATH")
            return 0, 1

    print_error("frmf2xml no encontrado")
    print_info("Verifica que Oracle Forms esté instalado correctamente")
    return 1, 0


def check_java_home() -> Tuple[int, int]:
    """
    Verifica JAVA_HOME
    Returns: (errores, advertencias)
    """
    print_check("\n[3/6] Verificando JAVA_HOME...")

    java_home = os.environ.get('JAVA_HOME')

    if not java_home:
        print_warning("JAVA_HOME no está configurado")
        print_info("Aunque no es crítico, se recomienda configurarlo")
        return 0, 1

    if not Path(java_home).exists():
        print_warning(f"JAVA_HOME apunta a un directorio inexistente: {java_home}")
        return 0, 1

    print_success(f"JAVA_HOME: {java_home}")
    return 0, 0


def check_java() -> Tuple[int, int]:
    """
    Verifica Java
    Returns: (errores, advertencias)
    """
    print_check("\n[4/6] Verificando Java...")

    java_path = shutil.which('java')

    if not java_path:
        print_warning("Java no encontrado en PATH")
        print_info("Considera instalar Java y añadirlo al PATH")
        return 0, 1

    try:
        result = subprocess.run(
            ['java', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        # java -version imprime en stderr
        version_output = result.stderr.split('\n')[0] if result.stderr else "desconocida"
        print_success(f"Java encontrado: {version_output}")
        return 0, 0

    except Exception as e:
        print_warning(f"Error al verificar versión de Java: {str(e)}")
        return 0, 1


def check_ld_library_path() -> Tuple[int, int]:
    """
    Verifica LD_LIBRARY_PATH
    Returns: (errores, advertencias)
    """
    print_check("\n[5/6] Verificando LD_LIBRARY_PATH...")

    ld_library_path = os.environ.get('LD_LIBRARY_PATH', '')
    oracle_home = os.environ.get('ORACLE_HOME', '')

    if ld_library_path and oracle_home and oracle_home in ld_library_path:
        print_success("LD_LIBRARY_PATH incluye ORACLE_HOME")
        return 0, 0

    if oracle_home and Path(oracle_home, "lib").exists():
        print_warning("LD_LIBRARY_PATH no incluye $ORACLE_HOME/lib")
        print_info("Si tienes problemas, ejecuta: export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH")
        return 0, 1

    print_warning("LD_LIBRARY_PATH no está configurado")
    return 0, 1


def check_path() -> Tuple[int, int]:
    """
    Verifica PATH
    Returns: (errores, advertencias)
    """
    print_check("\n[6/6] Verificando PATH...")

    path = os.environ.get('PATH', '')
    oracle_home = os.environ.get('ORACLE_HOME', '')

    if oracle_home and f"{oracle_home}/bin" in path:
        print_success("PATH incluye $ORACLE_HOME/bin")
        return 0, 0

    if oracle_home:
        print_warning("PATH no incluye $ORACLE_HOME/bin")
        print_info("Ejecuta: export PATH=$ORACLE_HOME/bin:$PATH")
        return 0, 1

    return 0, 0


def main():
    """Función principal"""
    print(f"{Colors.BLUE}=== Verificación de Configuración de Oracle Forms ==={Colors.NC}\n")

    total_errors = 0
    total_warnings = 0

    # Ejecutar todas las verificaciones
    checks = [
        check_oracle_home,
        check_frmf2xml,
        check_java_home,
        check_java,
        check_ld_library_path,
        check_path
    ]

    for check in checks:
        errors, warnings = check()
        total_errors += errors
        total_warnings += warnings

    # Resumen
    print_header("=== RESUMEN ===")

    if total_errors == 0 and total_warnings == 0:
        print_success("¡Todo está configurado correctamente!")
        print_info("\nPuedes usar el script convert_fmb_to_xml.py sin problemas.", indent=False)
        sys.exit(0)
    elif total_errors == 0:
        print_warning(f"Configuración funcional con {total_warnings} advertencia(s)")
        print_info("\nPuedes usar el script, pero considera resolver las advertencias.", indent=False)
        sys.exit(0)
    else:
        print_error(f"Encontrados {total_errors} error(es) y {total_warnings} advertencia(s)")
        print_info("\nPor favor, resuelve los errores antes de continuar.", indent=False)
        print_info("\nPara ayuda, consulta el README.md o ejecuta:", indent=False)
        print_info("  python3 setup_environment.py", indent=False)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script para convertir archivos Oracle Forms (.fmb) a XML
Requiere: Oracle Forms instalado con ORACLE_HOME configurado
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Tuple, List


class Colors:
    """Colores ANSI para terminal"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_error(message: str) -> None:
    """Imprime mensaje de error en rojo"""
    print(f"{Colors.RED}{message}{Colors.NC}", file=sys.stderr)


def print_success(message: str) -> None:
    """Imprime mensaje de éxito en verde"""
    print(f"{Colors.GREEN}{message}{Colors.NC}")


def print_warning(message: str) -> None:
    """Imprime mensaje de advertencia en amarillo"""
    print(f"{Colors.YELLOW}{message}{Colors.NC}")


def print_info(message: str) -> None:
    """Imprime mensaje informativo en azul"""
    print(f"{Colors.BLUE}{message}{Colors.NC}")


def check_oracle_home() -> Tuple[bool, str]:
    """
    Verifica que ORACLE_HOME está configurado y frmf2xml existe

    Returns:
        Tuple[bool, str]: (éxito, ruta a frmf2xml o mensaje de error)
    """
    oracle_home = os.environ.get('ORACLE_HOME')

    if not oracle_home:
        print_error("ERROR: ORACLE_HOME no está configurado")
        print("Por favor, configura ORACLE_HOME antes de ejecutar este script")
        print("Ejemplo: export ORACLE_HOME=/opt/oracle/middleware/forms")
        return False, ""

    # Verificar que existe frmf2xml
    frmf2xml = Path(oracle_home) / "bin" / "frmf2xml"

    if not frmf2xml.exists():
        print_error(f"ERROR: No se encuentra frmf2xml en {frmf2xml}")
        print("Verifica que Oracle Forms esté instalado correctamente")
        return False, ""

    print_success(f"✓ ORACLE_HOME encontrado: {oracle_home}")
    return True, str(frmf2xml)


def convert_file(input_file: Path, output_dir: Path, frmf2xml_path: str) -> bool:
    """
    Convierte un archivo .fmb a .xml

    Args:
        input_file: Ruta al archivo .fmb
        output_dir: Directorio de salida
        frmf2xml_path: Ruta al ejecutable frmf2xml

    Returns:
        bool: True si la conversión fue exitosa
    """
    # Obtener nombre base sin extensión
    basename = input_file.stem
    output_file = output_dir / f"{basename}.xml"

    print_warning(f"Convirtiendo: {input_file}")

    try:
        # Ejecutar frmf2xml
        result = subprocess.run(
            [frmf2xml_path, str(input_file), str(output_file), "overwrite=yes"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos de timeout
        )

        if result.returncode == 0:
            print_success(f"✓ Éxito: {output_file}")
            return True
        else:
            print_error(f"✗ Error al convertir: {input_file}")
            if result.stderr:
                print_error(f"  Detalle: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print_error(f"✗ Timeout al convertir: {input_file}")
        return False
    except Exception as e:
        print_error(f"✗ Error inesperado al convertir {input_file}: {str(e)}")
        return False


def find_fmb_files(directory: Path) -> List[Path]:
    """
    Busca recursivamente todos los archivos .fmb en un directorio

    Args:
        directory: Directorio donde buscar

    Returns:
        List[Path]: Lista de rutas a archivos .fmb
    """
    return list(directory.rglob("*.fmb"))


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Convierte archivos Oracle Forms (.fmb) a XML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s -f mi_formulario.fmb
  %(prog)s -d ./forms -o ./xml_output
  %(prog)s --file forms/ejemplo.fmb --output salida
        """
    )

    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Convertir un archivo específico'
    )

    parser.add_argument(
        '-d', '--directory',
        type=str,
        help='Convertir todos los .fmb en un directorio'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='./output',
        help='Directorio de salida (default: ./output)'
    )

    args = parser.parse_args()

    # Verificar que se proporcionó input
    if not args.file and not args.directory:
        print_error("ERROR: Debes especificar un archivo (-f) o directorio (-d)")
        parser.print_help()
        sys.exit(1)

    # Verificar ORACLE_HOME
    success, frmf2xml_path = check_oracle_home()
    if not success:
        sys.exit(1)

    # Crear directorio de salida
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    print_success(f"✓ Directorio de salida: {output_dir}")

    # Contadores
    success_count = 0
    error_count = 0

    # Procesar archivo único
    if args.file:
        input_file = Path(args.file)

        if not input_file.exists():
            print_error(f"ERROR: Archivo no encontrado: {input_file}")
            sys.exit(1)

        if not input_file.suffix == '.fmb':
            print_warning(f"ADVERTENCIA: El archivo no tiene extensión .fmb: {input_file}")

        if convert_file(input_file, output_dir, frmf2xml_path):
            success_count += 1
        else:
            error_count += 1

    # Procesar directorio
    if args.directory:
        input_dir = Path(args.directory)

        if not input_dir.exists():
            print_error(f"ERROR: Directorio no encontrado: {input_dir}")
            sys.exit(1)

        if not input_dir.is_dir():
            print_error(f"ERROR: La ruta no es un directorio: {input_dir}")
            sys.exit(1)

        print_info(f"\nBuscando archivos .fmb en: {input_dir}")

        fmb_files = find_fmb_files(input_dir)

        if not fmb_files:
            print_warning(f"No se encontraron archivos .fmb en {input_dir}")
            sys.exit(0)

        print_info(f"Encontrados {len(fmb_files)} archivo(s) .fmb\n")

        for fmb_file in fmb_files:
            if convert_file(fmb_file, output_dir, frmf2xml_path):
                success_count += 1
            else:
                error_count += 1

    # Resumen
    print_info("\n=== RESUMEN ===")
    print_success(f"Conversiones exitosas: {success_count}")
    print_error(f"Errores: {error_count}")

    # Exit code
    sys.exit(0 if error_count == 0 else 1)


if __name__ == "__main__":
    main()

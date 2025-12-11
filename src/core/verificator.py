#!/usr/bin/env python3
"""
Verificador de prerequisitos para la migración
Detecta Node.js, npm, Java, Oracle Home, Python
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PrerequisiteCheck:
    """Resultado de verificación de un prerequisito"""
    name: str
    found: bool
    version: Optional[str] = None
    path: Optional[str] = None
    message: Optional[str] = None


class Verificator:
    """Verificador de prerequisitos"""

    def __init__(self):
        self.results: Dict[str, PrerequisiteCheck] = {}

    def verify_all(self) -> Dict[str, PrerequisiteCheck]:
        """
        Verifica todos los prerequisitos

        Returns:
            Diccionario con resultados de todas las verificaciones
        """
        self.results = {
            'nodejs': self.verify_nodejs(),
            'npm': self.verify_npm(),
            'angular_cli': self.verify_angular_cli(),
            'java': self.verify_java(),
            'oracle_home': self.verify_oracle_home(),
            'frmf2xml': self.verify_frmf2xml(),
            'python': self.verify_python()
        }
        return self.results

    def verify_nodejs(self) -> PrerequisiteCheck:
        """Verifica Node.js"""
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                # Obtener ruta
                path_result = subprocess.run(
                    ['where' if os.name == 'nt' else 'which', 'node'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                path = path_result.stdout.strip().split('\n')[0] if path_result.returncode == 0 else None

                return PrerequisiteCheck(
                    name='Node.js',
                    found=True,
                    version=version,
                    path=path
                )
        except Exception as e:
            pass

        return PrerequisiteCheck(
            name='Node.js',
            found=False,
            message='Node.js not found'
        )

    def verify_npm(self) -> PrerequisiteCheck:
        """Verifica npm"""
        try:
            # En Windows, npm puede ser npm.cmd o necesitar cmd /c
            if os.name == 'nt':
                # Intentar primero con npm.cmd
                try:
                    result = subprocess.run(
                        ['npm.cmd', '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=False
                    )
                    if result.returncode != 0:
                        # Intentar con cmd /c npm
                        result = subprocess.run(
                            ['cmd', '/c', 'npm', '--version'],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            shell=False
                        )
                except:
                    # Fallback: usar npm directamente
                    result = subprocess.run(
                        ['npm', '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=True
                    )
            else:
                # Linux/Mac: usar npm directamente
                result = subprocess.run(
                    ['npm', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

            if result.returncode == 0:
                version = result.stdout.strip()

                # Obtener ruta de npm
                if os.name == 'nt':
                    path_result = subprocess.run(
                        ['where', 'npm'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=True
                    )
                else:
                    path_result = subprocess.run(
                        ['which', 'npm'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                path = path_result.stdout.strip().split('\n')[0] if path_result.returncode == 0 else None

                return PrerequisiteCheck(
                    name='npm',
                    found=True,
                    version=version,
                    path=path
                )
        except Exception as e:
            # Intentar una última vez con shell=True
            try:
                result = subprocess.run(
                    'npm --version',
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=True
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    return PrerequisiteCheck(
                        name='npm',
                        found=True,
                        version=version,
                        path=None,
                        message='Version detected but path unavailable'
                    )
            except:
                pass

        return PrerequisiteCheck(
            name='npm',
            found=False,
            message='npm not found'
        )

    def verify_angular_cli(self) -> PrerequisiteCheck:
        """Verifica Angular CLI"""
        try:
            # Intentar con ng
            result = subprocess.run(
                ['ng', 'version'],
                capture_output=True,
                text=True,
                timeout=10,
                shell=os.name == 'nt'  # Shell en Windows
            )

            if result.returncode == 0:
                # Extraer versión de Angular CLI
                output = result.stdout
                version = None

                for line in output.split('\n'):
                    if 'Angular CLI' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            version = parts[1].strip()
                            break

                if not version:
                    version = 'instalado'

                # Obtener ruta
                if os.name == 'nt':
                    path_result = subprocess.run(
                        ['where', 'ng'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=True
                    )
                else:
                    path_result = subprocess.run(
                        ['which', 'ng'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                path = path_result.stdout.strip().split('\n')[0] if path_result.returncode == 0 else None

                return PrerequisiteCheck(
                    name='Angular CLI',
                    found=True,
                    version=version,
                    path=path
                )
        except Exception as e:
            pass

        return PrerequisiteCheck(
            name='Angular CLI',
            found=False,
            message='Angular CLI not installed. Run: npm install -g @angular/cli'
        )

    def verify_java(self) -> PrerequisiteCheck:
        """Verifica Java JDK"""
        try:
            result = subprocess.run(
                ['java', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # java -version imprime en stderr
            if result.returncode == 0:
                version_output = result.stderr if result.stderr else result.stdout
                # Extraer versión (primera línea)
                version_line = version_output.split('\n')[0]

                path_result = subprocess.run(
                    ['where' if os.name == 'nt' else 'which', 'java'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                path = path_result.stdout.strip().split('\n')[0] if path_result.returncode == 0 else None

                return PrerequisiteCheck(
                    name='Java JDK',
                    found=True,
                    version=version_line,
                    path=path
                )
        except Exception:
            pass

        return PrerequisiteCheck(
            name='Java JDK',
            found=False,
            message='Java JDK not found'
        )

    def verify_oracle_home(self) -> PrerequisiteCheck:
        """Verifica ORACLE_HOME"""
        oracle_home = os.environ.get('ORACLE_HOME')

        if oracle_home:
            oracle_path = Path(oracle_home)
            if oracle_path.exists():
                return PrerequisiteCheck(
                    name='ORACLE_HOME',
                    found=True,
                    path=oracle_home,
                    message='ORACLE_HOME configured'
                )
            else:
                return PrerequisiteCheck(
                    name='ORACLE_HOME',
                    found=False,
                    path=oracle_home,
                    message='ORACLE_HOME path does not exist'
                )

        return PrerequisiteCheck(
            name='ORACLE_HOME',
            found=False,
            message='ORACLE_HOME not configured (will use JAVA_HOME)'
        )

    def verify_frmf2xml(self) -> PrerequisiteCheck:
        """Verifica frmf2xml.bat"""
        oracle_home = os.environ.get('ORACLE_HOME')

        if not oracle_home:
            return PrerequisiteCheck(
                name='Frmf2xml',
                found=False,
                message='Cannot verify: ORACLE_HOME not set'
            )

        # Rutas comunes de frmf2xml
        possible_paths = [
            Path(oracle_home) / 'forms' / 'templates' / 'scripts' / 'frmf2xml.bat',
            Path(oracle_home) / 'bin' / 'frmf2xml.bat',
            Path(oracle_home) / 'frmf2xml.bat'
        ]

        for path in possible_paths:
            if path.exists():
                return PrerequisiteCheck(
                    name='Frmf2xml (Oracle Forms)',
                    found=True,
                    path=str(path)
                )

        return PrerequisiteCheck(
            name='Frmf2xml (Oracle Forms)',
            found=False,
            message='frmf2xml.bat not found in ORACLE_HOME'
        )

    def verify_python(self) -> PrerequisiteCheck:
        """Verifica Python"""
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        python_path = sys.executable

        return PrerequisiteCheck(
            name='Python',
            found=True,
            version=version,
            path=python_path
        )

    def all_required_ok(self) -> bool:
        """
        Verifica si todos los prerequisitos requeridos están OK

        Returns:
            True si todos los prerequisitos críticos están presentes
        """
        if not self.results:
            self.verify_all()

        # Los críticos son: Java, Oracle Home, frmf2xml
        critical = ['java', 'oracle_home', 'frmf2xml']

        for key in critical:
            if key in self.results and not self.results[key].found:
                return False

        return True

    def get_summary(self) -> Tuple[int, int, int]:
        """
        Obtiene resumen de verificación

        Returns:
            Tupla (total, encontrados, no_encontrados)
        """
        if not self.results:
            self.verify_all()

        total = len(self.results)
        found = sum(1 for r in self.results.values() if r.found)
        not_found = total - found

        return (total, found, not_found)

    def install_angular_cli(self, callback=None) -> Tuple[bool, str]:
        """
        Instala Angular CLI automáticamente usando npm

        Args:
            callback: Función opcional para recibir output en tiempo real
                     callback(line: str) -> None

        Returns:
            Tupla (success: bool, message: str)
        """
        try:
            if callback:
                callback("📦 Instalando Angular CLI globalmente...\n")
                callback("⏳ Este proceso puede tomar varios minutos...\n\n")

            # Comando de instalación
            cmd = ['npm', 'install', '-g', '@angular/cli']

            # Ejecutar comando
            if os.name == 'nt':
                # Windows
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    shell=True
                )
            else:
                # Linux/Mac
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

            # Capturar output en tiempo real
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    output_lines.append(line)
                    if callback:
                        callback(line)

            process.wait()

            # Verificar resultado
            if process.returncode == 0:
                if callback:
                    callback("\n✅ Angular CLI instalado correctamente\n")
                    callback("🔄 Verificando instalación...\n")

                # Re-verificar
                check = self.verify_angular_cli()
                if check.found:
                    if callback:
                        callback(f"✅ Angular CLI {check.version} está listo para usar\n")
                    return (True, f"Angular CLI instalado: {check.version}")
                else:
                    return (False, "Instalación completada pero no se puede verificar. Reinicia el terminal.")
            else:
                error_msg = ''.join(output_lines[-10:]) if output_lines else "Error desconocido"
                if callback:
                    callback(f"\n❌ Error durante la instalación:\n{error_msg}\n")
                return (False, f"Error de instalación: {error_msg}")

        except Exception as e:
            error_msg = str(e)
            if callback:
                callback(f"\n❌ Excepción durante la instalación: {error_msg}\n")
            return (False, f"Excepción: {error_msg}")

    def install_nodejs_packages(self, packages: list, callback=None) -> Tuple[bool, str]:
        """
        Instala paquetes npm globalmente de manera genérica

        Args:
            packages: Lista de nombres de paquetes npm
            callback: Función opcional para recibir output en tiempo real

        Returns:
            Tupla (success: bool, message: str)
        """
        try:
            for package in packages:
                if callback:
                    callback(f"📦 Instalando {package}...\n")

                cmd = ['npm', 'install', '-g', package]

                if os.name == 'nt':
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                        shell=True
                    )
                else:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )

                for line in iter(process.stdout.readline, ''):
                    if line and callback:
                        callback(line)

                process.wait()

                if process.returncode != 0:
                    return (False, f"Error instalando {package}")

                if callback:
                    callback(f"✅ {package} instalado\n\n")

            return (True, "Todos los paquetes instalados correctamente")

        except Exception as e:
            return (False, f"Excepción: {str(e)}")

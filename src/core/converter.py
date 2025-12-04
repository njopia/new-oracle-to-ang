#!/usr/bin/env python3
"""
Convertidor de archivos Oracle Forms (.fmb) a XML
Usa frmf2xml.bat de Oracle Forms
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple, Callable, Optional
from dataclasses import dataclass
import time


@dataclass
class ConversionResult:
    """Resultado de una conversión"""
    fmb_file: str
    success: bool
    xml_file: Optional[str] = None
    error_message: Optional[str] = None
    duration: float = 0.0


class Converter:
    """Convertidor de FMB a XML"""

    def __init__(self, output_dir: str = "./output"):
        """
        Inicializa el convertidor

        Args:
            output_dir: Directorio donde se guardarán los XMLs
        """
        # Obtener la ruta del directorio de trabajo actual
        ruta_actual = Path.cwd()

        print(f"La ruta actual es: {ruta_actual}")
        print(f"Tipo de objeto: {type(ruta_actual)}")

        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        #self.temp_dir = Path("./temp")
        self.temp_dir = ruta_actual / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.frmf2xml_path = self._find_frmf2xml()
        self.results: List[ConversionResult] = []

    def _find_frmf2xml(self) -> Optional[Path]:
        """
        Encuentra el ejecutable frmf2xml.bat

        Returns:
            Path al ejecutable o None
        """
        oracle_home = os.environ.get('ORACLE_HOME')

        if not oracle_home:
            return None

        # Posibles ubicaciones
        possible_paths = [
            Path(oracle_home) / 'forms' / 'templates' / 'scripts' / 'frmf2xml.bat',
            Path(oracle_home) / 'bin' / 'frmf2xml.bat',
            Path(oracle_home) / 'frmf2xml.bat'
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def convert_file(self, fmb_file: str, progress_callback: Optional[Callable] = None) -> ConversionResult:
        """
        Convierte un archivo .fmb a .xml

        Args:
            fmb_file: Ruta al archivo .fmb
            progress_callback: Callback opcional para reportar progreso

        Returns:
            ConversionResult con el resultado de la conversión
        """
        start_time = time.time()
        fmb_path = Path(fmb_file)

        if not fmb_path.exists():
            return ConversionResult(
                fmb_file=str(fmb_file),
                success=False,
                error_message="File not found"
            )

        if not self.frmf2xml_path:
            return ConversionResult(
                fmb_file=str(fmb_file),
                success=False,
                error_message="frmf2xml.bat not found"
            )

        try:
            # Crear directorio temporal para esta conversión
            with tempfile.TemporaryDirectory(dir=self.temp_dir) as temp_conversion:
                temp_path = Path(temp_conversion)

                # Copiar .fmb al directorio temporal
                temp_fmb = temp_path / fmb_path.name
                shutil.copy2(fmb_path, temp_fmb)

                # Copiar frmf2xml.bat al directorio temporal (para evitar problemas de rutas)
                temp_bat = temp_path / 'frmf2xml.bat'
                
                shutil.copy2(self.frmf2xml_path, temp_bat)

                if progress_callback:
                    progress_callback(f"Converting  {fmb_path.name}...")

                # Ejecutar frmf2xml.bat
                # Comando: frmf2xml.bat archivo.fmb
                result = subprocess.run(
                    [str(temp_bat), fmb_path.name],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutos timeout
                )
                # Filtrar warnings no críticos de Oracle Forms
                # Estos son warnings comunes que no afectan la conversión
                oracle_warnings = [
                    "ERROR El secundario del grupo de objetos",
                    "La imagen IMAGE",
                    "se ha guardado como"
                ]

                # Solo mostrar errores críticos (no warnings esperados)
                if result.stderr:
                    critical_errors = []
                    for line in result.stderr.split('\n'):
                        # Ignorar warnings conocidos de Oracle Forms
                        if not any(warning in line for warning in oracle_warnings):
                            if line.strip() and 'ERROR' in line.upper():
                                critical_errors.append(line)

                    if critical_errors:
                        print("Errores críticos detectados:")
                        for error in critical_errors:
                            print(f"  - {error}")

                # Oracle Forms genera el XML con formato: nombre_fmb.xml
                xml_name_generated = fmb_path.stem + '_fmb.xml'
                temp_xml = temp_path / xml_name_generated

                # Nombre final sin el sufijo _fmb para mejor legibilidad
                final_xml_name = fmb_path.stem + '.xml'

                if temp_xml.exists():
                    # Mover XML al directorio de salida con nombre limpio
                    output_xml = self.output_dir / final_xml_name
                    shutil.move(str(temp_xml), str(output_xml))

                    duration = time.time() - start_time
                    print(f"✓ Conversión exitosa: {final_xml_name} ({duration:.2f}s)")

                    return ConversionResult(
                        fmb_file=str(fmb_file),
                        success=True,
                        xml_file=str(output_xml),
                        duration=duration
                    )
                else:
                    # Conversión falló
                    error_msg = result.stderr if result.stderr else "XML file not generated"
                    duration = time.time() - start_time

                    return ConversionResult(
                        fmb_file=str(fmb_file),
                        success=False,
                        error_message=error_msg,
                        duration=duration
                    )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return ConversionResult(
                fmb_file=str(fmb_file),
                success=False,
                error_message="Conversion timeout (>5 minutes)",
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return ConversionResult(
                fmb_file=str(fmb_file),
                success=False,
                error_message=str(e),
                duration=duration
            )

    def convert_batch(
        self,
        fmb_files: List[str],
        progress_callback: Optional[Callable] = None
    ) -> List[ConversionResult]:
        """
        Convierte múltiples archivos .fmb

        Args:
            fmb_files: Lista de rutas a archivos .fmb
            progress_callback: Callback opcional para reportar progreso

        Returns:
            Lista de ConversionResult
        """
        self.results = []
        total = len(fmb_files)

        for i, fmb_file in enumerate(fmb_files, 1):
            if progress_callback:
                progress_callback(f"Converting {i}/{total}: {Path(fmb_file).name}")

            result = self.convert_file(fmb_file, progress_callback)
            self.results.append(result)

        return self.results

    def get_summary(self) -> Tuple[int, int, int]:
        """
        Obtiene resumen de conversiones

        Returns:
            Tupla (total, exitosos, fallidos)
        """
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful

        return (total, successful, failed)

    def get_success_rate(self) -> float:
        """
        Calcula tasa de éxito

        Returns:
            Porcentaje de éxito (0-100)
        """
        if not self.results:
            return 0.0

        successful = sum(1 for r in self.results if r.success)
        return (successful / len(self.results)) * 100

    def cleanup_temp(self):
        """Limpia archivos temporales"""
        try:
            if self.temp_dir.exists():
                for item in self.temp_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
        except Exception as e:
            print(f"Error cleaning temp directory: {e}")
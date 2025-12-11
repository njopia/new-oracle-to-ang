#!/usr/bin/env python3
"""
Generador de LOVs (List of Values) para Angular
Convierte LOVs de Oracle Forms en enums TypeScript y servicios
"""

from pathlib import Path
from typing import Dict, List, Set
from ..parsers import FormStructure, LOV


class LovGenerator:
    """Genera enums y servicios para LOVs de Oracle Forms"""

    def __init__(self, config: Dict):
        self.config = config

    def generate_lovs(
        self,
        form_structures: List[FormStructure],
        output_dir: Path
    ) -> List[str]:
        """
        Genera archivos TypeScript para LOVs

        Args:
            form_structures: Lista de estructuras de formularios parseadas
            output_dir: Directorio de salida (models o enums)

        Returns:
            Lista de archivos generados
        """
        files_generated = []

        # Extraer todos los LOVs únicos
        lovs = self._extract_lovs(form_structures)

        if not lovs:
            return files_generated

        # Crear directorio para enums
        enums_dir = output_dir / "enums"
        enums_dir.mkdir(parents=True, exist_ok=True)

        # Generar archivo de enums consolidado
        enums_file = enums_dir / "lovs.enum.ts"
        enums_content = self._generate_enums_file(lovs)
        enums_file.write_text(enums_content, encoding='utf-8')
        files_generated.append(str(enums_file))

        # Generar servicio de LOVs
        services_dir = output_dir.parent / "services"
        services_dir.mkdir(parents=True, exist_ok=True)

        lov_service_file = services_dir / "lov.service.ts"
        lov_service_content = self._generate_lov_service(lovs)
        lov_service_file.write_text(lov_service_content, encoding='utf-8')
        files_generated.append(str(lov_service_file))

        # Generar interfaces para LOVs con columnas
        interfaces_file = enums_dir / "lovs.interface.ts"
        interfaces_content = self._generate_interfaces_file(lovs)
        interfaces_file.write_text(interfaces_content, encoding='utf-8')
        files_generated.append(str(interfaces_file))

        return files_generated

    def _extract_lovs(self, form_structures: List[FormStructure]) -> List[LOV]:
        """Extrae todos los LOVs únicos de los formularios"""
        lovs_dict = {}

        for form in form_structures:
            for lov in form.lovs:
                if lov.name not in lovs_dict:
                    lovs_dict[lov.name] = lov

        return list(lovs_dict.values())

    def _generate_enums_file(self, lovs: List[LOV]) -> str:
        """Genera archivo con enums para LOVs estáticos"""
        enums = []

        for lov in lovs:
            enum_name = self._format_enum_name(lov.name)

            # Generar enum con valores por defecto (sin datos reales)
            enum_content = f"""/**
 * {lov.title or lov.name}
 * Record Group: {lov.record_group or 'N/A'}
 */
export enum {enum_name} {{
  // TODO: Add actual values from database
  OPTION_1 = '1',
  OPTION_2 = '2',
  OPTION_3 = '3'
}}"""
            enums.append(enum_content)

        enums_str = "\n\n".join(enums)

        return f"""/**
 * LOVs (List of Values) enums
 * Generated from Oracle Forms LOVs
 *
 * These enums represent the List of Values used in the original forms.
 * Update the values according to your database data.
 */

{enums_str}
"""

    def _generate_interfaces_file(self, lovs: List[LOV]) -> str:
        """Genera interfaces para LOVs con múltiples columnas"""
        interfaces = []

        for lov in lovs:
            if not lov.columns or len(lov.columns) <= 1:
                continue

            interface_name = self._format_interface_name(lov.name)

            # Generar propiedades desde columnas
            properties = []
            for col in lov.columns:
                prop_name = self._camel_case(col)
                properties.append(f"  {prop_name}: string;")

            properties_str = "\n".join(properties)

            interface_content = f"""/**
 * Interface for {lov.title or lov.name}
 * Columns: {', '.join(lov.columns)}
 */
export interface {interface_name} {{
{properties_str}
}}"""
            interfaces.append(interface_content)

        if not interfaces:
            return """/**
 * LOV interfaces
 * No LOVs with multiple columns were found
 */

// No interfaces generated
"""

        interfaces_str = "\n\n".join(interfaces)

        return f"""/**
 * LOV interfaces for List of Values with multiple columns
 * Generated from Oracle Forms LOVs
 */

{interfaces_str}
"""

    def _generate_lov_service(self, lovs: List[LOV]) -> str:
        """Genera servicio para cargar LOVs dinámicos"""
        lov_names = [lov.name for lov in lovs]

        # Generar métodos para cada LOV
        methods = []
        for lov in lovs:
            method_name = self._format_method_name(lov.name)
            interface_name = self._format_interface_name(lov.name)

            if lov.columns and len(lov.columns) > 1:
                return_type = f"{interface_name}[]"
            else:
                return_type = "{ value: string; label: string }[]"

            method = f"""  /**
   * Get {lov.title or lov.name} options
   * Record Group: {lov.record_group or 'N/A'}
   */
  get{method_name}(): Observable<{return_type}> {{
    return this.http.get<{return_type}>(`${{this.baseUrl}}/lovs/{lov.name.lower()}`);
  }}"""
            methods.append(method)

        methods_str = "\n\n".join(methods)

        return f"""import {{ Injectable }} from '@angular/core';
import {{ HttpClient }} from '@angular/common/http';
import {{ Observable, of }} from 'rxjs';

/**
 * Service for loading List of Values (LOVs)
 * These correspond to LOVs from Oracle Forms
 */
@Injectable({{
  providedIn: 'root'
}})
export class LovService {{
  private baseUrl = 'http://localhost:3000/api';
  // TODO: Configure API base URL

  constructor(private http: HttpClient) {{ }}

{methods_str}

  /**
   * Generic method to get LOV by name
   * @param lovName Name of the LOV
   * @returns Observable of LOV options
   */
  getLovByName(lovName: string): Observable<{{ value: string; label: string }}[]> {{
    return this.http.get<{{ value: string; label: string }}[]>(
      `${{this.baseUrl}}/lovs/${{lovName.toLowerCase()}}`
    );
  }}

  /**
   * Mock data for development/testing
   * Remove this method when connecting to real API
   */
  getMockData(lovName: string): Observable<{{ value: string; label: string }}[]> {{
    const mockData = {{
{self._generate_mock_data(lovs)}
    }};

    return of(mockData[lovName] || []);
  }}
}}
"""

    def _generate_mock_data(self, lovs: List[LOV]) -> str:
        """Genera datos mock para testing"""
        mock_entries = []

        for lov in lovs:
            mock_entries.append(f"""      '{lov.name}': [
        {{ value: '1', label: 'Option 1' }},
        {{ value: '2', label: 'Option 2' }},
        {{ value: '3', label: 'Option 3' }}
      ]""")

        return ",\n".join(mock_entries)

    def _format_enum_name(self, lov_name: str) -> str:
        """Formatea nombre de LOV a nombre de enum"""
        # ACCOUNT_TYPES_LOV → AccountTypes
        name = lov_name.replace('_LOV', '').replace('_', ' ')
        return ''.join(word.capitalize() for word in name.split())

    def _format_interface_name(self, lov_name: str) -> str:
        """Formatea nombre de LOV a nombre de interface"""
        # ACCOUNT_TYPES_LOV → AccountTypesLov
        enum_name = self._format_enum_name(lov_name)
        return f"{enum_name}Item"

    def _format_method_name(self, lov_name: str) -> str:
        """Formatea nombre de LOV a nombre de método"""
        # ACCOUNT_TYPES_LOV → AccountTypes
        return self._format_enum_name(lov_name)

    def _camel_case(self, name: str) -> str:
        """Convierte UPPER_CASE a camelCase"""
        parts = name.lower().split('_')
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])

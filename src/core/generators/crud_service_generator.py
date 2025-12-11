#!/usr/bin/env python3
"""
Generador de servicios CRUD basados en data sources de Oracle Forms
"""

from pathlib import Path
from typing import Dict, List, Set
from ..parsers import FormStructure


class CrudServiceGenerator:
    """Genera servicios CRUD automáticos desde data sources"""

    def __init__(self, config: Dict):
        self.config = config

    def generate_crud_services(
        self,
        form_structures: List[FormStructure],
        output_dir: Path
    ) -> List[str]:
        """
        Genera servicios CRUD para cada data source único encontrado

        Args:
            form_structures: Lista de estructuras de formularios parseadas
            output_dir: Directorio de servicios

        Returns:
            Lista de archivos generados
        """
        files_generated = []

        # Extraer todos los data sources únicos
        data_sources = self._extract_data_sources(form_structures)

        for data_source in data_sources:
            # Generar servicio CRUD
            service_name = self._format_service_name(data_source)
            service_file = output_dir / f"{service_name}.service.ts"

            # Obtener estructura del formulario relacionado
            related_form = self._find_form_for_data_source(form_structures, data_source)

            content = self._generate_crud_service(data_source, service_name, related_form)
            service_file.write_text(content, encoding='utf-8')
            files_generated.append(str(service_file))

        return files_generated

    def _extract_data_sources(self, form_structures: List[FormStructure]) -> Set[str]:
        """Extrae todos los data sources únicos"""
        data_sources = set()

        for form in form_structures:
            for block in form.blocks:
                if block.query_data_source:
                    # Limpiar nombre de tabla (remover schema si existe)
                    table_name = block.query_data_source.split('.')[-1]
                    data_sources.add(table_name)

        return data_sources

    def _find_form_for_data_source(
        self,
        form_structures: List[FormStructure],
        data_source: str
    ) -> FormStructure:
        """Encuentra el formulario que usa este data source"""
        for form in form_structures:
            for block in form.blocks:
                if block.query_data_source:
                    table_name = block.query_data_source.split('.')[-1]
                    if table_name == data_source:
                        return form
        return None

    def _format_service_name(self, data_source: str) -> str:
        """Formatea el nombre del servicio"""
        # ACCOUNTS_TABLE → accounts
        name = data_source.lower().replace('_table', '').replace('_', '-')
        return name

    def _generate_crud_service(
        self,
        data_source: str,
        service_name: str,
        form_structure: FormStructure
    ) -> str:
        """Genera el código del servicio CRUD"""
        class_name = ''.join(word.capitalize() for word in service_name.split('-'))
        model_name = f"{class_name}Model"

        # Obtener bloque relacionado con este data source
        block = None
        if form_structure:
            for b in form_structure.blocks:
                if b.query_data_source:
                    table_name = b.query_data_source.split('.')[-1]
                    if table_name == data_source:
                        block = b
                        break

        # Determinar operaciones permitidas
        can_insert = block.insert_allowed if block else True
        can_update = block.update_allowed if block else True
        can_delete = block.delete_allowed if block else True
        can_query = block.query_allowed if block else True

        # Generar métodos CRUD
        methods = []

        if can_query:
            methods.append(self._generate_get_all_method(class_name, model_name))
            methods.append(self._generate_get_by_id_method(class_name, model_name))

        if can_insert:
            methods.append(self._generate_create_method(class_name, model_name))

        if can_update:
            methods.append(self._generate_update_method(class_name, model_name))

        if can_delete:
            methods.append(self._generate_delete_method(class_name))

        # Buscar con filtros
        if can_query and block and block.where_clause:
            methods.append(self._generate_search_method(class_name, model_name))

        methods_str = "\n\n".join(methods)

        return f"""import {{ Injectable }} from '@angular/core';
import {{ HttpClient, HttpParams }} from '@angular/common/http';
import {{ Observable }} from 'rxjs';

// TODO: Import the model interface
// import {{ {model_name} }} from '../models/{service_name}.model';

interface {model_name} {{
  id?: number;
  // TODO: Add fields from {data_source}
}}

@Injectable({{
  providedIn: 'root'
}})
export class {class_name}Service {{
  private baseUrl = 'http://localhost:3000/api/{service_name}';
  // TODO: Configure API base URL

  constructor(private http: HttpClient) {{ }}

{methods_str}
}}
"""

    def _generate_get_all_method(self, class_name: str, model_name: str) -> str:
        """Genera método getAll"""
        return f"""  /**
   * Get all {class_name.lower()} records
   * @returns Observable of {model_name} array
   */
  getAll(): Observable<{model_name}[]> {{
    return this.http.get<{model_name}[]>(this.baseUrl);
  }}"""

    def _generate_get_by_id_method(self, class_name: str, model_name: str) -> str:
        """Genera método getById"""
        return f"""  /**
   * Get {class_name.lower()} by ID
   * @param id Record ID
   * @returns Observable of {model_name}
   */
  getById(id: number): Observable<{model_name}> {{
    return this.http.get<{model_name}>(`${{this.baseUrl}}/${{id}}`);
  }}"""

    def _generate_create_method(self, class_name: str, model_name: str) -> str:
        """Genera método create"""
        return f"""  /**
   * Create new {class_name.lower()} record
   * @param data {model_name} data
   * @returns Observable of created {model_name}
   */
  create(data: {model_name}): Observable<{model_name}> {{
    return this.http.post<{model_name}>(this.baseUrl, data);
  }}"""

    def _generate_update_method(self, class_name: str, model_name: str) -> str:
        """Genera método update"""
        return f"""  /**
   * Update existing {class_name.lower()} record
   * @param id Record ID
   * @param data Partial {model_name} data
   * @returns Observable of updated {model_name}
   */
  update(id: number, data: Partial<{model_name}>): Observable<{model_name}> {{
    return this.http.put<{model_name}>(`${{this.baseUrl}}/${{id}}`, data);
  }}"""

    def _generate_delete_method(self, class_name: str) -> str:
        """Genera método delete"""
        return f"""  /**
   * Delete {class_name.lower()} record
   * @param id Record ID
   * @returns Observable of void
   */
  delete(id: number): Observable<void> {{
    return this.http.delete<void>(`${{this.baseUrl}}/${{id}}`);
  }}"""

    def _generate_search_method(self, class_name: str, model_name: str) -> str:
        """Genera método search con filtros"""
        return f"""  /**
   * Search {class_name.lower()} records with filters
   * @param filters Search filters
   * @returns Observable of {model_name} array
   */
  search(filters: Partial<{model_name}>): Observable<{model_name}[]> {{
    let params = new HttpParams();
    Object.keys(filters).forEach(key => {{
      if (filters[key] !== null && filters[key] !== undefined) {{
        params = params.set(key, String(filters[key]));
      }}
    }});
    return this.http.get<{model_name}[]>(this.baseUrl, {{ params }});
  }}"""

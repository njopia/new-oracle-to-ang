#!/usr/bin/env python3
"""
Generador de Proyecto Angular Completo
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, List

from .base_generator import BaseGenerator, GenerationResult
from .smart_component_generator import SmartComponentGenerator
from .crud_service_generator import CrudServiceGenerator
from .lov_generator import LovGenerator
from ..parsers import OracleFormsParser


class AngularProjectGenerator(BaseGenerator):
    """Generador de proyecto Angular completo"""

    def generate(self, output_dir: str) -> GenerationResult:
        """
        Genera un proyecto Angular completo

        Args:
            output_dir: Directorio de salida

        Returns:
            Resultado de la generación
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            files_generated = []

            # 1. Crear proyecto Angular con ng new
            self._log("🚀 Creando proyecto Angular base...\n")
            self._update_progress("Creando proyecto Angular...")

            project_name = self.config.get('project_name', 'angular-app')
            result = self._create_angular_project(output_path, project_name)

            if not result:
                return GenerationResult(
                    success=False,
                    output_dir=output_dir,
                    files_generated=[],
                    error_message="Failed to create Angular project"
                )

            self._log("✓ Proyecto base creado\n\n")

            # 2. Generar componentes migrados con Angular CLI
            self._log("🎨 Generando componentes migrados...\n")
            self._update_progress("Generando componentes...")

            project_path = output_path / project_name
            selected_files = self.config.get('selected_files', [])

            # Usar ng generate component para cada componente
            components_generated = self._generate_components_with_cli(
                project_path,
                selected_files
            )
            files_generated.extend(components_generated)

            self._log(f"\n✓ {len(selected_files)} componentes generados\n\n")

            # 3. Generar servicios (si está habilitado)
            if self.config.get('generate_services', True):
                self._generate_services(project_path)
                self._log("✓ Servicios base generados\n\n")

                # 3.5 Generar servicios CRUD automáticos desde data sources
                self._log("⚙️  Generando servicios CRUD desde data sources...\n")
                crud_services = self._generate_crud_services(project_path, selected_files)
                if crud_services:
                    files_generated.extend(crud_services)
                    self._log(f"✓ {len(crud_services)} servicios CRUD generados\n\n")
                else:
                    self._log("ℹ️  No se encontraron data sources para generar servicios\n\n")

                # 3.6 Generar LOVs (List of Values)
                self._log("📋 Generando LOVs (List of Values)...\n")
                lov_files = self._generate_lovs(project_path, selected_files)
                if lov_files:
                    files_generated.extend(lov_files)
                    self._log(f"✓ LOVs generados: enums, interfaces y servicio\n\n")
                else:
                    self._log("ℹ️  No se encontraron LOVs para generar\n\n")

            # 4. Configurar routing (si está habilitado)
            if self.config.get('routing', True):
                self._configure_routing(project_path, selected_files)
                self._log("✓ Routing configurado\n\n")

            # 5. Generar documentación (si está habilitado)
            if self.config.get('generate_docs', True):
                self._generate_documentation(project_path)
                self._log("✓ Documentación generada\n\n")

            return GenerationResult(
                success=True,
                output_dir=str(project_path),
                files_generated=files_generated
            )

        except Exception as e:
            self._log(f"\n✗ Error: {str(e)}\n")
            return GenerationResult(
                success=False,
                output_dir=output_dir,
                files_generated=[],
                error_message=str(e)
            )

    def _create_angular_project(self, output_path: Path, project_name: str) -> bool:
        """
        Crea el proyecto Angular base usando ng new

        Args:
            output_path: Directorio de salida
            project_name: Nombre del proyecto

        Returns:
            True si se creó exitosamente, False en caso contrario
        """
        try:
            style_ext = self.config.get('style_extension', 'scss')
            routing = self.config.get('routing', True)
            standalone = self.config.get('standalone', False)

            # Construir comando ng new
            cmd = [
                'ng', 'new', project_name,
                f'--style={style_ext}',
                '--skip-git',
                '--package-manager=npm'
            ]

            # Agregar opciones
            if routing:
                cmd.append('--routing')
            else:
                cmd.append('--routing=false')

            if standalone:
                cmd.append('--standalone')
            else:
                cmd.append('--standalone=false')

            # Ejecutar en el directorio de salida
            self._log(f"   Ejecutando: {' '.join(cmd)}\n")
            self._log(f"   Directorio: {output_path}\n\n")
            self._log("   Por favor espere, esto puede tomar varios minutos...\n")
            self._log("   (Instalando dependencias de Node.js)\n\n")

            # Ejecutar comando
            process = subprocess.Popen(
                cmd,
                cwd=str(output_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Capturar salida en tiempo real
            for line in iter(process.stdout.readline, ''):
                if line:
                    self._log(f"   {line}")

            process.wait()

            if process.returncode != 0:
                self._log(f"\n   ✗ Error: ng new falló con código {process.returncode}\n")
                return False

            # Verificar que el proyecto se creó
            project_path = output_path / project_name
            if not (project_path / "package.json").exists():
                self._log(f"\n   ✗ Error: No se encontró package.json\n")
                return False

            if not (project_path / "angular.json").exists():
                self._log(f"\n   ✗ Error: No se encontró angular.json\n")
                return False

            return True

        except FileNotFoundError:
            self._log(f"\n   ✗ Error: Angular CLI no está instalado\n")
            self._log(f"   Por favor instala Angular CLI: npm install -g @angular/cli\n")
            return False
        except Exception as e:
            self._log(f"\n   ✗ Error al crear proyecto: {str(e)}\n")
            return False

    def _generate_components_with_cli(self, project_path: Path, xml_files: List[str]) -> List[str]:
        """
        Genera componentes usando ng generate component

        Args:
            project_path: Ruta al proyecto Angular
            xml_files: Lista de archivos XML

        Returns:
            Lista de archivos generados
        """
        files_generated = []
        smart_generator = SmartComponentGenerator(self.config)

        for xml_file in xml_files:
            component_name = Path(xml_file).stem
            naming = self.config.get('naming_convention', 'kebab-case')
            formatted_name = self._format_name(component_name, naming)

            try:
                # 1. Usar ng generate component
                self._log(f"   → Generando {formatted_name}...\n")

                # Construir comando
                cmd = [
                    'ng', 'generate', 'component',
                    f'components/{formatted_name}',
                    '--skip-tests' if not self.config.get('generate_tests', True) else '--skip-tests=false'
                ]

                # Ejecutar ng generate
                result = subprocess.run(
                    cmd,
                    cwd=str(project_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.returncode != 0:
                    self._log(f"   ⚠ Advertencia: ng generate falló, generando manualmente\n")
                    # Fallback: generar manualmente
                    components_dir = project_path / "src" / "app" / "components"
                    components_dir.mkdir(parents=True, exist_ok=True)
                    component_files = smart_generator.generate_component_from_xml(
                        xml_file,
                        components_dir,
                        formatted_name
                    )
                    files_generated.extend(component_files)
                else:
                    # 2. Sobrescribir archivos con templates inteligentes
                    component_dir = project_path / "src" / "app" / "components" / formatted_name

                    # Parsear XML y generar contenido inteligente
                    from ..parsers import OracleFormsParser
                    parser = OracleFormsParser()
                    form_structure = parser.parse_file(xml_file)

                    # Sobrescribir .ts
                    ts_file = component_dir / f"{formatted_name}.component.ts"
                    ts_content = smart_generator._generate_smart_component_ts(formatted_name, form_structure)
                    ts_file.write_text(ts_content, encoding='utf-8')
                    files_generated.append(str(ts_file))

                    # Sobrescribir .html
                    html_file = component_dir / f"{formatted_name}.component.html"
                    html_content = smart_generator._generate_smart_component_html(formatted_name, form_structure)
                    html_file.write_text(html_content, encoding='utf-8')
                    files_generated.append(str(html_file))

                    # Sobrescribir .scss/.css
                    style_ext = self.config.get('style_extension', 'scss')
                    style_file = component_dir / f"{formatted_name}.component.{style_ext}"
                    style_content = smart_generator._generate_smart_component_styles(formatted_name, form_structure)
                    style_file.write_text(style_content, encoding='utf-8')
                    files_generated.append(str(style_file))

                    # Generar .model.ts si tiene items
                    if form_structure.get_all_items():
                        model_file = component_dir / f"{formatted_name}.model.ts"
                        model_content = smart_generator._generate_model(formatted_name, form_structure)
                        model_file.write_text(model_content, encoding='utf-8')
                        files_generated.append(str(model_file))

                    # Spec file ya fue generado por ng generate
                    spec_file = component_dir / f"{formatted_name}.component.spec.ts"
                    if spec_file.exists():
                        files_generated.append(str(spec_file))

                    self._log(f"   ✓ {formatted_name} generado e integrado\n")

            except Exception as e:
                self._log(f"   ✗ Error en {formatted_name}: {str(e)}\n")
                # Continuar con el siguiente componente
                continue

        return files_generated

    def _generate_crud_services(self, project_path: Path, xml_files: List[str]) -> List[str]:
        """
        Genera servicios CRUD automáticos desde data sources

        Args:
            project_path: Ruta al proyecto Angular
            xml_files: Lista de archivos XML

        Returns:
            Lista de archivos generados
        """
        try:
            # Parsear todos los XMLs para extraer estructuras
            parser = OracleFormsParser()
            form_structures = []

            for xml_file in xml_files:
                form_structure = parser.parse_file(xml_file)
                form_structures.append(form_structure)

            # Generar servicios CRUD
            services_dir = project_path / "src" / "app" / "services"
            services_dir.mkdir(parents=True, exist_ok=True)

            crud_generator = CrudServiceGenerator(self.config)
            files_generated = crud_generator.generate_crud_services(
                form_structures,
                services_dir
            )

            # Log de servicios generados
            for file_path in files_generated:
                service_name = Path(file_path).stem
                self._log(f"   ✓ {service_name}.service.ts (CRUD)\n")

            return files_generated

        except Exception as e:
            self._log(f"   ⚠ Error generando servicios CRUD: {str(e)}\n")
            return []

    def _generate_lovs(self, project_path: Path, xml_files: List[str]) -> List[str]:
        """
        Genera enums e interfaces para LOVs

        Args:
            project_path: Ruta al proyecto Angular
            xml_files: Lista de archivos XML

        Returns:
            Lista de archivos generados
        """
        try:
            # Parsear todos los XMLs para extraer LOVs
            parser = OracleFormsParser()
            form_structures = []

            for xml_file in xml_files:
                form_structure = parser.parse_file(xml_file)
                form_structures.append(form_structure)

            # Generar LOVs
            models_dir = project_path / "src" / "app" / "models"
            models_dir.mkdir(parents=True, exist_ok=True)

            lov_generator = LovGenerator(self.config)
            files_generated = lov_generator.generate_lovs(
                form_structures,
                models_dir
            )

            # Log de archivos generados
            for file_path in files_generated:
                file_name = Path(file_path).name
                self._log(f"   ✓ {file_name}\n")

            return files_generated

        except Exception as e:
            self._log(f"   ⚠ Error generando LOVs: {str(e)}\n")
            return []

    def _generate_services(self, project_path: Path):
        """Genera servicios Angular usando ng generate service"""
        self._log("⚙️  Generando servicios...\n")
        self._update_progress("Generando servicios...")

        services = ['data', 'api']

        for service_name in services:
            try:
                # Usar ng generate service
                cmd = [
                    'ng', 'generate', 'service',
                    f'services/{service_name}',
                    '--skip-tests'
                ]

                result = subprocess.run(
                    cmd,
                    cwd=str(project_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.returncode == 0:
                    # Sobrescribir con nuestro template
                    service_file = project_path / "src" / "app" / "services" / f"{service_name}.service.ts"

                    if service_name == 'data':
                        content = self._get_data_service_template()
                    else:  # api
                        content = self._get_api_service_template()

                    service_file.write_text(content, encoding='utf-8')
                    self._log(f"   ✓ {service_name}.service.ts\n")
                else:
                    # Fallback: crear manualmente
                    services_dir = project_path / "src" / "app" / "services"
                    services_dir.mkdir(parents=True, exist_ok=True)

                    service_file = services_dir / f"{service_name}.service.ts"
                    if service_name == 'data':
                        content = self._get_data_service_template()
                    else:
                        content = self._get_api_service_template()

                    service_file.write_text(content, encoding='utf-8')
                    self._log(f"   ✓ {service_name}.service.ts (manual)\n")

            except Exception as e:
                self._log(f"   ⚠ Error generando {service_name}.service: {str(e)}\n")

    def _configure_routing(self, project_path: Path, xml_files: List[str]):
        """Configura el routing del proyecto"""
        self._log("🗺️  Configurando routing...\n")
        self._update_progress("Configurando routing...")

        routing_file = project_path / "src" / "app" / "app-routing.module.ts"
        routing_content = self._generate_routing_module(xml_files)
        routing_file.write_text(routing_content, encoding='utf-8')
        self._log("   ✓ app-routing.module.ts configurado\n")

    def _generate_documentation(self, project_path: Path):
        """Genera documentación del proyecto"""
        self._log("📚 Generando documentación...\n")

        readme = project_path / "README.migration.md"
        readme_content = self._get_readme_template()
        readme.write_text(readme_content, encoding='utf-8')
        self._log("   ✓ README.migration.md\n")

    def _get_data_service_template(self) -> str:
        """Template para el servicio de datos"""
        return """import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private dataSubject = new BehaviorSubject<any>(null);
  public data$: Observable<any> = this.dataSubject.asObservable();

  constructor() { }

  setData(data: any): void {
    this.dataSubject.next(data);
  }

  getData(): any {
    return this.dataSubject.value;
  }
}
"""

    def _get_api_service_template(self) -> str:
        """Template para el servicio de API"""
        return """import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:3000/api'; // TODO: Configure API URL

  constructor(private http: HttpClient) { }

  get<T>(endpoint: string): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}/${endpoint}`);
  }

  post<T>(endpoint: string, data: any): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}/${endpoint}`, data);
  }

  put<T>(endpoint: string, data: any): Observable<T> {
    return this.http.put<T>(`${this.baseUrl}/${endpoint}`, data);
  }

  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}/${endpoint}`);
  }
}
"""

    def _generate_routing_module(self, xml_files: List[str]) -> str:
        """Genera el módulo de routing"""
        routes = []
        for xml_file in xml_files:
            component_name = Path(xml_file).stem
            naming = self.config.get('naming_convention', 'kebab-case')
            formatted_name = self._format_name(component_name, naming)
            class_name = ''.join(p.capitalize() for p in formatted_name.split('-'))

            routes.append(f"  {{ path: '{formatted_name}', component: {class_name}Component }}")

        routes_str = ',\n'.join(routes)

        return f"""import {{ NgModule }} from '@angular/core';
import {{ RouterModule, Routes }} from '@angular/router';

const routes: Routes = [
  {{ path: '', redirectTo: '/home', pathMatch: 'full' }},
{routes_str}
];

@NgModule({{
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
}})
export class AppRoutingModule {{ }}
"""

    def _get_readme_template(self) -> str:
        """Template para el README de migración"""
        return """# Oracle Forms to Angular Migration

This project was migrated from Oracle Forms using the Oracle Forms to Angular Migrator.

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   ng serve
   ```

3. Navigate to `http://localhost:4200/`

## Project Structure

- `src/app/components/` - Migrated components from Oracle Forms
- `src/app/services/` - Generated services
- `src/app/models/` - Data models

## Next Steps

- Review and customize generated components
- Implement business logic in services
- Add authentication and authorization
- Configure API endpoints
- Add error handling
- Write additional unit tests

## Notes

This is an initial migration. Review all generated code and adapt to your specific needs.
"""

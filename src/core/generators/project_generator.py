#!/usr/bin/env python3
"""
Generador de Proyecto Angular Completo
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, List

from .base_generator import BaseGenerator, GenerationResult
from .smart_component_generator import SmartComponentGenerator


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

            # 2. Generar componentes migrados
            self._log("🎨 Generando componentes migrados...\n")
            self._update_progress("Generando componentes...")

            project_path = output_path / project_name
            components_dir = project_path / "src" / "app" / "components"
            components_dir.mkdir(parents=True, exist_ok=True)

            selected_files = self.config.get('selected_files', [])
            smart_generator = SmartComponentGenerator(self.config)

            for xml_file in selected_files:
                component_name = Path(xml_file).stem
                # Formatear nombre según convención
                naming = self.config.get('naming_convention', 'kebab-case')
                formatted_name = self._format_name(component_name, naming)

                # Usar generador inteligente que parsea el XML
                component_files = smart_generator.generate_component_from_xml(
                    xml_file,
                    components_dir,
                    formatted_name
                )
                files_generated.extend(component_files)
                self._log(f"   ✓ Componente generado: {formatted_name}\n")

            self._log(f"\n✓ {len(selected_files)} componentes generados\n\n")

            # 3. Generar servicios (si está habilitado)
            if self.config.get('generate_services', True):
                self._generate_services(project_path)
                self._log("✓ Servicios generados\n\n")

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

    def _generate_services(self, project_path: Path):
        """Genera servicios Angular"""
        self._log("⚙️  Generando servicios...\n")
        self._update_progress("Generando servicios...")

        services_dir = project_path / "src" / "app" / "services"
        services_dir.mkdir(parents=True, exist_ok=True)

        # Servicio de datos
        data_service = services_dir / "data.service.ts"
        data_service.write_text(self._get_data_service_template(), encoding='utf-8')
        self._log("   ✓ data.service.ts\n")

        # Servicio de API
        api_service = services_dir / "api.service.ts"
        api_service.write_text(self._get_api_service_template(), encoding='utf-8')
        self._log("   ✓ api.service.ts\n")

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

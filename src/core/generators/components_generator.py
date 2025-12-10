#!/usr/bin/env python3
"""
Generador de Solo Componentes (sin proyecto)
"""

from pathlib import Path
from typing import Dict, Any

from .base_generator import BaseGenerator, GenerationResult


class ComponentsOnlyGenerator(BaseGenerator):
    """Generador de solo componentes sin estructura de proyecto"""

    def generate(self, output_dir: str) -> GenerationResult:
        """
        Genera solo componentes y servicios sin estructura de proyecto

        Args:
            output_dir: Directorio de salida

        Returns:
            Resultado de la generación
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            files_generated = []

            self._log("📁 Creando estructura de carpetas...\n")

            # Crear estructura de carpetas
            folders = {
                'components': output_path / 'components',
                'services': output_path / 'services',
                'models': output_path / 'models',
                'interfaces': output_path / 'interfaces'
            }

            for folder_name, folder_path in folders.items():
                folder_path.mkdir(exist_ok=True)
                self._log(f"   ✓ Carpeta creada: {folder_name}/\n")

            self._log("\n")

            # Generar componentes
            self._log("🎨 Generando componentes...\n")
            self._update_progress("Generando componentes...")

            selected_files = self.config.get('selected_files', [])
            for xml_file in selected_files:
                component_name = Path(xml_file).stem
                component_files = self._create_component(
                    component_name,
                    folders['components']
                )
                files_generated.extend(component_files)

                self._log(f"   ✓ Componente generado: {component_name}\n")
                for file_path in component_files:
                    rel_path = Path(file_path).relative_to(output_path)
                    self._log(f"      • {rel_path}\n")

            self._log(f"\n✓ {len(selected_files)} componentes generados\n\n")

            # Generar servicios (si está habilitado)
            if self.config.get('generate_services', True):
                self._log("⚙️  Generando servicios...\n")
                self._update_progress("Generando servicios...")

                service_files = self._generate_services(folders['services'])
                files_generated.extend(service_files)

                self._log("✓ Servicios generados\n\n")

            # Generar interfaces de modelos
            self._log("📋 Generando interfaces...\n")
            interface_files = self._generate_interfaces(folders['interfaces'])
            files_generated.extend(interface_files)
            self._log("✓ Interfaces generadas\n\n")

            # Generar README con instrucciones
            readme_path = self._generate_integration_readme(output_path)
            files_generated.append(readme_path)
            self._log("✓ README de integración generado\n\n")

            return GenerationResult(
                success=True,
                output_dir=output_dir,
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

    def _generate_services(self, services_dir: Path) -> list:
        """Genera servicios básicos"""
        files_created = []

        # Servicio de datos
        data_service = services_dir / "data.service.ts"
        data_service.write_text(self._get_data_service_template(), encoding='utf-8')
        files_created.append(str(data_service))
        self._log("   ✓ data.service.ts\n")

        # Servicio de API
        api_service = services_dir / "api.service.ts"
        api_service.write_text(self._get_api_service_template(), encoding='utf-8')
        files_created.append(str(api_service))
        self._log("   ✓ api.service.ts\n")

        return files_created

    def _generate_interfaces(self, interfaces_dir: Path) -> list:
        """Genera interfaces comunes"""
        files_created = []

        # Interface base
        base_interface = interfaces_dir / "base.interface.ts"
        base_interface.write_text(self._get_base_interface_template(), encoding='utf-8')
        files_created.append(str(base_interface))
        self._log("   ✓ base.interface.ts\n")

        return files_created

    def _generate_integration_readme(self, output_path: Path) -> str:
        """Genera README con instrucciones de integración"""
        readme_path = output_path / "INTEGRATION.md"
        readme_content = self._get_integration_readme_template()
        readme_path.write_text(readme_content, encoding='utf-8')
        return str(readme_path)

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

  clearData(): void {
    this.dataSubject.next(null);
  }
}
"""

    def _get_api_service_template(self) -> str:
        """Template para el servicio de API"""
        return """import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:3000/api'; // TODO: Configure your API URL

  constructor(private http: HttpClient) { }

  get<T>(endpoint: string, options?: any): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}/${endpoint}`, options);
  }

  post<T>(endpoint: string, data: any, options?: any): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}/${endpoint}`, data, options);
  }

  put<T>(endpoint: string, data: any, options?: any): Observable<T> {
    return this.http.put<T>(`${this.baseUrl}/${endpoint}`, data, options);
  }

  delete<T>(endpoint: string, options?: any): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}/${endpoint}`, options);
  }
}
"""

    def _get_base_interface_template(self) -> str:
        """Template para interface base"""
        return """export interface BaseEntity {
  id?: string | number;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}
"""

    def _get_integration_readme_template(self) -> str:
        """Template para el README de integración"""
        return """# Integración de Componentes Migrados

Este directorio contiene componentes migrados de Oracle Forms que deben ser integrados en un proyecto Angular existente.

## Estructura

```
components/     - Componentes Angular migrados
services/       - Servicios generados
models/         - Modelos de datos
interfaces/     - Interfaces TypeScript
```

## Pasos de Integración

### 1. Copiar Archivos

Copia los directorios generados a tu proyecto Angular:

```bash
# Desde el directorio de tu proyecto Angular
cp -r <ruta-a-este-directorio>/components/* src/app/components/
cp -r <ruta-a-este-directorio>/services/* src/app/services/
cp -r <ruta-a-este-directorio>/interfaces/* src/app/interfaces/
```

### 2. Registrar Componentes

Si NO estás usando componentes standalone, debes declarar los componentes en tu módulo:

```typescript
// app.module.ts o feature.module.ts
import { Component1Component } from './components/component-1/component-1.component';
import { Component2Component } from './components/component-2/component-2.component';

@NgModule({
  declarations: [
    Component1Component,
    Component2Component,
    // ... otros componentes
  ],
  // ...
})
export class AppModule { }
```

### 3. Configurar Routing (Opcional)

Si deseas agregar rutas para los componentes:

```typescript
// app-routing.module.ts
import { Component1Component } from './components/component-1/component-1.component';

const routes: Routes = [
  { path: 'component-1', component: Component1Component },
  // ... otras rutas
];
```

### 4. Importar Servicios

Los servicios están configurados con `providedIn: 'root'`, por lo que se pueden inyectar directamente:

```typescript
import { DataService } from './services/data.service';
import { ApiService } from './services/api.service';

constructor(
  private dataService: DataService,
  private apiService: ApiService
) { }
```

### 5. Configurar API

Actualiza la URL base del API en `services/api.service.ts`:

```typescript
private baseUrl = 'https://your-api-url.com/api';
```

## Notas Importantes

- **Revisar Código**: Los componentes generados son un punto de partida. Revisa y adapta el código según tus necesidades.
- **Dependencias**: Asegúrate de tener las dependencias necesarias instaladas (HttpClientModule, CommonModule, etc.).
- **Estilos**: Los estilos pueden necesitar ajustes según tu theme/diseño.
- **Lógica de Negocio**: Implementa la lógica de negocio específica en los servicios y componentes.

## Testing

Cada componente incluye un archivo `.spec.ts` básico. Actualiza los tests según la funcionalidad implementada:

```bash
ng test
```

## Soporte

Para más información sobre la migración, consulta la documentación del proyecto original o el reporte de análisis generado.
"""

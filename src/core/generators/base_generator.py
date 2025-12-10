#!/usr/bin/env python3
"""
Generador base para código Angular
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass


@dataclass
class GenerationResult:
    """Resultado de la generación"""
    success: bool
    output_dir: str
    files_generated: List[str]
    error_message: Optional[str] = None


class BaseGenerator(ABC):
    """Clase base para generadores de código Angular"""

    def __init__(self, config: Dict[str, Any], xml_files: List[str]):
        """
        Inicializa el generador

        Args:
            config: Configuración del proyecto
            xml_files: Lista de archivos XML a procesar
        """
        self.config = config
        self.xml_files = xml_files
        self.log_callback: Optional[Callable[[str], None]] = None
        self.progress_callback: Optional[Callable[[str], None]] = None

    def set_log_callback(self, callback: Callable[[str], None]):
        """Establece el callback para logging"""
        self.log_callback = callback

    def set_progress_callback(self, callback: Callable[[str], None]):
        """Establece el callback para actualizar progreso"""
        self.progress_callback = callback

    def _log(self, message: str):
        """Escribe en el log"""
        if self.log_callback:
            self.log_callback(message)

    def _update_progress(self, message: str):
        """Actualiza el progreso"""
        if self.progress_callback:
            self.progress_callback(message)

    @abstractmethod
    def generate(self, output_dir: str) -> GenerationResult:
        """
        Genera el código Angular

        Args:
            output_dir: Directorio de salida

        Returns:
            Resultado de la generación
        """
        pass

    def _create_component(self, component_name: str, output_dir: Path) -> List[str]:
        """
        Crea los archivos de un componente Angular

        Args:
            component_name: Nombre del componente
            output_dir: Directorio de salida

        Returns:
            Lista de archivos generados
        """
        files_created = []

        # Configuración
        style_ext = self.config.get('style_extension', 'scss')
        prefix = self.config.get('component_prefix', 'app')
        standalone = self.config.get('standalone', False)
        generate_tests = self.config.get('generate_tests', True)

        # Convertir nombre según convención
        naming = self.config.get('naming_convention', 'kebab-case')
        formatted_name = self._format_name(component_name, naming)

        # Directorio del componente
        component_dir = output_dir / formatted_name
        component_dir.mkdir(parents=True, exist_ok=True)

        # 1. TypeScript (.ts)
        ts_file = component_dir / f"{formatted_name}.component.ts"
        ts_content = self._generate_component_ts(formatted_name, prefix, standalone)
        ts_file.write_text(ts_content, encoding='utf-8')
        files_created.append(str(ts_file))

        # 2. Template (.html)
        html_file = component_dir / f"{formatted_name}.component.html"
        html_content = self._generate_component_html(formatted_name)
        html_file.write_text(html_content, encoding='utf-8')
        files_created.append(str(html_file))

        # 3. Styles
        style_file = component_dir / f"{formatted_name}.component.{style_ext}"
        style_content = self._generate_component_styles(formatted_name)
        style_file.write_text(style_content, encoding='utf-8')
        files_created.append(str(style_file))

        # 4. Tests (opcional)
        if generate_tests:
            spec_file = component_dir / f"{formatted_name}.component.spec.ts"
            spec_content = self._generate_component_spec(formatted_name, prefix)
            spec_file.write_text(spec_content, encoding='utf-8')
            files_created.append(str(spec_file))

        return files_created

    def _format_name(self, name: str, convention: str) -> str:
        """Formatea un nombre según la convención"""
        if convention == 'kebab-case':
            return name.lower().replace('_', '-')
        elif convention == 'camelCase':
            parts = name.split('_')
            return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])
        elif convention == 'PascalCase':
            return ''.join(p.capitalize() for p in name.split('_'))
        elif convention == 'snake_case':
            return name.lower()
        return name

    def _generate_component_ts(self, name: str, prefix: str, standalone: bool) -> str:
        """Genera el archivo TypeScript del componente"""
        class_name = ''.join(p.capitalize() for p in name.split('-'))

        imports = "import { Component"
        if standalone:
            imports += ", CommonModule"
        imports += " } from '@angular/core';"

        decorator = "@Component({\n"
        if standalone:
            decorator += "  standalone: true,\n"
            decorator += "  imports: [CommonModule],\n"
        decorator += f"  selector: '{prefix}-{name}',\n"
        decorator += f"  templateUrl: './{name}.component.html',\n"
        decorator += f"  styleUrls: ['./{name}.component.scss']\n"
        decorator += "})"

        return f"""{imports}

{decorator}
export class {class_name}Component {{
  constructor() {{
    // TODO: Initialize component
  }}

  ngOnInit(): void {{
    // TODO: Component initialization logic
  }}
}}
"""

    def _generate_component_html(self, name: str) -> str:
        """Genera el template HTML del componente"""
        display_name = ' '.join(p.capitalize() for p in name.split('-'))
        return f"""<div class="{name}-container">
  <h2>{display_name}</h2>
  <p>Component generated from Oracle Forms migration</p>
  <!-- TODO: Add component template -->
</div>
"""

    def _generate_component_styles(self, name: str) -> str:
        """Genera los estilos del componente"""
        return f""".{name}-container {{
  padding: 1rem;

  h2 {{
    color: #333;
    margin-bottom: 1rem;
  }}
}}
"""

    def _generate_component_spec(self, name: str, prefix: str) -> str:
        """Genera el archivo de tests del componente"""
        class_name = ''.join(p.capitalize() for p in name.split('-'))
        return f"""import {{ ComponentFixture, TestBed }} from '@angular/core/testing';
import {{ {class_name}Component }} from './{name}.component';

describe('{class_name}Component', () => {{
  let component: {class_name}Component;
  let fixture: ComponentFixture<{class_name}Component>;

  beforeEach(async () => {{
    await TestBed.configureTestingModule({{
      declarations: [ {class_name}Component ]
    }})
    .compileComponents();

    fixture = TestBed.createComponent({class_name}Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }});

  it('should create', () => {{
    expect(component).toBeTruthy();
  }});
}});
"""

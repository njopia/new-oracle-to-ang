#!/usr/bin/env python3
"""
Generador inteligente de componentes Angular
Usa el parser XML para generar código basado en la estructura real del formulario
"""

from pathlib import Path
from typing import Dict, Any, List
from ..parsers import OracleFormsParser, FormStructure, Item, Block


class SmartComponentGenerator:
    """Generador inteligente de componentes que parsea XMLs"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.parser = OracleFormsParser()

    def generate_component_from_xml(self, xml_file: str, output_dir: Path, component_name: str) -> List[str]:
        """
        Genera un componente Angular basado en el análisis del XML

        Args:
            xml_file: Ruta al archivo XML
            output_dir: Directorio de salida
            component_name: Nombre del componente

        Returns:
            Lista de archivos generados
        """
        # Parsear XML para obtener estructura
        form_structure = self.parser.parse_file(xml_file)

        # Generar archivos del componente
        files_created = []

        component_dir = output_dir / component_name
        component_dir.mkdir(parents=True, exist_ok=True)

        # 1. TypeScript component
        ts_file = component_dir / f"{component_name}.component.ts"
        ts_content = self._generate_smart_component_ts(component_name, form_structure)
        ts_file.write_text(ts_content, encoding='utf-8')
        files_created.append(str(ts_file))

        # 2. Template HTML
        html_file = component_dir / f"{component_name}.component.html"
        html_content = self._generate_smart_component_html(component_name, form_structure)
        html_file.write_text(html_content, encoding='utf-8')
        files_created.append(str(html_file))

        # 3. Styles
        style_ext = self.config.get('style_extension', 'scss')
        style_file = component_dir / f"{component_name}.component.{style_ext}"
        style_content = self._generate_smart_component_styles(component_name, form_structure)
        style_file.write_text(style_content, encoding='utf-8')
        files_created.append(str(style_file))

        # 4. Tests
        if self.config.get('generate_tests', True):
            spec_file = component_dir / f"{component_name}.component.spec.ts"
            spec_content = self._generate_component_spec(component_name)
            spec_file.write_text(spec_content, encoding='utf-8')
            files_created.append(str(spec_file))

        # 5. Model/Interface (si tiene items)
        if form_structure.get_all_items():
            model_file = component_dir / f"{component_name}.model.ts"
            model_content = self._generate_model(component_name, form_structure)
            model_file.write_text(model_content, encoding='utf-8')
            files_created.append(str(model_file))

        return files_created

    def _generate_smart_component_ts(self, name: str, form: FormStructure) -> str:
        """Genera TypeScript del componente con datos reales del formulario"""
        class_name = ''.join(p.capitalize() for p in name.split('-'))
        prefix = self.config.get('component_prefix', 'app')
        standalone = self.config.get('standalone', False)

        # Generar imports
        imports = ["import { Component, OnInit"]
        if standalone:
            imports[0] += ", CommonModule"
        imports[0] += " } from '@angular/core';"
        imports.append("import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';")

        if form.get_all_items():
            imports.append(f"import {{ {class_name}Model }} from './{name}.model';")

        imports_str = "\n".join(imports)

        # Generar decorator
        decorator_parts = []
        if standalone:
            decorator_parts.append("  standalone: true,")
            decorator_parts.append("  imports: [CommonModule, ReactiveFormsModule],")

        decorator_parts.append(f"  selector: '{prefix}-{name}',")
        decorator_parts.append(f"  templateUrl: './{name}.component.html',")
        decorator_parts.append(f"  styleUrls: ['./{name}.component.scss']")

        decorator = "@Component({\n" + "\n".join(decorator_parts) + "\n})"

        # Generar campos del formulario
        form_fields = []
        validators = []

        if form.blocks:
            main_block = form.blocks[0]  # Usar primer bloque como principal
            for item in main_block.items:
                field_name = self._camel_case(item.name)
                form_fields.append(f"  {field_name}: [''")

                # Agregar validadores según propiedades del item
                item_validators = []
                if item.required:
                    item_validators.append("Validators.required")
                if item.max_length > 0:
                    item_validators.append(f"Validators.maxLength({item.max_length})")

                if item_validators:
                    form_fields[-1] += f", [{', '.join(item_validators)}]"

                form_fields[-1] += "]"

        form_fields_str = ",\n    ".join(form_fields) if form_fields else ""

        # Generar propiedades basadas en bloques
        block_props = []
        for block in form.blocks:
            if block.query_data_source:
                block_props.append(f"  // Data source: {block.query_data_source}")

        block_props_str = "\n".join(block_props)

        # Generar métodos CRUD si el bloque lo permite
        crud_methods = []
        if form.blocks and form.blocks[0].insert_allowed:
            crud_methods.append(self._generate_save_method(class_name))
        if form.blocks and form.blocks[0].update_allowed:
            crud_methods.append(self._generate_update_method(class_name))
        if form.blocks and form.blocks[0].delete_allowed:
            crud_methods.append(self._generate_delete_method(class_name))

        crud_methods_str = "\n\n".join(crud_methods)

        return f"""{imports_str}

{decorator}
export class {class_name}Component implements OnInit {{
  {class_name.lower()}Form!: FormGroup;
  isLoading = false;
  errorMessage = '';

{block_props_str}

  constructor(private fb: FormBuilder) {{}}

  ngOnInit(): void {{
    this.initForm();
  }}

  private initForm(): void {{
    this.{class_name.lower()}Form = this.fb.group({{
      {form_fields_str}
    }});
  }}

{crud_methods_str}

  onSubmit(): void {{
    if (this.{class_name.lower()}Form.valid) {{
      console.log('Form data:', this.{class_name.lower()}Form.value);
      // TODO: Implement submit logic
    }}
  }}
}}
"""

    def _generate_smart_component_html(self, name: str, form: FormStructure) -> str:
        """Genera HTML del componente con campos reales"""
        display_name = ' '.join(p.capitalize() for p in name.split('-'))
        class_name = ''.join(p.capitalize() for p in name.split('-'))

        # Generar campos del formulario
        form_fields = []

        if form.blocks and form.blocks[0].items:
            for item in form.blocks[0].items:
                field_name = self._camel_case(item.name)
                label = item.prompt or item.name.replace('_', ' ').title()

                # Determinar tipo de input según tipo de item
                input_type = self._get_html_input_type(item)

                if input_type == 'checkbox':
                    form_fields.append(f"""
    <div class="form-check mb-3">
      <input
        type="checkbox"
        class="form-check-input"
        id="{field_name}"
        formControlName="{field_name}">
      <label class="form-check-label" for="{field_name}">
        {label}
      </label>
    </div>""")
                elif input_type == 'select' and item.lov_name:
                    form_fields.append(f"""
    <div class="mb-3">
      <label for="{field_name}" class="form-label">{label}</label>
      <select
        class="form-select"
        id="{field_name}"
        formControlName="{field_name}">
        <option value="">Seleccione...</option>
        <!-- TODO: Load options from {item.lov_name} -->
      </select>
      <div class="invalid-feedback">
        {label} es requerido
      </div>
    </div>""")
                else:
                    form_fields.append(f"""
    <div class="mb-3">
      <label for="{field_name}" class="form-label">{label}</label>
      <input
        type="{input_type}"
        class="form-control"
        id="{field_name}"
        formControlName="{field_name}"
        placeholder="{item.default_value or ''}"
        {f'maxlength="{item.max_length}"' if item.max_length > 0 else ''}>
      <div class="invalid-feedback">
        {label} es requerido
      </div>
    </div>""")

        form_fields_str = "\n".join(form_fields)

        return f"""<div class="{name}-container">
  <div class="card">
    <div class="card-header">
      <h2>{display_name}</h2>
      <p class="text-muted">Formulario migrado de Oracle Forms</p>
    </div>

    <div class="card-body">
      <form [formGroup]="{class_name.lower()}Form" (ngSubmit)="onSubmit()">
{form_fields_str}

        <div class="d-flex justify-content-end gap-2 mt-4">
          <button type="button" class="btn btn-secondary">
            Cancelar
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            [disabled]="{class_name.lower()}Form.invalid || isLoading">
            {{ isLoading ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
"""

    def _generate_smart_component_styles(self, name: str, form: FormStructure) -> str:
        """Genera estilos del componente"""
        return f""".{name}-container {{
  padding: 1.5rem;
  max-width: 800px;
  margin: 0 auto;

  .card {{
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

    .card-header {{
      background-color: #f8f9fa;
      border-bottom: 1px solid #dee2e6;
      padding: 1.5rem;

      h2 {{
        margin: 0;
        color: #333;
        font-size: 1.5rem;
      }}

      .text-muted {{
        margin: 0.25rem 0 0 0;
        font-size: 0.875rem;
      }}
    }}

    .card-body {{
      padding: 2rem;
    }}
  }}

  .form-label {{
    font-weight: 500;
    color: #495057;
  }}

  .form-control, .form-select {{
    &:focus {{
      border-color: #80bdff;
      box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
    }}
  }}

  .invalid-feedback {{
    display: none;
  }}

  .form-control.ng-invalid.ng-touched,
  .form-select.ng-invalid.ng-touched {{
    border-color: #dc3545;

    ~ .invalid-feedback {{
      display: block;
    }}
  }}

  .btn {{
    padding: 0.5rem 1.5rem;
    font-weight: 500;
  }}
}}
"""

    def _generate_model(self, name: str, form: FormStructure) -> str:
        """Genera el modelo TypeScript basado en los items del formulario"""
        class_name = ''.join(p.capitalize() for p in name.split('-'))

        if not form.blocks or not form.blocks[0].items:
            return f"""export interface {class_name}Model {{
  id?: number;
}}
"""

        # Generar propiedades del modelo
        properties = []
        for item in form.blocks[0].items:
            field_name = self._camel_case(item.name)
            ts_type = self._get_typescript_type(item.data_type)
            optional = "?" if not item.required else ""

            properties.append(f"  {field_name}{optional}: {ts_type};")

        properties_str = "\n".join(properties)

        return f"""export interface {class_name}Model {{
  id?: number;
{properties_str}
  createdAt?: Date;
  updatedAt?: Date;
}}
"""

    def _generate_component_spec(self, name: str) -> str:
        """Genera el archivo de tests"""
        class_name = ''.join(p.capitalize() for p in name.split('-'))
        return f"""import {{ ComponentFixture, TestBed }} from '@angular/core/testing';
import {{ ReactiveFormsModule }} from '@angular/forms';
import {{ {class_name}Component }} from './{name}.component';

describe('{class_name}Component', () => {{
  let component: {class_name}Component;
  let fixture: ComponentFixture<{class_name}Component>;

  beforeEach(async () => {{
    await TestBed.configureTestingModule({{
      declarations: [ {class_name}Component ],
      imports: [ ReactiveFormsModule ]
    }})
    .compileComponents();

    fixture = TestBed.createComponent({class_name}Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }});

  it('should create', () => {{
    expect(component).toBeTruthy();
  }});

  it('should initialize form', () => {{
    expect(component.{class_name.lower()}Form).toBeDefined();
  }});

  it('should validate required fields', () => {{
    expect(component.{class_name.lower()}Form.valid).toBeFalsy();
  }});
}});
"""

    # Métodos helper

    def _camel_case(self, name: str) -> str:
        """Convierte UPPER_CASE a camelCase"""
        parts = name.lower().split('_')
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])

    def _get_html_input_type(self, item: Item) -> str:
        """Determina el tipo de input HTML según el tipo de item"""
        if item.item_type == 'CHECKBOX':
            return 'checkbox'
        elif item.lov_name:
            return 'select'
        elif item.data_type == 'NUMBER':
            return 'number'
        elif item.data_type == 'DATE':
            return 'date'
        else:
            return 'text'

    def _get_typescript_type(self, data_type: str) -> str:
        """Mapea tipos de datos Oracle a TypeScript"""
        type_map = {
            'VARCHAR2': 'string',
            'CHAR': 'string',
            'NUMBER': 'number',
            'INTEGER': 'number',
            'FLOAT': 'number',
            'DATE': 'Date',
            'TIMESTAMP': 'Date',
            'BOOLEAN': 'boolean'
        }
        return type_map.get(data_type.upper(), 'string')

    def _generate_save_method(self, class_name: str) -> str:
        """Genera método save"""
        return f"""  save(): void {{
    if (this.{class_name.lower()}Form.valid) {{
      this.isLoading = true;
      // TODO: Implement save via API service
      console.log('Saving:', this.{class_name.lower()}Form.value);
      this.isLoading = false;
    }}
  }}"""

    def _generate_update_method(self, class_name: str) -> str:
        """Genera método update"""
        return f"""  update(id: number): void {{
    if (this.{class_name.lower()}Form.valid) {{
      this.isLoading = true;
      // TODO: Implement update via API service
      console.log('Updating:', id, this.{class_name.lower()}Form.value);
      this.isLoading = false;
    }}
  }}"""

    def _generate_delete_method(self, class_name: str) -> str:
        """Genera método delete"""
        return f"""  delete(id: number): void {{
    if (confirm('¿Está seguro de eliminar este registro?')) {{
      this.isLoading = true;
      // TODO: Implement delete via API service
      console.log('Deleting:', id);
      this.isLoading = false;
    }}
  }}"""

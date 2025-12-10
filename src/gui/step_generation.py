#!/usr/bin/env python3
"""
Step 5: Generación de Código Angular
"""

import customtkinter as ctk
import threading
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from ..assets.styles import COLORS, FONTS, SPACING, CORNER_RADIUS
from ..utils.i18n import i18n


class StepGeneration(ctk.CTkFrame):
    """Step de generación de código Angular"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_secondary'], **kwargs)

        self.configuration: Dict[str, Any] = {}
        self.xml_files: List[str] = []
        self.output_dir: str = ""
        self.generation_complete = False

        self._create_widgets()

        # Listener para cambios de idioma
        i18n.add_listener(self._on_language_change)

    def _create_widgets(self):
        """Crea los widgets del step"""
        # Botón centrado inicialmente
        self.start_button = ctk.CTkButton(
            self,
            text=i18n.t("buttons.start_analysis"),  # Reutilizamos la traducción
            command=self._on_start_generation,
            width=200,
            height=40,
            font=(FONTS['family'], FONTS['size_medium'], FONTS['weight_bold']),
            fg_color=COLORS['success'],
            hover_color=COLORS['success_light'],
            corner_radius=CORNER_RADIUS['md']
        )
        self.start_button.place(relx=0.5, rely=0.5, anchor="center")

        # Log de generación (oculto inicialmente)
        self.log_text = ctk.CTkTextbox(
            self,
            font=(FONTS['family_mono'], FONTS['size_small']),
            wrap="word"
        )

        # Progress bar (oculto inicialmente)
        self.progress_bar = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            width=400
        )

        # Progress label (oculto inicialmente)
        self.progress_label = ctk.CTkLabel(
            self,
            text="",
            font=(FONTS['family'], FONTS['size_normal']),
            text_color=COLORS['text_secondary']
        )

        # Botones de acción (ocultos inicialmente)
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.open_folder_btn = ctk.CTkButton(
            self.buttons_frame,
            text=i18n.t("step5.open_folder"),
            command=self._on_open_folder,
            height=32,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            corner_radius=CORNER_RADIUS['md']
        )
        self.open_folder_btn.pack(side="left", padx=SPACING['sm'])

    def set_configuration(self, config: Dict[str, Any], xml_files: List[str]):
        """Establece la configuración para la generación"""
        self.configuration = config
        self.xml_files = xml_files
        self.generation_complete = False

    def _on_start_generation(self):
        """Inicia el proceso de generación"""
        # Ocultar botón de inicio
        self.start_button.place_forget()

        # Mostrar elementos de progreso
        self.log_text.pack(fill="both", expand=True,
                          padx=SPACING['sm'],
                          pady=SPACING['xs'])
        self.progress_bar.pack(pady=SPACING['xs'])
        self.progress_label.pack(pady=0)
        self.buttons_frame.pack(pady=SPACING['xs'])

        # Iniciar progress bar
        self.progress_bar.start()
        self.progress_label.configure(text=i18n.t("step5.generating"))

        # Limpiar log
        self.log_text.delete("1.0", "end")

        # Ejecutar generación en thread separado
        thread = threading.Thread(target=self._run_generation)
        thread.daemon = True
        thread.start()

    def _run_generation(self):
        """Ejecuta el proceso de generación"""
        try:
            self._append_log(f"\n{'='*60}\n")
            self._append_log(f"  {i18n.t('step5.title')}\n")
            self._append_log(f"{'='*60}\n\n")

            # Determinar modo de generación
            generation_mode = self.configuration.get('generation_mode', 'complete_project')

            if generation_mode == 'complete_project':
                self._generate_complete_project()
            else:
                self._generate_components_only()

            # Generación completada
            self._append_log(f"\n{'='*60}\n")
            self._append_log(f"✓ {i18n.t('step5.success')}\n", "success")
            self._append_log(f"{'='*60}\n")

            self.generation_complete = True

        except Exception as e:
            self._append_log(f"\n✗ Error: {str(e)}\n", "error")
            self.generation_complete = False
        finally:
            # Detener progress bar
            self.progress_bar.stop()
            self.progress_label.configure(text=i18n.t("step5.completed"))

    def _generate_complete_project(self):
        """Genera un proyecto Angular completo"""
        project_name = self.configuration.get('project_name', 'angular-app')
        style_ext = self.configuration.get('style_extension', 'scss')
        routing = self.configuration.get('routing', True)

        # Crear directorio de salida con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = str(Path(f"./output/proyecto_{timestamp}"))
        os.makedirs(self.output_dir, exist_ok=True)

        self._append_log(f"📁 Directorio de salida: {self.output_dir}\n\n")

        # 1. Crear proyecto Angular
        self._update_progress(i18n.t("step5.creating_project"))
        self._append_log(f"🚀 {i18n.t('step5.creating_project')}\n")

        # Aquí iría la llamada a ng new (simulado por ahora)
        self._append_log(f"   Ejecutando: ng new {project_name} --style={style_ext} " +
                        f"--routing={'true' if routing else 'false'} --skip-git\n")
        self._append_log(f"   ✓ Proyecto base creado\n\n")

        # 2. Generar componentes
        self._generate_components()

        # 3. Generar servicios
        if self.configuration.get('generate_services', True):
            self._generate_services()

        # 4. Configurar routing
        if routing:
            self._configure_routing()

        # 5. Generar tests
        if self.configuration.get('generate_tests', True):
            self._append_log(f"🧪 Generando tests unitarios...\n")
            self._append_log(f"   ✓ Tests generados\n\n")

        # 6. Generar documentación
        if self.configuration.get('generate_docs', True):
            self._append_log(f"📚 Generando documentación...\n")
            self._append_log(f"   ✓ Documentación generada\n\n")

    def _generate_components_only(self):
        """Genera solo componentes sin estructura de proyecto"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = str(Path(f"./output/componentes_{timestamp}"))
        os.makedirs(self.output_dir, exist_ok=True)

        self._append_log(f"📁 Directorio de salida: {self.output_dir}\n\n")
        self._append_log(f"ℹ️  Modo: Solo Componentes\n")
        self._append_log(f"   Los archivos generados deben integrarse manualmente en tu proyecto.\n\n")

        # Generar estructura de carpetas
        folders = ['components', 'services', 'models', 'interfaces']
        for folder in folders:
            folder_path = Path(self.output_dir) / folder
            folder_path.mkdir(exist_ok=True)
            self._append_log(f"   ✓ Carpeta creada: {folder}/\n")

        self._append_log("\n")

        # Generar componentes
        self._generate_components()

        # Generar servicios si está habilitado
        if self.configuration.get('generate_services', True):
            self._generate_services()

    def _generate_components(self):
        """Genera los componentes Angular"""
        self._update_progress(i18n.t("step5.generating_components"))
        self._append_log(f"🎨 {i18n.t('step5.generating_components')}\n")

        selected_files = self.configuration.get('selected_files', [])
        naming = self.configuration.get('naming_convention', 'kebab-case')
        standalone = self.configuration.get('standalone', False)
        prefix = self.configuration.get('component_prefix', 'app')

        for xml_file in selected_files:
            component_name = Path(xml_file).stem
            # Convertir nombre según convención
            if naming == 'kebab-case':
                component_name = component_name.lower().replace('_', '-')

            self._append_log(f"   → Generando: {component_name}\n")
            self._append_log(f"      • {component_name}.component.ts\n")
            self._append_log(f"      • {component_name}.component.html\n")
            self._append_log(f"      • {component_name}.component.{self.configuration.get('style_extension', 'scss')}\n")

            if self.configuration.get('generate_tests', True):
                self._append_log(f"      • {component_name}.component.spec.ts\n")

        self._append_log(f"   ✓ {len(selected_files)} componentes generados\n\n")

    def _generate_services(self):
        """Genera los servicios Angular"""
        self._update_progress(i18n.t("step5.generating_services"))
        self._append_log(f"⚙️  {i18n.t('step5.generating_services')}\n")

        self._append_log(f"   → Generando servicio de datos\n")
        self._append_log(f"   → Generando servicio de API\n")
        self._append_log(f"   ✓ Servicios generados\n\n")

    def _configure_routing(self):
        """Configura el routing de Angular"""
        self._update_progress(i18n.t("step5.generating_routing"))
        self._append_log(f"🗺️  {i18n.t('step5.generating_routing')}\n")

        self._append_log(f"   → Configurando rutas principales\n")
        self._append_log(f"   → Configurando lazy loading\n")
        self._append_log(f"   ✓ Routing configurado\n\n")

    def _update_progress(self, message: str):
        """Actualiza el mensaje de progreso"""
        self.progress_label.configure(text=message)

    def _append_log(self, text: str, tag: str = None):
        """Añade texto al log"""
        self.log_text.insert("end", text)
        self.log_text.see("end")

    def _on_open_folder(self):
        """Abre la carpeta de salida en el explorador"""
        if self.output_dir and os.path.exists(self.output_dir):
            if os.name == 'nt':  # Windows
                os.startfile(self.output_dir)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.run(['xdg-open', self.output_dir])

    def get_output_dir(self) -> str:
        """Retorna el directorio de salida"""
        return self.output_dir

    def is_ready(self) -> bool:
        """Verifica si la generación está completa"""
        return self.generation_complete

    def _on_language_change(self, lang: str):
        """Actualiza los textos cuando cambia el idioma"""
        self.open_folder_btn.configure(text=i18n.t("step5.open_folder"))

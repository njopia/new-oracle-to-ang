#!/usr/bin/env python3
"""
Step 4: Configuración de Generación Angular
"""

import customtkinter as ctk
from typing import Dict, List, Any
from pathlib import Path

from ..assets.styles import COLORS, FONTS, SPACING, CORNER_RADIUS
from ..utils.i18n import i18n


class StepConfiguration(ctk.CTkFrame):
    """Step de configuración de generación Angular"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_secondary'], **kwargs)

        self.config_data: Dict[str, Any] = {
            'generation_mode': 'complete_project',  # 'complete_project' o 'components_only'
            'project_name': 'angular-app',
            'component_prefix': 'app',
            'style_extension': 'scss',
            'routing': True,
            'standalone': False,
            'naming_convention': 'kebab-case',
            'folder_structure': 'feature',
            'generate_tests': True,
            'generate_docs': True,
            'generate_services': True,
            'generate_guards': False,
            'selected_files': []
        }

        self.available_files: List[str] = []
        self.file_checkboxes: List[ctk.CTkCheckBox] = []

        self._create_widgets()

        # Listener para cambios de idioma
        i18n.add_listener(self._on_language_change)

    def _create_widgets(self):
        """Crea los widgets del step"""
        # Scrollable container (ultra compacto, sin scroll si cabe todo)
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scroll_container.pack(fill="both", expand=True, padx=SPACING['sm'], pady=SPACING['xs'])

        # Sección 1: Configuración de Proyecto (layout compacto en 2 columnas)
        self._create_project_section()

        # Sección 2: Opciones de Generación (inline, compacto)
        self._create_generation_section()

        # Sección 3: Selección de Componentes (compacto)
        self._create_components_section()

    def _create_project_section(self):
        """Crea la sección de configuración de proyecto"""
        section_frame = ctk.CTkFrame(
            self.scroll_container,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=CORNER_RADIUS['sm']
        )
        section_frame.pack(fill="x", pady=(0, SPACING['xs']))

        # Título de sección (ultra compacto)
        title = ctk.CTkLabel(
            section_frame,
            text=i18n.t("step4.project_config"),
            font=(FONTS['family'], FONTS['size_tiny'], FONTS['weight_bold']),
            text_color=COLORS['text_primary']
        )
        title.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], 0))

        # Grid de 2 columnas para aprovechar el espacio horizontal
        grid_container = ctk.CTkFrame(section_frame, fg_color="transparent")
        grid_container.pack(fill="x", padx=SPACING['xs'], pady=SPACING['xs'])

        # Columna izquierda
        left_column = ctk.CTkFrame(grid_container, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=SPACING['xs'])

        # Modo de generación (NUEVO - campo crítico al inicio)
        self._create_option_menu_with_mapping(
            left_column,
            i18n.t("step4.generation_mode"),
            "generation_mode",
            {
                i18n.t("step4.mode_complete"): "complete_project",
                i18n.t("step4.mode_components"): "components_only"
            }
        )

        self._create_input_field(left_column, i18n.t("step4.project_name"), "project_name", "angular-app")
        self._create_input_field(left_column, i18n.t("step4.component_prefix"), "component_prefix", "app")
        self._create_option_menu(left_column, i18n.t("step4.style_extension"), "style_extension", ["css", "scss", "sass", "less"])

        # Columna derecha
        right_column = ctk.CTkFrame(grid_container, fg_color="transparent")
        right_column.pack(side="left", fill="both", expand=True, padx=SPACING['xs'])

        self._create_option_menu(right_column, i18n.t("step4.naming_convention"), "naming_convention", ["kebab-case", "camelCase", "PascalCase", "snake_case"])
        self._create_option_menu(right_column, i18n.t("step4.folder_structure"), "folder_structure", ["feature", "type", "hybrid"])

    def _create_generation_section(self):
        """Crea la sección de opciones de generación"""
        section_frame = ctk.CTkFrame(
            self.scroll_container,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=CORNER_RADIUS['sm']
        )
        section_frame.pack(fill="x", pady=(0, SPACING['xs']))

        # Título de sección (ultra compacto)
        title = ctk.CTkLabel(
            section_frame,
            text=i18n.t("step4.generation_options"),
            font=(FONTS['family'], FONTS['size_tiny'], FONTS['weight_bold']),
            text_color=COLORS['text_primary']
        )
        title.pack(anchor="w", padx=SPACING['sm'], pady=(SPACING['xs'], 0))

        # Grid de 2 columnas para checkboxes
        grid_container = ctk.CTkFrame(section_frame, fg_color="transparent")
        grid_container.pack(fill="x", padx=SPACING['xs'], pady=SPACING['xs'])

        # Columna izquierda
        left_column = ctk.CTkFrame(grid_container, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=SPACING['xs'])

        self._create_checkbox(left_column, i18n.t("step4.routing"), "routing")
        self._create_checkbox(left_column, i18n.t("step4.generate_tests"), "generate_tests")
        self._create_checkbox(left_column, i18n.t("step4.generate_services"), "generate_services")

        # Columna derecha
        right_column = ctk.CTkFrame(grid_container, fg_color="transparent")
        right_column.pack(side="left", fill="both", expand=True, padx=SPACING['xs'])

        self._create_checkbox(right_column, i18n.t("step4.standalone"), "standalone")
        self._create_checkbox(right_column, i18n.t("step4.generate_docs"), "generate_docs")
        self._create_checkbox(right_column, i18n.t("step4.generate_guards"), "generate_guards")

    def _create_components_section(self):
        """Crea la sección de selección de componentes"""
        section_frame = ctk.CTkFrame(
            self.scroll_container,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=CORNER_RADIUS['sm']
        )
        section_frame.pack(fill="x", pady=0)

        # Título de sección con botones (ultra compacto)
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['sm'], pady=(SPACING['xs'], 0))

        title = ctk.CTkLabel(
            header_frame,
            text=i18n.t("step4.select_components"),
            font=(FONTS['family'], FONTS['size_tiny'], FONTS['weight_bold']),
            text_color=COLORS['text_primary']
        )
        title.pack(side="left")

        # Botones Seleccionar todos/ninguno (ultra compactos)
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.pack(side="right")

        select_all_btn = ctk.CTkButton(
            buttons_frame,
            text=i18n.t("step4.select_all"),
            command=self._select_all_files,
            width=60,
            height=22,
            font=(FONTS['family'], FONTS['size_tiny']),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark']
        )
        select_all_btn.pack(side="left", padx=SPACING['xs'])

        select_none_btn = ctk.CTkButton(
            buttons_frame,
            text=i18n.t("step4.select_none"),
            command=self._select_no_files,
            width=60,
            height=22,
            font=(FONTS['family'], FONTS['size_tiny']),
            fg_color=COLORS['error'],
            hover_color=COLORS['error_light']
        )
        select_none_btn.pack(side="left", padx=SPACING['xs'])

        # Container para checkboxes de archivos (ultra compacto)
        self.files_container = ctk.CTkFrame(
            section_frame,
            fg_color=COLORS['bg_primary'],
            corner_radius=CORNER_RADIUS['sm']
        )
        self.files_container.pack(fill="x", padx=SPACING['sm'], pady=SPACING['xs'])

        # Placeholder si no hay archivos
        self.no_files_label = ctk.CTkLabel(
            self.files_container,
            text=i18n.t("step4.no_files_analyzed"),
            font=(FONTS['family'], FONTS['size_small']),
            text_color=COLORS['text_secondary']
        )
        self.no_files_label.pack(pady=SPACING['md'])

    def _create_input_field(self, parent, label_text: str, config_key: str, placeholder: str):
        """Crea un campo de entrada con label"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=(0, SPACING['xs']))

        label = ctk.CTkLabel(
            container,
            text=label_text,
            font=(FONTS['family'], FONTS['size_tiny']),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        label.pack(anchor="w")

        entry = ctk.CTkEntry(
            container,
            placeholder_text=placeholder,
            height=26,
            font=(FONTS['family'], FONTS['size_small']),
            fg_color=COLORS['bg_primary'],
            border_color=COLORS['border']
        )
        entry.pack(fill="x", pady=(1, 0))
        entry.insert(0, self.config_data[config_key])

        # Bind para actualizar config_data
        entry.bind("<KeyRelease>", lambda e: self._update_config(config_key, entry.get()))

    def _create_option_menu(self, parent, label_text: str, config_key: str, options: List[str]):
        """Crea un menú de opciones con label"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=(0, SPACING['xs']))

        label = ctk.CTkLabel(
            container,
            text=label_text,
            font=(FONTS['family'], FONTS['size_tiny']),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        label.pack(anchor="w")

        option_menu = ctk.CTkOptionMenu(
            container,
            values=options,
            command=lambda value: self._update_config(config_key, value),
            height=26,
            font=(FONTS['family'], FONTS['size_small']),
            fg_color=COLORS['bg_primary'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_dark']
        )
        option_menu.pack(fill="x", pady=(1, 0))
        option_menu.set(self.config_data[config_key])

    def _create_option_menu_with_mapping(self, parent, label_text: str, config_key: str, options_map: Dict[str, str]):
        """
        Crea un menú de opciones con mapeo de valores display -> valores internos

        Args:
            parent: Widget padre
            label_text: Texto del label
            config_key: Key en config_data
            options_map: Dict con {display_value: internal_value}
        """
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=(0, SPACING['xs']))

        label = ctk.CTkLabel(
            container,
            text=label_text,
            font=(FONTS['family'], FONTS['size_tiny']),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        label.pack(anchor="w")

        # Crear reverse mapping para encontrar display value desde internal value
        reverse_map = {v: k for k, v in options_map.items()}
        display_values = list(options_map.keys())

        def on_select(display_value: str):
            internal_value = options_map[display_value]
            self._update_config(config_key, internal_value)

        option_menu = ctk.CTkOptionMenu(
            container,
            values=display_values,
            command=on_select,
            height=26,
            font=(FONTS['family'], FONTS['size_small']),
            fg_color=COLORS['bg_primary'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_dark']
        )
        option_menu.pack(fill="x", pady=(1, 0))

        # Set valor inicial usando reverse mapping
        current_internal = self.config_data[config_key]
        if current_internal in reverse_map:
            option_menu.set(reverse_map[current_internal])

    def _create_checkbox(self, parent, label_text: str, config_key: str):
        """Crea un checkbox con label"""
        checkbox = ctk.CTkCheckBox(
            parent,
            text=label_text,
            font=(FONTS['family'], FONTS['size_small']),
            text_color=COLORS['text_primary'],
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            border_color=COLORS['border'],
            command=lambda: self._update_config(config_key, checkbox.get())
        )
        checkbox.pack(anchor="w", pady=(0, SPACING['xs']))

        # Establecer valor inicial
        if self.config_data[config_key]:
            checkbox.select()

    def _update_config(self, key: str, value: Any):
        """Actualiza el diccionario de configuración"""
        self.config_data[key] = value

    def set_analyzed_files(self, files: List[str]):
        """Establece los archivos analizados para selección"""
        self.available_files = files

        # Limpiar checkboxes anteriores
        for checkbox in self.file_checkboxes:
            checkbox.destroy()
        self.file_checkboxes.clear()

        if files:
            # Ocultar placeholder
            self.no_files_label.pack_forget()

            # Crear checkbox para cada archivo (ultra compacto)
            for file_path in files:
                filename = Path(file_path).stem  # Solo el nombre sin extensión

                checkbox = ctk.CTkCheckBox(
                    self.files_container,
                    text=filename,
                    font=(FONTS['family'], FONTS['size_small']),
                    text_color=COLORS['text_primary'],
                    fg_color=COLORS['success'],
                    hover_color=COLORS['success_light'],
                    border_color=COLORS['border'],
                    command=self._update_selected_files
                )
                checkbox.pack(anchor="w", padx=SPACING['sm'], pady=(0, SPACING['xs']))
                checkbox.select()  # Seleccionado por defecto
                self.file_checkboxes.append(checkbox)

            # Actualizar archivos seleccionados
            self._update_selected_files()
        else:
            # Mostrar placeholder
            self.no_files_label.pack(pady=SPACING['xl'])

    def _update_selected_files(self):
        """Actualiza la lista de archivos seleccionados"""
        selected = []
        for i, checkbox in enumerate(self.file_checkboxes):
            if checkbox.get():
                selected.append(self.available_files[i])
        self.config_data['selected_files'] = selected

    def _select_all_files(self):
        """Selecciona todos los archivos"""
        for checkbox in self.file_checkboxes:
            checkbox.select()
        self._update_selected_files()

    def _select_no_files(self):
        """Deselecciona todos los archivos"""
        for checkbox in self.file_checkboxes:
            checkbox.deselect()
        self._update_selected_files()

    def get_configuration(self) -> Dict[str, Any]:
        """Retorna la configuración actual"""
        return self.config_data.copy()

    def is_ready(self) -> bool:
        """Verifica si la configuración está lista"""
        # Validar que haya al menos un archivo seleccionado
        if not self.config_data['selected_files']:
            return False

        # Validar que el nombre del proyecto no esté vacío
        if not self.config_data['project_name'].strip():
            return False

        return True

    def _on_language_change(self, lang: str):
        """Actualiza los textos cuando cambia el idioma"""
        # Recrear widgets con nuevos textos
        for widget in self.scroll_container.winfo_children():
            widget.destroy()
        self._create_widgets()

        # Restaurar archivos si había
        if self.available_files:
            self.set_analyzed_files(self.available_files)

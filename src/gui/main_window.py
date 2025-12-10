#!/usr/bin/env python3
"""
Ventana principal de la aplicación
"""

import customtkinter as ctk
from tkinter import messagebox

from ..assets.styles import COLORS, FONTS, SPACING, CORNER_RADIUS, WINDOW
from ..utils.i18n import i18n
from ..utils.config import config

from .stepper import Stepper
from .step_prerequisites import StepPrerequisites
from .step_file import StepFile
from .step_analysis import StepAnalysis
from .step_configuration import StepConfiguration


class MainWindow(ctk.CTk):
    """Ventana principal de la aplicación"""

    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.title(i18n.t("app.title"))
        self.geometry(f"{WINDOW['default_width']}x{WINDOW['default_height']}")
        self.minsize(WINDOW['min_width'], WINDOW['min_height'])
        self.resizable(True, True)

        # Configurar tema
        ctk.set_appearance_mode(config.get("ui.appearance_mode", "light"))
        ctk.set_default_color_theme("blue")

        # Variables
        self.current_language = config.get("app.language", "es")
        i18n.set_language(self.current_language)

        self._create_widgets()
        self._show_step(0)

        # Listener para cambios de idioma
        i18n.add_listener(self._on_language_change)

    def _create_widgets(self):
        """Crea los widgets de la ventana"""
        # Header ultra compacto
        header = ctk.CTkFrame(self, fg_color=COLORS['primary'], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Title y subtitle en una línea
        title_text = f"{i18n.t('app.title')} - {i18n.t('app.subtitle')}"
        title_label = ctk.CTkLabel(
            header,
            text=title_text,
            font=(FONTS['family'], FONTS['size_medium'], FONTS['weight_bold']),
            text_color=COLORS['text_white']
        )
        title_label.pack(pady=SPACING['sm'])

        # Language selector (top right) - Improved visibility
        lang_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )
        lang_frame.place(relx=0.98, rely=0.5, anchor="e")

        # Language icon/label
        lang_icon = ctk.CTkLabel(
            lang_frame,
            text="🌐",
            font=(FONTS['family'], 16),
            text_color=COLORS['text_white']
        )
        lang_icon.pack(side="left", padx=(0, SPACING['xs']))

        self.lang_selector = ctk.CTkSegmentedButton(
            lang_frame,
            values=["ES", "EN"],
            command=self._on_language_selected,

            # ESTILO ULTRA COMPACTO
            corner_radius=CORNER_RADIUS['sm'],
            height=28,
            width=100,

            # COLORES - Alto contraste para visibilidad
            fg_color=COLORS['bg_primary'],           # Fondo del contenedor
            selected_color=COLORS['text_white'],      # Botón activo blanco
            selected_hover_color=COLORS['hover'],
            unselected_color=COLORS['bg_primary'],    # Mismo color que fondo
            unselected_hover_color=COLORS['bg_tertiary'],
            text_color=COLORS['text_white']          # Texto blanco
        )
        self.lang_selector.pack(side="left")
        self.lang_selector.set("ES" if self.current_language == "es" else "EN")

        # Stepper ultra compacto
        self.stepper = Stepper(
            self,
            steps=["prerequisites", "file", "analysis", "configuration", "generation", "completed"],
            on_step_change=self._on_step_changed
        )
        self.stepper.pack(pady=SPACING['xs'])

        # Navigation buttons ARRIBA (después del stepper, antes del contenido)
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=(0, SPACING['xs']))

        self.back_button = ctk.CTkButton(
            nav_frame,
            text=i18n.t("buttons.back"),
            command=self._on_back,
            width=100,
            height=30,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS['primary'],
            text_color=COLORS['primary'],
            hover_color=COLORS['hover'],
            corner_radius=CORNER_RADIUS['md'],
            font=(FONTS['family'], FONTS['size_small'])
        )
        self.back_button.pack(side="left", padx=SPACING['sm'])

        self.next_button = ctk.CTkButton(
            nav_frame,
            text=i18n.t("buttons.next"),
            command=self._on_next,
            width=100,
            height=30,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            corner_radius=CORNER_RADIUS['md'],
            font=(FONTS['family'], FONTS['size_small'])
        )
        self.next_button.pack(side="left", padx=SPACING['sm'])

        # Content frame (ahora ocupa TODO el espacio restante)
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            orientation="vertical",
            scrollbar_button_color=COLORS['secondary'],
            scrollbar_button_hover_color=COLORS['primary']
        )
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Create steps
        self.steps = []

        # Step 1: Prerequisites
        self.step_prerequisites = StepPrerequisites(self.content_frame)
        self.steps.append(self.step_prerequisites)

        # Step 2: File
        self.step_file = StepFile(self.content_frame)
        self.steps.append(self.step_file)

        # Step 3: Analysis
        self.step_analysis = StepAnalysis(self.content_frame)
        self.steps.append(self.step_analysis)

        # Step 4: Configuration
        self.step_configuration = StepConfiguration(self.content_frame)
        self.steps.append(self.step_configuration)

    def _show_step(self, step_index: int):
        """Muestra el paso especificado"""
        # Ocultar todos los steps
        for step in self.steps:
            step.pack_forget()

        # Mostrar step actual
        if 0 <= step_index < len(self.steps):
            self.steps[step_index].pack(fill="both", expand=True)

        # Actualizar botones de navegación
        self.back_button.configure(state="normal" if step_index > 0 else "disabled")

        # El botón next se deshabilita en el último step implementado
        if step_index >= len(self.steps) - 1:
            self.next_button.configure(state="disabled")
        else:
            self.next_button.configure(state="normal")

    def _on_step_changed(self, step_index: int):
        """Callback cuando cambia el step en el stepper"""
        self._show_step(step_index)

    def _on_back(self):
        """Retrocede al paso anterior"""
        self.stepper.previous_step()

    def _on_next(self):
        """Avanza al siguiente paso"""
        current_step = self.stepper.get_current_step()

        # Validar que el step actual esté completo
        if current_step < len(self.steps):
            current_step_widget = self.steps[current_step]

            if hasattr(current_step_widget, 'is_ready') and not current_step_widget.is_ready():
                messagebox.showwarning(
                    i18n.t("messages.warning"),
                    self._get_step_warning_message(current_step)
                )
                return

            # Si es el step de archivo, pasar los archivos al step de análisis
            if current_step == 1:  # Step File
                files = self.step_file.get_selected_files()
                self.step_analysis.set_files(files)

            # Si es el step de análisis, pasar los archivos XML al step de configuración
            if current_step == 2:  # Step Analysis
                # Obtener archivos XML generados exitosamente
                xml_files = [
                    result.xml_file
                    for result in self.step_analysis.conversion_results
                    if result.success and result.xml_file
                ]
                self.step_configuration.set_analyzed_files(xml_files)

        self.stepper.next_step()

    def _get_step_warning_message(self, step_index: int) -> str:
        """Retorna el mensaje de advertencia para un step"""
        if step_index == 0:
            return "Please verify prerequisites first"
        elif step_index == 1:
            return i18n.t("errors.no_files_selected")
        elif step_index == 2:
            return "Please complete the analysis first"
        elif step_index == 3:
            return "Please configure the project settings and select at least one component"
        return "Please complete the current step"

    def _on_language_selected(self, value: str):
        """Maneja el cambio de idioma"""
        new_lang = "es" if value == "ES" else "en"
        if new_lang != self.current_language:
            self.current_language = new_lang
            i18n.set_language(new_lang)
            config.set("app.language", new_lang)
            config.save()

    def _on_language_change(self, lang: str):
        """Actualiza los textos cuando cambia el idioma"""
        self.title(i18n.t("app.title"))
        self.back_button.configure(text=i18n.t("buttons.back"))
        self.next_button.configure(text=i18n.t("buttons.next"))

    def run(self):
        """Ejecuta la aplicación"""
        self.mainloop()

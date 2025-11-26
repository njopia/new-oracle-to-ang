#!/usr/bin/env python3
"""
Step 1: Verificación de Prerequisitos
"""

import customtkinter as ctk
import threading

from ..assets.styles import COLORS, FONTS, SPACING, CORNER_RADIUS
from ..utils.i18n import i18n
from ..core.verificator import Verificator


class StepPrerequisites(ctk.CTkFrame):
    """Step de verificación de prerequisitos"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_secondary'], **kwargs)

        self.verificator = Verificator()
        self.results = {}

        self._create_widgets()

        # Listener para cambios de idioma
        i18n.add_listener(self._on_language_change)

    def _create_widgets(self):
        """Crea los widgets del step"""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=i18n.t("step1.title"),
            font=(FONTS['family'], FONTS['size_hero'], FONTS['weight_bold']),
            text_color=COLORS['primary']
        )
        self.title_label.pack(pady=(SPACING['xl'], SPACING['sm']))

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self,
            text=i18n.t("step1.subtitle"),
            font=(FONTS['family'], FONTS['size_medium']),
            text_color=COLORS['text_secondary']
        )
        self.subtitle_label.pack(pady=(0, SPACING['lg']))

        # Results frame
        self.results_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_primary'],
            corner_radius=CORNER_RADIUS['lg']
        )
        self.results_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['md'])

        # Results text area
        self.results_text = ctk.CTkTextbox(
            self.results_frame,
            font=(FONTS['family_mono'], FONTS['size_normal']),
            wrap="none"
        )
        self.results_text.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['md'])

        # Verify button
        self.verify_button = ctk.CTkButton(
            self,
            text=i18n.t("buttons.verify"),
            command=self._on_verify_clicked,
            height=40,
            font=(FONTS['family'], FONTS['size_medium'], FONTS['weight_bold']),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            corner_radius=CORNER_RADIUS['md']
        )
        self.verify_button.pack(pady=SPACING['lg'])

    def _on_verify_clicked(self):
        """Maneja el click del botón verificar"""
        self.verify_button.configure(state="disabled", text=i18n.t("step1.verifying"))
        self.results_text.delete("1.0", "end")

        # Ejecutar verificación en thread separado
        thread = threading.Thread(target=self._run_verification)
        thread.daemon = True
        thread.start()

    def _run_verification(self):
        """Ejecuta la verificación"""
        self._append_text(f"{i18n.t('step1.header')}\n")
        self._append_text("="*60 + "\n\n")

        # Verificar todos
        self.results = self.verificator.verify_all()

        self._append_text(f"● {i18n.t('step1.required')}\n")

        # Mostrar resultados
        for key, result in self.results.items():
            self._append_text(f"  ✓ {result.name} ", tag="bold")

            if result.found:
                if result.version:
                    self._append_text(f"{result.version}\n", tag="success")
                else:
                    self._append_text(f"{i18n.t('step1.found')}\n", tag="success")

                if result.path:
                    self._append_text(f"     {i18n.t('step1.path')} {result.path}\n", tag="info")
            else:
                self._append_text(f"{i18n.t('step1.not_found')}\n", tag="error")
                if result.message:
                    self._append_text(f"     {result.message}\n", tag="warning")

            self._append_text("\n")

        # Resumen
        self._append_text("\n" + "="*60 + "\n")
        if self.verificator.all_required_ok():
            self._append_text(f"{i18n.t('step1.all_ok')}\n", tag="success")
        else:
            self._append_text(f"{i18n.t('step1.some_missing')}\n", tag="warning")

        # Rehabilitar botón
        self.verify_button.configure(state="normal", text=i18n.t("buttons.verify"))

    def _append_text(self, text: str, tag: str = None):
        """Añade texto al textbox"""
        self.results_text.insert("end", text)
        self.results_text.see("end")

    def is_ready(self) -> bool:
        """Verifica si se puede avanzar al siguiente paso"""
        return self.verificator.all_required_ok()

    def _on_language_change(self, lang: str):
        """Actualiza los textos cuando cambia el idioma"""
        self.title_label.configure(text=i18n.t("step1.title"))
        self.subtitle_label.configure(text=i18n.t("step1.subtitle"))
        if self.verify_button.cget("state") == "normal":
            self.verify_button.configure(text=i18n.t("buttons.verify"))

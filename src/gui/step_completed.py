#!/usr/bin/env python3
"""
Step 6: Migración Completada
"""

import customtkinter as ctk
import subprocess
import os
from pathlib import Path
from typing import Dict, Any

from ..assets.styles import COLORS, FONTS, SPACING, CORNER_RADIUS
from ..utils.i18n import i18n


class StepCompleted(ctk.CTkFrame):
    """Step de migración completada"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_secondary'], **kwargs)

        self.output_dir: str = ""
        self.report_path: str = ""
        self.stats: Dict[str, Any] = {}

        self._create_widgets()

        # Listener para cambios de idioma
        i18n.add_listener(self._on_language_change)

    def _create_widgets(self):
        """Crea los widgets del step"""
        # Contenedor principal con scroll
        scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        scroll_container.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['sm'])

        # Success Icon y título
        success_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        success_frame.pack(pady=SPACING['md'])

        success_icon = ctk.CTkLabel(
            success_frame,
            text="✅",
            font=(FONTS['family'], 48)
        )
        success_icon.pack()

        title = ctk.CTkLabel(
            success_frame,
            text=i18n.t("step6.title"),
            font=(FONTS['family'], FONTS['size_large'], FONTS['weight_bold']),
            text_color=COLORS['success']
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            success_frame,
            text=i18n.t("step6.subtitle"),
            font=(FONTS['family'], FONTS['size_normal']),
            text_color=COLORS['text_secondary']
        )
        subtitle.pack(pady=(SPACING['xs'], 0))

        # Sección de estadísticas
        stats_section = self._create_stats_section(scroll_container)
        stats_section.pack(fill="x", pady=SPACING['md'])

        # Sección de ubicación
        location_section = self._create_location_section(scroll_container)
        location_section.pack(fill="x", pady=SPACING['sm'])

        # Sección de próximos pasos
        next_steps_section = self._create_next_steps_section(scroll_container)
        next_steps_section.pack(fill="x", pady=SPACING['sm'])

        # Botones de acción
        actions_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        actions_frame.pack(pady=SPACING['md'])

        self.open_folder_btn = ctk.CTkButton(
            actions_frame,
            text=i18n.t("step6.open_folder"),
            command=self._on_open_folder,
            height=40,
            width=200,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            corner_radius=CORNER_RADIUS['md'],
            font=(FONTS['family'], FONTS['size_normal'], FONTS['weight_bold'])
        )
        self.open_folder_btn.pack(side="left", padx=SPACING['sm'])

        self.view_report_btn = ctk.CTkButton(
            actions_frame,
            text=i18n.t("step6.view_report"),
            command=self._on_view_report,
            height=40,
            width=200,
            fg_color=COLORS['info'],
            hover_color=COLORS['hover'],
            corner_radius=CORNER_RADIUS['md'],
            font=(FONTS['family'], FONTS['size_normal'], FONTS['weight_bold'])
        )
        self.view_report_btn.pack(side="left", padx=SPACING['sm'])

    def _create_stats_section(self, parent) -> ctk.CTkFrame:
        """Crea la sección de estadísticas"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=CORNER_RADIUS['md']
        )

        title = ctk.CTkLabel(
            section,
            text=i18n.t("step6.summary"),
            font=(FONTS['family'], FONTS['size_medium'], FONTS['weight_bold']),
            text_color=COLORS['text_primary']
        )
        title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['xs']))

        # Grid de estadísticas
        stats_grid = ctk.CTkFrame(section, fg_color="transparent")
        stats_grid.pack(fill="x", padx=SPACING['md'], pady=SPACING['sm'])

        # Crear tarjetas de estadísticas
        self.total_forms_label = self._create_stat_card(
            stats_grid,
            i18n.t("step6.total_forms"),
            "0",
            0, 0
        )

        self.components_label = self._create_stat_card(
            stats_grid,
            i18n.t("step6.components_generated"),
            "0",
            0, 1
        )

        self.services_label = self._create_stat_card(
            stats_grid,
            i18n.t("step6.services_generated"),
            "0",
            0, 2
        )

        return section

    def _create_stat_card(self, parent, label: str, value: str, row: int, col: int) -> ctk.CTkLabel:
        """Crea una tarjeta de estadística"""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_primary'],
            corner_radius=CORNER_RADIUS['sm']
        )
        card.grid(row=row, column=col, padx=SPACING['sm'], pady=SPACING['xs'], sticky="ew")

        parent.grid_columnconfigure(col, weight=1)

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=(FONTS['family'], FONTS['size_xlarge'], FONTS['weight_bold']),
            text_color=COLORS['primary']
        )
        value_label.pack(pady=(SPACING['sm'], 0))

        text_label = ctk.CTkLabel(
            card,
            text=label,
            font=(FONTS['family'], FONTS['size_small']),
            text_color=COLORS['text_secondary']
        )
        text_label.pack(pady=(0, SPACING['sm']))

        return value_label

    def _create_location_section(self, parent) -> ctk.CTkFrame:
        """Crea la sección de ubicación"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=CORNER_RADIUS['md']
        )

        title = ctk.CTkLabel(
            section,
            text=i18n.t("step6.output_location"),
            font=(FONTS['family'], FONTS['size_small'], FONTS['weight_bold']),
            text_color=COLORS['text_primary']
        )
        title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['xs']))

        self.location_label = ctk.CTkLabel(
            section,
            text="",
            font=(FONTS['family_mono'], FONTS['size_small']),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        self.location_label.pack(anchor="w", padx=SPACING['md'], pady=(0, SPACING['sm']))

        return section

    def _create_next_steps_section(self, parent) -> ctk.CTkFrame:
        """Crea la sección de próximos pasos"""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=CORNER_RADIUS['md']
        )

        title = ctk.CTkLabel(
            section,
            text=i18n.t("step6.next_steps"),
            font=(FONTS['family'], FONTS['size_small'], FONTS['weight_bold']),
            text_color=COLORS['text_primary']
        )
        title.pack(anchor="w", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['xs']))

        steps = [
            ("1", i18n.t("step6.step_install")),
            ("2", i18n.t("step6.step_serve")),
            ("3", i18n.t("step6.step_test")),
            ("4", i18n.t("step6.step_build"))
        ]

        for num, step_text in steps:
            step_frame = ctk.CTkFrame(section, fg_color="transparent")
            step_frame.pack(fill="x", padx=SPACING['md'], pady=SPACING['xs'])

            number_label = ctk.CTkLabel(
                step_frame,
                text=num,
                font=(FONTS['family'], FONTS['size_normal'], FONTS['weight_bold']),
                text_color=COLORS['primary'],
                width=30
            )
            number_label.pack(side="left")

            text_label = ctk.CTkLabel(
                step_frame,
                text=step_text,
                font=(FONTS['family_mono'], FONTS['size_small']),
                text_color=COLORS['text_secondary'],
                anchor="w"
            )
            text_label.pack(side="left", fill="x", expand=True)

        # Añadir espacio al final
        ctk.CTkLabel(section, text="", height=SPACING['sm']).pack()

        return section

    def set_results(self, output_dir: str, report_path: str, stats: Dict[str, Any]):
        """Establece los resultados de la migración"""
        self.output_dir = output_dir
        self.report_path = report_path
        self.stats = stats

        # Actualizar estadísticas
        self.total_forms_label.configure(text=str(stats.get('total_forms', 0)))
        self.components_label.configure(text=str(stats.get('components_generated', 0)))
        self.services_label.configure(text=str(stats.get('services_generated', 0)))

        # Actualizar ubicación
        self.location_label.configure(text=output_dir)

    def _on_open_folder(self):
        """Abre la carpeta de salida"""
        if self.output_dir and os.path.exists(self.output_dir):
            if os.name == 'nt':  # Windows
                os.startfile(self.output_dir)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.run(['xdg-open', self.output_dir])

    def _on_view_report(self):
        """Abre el reporte HTML"""
        if self.report_path and os.path.exists(self.report_path):
            if os.name == 'nt':  # Windows
                os.startfile(self.report_path)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.run(['xdg-open', self.report_path])

    def is_ready(self) -> bool:
        """Siempre está listo (es el último step)"""
        return True

    def _on_language_change(self, lang: str):
        """Actualiza los textos cuando cambia el idioma"""
        self.open_folder_btn.configure(text=i18n.t("step6.open_folder"))
        self.view_report_btn.configure(text=i18n.t("step6.view_report"))

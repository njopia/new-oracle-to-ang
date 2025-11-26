#!/usr/bin/env python3
"""
Step 2: Carga de Archivos
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from typing import List

from ..assets.styles import COLORS, FONTS, SPACING, CORNER_RADIUS
from ..utils.i18n import i18n


class StepFile(ctk.CTkFrame):
    """Step de carga de archivos"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_secondary'], **kwargs)

        self.selected_files: List[str] = []

        self._create_widgets()

        # Listener para cambios de idioma
        i18n.add_listener(self._on_language_change)

    def _create_widgets(self):
        """Crea los widgets del step"""
        # Title
    
        # Drop area
        self.drop_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_primary'],
            border_width=2,
            border_color=COLORS['primary'],
            corner_radius=CORNER_RADIUS['lg'],
            height=150
        )
        self.drop_frame.pack(fill="x", padx=SPACING['xl'], pady=SPACING['md'])

        self.drop_label = ctk.CTkLabel(
            self.drop_frame,
            text=i18n.t("step2.drag_drop"),
            font=(FONTS['family'], FONTS['size_large']),
            text_color=COLORS['text_secondary']
        )
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        # Make drop frame clickable
        self.drop_frame.bind("<Button-1>", lambda e: self._on_add_files())
        self.drop_label.bind("<Button-1>", lambda e: self._on_add_files())

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(pady=SPACING['md'])

        self.add_button = ctk.CTkButton(
            buttons_frame,
            text=i18n.t("buttons.add_files"),
            command=self._on_add_files,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            corner_radius=CORNER_RADIUS['md']
        )
        self.add_button.pack(side="left", padx=SPACING['sm'])

        self.clear_button = ctk.CTkButton(
            buttons_frame,
            text=i18n.t("buttons.clear_all"),
            command=self._on_clear_all,
            fg_color=COLORS['error'],
            hover_color=COLORS['error_light'],
            corner_radius=CORNER_RADIUS['md']
        )
        self.clear_button.pack(side="left", padx=SPACING['sm'])

        # Files list frame
        files_label = ctk.CTkLabel(
            self,
            text=i18n.t("step2.selected_files"),
            font=(FONTS['family'], FONTS['size_large'], FONTS['weight_bold']),
            text_color=COLORS['text_primary']
        )
        files_label.pack(pady=(SPACING['lg'], SPACING['sm']))

        self.files_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_primary'],
            corner_radius=CORNER_RADIUS['lg']
        )
        self.files_frame.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['md'])

        self._update_files_list()

    def _on_add_files(self):
        """Abre diálogo para seleccionar archivos"""
        files = filedialog.askopenfilenames(
            title=i18n.t("step2.title"),
            filetypes=[
                ("Oracle Forms", "*.fmb"),
                ("All files", "*.*")
            ]
        )

        for file in files:
            if file and file not in self.selected_files:
                self.selected_files.append(file)

        self._update_files_list()

    def _on_remove_file(self, file_path: str):
        """Elimina un archivo de la lista"""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            self._update_files_list()

    def _on_clear_all(self):
        """Limpia todos los archivos"""
        self.selected_files.clear()
        self._update_files_list()

    def _update_files_list(self):
        """Actualiza la visualización de la lista de archivos"""
        # Limpiar frame
        for widget in self.files_frame.winfo_children():
            widget.destroy()

        if not self.selected_files:
            no_files_label = ctk.CTkLabel(
                self.files_frame,
                text=i18n.t("step2.no_files"),
                font=(FONTS['family'], FONTS['size_medium']),
                text_color=COLORS['text_secondary']
            )
            no_files_label.pack(pady=SPACING['xl'])
        else:
            for file_path in self.selected_files:
                file_frame = ctk.CTkFrame(
                    self.files_frame,
                    fg_color=COLORS['bg_tertiary'],
                    corner_radius=CORNER_RADIUS['md']
                )
                file_frame.pack(fill="x", pady=SPACING['xs'], padx=SPACING['sm'])

                # File name
                file_name = Path(file_path).name
                name_label = ctk.CTkLabel(
                    file_frame,
                    text=f"📄 {file_name}",
                    font=(FONTS['family'], FONTS['size_normal']),
                    anchor="w"
                )
                name_label.pack(side="left", padx=SPACING['md'], pady=SPACING['sm'], fill="x", expand=True)

                # Remove button
                remove_btn = ctk.CTkButton(
                    file_frame,
                    text="✕",
                    width=30,
                    height=30,
                    command=lambda f=file_path: self._on_remove_file(f),
                    fg_color=COLORS['error'],
                    hover_color=COLORS['error_light'],
                    corner_radius=CORNER_RADIUS['round']
                )
                remove_btn.pack(side="right", padx=SPACING['sm'])

    def get_selected_files(self) -> List[str]:
        """Retorna la lista de archivos seleccionados"""
        return self.selected_files.copy()

    def is_ready(self) -> bool:
        """Verifica si se puede avanzar al siguiente paso"""
        return len(self.selected_files) > 0

    def _on_language_change(self, lang: str):
        """Actualiza los textos cuando cambia el idioma"""
        self.drop_label.configure(text=i18n.t("step2.drag_drop"))
        self.add_button.configure(text=i18n.t("buttons.add_files"))
        self.clear_button.configure(text=i18n.t("buttons.clear_all"))

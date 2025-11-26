#!/usr/bin/env python3
"""
Widget Stepper personalizado para CustomTkinter
"""

import customtkinter as ctk
from typing import List, Callable, Optional

from ..assets.styles import COLORS, FONTS, SIZES, SPACING
from ..utils.i18n import i18n


class Stepper(ctk.CTkFrame):
    """Widget Stepper horizontal para navegación por pasos"""

    def __init__(
        self,
        master,
        steps: List[str],
        on_step_change: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.steps = steps
        self.current_step = 0
        self.on_step_change = on_step_change
        self.completed_steps = set()

        self._create_widgets()
        self._update_appearance()

        # Listener para cambios de idioma
        i18n.add_listener(self._on_language_change)

    def _create_widgets(self):
        """Crea los widgets del stepper"""
        self.step_frames = []
        self.step_circles = []
        self.step_labels = []
        self.step_lines = []

        for i, step in enumerate(self.steps):
            # Frame contenedor para cada paso
            step_frame = ctk.CTkFrame(self, fg_color="transparent")
            step_frame.grid(row=0, column=i*2, padx=SPACING['sm'], pady=SPACING['md'])
            self.step_frames.append(step_frame)

            # Círculo del paso
            circle_size = SIZES['stepper_circle']
            circle = ctk.CTkLabel(
                step_frame,
                text=str(i+1),
                width=circle_size,
                height=circle_size,
                corner_radius=circle_size//2,
                font=(FONTS['family'], FONTS['size_medium'], FONTS['weight_bold'])
            )
            circle.pack()
            self.step_circles.append(circle)

            # Label del paso
            label = ctk.CTkLabel(
                step_frame,
                text=i18n.t(f"steps.{step}"),
                font=(FONTS['family'], FONTS['size_small'])
            )
            label.pack(pady=(SPACING['xs'], 0))
            self.step_labels.append(label)

            # Línea conectora (excepto después del último paso)
            if i < len(self.steps) - 1:
                line = ctk.CTkFrame(
                    self,
                    height=SIZES['stepper_line_height'],
                    width=60,
                    fg_color=COLORS['stepper_line']
                )
                line.grid(row=0, column=i*2+1, sticky="ew", pady=SPACING['lg'])
                self.step_lines.append(line)

    def _update_appearance(self):
        """Actualiza la apariencia según el paso actual"""
        for i, (circle, label) in enumerate(zip(self.step_circles, self.step_labels)):
            if i < self.current_step or i in self.completed_steps:
                # Paso completado
                circle.configure(
                    fg_color=COLORS['stepper_completed'],
                    text_color=COLORS['text_white'],
                    text="✓"
                )
                label.configure(text_color=COLORS['stepper_completed'])
            elif i == self.current_step:
                # Paso actual
                circle.configure(
                    fg_color=COLORS['stepper_active'],
                    text_color=COLORS['text_white'],
                    text=str(i+1)
                )
                label.configure(text_color=COLORS['stepper_active'])
            else:
                # Paso pendiente
                circle.configure(
                    fg_color=COLORS['stepper_pending'],
                    text_color=COLORS['text_white'],
                    text=str(i+1)
                )
                label.configure(text_color=COLORS['stepper_pending'])

        # Actualizar líneas
        for i, line in enumerate(self.step_lines):
            if i < self.current_step:
                line.configure(fg_color=COLORS['stepper_completed'])
            else:
                line.configure(fg_color=COLORS['stepper_line'])

    def set_step(self, step: int):
        """Cambia al paso especificado"""
        if 0 <= step < len(self.steps):
            self.current_step = step
            self._update_appearance()

            if self.on_step_change:
                self.on_step_change(step)

    def next_step(self):
        """Avanza al siguiente paso"""
        if self.current_step < len(self.steps) - 1:
            self.completed_steps.add(self.current_step)
            self.set_step(self.current_step + 1)

    def previous_step(self):
        """Retrocede al paso anterior"""
        if self.current_step > 0:
            self.set_step(self.current_step - 1)

    def mark_as_completed(self, step: int):
        """Marca un paso como completado"""
        if 0 <= step < len(self.steps):
            self.completed_steps.add(step)
            self._update_appearance()

    def get_current_step(self) -> int:
        """Retorna el índice del paso actual"""
        return self.current_step

    def _on_language_change(self, lang: str):
        """Actualiza los textos cuando cambia el idioma"""
        for i, label in enumerate(self.step_labels):
            label.configure(text=i18n.t(f"steps.{self.steps[i]}"))

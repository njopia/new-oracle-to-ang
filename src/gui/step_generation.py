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
from ..core.generators import AngularProjectGenerator, ComponentsOnlyGenerator
from ..core.verificator import Verificator


class StepGeneration(ctk.CTkFrame):
    """Step de generación de código Angular"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_secondary'], **kwargs)

        self.configuration: Dict[str, Any] = {}
        self.xml_files: List[str] = []
        self.output_dir: str = ""
        self.generation_complete = False
        self.verificator = Verificator()
        self.installing_cli = False

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

            # Verificar prerequisitos antes de generar
            generation_mode = self.configuration.get('generation_mode', 'complete_project')

            # Solo verificar Angular CLI en modo proyecto completo
            if generation_mode == 'complete_project':
                self._append_log("🔍 Verificando prerequisitos...\n")
                cli_check = self.verificator.verify_angular_cli()

                if not cli_check.found:
                    self._append_log("\n⚠️  Angular CLI no está instalado\n")
                    self._append_log("━" * 60 + "\n\n")
                    self._append_log("🔧 Instalando Angular CLI automáticamente...\n\n")

                    # Instalar automáticamente SIN PREGUNTAR
                    self.installing_cli = True
                    self.progress_label.configure(text="⏳ Instalando Angular CLI...")

                    def log_callback(text):
                        self._append_log(text)

                    # Ejecutar instalación directamente
                    success, message = self.verificator.install_angular_cli(callback=log_callback)

                    if not success:
                        self._append_log(f"\n{'='*60}\n")
                        self._append_log("❌ ERROR EN LA INSTALACIÓN\n")
                        self._append_log(f"{'='*60}\n")
                        self._append_log(f"\n{message}\n\n")
                        self.installing_cli = False
                        self.progress_bar.stop()
                        self.progress_label.configure(text="❌ Error en instalación")
                        return

                    # Instalación exitosa, continuar
                    self._append_log(f"\n{'='*60}\n")
                    self._append_log("✅ Angular CLI instalado correctamente\n")
                    self._append_log(f"{'='*60}\n\n")
                    self.installing_cli = False

                    # Re-verificar
                    cli_check = self.verificator.verify_angular_cli()
                    if cli_check.found:
                        self._append_log(f"✓ Angular CLI {cli_check.version} verificado\n\n")
                    else:
                        self._append_log("⚠️ Angular CLI instalado pero requiere reinicio de la aplicación\n")
                        self.progress_bar.stop()
                        self.progress_label.configure(text="⚠️ Reinicia la aplicación")
                        return
                else:
                    self._append_log(f"✓ Angular CLI {cli_check.version} detectado\n\n")

            # Crear directorio de salida con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if generation_mode == 'complete_project':
                self.output_dir = str(Path(f"./output/proyecto_{timestamp}"))
                generator = AngularProjectGenerator(self.configuration, self.xml_files)
            else:
                self.output_dir = str(Path(f"./output/componentes_{timestamp}"))
                generator = ComponentsOnlyGenerator(self.configuration, self.xml_files)

            # Configurar callbacks
            generator.set_log_callback(self._append_log)
            generator.set_progress_callback(self._update_progress)

            # Ejecutar generación
            result = generator.generate(self.output_dir)

            if result.success:
                self._append_log(f"\n{'='*60}\n")
                self._append_log(f"✓ {i18n.t('step5.success')}\n")
                self._append_log(f"📁 Directorio: {result.output_dir}\n")
                self._append_log(f"📄 Archivos generados: {len(result.files_generated)}\n")
                self._append_log(f"{'='*60}\n")
                self.generation_complete = True
                # Actualizar output_dir con el real del generador
                self.output_dir = result.output_dir
            else:
                self._append_log(f"\n{'='*60}\n")
                self._append_log(f"✗ Error: {result.error_message}\n")
                self._append_log(f"{'='*60}\n")
                self.generation_complete = False

        except Exception as e:
            self._append_log(f"\n✗ Error: {str(e)}\n")
            import traceback
            self._append_log(f"{traceback.format_exc()}\n")
            self.generation_complete = False
        finally:
            # Detener progress bar si aún está corriendo
            if self.progress_bar.cget("mode") == "indeterminate":
                self.progress_bar.stop()
            if not self.installing_cli:
                self.progress_label.configure(text=i18n.t("step5.completed"))

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

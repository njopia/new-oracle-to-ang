#!/usr/bin/env python3
"""
Step 3: Análisis y Conversión
"""

import customtkinter as ctk
import threading
import webbrowser
from typing import List

from ..assets.styles import COLORS, FONTS, SPACING, CORNER_RADIUS
from ..utils.i18n import i18n
from ..core.converter import Converter
from ..core.analyzer import Analyzer
from ..core.report_generator import ReportGenerator


class StepAnalysis(ctk.CTkFrame):
    """Step de análisis y conversión"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS['bg_secondary'], **kwargs)

        self.converter = Converter()
        self.analyzer = Analyzer()
        self.report_generator = ReportGenerator()

        self.files_to_convert: List[str] = []
        self.conversion_results = []
        self.analysis_metrics = []
        self.report_path = None
        self.is_analyzing = False

        self._create_widgets()

        # Listener para cambios de idioma
        i18n.add_listener(self._on_language_change)

    def _create_widgets(self):
        """Crea los widgets del step"""
        # Title
      

        self.log_text = ctk.CTkTextbox(
            self,
            font=(FONTS['family_mono'], FONTS['size_small']),
            wrap="none"
        )
        self.log_text.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['md'])
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=400,
            height=20,
            corner_radius=CORNER_RADIUS['md']
        )
        self.progress_bar.pack(pady=SPACING['md'])
        self.progress_bar.set(0)

        # Progress label
        self.progress_label = ctk.CTkLabel(
            self,
            text="",
            font=(FONTS['family'], FONTS['size_normal']),
            text_color=COLORS['text_secondary']
        )
        self.progress_label.pack()
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(pady=SPACING['lg'])

        self.start_button = ctk.CTkButton(
            buttons_frame,
            text=i18n.t("buttons.start_analysis"),
            command=self._on_start_analysis,
            height=40,
            width=180,
            font=(FONTS['family'], FONTS['size_medium'], FONTS['weight_bold']),
            fg_color=COLORS['success'],
            hover_color=COLORS['success_light'],
            corner_radius=CORNER_RADIUS['md']
        )
        self.start_button.pack(side="left", padx=SPACING['sm'])

        self.report_button = ctk.CTkButton(
            buttons_frame,
            text=i18n.t("buttons.open_report"),
            command=self._on_open_report,
            height=40,
            width=180,
            font=(FONTS['family'], FONTS['size_medium'], FONTS['weight_bold']),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            corner_radius=CORNER_RADIUS['md'],
            state="disabled"
        )
        self.report_button.pack(side="left", padx=SPACING['sm'])

    def set_files(self, files: List[str]):
        """Establece los archivos a convertir"""
        self.files_to_convert = files

    def _on_start_analysis(self):
        """Inicia el análisis"""
        if not self.files_to_convert:
            self._log("❌ " + i18n.t("errors.no_files_selected"))
            return

        if self.is_analyzing:
            return

        self.is_analyzing = True
        self.start_button.configure(state="disabled")
        self.log_text.delete("1.0", "end")
        self.progress_bar.set(0)

        # Ejecutar en thread separado
        thread = threading.Thread(target=self._run_analysis)
        thread.daemon = True
        thread.start()

    def _run_analysis(self):
        """Ejecuta el análisis completo"""
        # Limpiar resultados anteriores
        self.converter.clear_results()

        total_files = len(self.files_to_convert)
        self._log(f"{'converte: '}{self.converter.temp_dir}\n")
        self._log(f"{'='*60}\n")
        self._log(f"📦 {i18n.t('step3.total_files')}: {total_files}\n")
        self._log(f"{'='*60}\n\n")

        # Fase 1: Conversión
        self._log(f"🔄 {i18n.t('step3.converting')}\n\n")

        self.conversion_results = []
        for i, file_path in enumerate(self.files_to_convert, 1):
            progress = i / total_files
            self.progress_bar.set(progress)
            self.progress_label.configure(text=f"{i}/{total_files}")

            self._log(f"[{i}/{total_files}] Converting: {file_path}\n")

            result = self.converter.convert_file(file_path)
            self.conversion_results.append(result)

            if result.success:
                self._log(f"  ✓ Success: {result.xml_file}\n", tag="success")
            else:
                self._log(f"  ✗ Error: {result.error_message}\n", tag="error")

            self._log("\n")

        # Fase 2: Análisis
        self._log(f"\n{'='*60}\n")
        self._log(f"📊 {i18n.t('step3.analyzing')}\n\n")
        printTest = self.converter.frmf2xml_path
        self._log(f"{printTest}\n")

        xml_files = [r.xml_file for r in self.conversion_results if r.success and r.xml_file]
        self.analysis_metrics = self.analyzer.analyze_batch(xml_files)

        for metrics in self.analysis_metrics:
            self._log(f"📄 {metrics.file_name}:\n")
            self._log(f"  - Blocks: {metrics.blocks}\n")
            self._log(f"  - Items: {metrics.items}\n")
            self._log(f"  - Triggers: {metrics.triggers}\n")
            self._log(f"  - Complexity: {metrics.complexity_level} ({metrics.complexity_score})\n")
            self._log("\n")

        # Fase 3: Generar reporte
        self._log(f"\n{'='*60}\n")
        self._log(f"📝 {i18n.t('step3.generating_report')}\n\n")

        statistics = self.analyzer.get_statistics()
        self.report_path = self.report_generator.generate_report(
            self.conversion_results,
            self.analysis_metrics,
            statistics,
            i18n.get_current_language()
        )

        self._log(f"✓ {i18n.t('step3.report_generated')}\n", tag="success")
        self._log(f"📁 {self.report_path}\n\n")

        # Resumen final
        self._log(f"{'='*60}\n")
        self._log(f"✅ {i18n.t('step3.completed')}\n\n")

        total, successful, failed = self.converter.get_summary()
        success_rate = self.converter.get_success_rate()

        self._log(f"{i18n.t('step3.total_files')}: {total}\n")
        self._log(f"{i18n.t('step3.successful')}: {successful}\n")
        self._log(f"{i18n.t('step3.failed')}: {failed}\n")
        self._log(f"{i18n.t('step3.success_rate')}: {success_rate:.2f}%\n")

        # Habilitar botón de reporte
        self.report_button.configure(state="normal")
        self.start_button.configure(state="normal")
        self.is_analyzing = False

        self.progress_bar.set(1.0)
        self.progress_label.configure(text=i18n.t("step3.completed"))

    def _log(self, text: str, tag: str = None):  # type: ignore
        """Añade texto al log"""
        self.log_text.insert("end", text)
        self.log_text.see("end")

    def _on_open_report(self):
        """Abre el reporte HTML en el navegador"""
        if self.report_path:
            webbrowser.open(f"file://{self.report_path}")

    def is_ready(self) -> bool:
        """Verifica si el análisis está completo"""
        return bool(self.report_path)

    def _on_language_change(self, lang: str):
        """Actualiza los textos cuando cambia el idioma"""

        if not self.is_analyzing:
            self.start_button.configure(text=i18n.t("buttons.start_analysis"))
        self.report_button.configure(text=i18n.t("buttons.open_report"))

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
        self.auto_verified = False  # Flag para verificación automática
        self.install_window = None  # Ventana de instalación

        self._create_widgets()

        # Listener para cambios de idioma
        i18n.add_listener(self._on_language_change)

        # Ejecutar verificación automática después de que se cargue la ventana
        self.after(500, self._auto_verify)

    def _create_widgets(self):
        """Crea los widgets del step"""

        # Results frame (ultra compacto)
        self.results_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_primary'],
            corner_radius=CORNER_RADIUS['md']
        )
        self.results_frame.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['xs'])

        # Results text area (ultra compacto)
        self.results_text = ctk.CTkTextbox(
            self.results_frame,
            font=(FONTS['family_mono'], FONTS['size_small']),
            wrap="none"
        )
        self.results_text.pack(fill="both", expand=True, padx=SPACING['sm'], pady=SPACING['sm'])

        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.pack(pady=SPACING['xs'])

        # Verify button (ultra compacto)
        self.verify_button = ctk.CTkButton(
            self.buttons_frame,
            text=i18n.t("buttons.verify"),
            command=self._on_verify_clicked,
            height=34,
            width=140,
            font=(FONTS['family'], FONTS['size_normal'], FONTS['weight_bold']),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            corner_radius=CORNER_RADIUS['md']
        )
        self.verify_button.pack(side="left", padx=SPACING['xs'])

        # Install Angular CLI button (inicialmente oculto)
        self.install_cli_button = ctk.CTkButton(
            self.buttons_frame,
            text="🔧 Instalar Angular CLI",
            command=self._on_install_cli_clicked,
            height=34,
            width=180,
            font=(FONTS['family'], FONTS['size_normal'], FONTS['weight_bold']),
            fg_color=COLORS['warning'],
            hover_color="#d97706",
            corner_radius=CORNER_RADIUS['md']
        )
        # No se muestra inicialmente

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
        angular_cli_missing = False
        npm_available = False

        for key, result in self.results.items():
            self._append_text(f"  ✓ {result.name} ", tag="bold")

            if result.found:
                if result.version:
                    self._append_text(f"{result.version}\n", tag="success")
                else:
                    self._append_text(f"{i18n.t('step1.found')}\n", tag="success")

                if result.path:
                    self._append_text(f"     {i18n.t('step1.path')} {result.path}\n", tag="info")

                # Detectar si npm está disponible
                if key == 'npm':
                    npm_available = True
            else:
                self._append_text(f"{i18n.t('step1.not_found')}\n", tag="error")
                if result.message:
                    self._append_text(f"     {result.message}\n", tag="warning")

                # Detectar si Angular CLI está faltando
                if key == 'angular_cli':
                    angular_cli_missing = True

            self._append_text("\n")

        # Resumen
        self._append_text("\n" + "="*60 + "\n")
        if self.verificator.all_required_ok():
            self._append_text(f"{i18n.t('step1.all_ok')}\n", tag="success")
        else:
            self._append_text(f"{i18n.t('step1.some_missing')}\n", tag="warning")

        # Mostrar/ocultar botón de instalación de Angular CLI
        if angular_cli_missing and npm_available:
            self.install_cli_button.pack(side="left", padx=SPACING['xs'])
        else:
            self.install_cli_button.pack_forget()

        # Rehabilitar botón
        self.verify_button.configure(state="normal", text=i18n.t("buttons.verify"))

    def _on_install_cli_clicked(self):
        """Maneja el click del botón de instalación de Angular CLI"""
        if self.install_window is not None:
            return  # Ya hay una ventana abierta

        # Crear ventana modal
        self.install_window = ctk.CTkToplevel(self)
        self.install_window.title("Instalando Angular CLI")
        self.install_window.geometry("700x500")
        self.install_window.transient(self.winfo_toplevel())
        self.install_window.grab_set()

        # Frame principal
        main_frame = ctk.CTkFrame(self.install_window, fg_color=COLORS['bg_secondary'])
        main_frame.pack(fill="both", expand=True, padx=SPACING['md'], pady=SPACING['md'])

        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔧 Instalación de Angular CLI",
            font=(FONTS['family'], FONTS['size_large'], FONTS['weight_bold']),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=SPACING['sm'])

        # Descripción
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Se instalará Angular CLI globalmente usando npm.\nEsto puede tomar varios minutos.",
            font=(FONTS['family'], FONTS['size_normal']),
            text_color=COLORS['text_secondary']
        )
        desc_label.pack(pady=SPACING['xs'])

        # Log frame
        log_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_primary'])
        log_frame.pack(fill="both", expand=True, padx=SPACING['sm'], pady=SPACING['sm'])

        # Log textbox
        self.install_log = ctk.CTkTextbox(
            log_frame,
            font=(FONTS['family_mono'], FONTS['size_small']),
            wrap="word"
        )
        self.install_log.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])

        # Botón cerrar (inicialmente deshabilitado)
        self.install_close_button = ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=self._close_install_window,
            state="disabled",
            height=34,
            font=(FONTS['family'], FONTS['size_normal'], FONTS['weight_bold']),
            corner_radius=CORNER_RADIUS['md']
        )
        self.install_close_button.pack(pady=SPACING['sm'])

        # Iniciar instalación en thread separado
        thread = threading.Thread(target=self._run_installation)
        thread.daemon = True
        thread.start()

    def _run_installation(self):
        """Ejecuta la instalación de Angular CLI"""
        def log_callback(text):
            """Callback para recibir logs en tiempo real"""
            self.install_log.insert("end", text)
            self.install_log.see("end")

        # Ejecutar instalación
        success, message = self.verificator.install_angular_cli(callback=log_callback)

        # Mostrar resultado final
        if success:
            self.install_log.insert("end", f"\n{'='*60}\n")
            self.install_log.insert("end", "✅ INSTALACIÓN COMPLETADA CON ÉXITO\n")
            self.install_log.insert("end", f"{'='*60}\n")

            # Re-verificar automáticamente
            self.after(1000, self._auto_reverify_after_install)
        else:
            self.install_log.insert("end", f"\n{'='*60}\n")
            self.install_log.insert("end", "❌ ERROR EN LA INSTALACIÓN\n")
            self.install_log.insert("end", f"{'='*60}\n")
            self.install_log.insert("end", f"\n{message}\n")

        # Habilitar botón de cerrar
        self.install_close_button.configure(state="normal")

    def _close_install_window(self):
        """Cierra la ventana de instalación"""
        if self.install_window:
            self.install_window.destroy()
            self.install_window = None

    def _auto_reverify_after_install(self):
        """Re-verifica automáticamente después de la instalación"""
        self._close_install_window()
        self._on_verify_clicked()

    def _append_text(self, text: str, tag: str = None):
        """Añade texto al textbox"""
        self.results_text.insert("end", text)
        self.results_text.see("end")

    def _auto_verify(self):
        """Ejecuta la verificación automáticamente al cargar el step"""
        if not self.auto_verified:
            self.auto_verified = True
            self._on_verify_clicked()

    def is_ready(self) -> bool:
        """Verifica si se puede avanzar al siguiente paso"""
        return self.verificator.all_required_ok()

    def _on_language_change(self, lang: str):
        """Actualiza los textos cuando cambia el idioma"""
        if self.verify_button.cget("state") == "normal":
            self.verify_button.configure(text=i18n.t("buttons.verify"))

#!/usr/bin/env python3
"""
Gestor de Configuración para generación de código Angular
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ConfigManager:
    """Gestiona la configuración de generación de código Angular"""

    def __init__(self, config_file: str = "./angular_config.json"):
        """
        Inicializa el gestor de configuración

        Args:
            config_file: Ruta al archivo de configuración
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}

    def save_configuration(self, config_data: Dict[str, Any]) -> bool:
        """
        Guarda la configuración en un archivo JSON

        Args:
            config_data: Diccionario con la configuración

        Returns:
            True si se guardó exitosamente
        """
        try:
            # Agregar metadata
            config_with_metadata = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0.0"
                },
                "configuration": config_data
            }

            # Guardar a archivo
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_with_metadata, f, indent=2, ensure_ascii=False)

            self.config = config_data
            return True

        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False

    def load_configuration(self) -> Optional[Dict[str, Any]]:
        """
        Carga la configuración desde el archivo JSON

        Returns:
            Diccionario con la configuración o None si hay error
        """
        try:
            if not self.config_file.exists():
                return None

            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.config = data.get("configuration", {})
            return self.config

        except Exception as e:
            print(f"Error loading configuration: {e}")
            return None

    def get_project_name(self) -> str:
        """Retorna el nombre del proyecto"""
        return self.config.get('project_name', 'angular-app')

    def get_component_prefix(self) -> str:
        """Retorna el prefijo de componentes"""
        return self.config.get('component_prefix', 'app')

    def get_style_extension(self) -> str:
        """Retorna la extensión de estilos"""
        return self.config.get('style_extension', 'scss')

    def get_naming_convention(self) -> str:
        """Retorna la convención de nombres"""
        return self.config.get('naming_convention', 'kebab-case')

    def get_folder_structure(self) -> str:
        """Retorna el tipo de estructura de carpetas"""
        return self.config.get('folder_structure', 'feature')

    def is_routing_enabled(self) -> bool:
        """Retorna si el routing está habilitado"""
        return self.config.get('routing', True)

    def is_standalone_enabled(self) -> bool:
        """Retorna si los componentes standalone están habilitados"""
        return self.config.get('standalone', False)

    def should_generate_tests(self) -> bool:
        """Retorna si se deben generar tests"""
        return self.config.get('generate_tests', True)

    def should_generate_docs(self) -> bool:
        """Retorna si se debe generar documentación"""
        return self.config.get('generate_docs', True)

    def should_generate_services(self) -> bool:
        """Retorna si se deben generar servicios"""
        return self.config.get('generate_services', True)

    def should_generate_guards(self) -> bool:
        """Retorna si se deben generar guards"""
        return self.config.get('generate_guards', False)

    def get_selected_files(self) -> list:
        """Retorna la lista de archivos seleccionados para migración"""
        return self.config.get('selected_files', [])

    def get_all_config(self) -> Dict[str, Any]:
        """Retorna toda la configuración"""
        return self.config.copy()

    def export_to_angular_json(self, output_path: str) -> bool:
        """
        Exporta la configuración en formato angular.json

        Args:
            output_path: Ruta donde guardar el angular.json

        Returns:
            True si se exportó exitosamente
        """
        try:
            project_name = self.get_project_name()
            angular_config = {
                "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
                "version": 1,
                "newProjectRoot": "projects",
                "projects": {
                    project_name: {
                        "projectType": "application",
                        "schematics": {
                            "@schematics/angular:component": {
                                "style": self.get_style_extension(),
                                "standalone": self.is_standalone_enabled()
                            },
                            "@schematics/angular:application": {
                                "strict": True
                            }
                        },
                        "root": "",
                        "sourceRoot": "src",
                        "prefix": self.get_component_prefix(),
                        "architect": {
                            "build": {
                                "builder": "@angular-devkit/build-angular:browser",
                                "options": {
                                    "outputPath": f"dist/{project_name}",
                                    "index": "src/index.html",
                                    "main": "src/main.ts",
                                    "polyfills": ["zone.js"],
                                    "tsConfig": "tsconfig.app.json",
                                    "assets": [
                                        "src/favicon.ico",
                                        "src/assets"
                                    ],
                                    "styles": [
                                        f"src/styles.{self.get_style_extension()}"
                                    ],
                                    "scripts": []
                                }
                            },
                            "serve": {
                                "builder": "@angular-devkit/build-angular:dev-server",
                                "options": {
                                    "buildTarget": f"{project_name}:build"
                                }
                            }
                        }
                    }
                }
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(angular_config, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error exporting to angular.json: {e}")
            return False

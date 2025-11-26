#!/usr/bin/env python3
"""
Analizador de archivos XML de Oracle Forms
Extrae métricas y estadísticas
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from lxml import etree # type: ignore


@dataclass
class FormMetrics:
    """Métricas de un formulario"""
    file_name: str
    xml_path: str
    blocks: int = 0
    items: int = 0
    triggers: int = 0
    lovs: int = 0  # List of Values
    canvas: int = 0
    windows: int = 0
    program_units: int = 0
    alerts: int = 0
    record_groups: int = 0
    parameters: int = 0
    complexity_score: float = 0.0
    complexity_level: str = "Low"
    details: Dict = field(default_factory=dict)


class Analyzer:
    """Analizador de XMLs de Oracle Forms"""

    def __init__(self):
        self.metrics: List[FormMetrics] = []

    def analyze_xml(self, xml_file: str) -> Optional[FormMetrics]:
        """
        Analiza un archivo XML de Oracle Forms

        Args:
            xml_file: Ruta al archivo XML

        Returns:
            FormMetrics con las métricas extraídas o None si hay error
        """
        xml_path = Path(xml_file)

        if not xml_path.exists():
            return None

        try:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()

            metrics = FormMetrics(
                file_name=xml_path.stem,
                xml_path=str(xml_path)
            )

            # Contar elementos principales
            metrics.blocks = len(root.xpath(".//Block"))
            metrics.items = len(root.xpath(".//Item"))
            metrics.triggers = len(root.xpath(".//Trigger"))
            metrics.lovs = len(root.xpath(".//LOV"))
            metrics.canvas = len(root.xpath(".//Canvas"))
            metrics.windows = len(root.xpath(".//Window"))
            metrics.program_units = len(root.xpath(".//ProgramUnit"))
            metrics.alerts = len(root.xpath(".//Alert"))
            metrics.record_groups = len(root.xpath(".//RecordGroup"))
            metrics.parameters = len(root.xpath(".//FormParameter"))

            # Extraer detalles adicionales
            metrics.details = self._extract_details(root)

            # Calcular complejidad
            metrics.complexity_score = self._calculate_complexity(metrics)
            metrics.complexity_level = self._get_complexity_level(metrics.complexity_score)

            return metrics

        except Exception as e:
            print(f"Error analyzing {xml_file}: {e}")
            return None

    def _extract_details(self, root) -> Dict:
        """Extrae detalles adicionales del XML"""
        details = {}

        try:
            # Información del módulo
            module = root.find(".//Module")
            if module is not None:
                details['module_name'] = module.get('Name', 'Unknown')

            # Bloques con sus items
            blocks_info = []
            for block in root.xpath(".//Block"):
                block_name = block.get('Name', 'Unknown')
                items_in_block = len(block.xpath(".//Item"))
                blocks_info.append({
                    'name': block_name,
                    'items': items_in_block
                })
            details['blocks_info'] = blocks_info

            # Triggers por tipo
            trigger_types = {}
            for trigger in root.xpath(".//Trigger"):
                trigger_name = trigger.get('Name', 'Unknown')
                trigger_types[trigger_name] = trigger_types.get(trigger_name, 0) + 1
            details['trigger_types'] = trigger_types

            # LOVs
            lov_names = [lov.get('Name', 'Unknown') for lov in root.xpath(".//LOV")]
            details['lov_names'] = lov_names

            # Program Units
            program_unit_names = [pu.get('Name', 'Unknown') for pu in root.xpath(".//ProgramUnit")]
            details['program_unit_names'] = program_unit_names

        except Exception as e:
            print(f"Error extracting details: {e}")

        return details

    def _calculate_complexity(self, metrics: FormMetrics) -> float:
        """
        Calcula un score de complejidad basado en las métricas

        Args:
            metrics: Métricas del formulario

        Returns:
            Score de complejidad (0-100)
        """
        # Pesos para cada elemento
        weights = {
            'blocks': 2.0,
            'items': 0.5,
            'triggers': 3.0,
            'lovs': 2.0,
            'canvas': 1.5,
            'windows': 1.5,
            'program_units': 5.0,
            'alerts': 1.0,
            'record_groups': 2.0
        }

        score = 0.0
        score += metrics.blocks * weights['blocks']
        score += metrics.items * weights['items']
        score += metrics.triggers * weights['triggers']
        score += metrics.lovs * weights['lovs']
        score += metrics.canvas * weights['canvas']
        score += metrics.windows * weights['windows']
        score += metrics.program_units * weights['program_units']
        score += metrics.alerts * weights['alerts']
        score += metrics.record_groups * weights['record_groups']

        # Normalizar a escala 0-100
        # Asumimos que un form muy complejo tiene score ~500
        normalized_score = min(score / 5.0, 100.0)

        return round(normalized_score, 2)

    def _get_complexity_level(self, score: float) -> str:
        """
        Determina el nivel de complejidad basado en el score

        Args:
            score: Score de complejidad

        Returns:
            Nivel: Low, Medium, High, Very High
        """
        if score < 25:
            return "Low"
        elif score < 50:
            return "Medium"
        elif score < 75:
            return "High"
        else:
            return "Very High"

    def analyze_batch(self, xml_files: List[str]) -> List[FormMetrics]:
        """
        Analiza múltiples archivos XML

        Args:
            xml_files: Lista de rutas a archivos XML

        Returns:
            Lista de FormMetrics
        """
        self.metrics = []

        for xml_file in xml_files:
            metrics = self.analyze_xml(xml_file)
            if metrics:
                self.metrics.append(metrics)

        return self.metrics

    def get_statistics(self) -> Dict:
        """
        Calcula estadísticas generales de todos los formularios analizados

        Returns:
            Diccionario con estadísticas
        """
        if not self.metrics:
            return {}

        total_forms = len(self.metrics)

        stats = {
            'total_forms': total_forms,
            'total_blocks': sum(m.blocks for m in self.metrics),
            'total_items': sum(m.items for m in self.metrics),
            'total_triggers': sum(m.triggers for m in self.metrics),
            'total_lovs': sum(m.lovs for m in self.metrics),
            'total_canvas': sum(m.canvas for m in self.metrics),
            'total_windows': sum(m.windows for m in self.metrics),
            'total_program_units': sum(m.program_units for m in self.metrics),
            'avg_complexity': round(sum(m.complexity_score for m in self.metrics) / total_forms, 2),
            'complexity_distribution': self._get_complexity_distribution()
        }

        return stats

    def _get_complexity_distribution(self) -> Dict[str, int]:
        """Obtiene distribución de complejidad"""
        distribution = {
            'Low': 0,
            'Medium': 0,
            'High': 0,
            'Very High': 0
        }

        for metrics in self.metrics:
            level = metrics.complexity_level
            distribution[level] = distribution.get(level, 0) + 1

        return distribution

    def get_most_complex(self, n: int = 5) -> List[FormMetrics]:
        """
        Obtiene los N formularios más complejos

        Args:
            n: Número de formularios a retornar

        Returns:
            Lista de FormMetrics ordenada por complejidad
        """
        sorted_metrics = sorted(self.metrics, key=lambda m: m.complexity_score, reverse=True)
        return sorted_metrics[:n]

#!/usr/bin/env python3
"""
Generador de reportes HTML con gráficos interactivos
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict
from jinja2 import Template

from .analyzer import FormMetrics
from .converter import ConversionResult


class ReportGenerator:
    """Generador de reportes HTML"""

    def __init__(self, output_dir: str = "./output"):
        """
        Inicializa el generador de reportes

        Args:
            output_dir: Directorio donde se guardarán los reportes
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        conversion_results: List[ConversionResult],
        metrics: List[FormMetrics],
        statistics: Dict,
        language: str = "es"
    ) -> str:
        """
        Genera reporte HTML completo

        Args:
            conversion_results: Resultados de conversión
            metrics: Métricas de análisis
            statistics: Estadísticas generales
            language: Idioma del reporte

        Returns:
            Ruta al archivo HTML generado
        """
        template = self._get_template()

        # Preparar datos para el template
        context = {
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_files': len(conversion_results),
            'successful': sum(1 for r in conversion_results if r.success),
            'failed': sum(1 for r in conversion_results if not r.success),
            'success_rate': self._calculate_success_rate(conversion_results),
            'total_time': sum(r.duration for r in conversion_results),
            'conversion_results': conversion_results,
            'metrics': metrics,
            'statistics': statistics,
            'language': language,
            'charts_data': self._prepare_charts_data(metrics, statistics)
        }

        # Renderizar template
        html_content = template.render(**context)

        # Guardar archivo
        report_path = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(report_path)

    def _calculate_success_rate(self, results: List[ConversionResult]) -> float:
        """Calcula tasa de éxito"""
        if not results:
            return 0.0
        successful = sum(1 for r in results if r.success)
        return round((successful / len(results)) * 100, 2)

    def _prepare_charts_data(self, metrics: List[FormMetrics], statistics: Dict) -> Dict:
        """Prepara datos para gráficos Chart.js"""
        charts_data = {}

        # Gráfico de complejidad
        if metrics:
            complexity_labels = [m.file_name for m in metrics]
            complexity_scores = [m.complexity_score for m in metrics]

            charts_data['complexity_chart'] = {
                'labels': complexity_labels,
                'data': complexity_scores
            }

        # Distribución de complejidad
        if 'complexity_distribution' in statistics:
            dist = statistics['complexity_distribution']
            charts_data['complexity_distribution'] = {
                'labels': list(dist.keys()),
                'data': list(dist.values())
            }

        # Elementos por formulario (promedio)
        if metrics:
            avg_blocks = round(sum(m.blocks for m in metrics) / len(metrics), 2)
            avg_items = round(sum(m.items for m in metrics) / len(metrics), 2)
            avg_triggers = round(sum(m.triggers for m in metrics) / len(metrics), 2)
            avg_lovs = round(sum(m.lovs for m in metrics) / len(metrics), 2)

            charts_data['elements_average'] = {
                'labels': ['Blocks', 'Items', 'Triggers', 'LOVs'],
                'data': [avg_blocks, avg_items, avg_triggers, avg_lovs]
            }

        return charts_data

    def _get_template(self) -> Template:
        """Retorna el template HTML"""
        template_str = '''
<!DOCTYPE html>
<html lang="{{ language }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if language == "es" %}Reporte de Análisis - Oracle Forms{% else %}Analysis Report - Oracle Forms{% endif %}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #212121;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: linear-gradient(135deg, #1976D2 0%, #0D47A1 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .card h3 {
            color: #757575;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .card .value {
            font-size: 2.5em;
            font-weight: bold;
            color: #1976D2;
        }

        .card .value.success {
            color: #4CAF50;
        }

        .card .value.error {
            color: #F44336;
        }

        .section {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin: 30px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .section h2 {
            color: #1976D2;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #E0E0E0;
            padding-bottom: 10px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th {
            background: #1976D2;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #E0E0E0;
        }

        tr:hover {
            background: #F5F5F5;
        }

        .status-success {
            color: #4CAF50;
            font-weight: bold;
        }

        .status-error {
            color: #F44336;
            font-weight: bold;
        }

        .complexity-low {
            background: #4CAF50;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }

        .complexity-medium {
            background: #FF9800;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }

        .complexity-high {
            background: #F44336;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }

        .complexity-very-high {
            background: #9C27B0;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }

        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .chart-container h3 {
            margin-bottom: 15px;
            color: #1976D2;
        }

        footer {
            text-align: center;
            padding: 20px;
            color: #757575;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <header>
        <h1>{% if language == "es" %}📊 Reporte de Análisis - Oracle Forms{% else %}📊 Analysis Report - Oracle Forms{% endif %}</h1>
        <p>{% if language == "es" %}Generado el{% else %}Generated on{% endif %}: {{ generation_date }}</p>
    </header>

    <div class="container">
        <!-- Summary Cards -->
        <div class="summary-cards">
            <div class="card">
                <h3>{% if language == "es" %}Archivos Procesados{% else %}Processed Files{% endif %}</h3>
                <div class="value">{{ total_files }}</div>
            </div>
            <div class="card">
                <h3>{% if language == "es" %}Conversiones Exitosas{% else %}Successful Conversions{% endif %}</h3>
                <div class="value success">{{ successful }}</div>
            </div>
            <div class="card">
                <h3>{% if language == "es" %}Errores{% else %}Errors{% endif %}</h3>
                <div class="value error">{{ failed }}</div>
            </div>
            <div class="card">
                <h3>{% if language == "es" %}Tasa de Éxito{% else %}Success Rate{% endif %}</h3>
                <div class="value">{{ success_rate }}%</div>
            </div>
        </div>

        <!-- Conversion Details -->
        <div class="section">
            <h2>{% if language == "es" %}Detalle de Conversiones{% else %}Conversion Details{% endif %}</h2>
            <table>
                <thead>
                    <tr>
                        <th>{% if language == "es" %}Archivo{% else %}File{% endif %}</th>
                        <th>{% if language == "es" %}Estado{% else %}Status{% endif %}</th>
                        <th>{% if language == "es" %}Duración (s){% else %}Duration (s){% endif %}</th>
                        <th>{% if language == "es" %}Mensaje{% else %}Message{% endif %}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for result in conversion_results %}
                    <tr>
                        <td>{{ result.fmb_file }}</td>
                        <td>
                            {% if result.success %}
                            <span class="status-success">✓ {% if language == "es" %}Exitoso{% else %}Success{% endif %}</span>
                            {% else %}
                            <span class="status-error">✗ {% if language == "es" %}Error{% else %}Error{% endif %}</span>
                            {% endif %}
                        </td>
                        <td>{{ "%.2f"|format(result.duration) }}</td>
                        <td>{{ result.error_message if result.error_message else "-" }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Metrics Table -->
        {% if metrics %}
        <div class="section">
            <h2>{% if language == "es" %}Métricas por Formulario{% else %}Metrics by Form{% endif %}</h2>
            <table>
                <thead>
                    <tr>
                        <th>{% if language == "es" %}Archivo{% else %}File{% endif %}</th>
                        <th>Blocks</th>
                        <th>Items</th>
                        <th>Triggers</th>
                        <th>LOVs</th>
                        <th>Canvas</th>
                        <th>{% if language == "es" %}Ventanas{% else %}Windows{% endif %}</th>
                        <th>Program Units</th>
                        <th>{% if language == "es" %}Complejidad{% else %}Complexity{% endif %}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for m in metrics %}
                    <tr>
                        <td>{{ m.file_name }}</td>
                        <td>{{ m.blocks }}</td>
                        <td>{{ m.items }}</td>
                        <td>{{ m.triggers }}</td>
                        <td>{{ m.lovs }}</td>
                        <td>{{ m.canvas }}</td>
                        <td>{{ m.windows }}</td>
                        <td>{{ m.program_units }}</td>
                        <td>
                            <span class="complexity-{{ m.complexity_level.lower().replace(' ', '-') }}">
                                {% if language == "es" %}
                                {{ {"Low": "Baja", "Medium": "Media", "High": "Alta", "Very High": "Muy Alta"}[m.complexity_level] }}
                                {% else %}
                                {{ m.complexity_level }}
                                {% endif %}
                                ({{ m.complexity_score }})
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Charts -->
        {% if charts_data %}
        <div class="section">
            <h2>{% if language == "es" %}Estadísticas Visuales{% else %}Visual Statistics{% endif %}</h2>
            <div class="charts-grid">
                {% if charts_data.complexity_distribution %}
                <div class="chart-container">
                    <h3>{% if language == "es" %}Distribución de Complejidad{% else %}Complexity Distribution{% endif %}</h3>
                    <canvas id="complexityDistChart"></canvas>
                </div>
                {% endif %}

                {% if charts_data.elements_average %}
                <div class="chart-container">
                    <h3>{% if language == "es" %}Promedio de Elementos{% else %}Average Elements{% endif %}</h3>
                    <canvas id="elementsChart"></canvas>
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}
        {% endif %}
    </div>

    <footer>
        <p>Oracle Forms to Angular Migrator v3.0 | &copy; 2024</p>
    </footer>

    <script>
        // Complexity Distribution Chart
        {% if charts_data and charts_data.complexity_distribution %}
        const distCtx = document.getElementById('complexityDistChart');
        new Chart(distCtx, {
            type: 'doughnut',
            data: {
                labels: {{ charts_data.complexity_distribution.labels | tojson }},
                datasets: [{
                    data: {{ charts_data.complexity_distribution.data | tojson }},
                    backgroundColor: ['#4CAF50', '#FF9800', '#F44336', '#9C27B0']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        {% endif %}

        // Elements Average Chart
        {% if charts_data and charts_data.elements_average %}
        const elemCtx = document.getElementById('elementsChart');
        new Chart(elemCtx, {
            type: 'bar',
            data: {
                labels: {{ charts_data.elements_average.labels | tojson }},
                datasets: [{
                    label: '{% if language == "es" %}Promedio{% else %}Average{% endif %}',
                    data: {{ charts_data.elements_average.data | tojson }},
                    backgroundColor: '#1976D2'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        {% endif %}
    </script>
</body>
</html>
        '''

        return Template(template_str)

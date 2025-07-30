"""
Reports Module for FourPoints.

This module provides functionality for generating PDF and HTML reports
of vehicle health, diagnostics, and maintenance recommendations.
"""

import logging
import os
import datetime
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import tempfile
import base64

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generator for vehicle health and diagnostic reports in PDF and HTML formats.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save reports (default: current directory)
        """
        self.output_dir = output_dir or os.getcwd()
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Check for required libraries
        try:
            import jinja2
            self.jinja2 = jinja2
            self.jinja2_available = True
        except ImportError:
            logger.warning("jinja2 library not installed. Install with 'pip install jinja2' for HTML report generation.")
            self.jinja2 = None
            self.jinja2_available = False
            
        try:
            import weasyprint
            self.weasyprint = weasyprint
            self.weasyprint_available = True
        except ImportError:
            logger.warning("weasyprint library not installed. Install with 'pip install weasyprint' for PDF report generation.")
            self.weasyprint = None
            self.weasyprint_available = False
            
        try:
            import matplotlib
            import matplotlib.pyplot as plt
            self.plt = plt
            self.matplotlib_available = True
        except ImportError:
            logger.warning("matplotlib library not installed. Install with 'pip install matplotlib' for chart generation.")
            self.plt = None
            self.matplotlib_available = False
            
        # Initialize Jinja2 environment
        if self.jinja2_available:
            template_dir = os.path.join(os.path.dirname(__file__), 'templates')
            if not os.path.exists(template_dir):
                os.makedirs(template_dir, exist_ok=True)
                self._create_default_templates(template_dir)
                
            self.jinja_env = self.jinja2.Environment(
                loader=self.jinja2.FileSystemLoader(template_dir)
            )
            
    def _create_default_templates(self, template_dir: str) -> None:
        """
        Create default HTML templates for reports.
        
        Args:
            template_dir: Directory to create templates in
        """
        # Create base template
        base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ddd;
        }
        .header h1 {
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .header p {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .section {
            margin-bottom: 30px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #2980b9;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .good {
            color: #27ae60;
            font-weight: bold;
        }
        .warning {
            color: #f39c12;
            font-weight: bold;
        }
        .critical {
            color: #c0392b;
            font-weight: bold;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
            font-size: 0.8em;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p>Generated on {{ timestamp }}</p>
    </div>
    
    {% block content %}{% endblock %}
    
    <div class="footer">
        <p>Generated by FourPoints Vehicle Diagnostics</p>
    </div>
</body>
</html>"""

        # Create vehicle health report template
        health_template = """{% extends "base.html" %}

{% block content %}
    <div class="section">
        <h2>Vehicle Information</h2>
        <table>
            <tr>
                <th>VIN</th>
                <td>{{ vehicle_info.vin|default('N/A') }}</td>
                <th>Make</th>
                <td>{{ vehicle_info.make|default('N/A') }}</td>
            </tr>
            <tr>
                <th>Model</th>
                <td>{{ vehicle_info.model|default('N/A') }}</td>
                <th>Year</th>
                <td>{{ vehicle_info.year|default('N/A') }}</td>
            </tr>
            <tr>
                <th>Engine</th>
                <td>{{ vehicle_info.engine|default('N/A') }}</td>
                <th>Odometer</th>
                <td>{{ vehicle_info.odometer|default('N/A') }} {{ vehicle_info.odometer_unit|default('') }}</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>Health Summary</h2>
        <p>Overall Health Status: 
            {% if health_data.status == 'Good' %}
                <span class="good">{{ health_data.status }}</span>
            {% elif health_data.status == 'Warning' %}
                <span class="warning">{{ health_data.status }}</span>
            {% elif health_data.status == 'Critical' %}
                <span class="critical">{{ health_data.status }}</span>
            {% else %}
                {{ health_data.status }}
            {% endif %}
        </p>
        
        {% if health_data.issues %}
            <h3>Detected Issues:</h3>
            <ul>
                {% for issue in health_data.issues %}
                    <li>{{ issue }}</li>
                {% endfor %}
            </ul>
        {% else %}
            <p>No issues detected.</p>
        {% endif %}
        
        {% if charts.health_chart %}
            <div class="chart-container">
                <img src="data:image/png;base64,{{ charts.health_chart }}" alt="Health Metrics Chart">
            </div>
        {% endif %}
    </div>

    <div class="section">
        <h2>Diagnostic Trouble Codes</h2>
        {% if health_data.dtc_analysis.codes %}
            <p>{{ health_data.dtc_analysis.count }} trouble code(s) detected:</p>
            <table>
                <tr>
                    <th>Code</th>
                    <th>Description</th>
                    <th>Severity</th>
                    <th>Possible Causes</th>
                </tr>
                {% for code in health_data.dtc_analysis.codes %}
                    <tr>
                        <td>{{ code }}</td>
                        <td>{{ dtc_explanations[code].description|default('Unknown') }}</td>
                        <td>
                            {% if code in health_data.dtc_analysis.critical_codes %}
                                <span class="critical">Critical</span>
                            {% elif code in health_data.dtc_analysis.warning_codes %}
                                <span class="warning">Warning</span>
                            {% else %}
                                <span class="good">Low</span>
                            {% endif %}
                        </td>
                        <td>{{ dtc_explanations[code].possible_causes|default('Unknown') }}</td>
                    </tr>
                {% endfor %}
            </table>
        {% else %}
            <p>No trouble codes detected.</p>
        {% endif %}
    </div>

    <div class="section">
        <h2>Key Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Status</th>
            </tr>
            {% for metric_name, metric_data in health_data.metrics_analysis.items() %}
                <tr>
                    <td>{{ metric_name }}</td>
                    <td>{{ metric_data.value }} {{ telemetry_data[metric_name].unit|default('') }}</td>
                    <td>
                        {% if metric_data.status == 'Good' %}
                            <span class="good">{{ metric_data.status }}</span>
                        {% elif metric_data.status == 'Warning' %}
                            <span class="warning">{{ metric_data.status }}</span>
                        {% elif metric_data.status == 'Critical' %}
                            <span class="critical">{{ metric_data.status }}</span>
                        {% else %}
                            {{ metric_data.status }}
                        {% endif %}
                    </td>
                </tr>
            {% endfor %}
        </table>
    </div>

    <div class="section">
        <h2>Maintenance Recommendations</h2>
        {% if maintenance_data.predictions %}
            <table>
                <tr>
                    <th>Component</th>
                    <th>Issue</th>
                    <th>Confidence</th>
                    <th>Recommendation</th>
                </tr>
                {% for prediction in maintenance_data.predictions %}
                    <tr>
                        <td>{{ prediction.component }}</td>
                        <td>{{ prediction.issue }}</td>
                        <td>{{ "%.0f"|format(prediction.confidence * 100) }}%</td>
                        <td>{{ prediction.recommendation }}</td>
                    </tr>
                {% endfor %}
            </table>
        {% else %}
            <p>No maintenance recommendations at this time.</p>
        {% endif %}
    </div>

    {% if gemini_insights %}
    <div class="section">
        <h2>AI Insights</h2>
        <p><strong>{{ gemini_insights.summary }}</strong></p>
        
        {% if gemini_insights.insights %}
            <ul>
                {% for insight in gemini_insights.insights %}
                    <li>
                        <strong>{{ insight.title }}</strong>: 
                        {{ insight.description }}
                        {% if insight.action_needed %}
                            <br><em>Recommended action: {{ insight.recommendation }}</em>
                        {% endif %}
                    </li>
                {% endfor %}
            </ul>
        {% endif %}
    </div>
    {% endif %}
{% endblock %}"""

        # Write templates to files
        with open(os.path.join(template_dir, 'base.html'), 'w') as f:
            f.write(base_template)
            
        with open(os.path.join(template_dir, 'health_report.html'), 'w') as f:
            f.write(health_template)
            
        logger.info("Created default report templates")
        
    def _generate_health_chart(self, telemetry_data: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Generate a chart of key health metrics.
        
        Args:
            telemetry_data: Dictionary of telemetry data
            
        Returns:
            Optional[str]: Base64-encoded PNG image or None if chart generation fails
        """
        if not self.matplotlib_available or not telemetry_data:
            return None
            
        try:
            # Select key metrics for the chart
            metrics = {}
            for key in ['RPM', 'ENGINE_LOAD', 'COOLANT_TEMP', 'INTAKE_TEMP', 'THROTTLE_POS']:
                if key in telemetry_data and 'value' in telemetry_data[key]:
                    metrics[key] = telemetry_data[key]['value']
                    
            if not metrics:
                return None
                
            # Create the chart
            fig, ax = self.plt.subplots(figsize=(10, 6))
            
            # Normalize values for better visualization
            normalized_metrics = {}
            for key, value in metrics.items():
                if key == 'RPM':
                    normalized_metrics[key] = value / 6000  # Assuming max RPM of 6000
                elif key == 'ENGINE_LOAD' or key == 'THROTTLE_POS':
                    normalized_metrics[key] = value / 100  # These are percentages
                elif key == 'COOLANT_TEMP' or key == 'INTAKE_TEMP':
                    normalized_metrics[key] = value / 150  # Assuming max temp of 150°C
                else:
                    normalized_metrics[key] = value / 100  # Default normalization
                    
            # Create bar chart
            bars = ax.bar(normalized_metrics.keys(), normalized_metrics.values())
            
            # Add value labels on top of bars
            for bar, key in zip(bars, metrics.keys()):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                        f"{metrics[key]}", ha='center', va='bottom')
                        
            ax.set_ylim(0, 1.1)  # Set y-axis limit with some padding
            ax.set_title('Key Vehicle Metrics (Normalized)')
            ax.set_ylabel('Normalized Value')
            
            # Save chart to a base64 string
            with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
                fig.savefig(tmp.name, format='png', bbox_inches='tight')
                self.plt.close(fig)
                
                with open(tmp.name, 'rb') as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
                    
        except Exception as e:
            logger.error(f"Error generating health chart: {str(e)}")
            return None
            
    def generate_html_report(self, report_data: Dict[str, Any], report_type: str = 'health') -> Optional[str]:
        """
        Generate an HTML report.
        
        Args:
            report_data: Dictionary containing report data
            report_type: Type of report ('health', 'maintenance', etc.)
            
        Returns:
            Optional[str]: Path to the generated HTML file or None if generation fails
        """
        if not self.jinja2_available:
            logger.error("jinja2 library not available, cannot generate HTML report")
            return None
            
        try:
            # Generate charts if matplotlib is available
            charts = {}
            if self.matplotlib_available and 'telemetry_data' in report_data:
                health_chart = self._generate_health_chart(report_data['telemetry_data'])
                if health_chart:
                    charts['health_chart'] = health_chart
                    
            # Add charts to report data
            report_data['charts'] = charts
            
            # Add timestamp
            report_data['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Select template based on report type
            if report_type == 'health':
                template = self.jinja_env.get_template('health_report.html')
                filename = f"health_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                title = "Vehicle Health Report"
            else:
                # Default to health report
                template = self.jinja_env.get_template('health_report.html')
                filename = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                title = "Vehicle Report"
                
            # Add title if not provided
            if 'title' not in report_data:
                report_data['title'] = title
                
            # Render template
            html_content = template.render(**report_data)
            
            # Write to file
            output_path = os.path.join(self.output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.info(f"Generated HTML report: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return None
            
    def generate_pdf_report(self, report_data: Dict[str, Any], report_type: str = 'health') -> Optional[str]:
        """
        Generate a PDF report.
        
        Args:
            report_data: Dictionary containing report data
            report_type: Type of report ('health', 'maintenance', etc.)
            
        Returns:
            Optional[str]: Path to the generated PDF file or None if generation fails
        """
        if not self.weasyprint_available:
            logger.error("weasyprint library not available, cannot generate PDF report")
            return None
            
        try:
            # First generate HTML report
            html_path = self.generate_html_report(report_data, report_type)
            if not html_path:
                return None
                
            # Convert HTML to PDF
            pdf_path = html_path.replace('.html', '.pdf')
            html = self.weasyprint.HTML(filename=html_path)
            html.write_pdf(pdf_path)
            
            logger.info(f"Generated PDF report: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            return None
            
    def generate_report(self, report_data: Dict[str, Any], report_type: str = 'health',
                       format: str = 'pdf') -> Optional[str]:
        """
        Generate a report in the specified format.
        
        Args:
            report_data: Dictionary containing report data
            report_type: Type of report ('health', 'maintenance', etc.)
            format: Report format ('pdf', 'html')
            
        Returns:
            Optional[str]: Path to the generated report file or None if generation fails
        """
        if format.lower() == 'pdf':
            return self.generate_pdf_report(report_data, report_type)
        elif format.lower() == 'html':
            return self.generate_html_report(report_data, report_type)
        else:
            logger.error(f"Unsupported report format: {format}")
            return None

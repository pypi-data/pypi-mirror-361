"""
Unit tests for the reports module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
import os
import tempfile
from pathlib import Path
from datetime import datetime

from fourpoints.reports import ReportGenerator, ReportFormat


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for reports
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create report generator
        self.report_generator = ReportGenerator(output_dir=self.temp_dir.name)
        
        # Mock data
        self.mock_telemetry = {
            "RPM": 1500,
            "SPEED": 60,
            "ENGINE_LOAD": 40,
            "COOLANT_TEMP": 90
        }
        
        self.mock_dtcs = ["P0123", "P0456"]
        
        self.mock_health_status = {
            "status": "WARNING",
            "score": 75,
            "issues": ["High coolant temperature", "Throttle position sensor issue"]
        }
        
        self.mock_maintenance = [
            {
                "component": "Throttle Position Sensor",
                "severity": "MODERATE",
                "description": "Throttle position sensor circuit high input",
                "recommendation": "Check wiring and replace sensor if necessary"
            }
        ]
        
        self.mock_location = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "altitude": 10.0,
            "speed": 60.0
        }
        
        self.mock_trip_data = {
            "distance": 100.0,
            "duration": 3600,  # 1 hour in seconds
            "average_speed": 100.0,
            "start_time": datetime.now().isoformat()
        }
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
        
    def test_init(self):
        """Test initialization."""
        # Verify
        self.assertEqual(self.report_generator.output_dir, Path(self.temp_dir.name))
        self.assertTrue(os.path.exists(self.temp_dir.name))
        
    def test_generate_html_report(self):
        """Test generating HTML report."""
        # Setup
        with patch('jinja2.Environment') as mock_env:
            mock_template = Mock()
            mock_env.return_value.get_template.return_value = mock_template
            mock_template.render.return_value = "<html>Test Report</html>"
            
            # Test
            report_path = self.report_generator.generate_report(
                format=ReportFormat.HTML,
                telemetry=self.mock_telemetry,
                dtcs=self.mock_dtcs,
                health_status=self.mock_health_status,
                maintenance=self.mock_maintenance,
                location=self.mock_location,
                trip_data=self.mock_trip_data,
                vehicle_info={"make": "Toyota", "model": "Camry", "year": 2020}
            )
            
            # Verify
            self.assertTrue(os.path.exists(report_path))
            self.assertTrue(report_path.endswith(".html"))
            mock_env.return_value.get_template.assert_called_once()
            mock_template.render.assert_called_once()
            
    def test_generate_pdf_report(self):
        """Test generating PDF report."""
        # Setup
        with patch('jinja2.Environment') as mock_env, \
             patch('weasyprint.HTML') as mock_weasyprint:
            mock_template = Mock()
            mock_env.return_value.get_template.return_value = mock_template
            mock_template.render.return_value = "<html>Test Report</html>"
            
            mock_html = Mock()
            mock_weasyprint.return_value = mock_html
            
            # Test
            report_path = self.report_generator.generate_report(
                format=ReportFormat.PDF,
                telemetry=self.mock_telemetry,
                dtcs=self.mock_dtcs,
                health_status=self.mock_health_status,
                maintenance=self.mock_maintenance,
                location=self.mock_location,
                trip_data=self.mock_trip_data,
                vehicle_info={"make": "Toyota", "model": "Camry", "year": 2020}
            )
            
            # Verify
            self.assertTrue(os.path.exists(report_path))
            self.assertTrue(report_path.endswith(".pdf"))
            mock_env.return_value.get_template.assert_called_once()
            mock_template.render.assert_called_once()
            mock_html.write_pdf.assert_called_once()
            
    def test_generate_charts(self):
        """Test generating charts."""
        # Setup
        with patch('matplotlib.pyplot') as mock_plt, \
             patch('matplotlib.figure.Figure.savefig') as mock_savefig:
            # Test
            chart_paths = self.report_generator._generate_charts(self.mock_telemetry)
            
            # Verify
            self.assertIsInstance(chart_paths, dict)
            self.assertGreater(len(chart_paths), 0)
            mock_plt.figure.assert_called()
            mock_savefig.assert_called()
            
    def test_cleanup_old_reports(self):
        """Test cleaning up old reports."""
        # Setup - Create some test files
        old_file = os.path.join(self.temp_dir.name, "old_report.pdf")
        new_file = os.path.join(self.temp_dir.name, "new_report.pdf")
        
        # Create files
        with open(old_file, 'w') as f:
            f.write("test")
        with open(new_file, 'w') as f:
            f.write("test")
            
        # Mock file stats to make one file appear old
        old_stat = os.stat(old_file)
        new_stat = os.stat(new_file)
        
        with patch('os.stat') as mock_stat, \
             patch('time.time') as mock_time:
            def mock_stat_side_effect(path):
                if path == old_file:
                    return old_stat
                else:
                    return new_stat
                    
            mock_stat.side_effect = mock_stat_side_effect
            mock_time.return_value = old_stat.st_mtime + (8 * 24 * 60 * 60)  # 8 days later
            
            # Test
            self.report_generator.cleanup_old_reports(max_age_days=7)
            
            # Verify
            self.assertFalse(os.path.exists(old_file))
            self.assertTrue(os.path.exists(new_file))
            
    def test_get_report_filename(self):
        """Test getting report filename."""
        # Test
        filename = self.report_generator._get_report_filename(ReportFormat.PDF)
        
        # Verify
        self.assertTrue(filename.endswith(".pdf"))
        self.assertIn("vehicle_report", filename)
        
        # Test HTML format
        filename = self.report_generator._get_report_filename(ReportFormat.HTML)
        
        # Verify
        self.assertTrue(filename.endswith(".html"))
        
    def test_get_all_reports(self):
        """Test getting all reports."""
        # Setup - Create some test files
        report1 = os.path.join(self.temp_dir.name, "vehicle_report_1.pdf")
        report2 = os.path.join(self.temp_dir.name, "vehicle_report_2.html")
        non_report = os.path.join(self.temp_dir.name, "not_a_report.txt")
        
        # Create files
        with open(report1, 'w') as f:
            f.write("test")
        with open(report2, 'w') as f:
            f.write("test")
        with open(non_report, 'w') as f:
            f.write("test")
            
        # Test
        reports = self.report_generator.get_all_reports()
        
        # Verify
        self.assertEqual(len(reports), 2)
        self.assertIn(os.path.basename(report1), [os.path.basename(r) for r in reports])
        self.assertIn(os.path.basename(report2), [os.path.basename(r) for r in reports])
        self.assertNotIn(os.path.basename(non_report), [os.path.basename(r) for r in reports])
        
    def test_get_report_path(self):
        """Test getting report path."""
        # Test
        report_path = self.report_generator.get_report_path("vehicle_report_1.pdf")
        
        # Verify
        self.assertEqual(report_path, os.path.join(self.temp_dir.name, "vehicle_report_1.pdf"))


if __name__ == '__main__':
    unittest.main()

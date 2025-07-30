"""
Unit tests for the analytics module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime, timedelta

from fourpoints.analytics import VehicleAnalytics, HealthStatus, MaintenanceItem, MaintenanceSeverity, SensorStatus


class TestVehicleAnalytics(unittest.TestCase):
    """Test cases for VehicleAnalytics."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock OBD client
        self.mock_obd_client = Mock()
        self.mock_obd_client.is_connected = True
        self.mock_obd_client.get_dtcs = Mock(return_value=[])
        
        # Create mock responses for telemetry data
        self.mock_telemetry = {
            "RPM": 1500,
            "SPEED": 60,
            "ENGINE_LOAD": 40,
            "COOLANT_TEMP": 90,
            "INTAKE_TEMP": 25,
            "MAF": 15,
            "FUEL_LEVEL": 75,
            "THROTTLE_POS": 20,
            "TIMING_ADVANCE": 12,
            "FUEL_PRESSURE": 400,
            "OIL_TEMP": 100,
            "BAROMETRIC_PRESSURE": 101,
            "FUEL_RATE": 5.5,
            "AIR_FUEL_RATIO": 14.7,
            "OXYGEN_SENSORS": [0.9, 0.9, 0.9, 0.9],
            "VOLTAGE": 14.2
        }
        
        self.mock_obd_client.get_telemetry = Mock(return_value=self.mock_telemetry)
        
        # Create analytics instance
        self.analytics = VehicleAnalytics(self.mock_obd_client)
        
    def test_get_health_status_healthy(self):
        """Test getting health status when vehicle is healthy."""
        # Test
        health = self.analytics.get_health_status()
        
        # Verify
        self.assertEqual(health.status, HealthStatus.HEALTHY)
        self.assertEqual(health.score, 100)
        self.assertEqual(len(health.issues), 0)
        
    def test_get_health_status_with_dtcs(self):
        """Test getting health status when vehicle has DTCs."""
        # Setup
        self.mock_obd_client.get_dtcs = Mock(return_value=["P0123", "P0456"])
        
        # Test
        health = self.analytics.get_health_status()
        
        # Verify
        self.assertEqual(health.status, HealthStatus.ATTENTION)
        self.assertLess(health.score, 100)
        self.assertEqual(len(health.issues), 2)
        
    def test_get_health_status_with_abnormal_telemetry(self):
        """Test getting health status with abnormal telemetry."""
        # Setup - Coolant temp too high
        abnormal_telemetry = self.mock_telemetry.copy()
        abnormal_telemetry["COOLANT_TEMP"] = 120  # Very high coolant temp
        self.mock_obd_client.get_telemetry = Mock(return_value=abnormal_telemetry)
        
        # Test
        health = self.analytics.get_health_status()
        
        # Verify
        self.assertEqual(health.status, HealthStatus.WARNING)
        self.assertLess(health.score, 100)
        self.assertGreater(len(health.issues), 0)
        
    def test_analyze_dtcs_severity(self):
        """Test analyzing DTC severity."""
        # Test
        severity = self.analytics.analyze_dtcs_severity(["P0123"])  # Throttle position sensor circuit high input
        
        # Verify
        self.assertEqual(severity, MaintenanceSeverity.MODERATE)
        
        # Test with multiple DTCs
        severity = self.analytics.analyze_dtcs_severity(["P0123", "P0456", "P0301"])  # Added misfire
        
        # Verify
        self.assertEqual(severity, MaintenanceSeverity.SEVERE)
        
    def test_get_maintenance_recommendations_no_issues(self):
        """Test getting maintenance recommendations with no issues."""
        # Test
        recommendations = self.analytics.get_maintenance_recommendations()
        
        # Verify
        self.assertEqual(len(recommendations), 0)
        
    def test_get_maintenance_recommendations_with_issues(self):
        """Test getting maintenance recommendations with issues."""
        # Setup - Add DTCs and abnormal telemetry
        self.mock_obd_client.get_dtcs = Mock(return_value=["P0123"])
        abnormal_telemetry = self.mock_telemetry.copy()
        abnormal_telemetry["ENGINE_LOAD"] = 90  # High engine load
        self.mock_obd_client.get_telemetry = Mock(return_value=abnormal_telemetry)
        
        # Test
        recommendations = self.analytics.get_maintenance_recommendations()
        
        # Verify
        self.assertGreater(len(recommendations), 0)
        
    def test_get_sensor_status_all_normal(self):
        """Test getting sensor status when all sensors are normal."""
        # Test
        sensor_status = self.analytics.get_sensor_status()
        
        # Verify
        self.assertEqual(len(sensor_status), len(self.mock_telemetry))
        for sensor in sensor_status:
            self.assertEqual(sensor.status, SensorStatus.NORMAL)
            
    def test_get_sensor_status_with_abnormal(self):
        """Test getting sensor status with abnormal readings."""
        # Setup - Abnormal coolant temp
        abnormal_telemetry = self.mock_telemetry.copy()
        abnormal_telemetry["COOLANT_TEMP"] = 120  # Very high coolant temp
        self.mock_obd_client.get_telemetry = Mock(return_value=abnormal_telemetry)
        
        # Test
        sensor_status = self.analytics.get_sensor_status()
        
        # Verify
        coolant_sensor = next((s for s in sensor_status if s.name == "COOLANT_TEMP"), None)
        self.assertIsNotNone(coolant_sensor)
        self.assertEqual(coolant_sensor.status, SensorStatus.WARNING)
        
    def test_predict_failures_no_issues(self):
        """Test predicting failures with no issues."""
        # Test
        failures = self.analytics.predict_failures()
        
        # Verify
        self.assertEqual(len(failures), 0)
        
    def test_predict_failures_with_issues(self):
        """Test predicting failures with issues."""
        # Setup - Add history of high coolant temp
        history = []
        for i in range(10):
            entry = self.mock_telemetry.copy()
            entry["COOLANT_TEMP"] = 110 + i  # Increasing coolant temp
            history.append(entry)
            
        with patch.object(self.analytics, '_get_telemetry_history', return_value=history):
            # Test
            failures = self.analytics.predict_failures()
            
            # Verify
            self.assertGreater(len(failures), 0)
            coolant_failure = next((f for f in failures if "coolant" in f.component.lower()), None)
            self.assertIsNotNone(coolant_failure)
            
    def test_calculate_health_score_perfect(self):
        """Test calculating health score with perfect conditions."""
        # Test
        score = self.analytics._calculate_health_score([], self.mock_telemetry)
        
        # Verify
        self.assertEqual(score, 100)
        
    def test_calculate_health_score_with_issues(self):
        """Test calculating health score with issues."""
        # Setup
        dtcs = ["P0123", "P0456"]
        abnormal_telemetry = self.mock_telemetry.copy()
        abnormal_telemetry["COOLANT_TEMP"] = 120
        
        # Test
        score = self.analytics._calculate_health_score(dtcs, abnormal_telemetry)
        
        # Verify
        self.assertLess(score, 100)
        
    def test_get_dtc_description(self):
        """Test getting DTC description."""
        # Test
        description = self.analytics._get_dtc_description("P0123")
        
        # Verify
        self.assertIsNotNone(description)
        self.assertIn("throttle", description.lower())


if __name__ == '__main__':
    unittest.main()

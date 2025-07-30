"""
Unit tests for the API module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from fourpoints.api import FourPointsAPI, APIConfig, VehicleInfo


class TestFourPointsAPI(unittest.TestCase):
    """Test cases for FourPointsAPI."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock components
        self.mock_obd_client = Mock()
        self.mock_analytics = Mock()
        self.mock_gemini_client = Mock()
        self.mock_location_tracker = Mock()
        self.mock_report_generator = Mock()
        self.mock_data_stream = Mock()
        self.mock_websocket_streamer = Mock()
        
        # Create API config
        self.config = APIConfig(
            host="localhost",
            port=8000,
            obd_port="mock_port",
            gemini_api_key="mock_api_key",
            reports_dir="mock_reports_dir"
        )
        
        # Create API with patched components
        with patch('fourpoints.api.OBDClient', return_value=self.mock_obd_client), \
             patch('fourpoints.api.VehicleAnalytics', return_value=self.mock_analytics), \
             patch('fourpoints.api.GeminiClient', return_value=self.mock_gemini_client), \
             patch('fourpoints.api.LocationTracker', return_value=self.mock_location_tracker), \
             patch('fourpoints.api.ReportGenerator', return_value=self.mock_report_generator), \
             patch('fourpoints.api.DataStream', return_value=self.mock_data_stream), \
             patch('fourpoints.api.WebSocketStreamer', return_value=self.mock_websocket_streamer):
            self.api = FourPointsAPI(self.config)
            
        # Create test client
        self.client = TestClient(self.api.app)
        
    def test_init(self):
        """Test initialization."""
        # Verify
        self.assertEqual(self.api.config, self.config)
        self.assertIsNotNone(self.api.app)
        self.assertEqual(self.api.obd_client, self.mock_obd_client)
        self.assertEqual(self.api.analytics, self.mock_analytics)
        self.assertEqual(self.api.gemini_client, self.mock_gemini_client)
        self.assertEqual(self.api.location_tracker, self.mock_location_tracker)
        self.assertEqual(self.api.report_generator, self.mock_report_generator)
        self.assertEqual(self.api.data_stream, self.mock_data_stream)
        self.assertEqual(self.api.websocket_streamer, self.mock_websocket_streamer)
        
    def test_realtime_endpoint(self):
        """Test /realtime endpoint."""
        # Setup
        self.mock_obd_client.get_telemetry.return_value = {
            "RPM": 1500,
            "SPEED": 60
        }
        
        # Test
        response = self.client.get("/realtime")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"RPM": 1500, "SPEED": 60})
        self.mock_obd_client.get_telemetry.assert_called_once()
        
    def test_dtcs_endpoint(self):
        """Test /dtcs endpoint."""
        # Setup
        self.mock_obd_client.get_dtcs.return_value = ["P0123", "P0456"]
        self.mock_gemini_client.explain_dtc.side_effect = lambda dtc: f"Explanation for {dtc}"
        
        # Test
        response = self.client.get("/dtcs")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["code"], "P0123")
        self.assertEqual(data[0]["explanation"], "Explanation for P0123")
        self.assertEqual(data[1]["code"], "P0456")
        self.assertEqual(data[1]["explanation"], "Explanation for P0456")
        
    def test_clear_cel_endpoint(self):
        """Test /clear_cel endpoint."""
        # Setup
        self.mock_obd_client.clear_dtcs.return_value = True
        
        # Test
        response = self.client.post("/clear_cel")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "message": "Check Engine Light and DTCs cleared"})
        
    def test_health_endpoint(self):
        """Test /health endpoint."""
        # Setup
        self.mock_analytics.get_health_status.return_value = {
            "status": "HEALTHY",
            "score": 100,
            "issues": []
        }
        
        # Test
        response = self.client.get("/health")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["score"], 100)
        self.assertEqual(data["issues"], [])
        
    def test_maintenance_endpoint(self):
        """Test /maintenance endpoint."""
        # Setup
        self.mock_analytics.get_maintenance_recommendations.return_value = [
            {
                "component": "Oil",
                "severity": "LOW",
                "description": "Oil change recommended",
                "recommendation": "Change oil and filter"
            }
        ]
        
        # Test
        response = self.client.get("/maintenance")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["component"], "Oil")
        self.assertEqual(data[0]["severity"], "LOW")
        
    def test_sensors_endpoint(self):
        """Test /sensors endpoint."""
        # Setup
        self.mock_analytics.get_sensor_status.return_value = [
            {
                "name": "RPM",
                "value": 1500,
                "status": "NORMAL",
                "min": 0,
                "max": 6000
            }
        ]
        
        # Test
        response = self.client.get("/sensors")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "RPM")
        self.assertEqual(data[0]["value"], 1500)
        
    def test_report_endpoint(self):
        """Test /report endpoint."""
        # Setup
        self.mock_report_generator.generate_report.return_value = "/path/to/report.pdf"
        self.mock_obd_client.get_telemetry.return_value = {"RPM": 1500}
        self.mock_obd_client.get_dtcs.return_value = ["P0123"]
        self.mock_analytics.get_health_status.return_value = {"status": "HEALTHY", "score": 100, "issues": []}
        self.mock_analytics.get_maintenance_recommendations.return_value = []
        self.mock_location_tracker.get_current_location.return_value = {"latitude": 37.7749, "longitude": -122.4194}
        self.mock_location_tracker.get_trip_data.return_value = {"distance": 100.0}
        
        # Mock FileResponse
        with patch('fourpoints.api.FileResponse', return_value=MagicMock(status_code=200)) as mock_file_response:
            # Test
            response = self.client.get("/report?format=pdf")
            
            # Verify
            self.mock_report_generator.generate_report.assert_called_once()
            mock_file_response.assert_called_once()
            
    def test_vehicle_info_get_endpoint(self):
        """Test GET /vehicle_info endpoint."""
        # Setup
        self.api.vehicle_info = VehicleInfo(
            make="Toyota",
            model="Camry",
            year=2020,
            vin="1234567890"
        )
        
        # Test
        response = self.client.get("/vehicle_info")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["make"], "Toyota")
        self.assertEqual(data["model"], "Camry")
        self.assertEqual(data["year"], 2020)
        self.assertEqual(data["vin"], "1234567890")
        
    def test_vehicle_info_put_endpoint(self):
        """Test PUT /vehicle_info endpoint."""
        # Test
        response = self.client.put(
            "/vehicle_info",
            json={
                "make": "Honda",
                "model": "Accord",
                "year": 2021,
                "vin": "0987654321"
            }
        )
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["make"], "Honda")
        self.assertEqual(data["model"], "Accord")
        self.assertEqual(data["year"], 2021)
        self.assertEqual(data["vin"], "0987654321")
        self.assertEqual(self.api.vehicle_info.make, "Honda")
        self.assertEqual(self.api.vehicle_info.model, "Accord")
        
    def test_stream_start_endpoint(self):
        """Test /stream/start endpoint."""
        # Setup
        self.mock_data_stream.streaming = False
        self.mock_data_stream.add_commands.return_value = ["RPM", "SPEED"]
        self.mock_data_stream.start = Mock(return_value=True)
        self.mock_data_stream.commands = ["RPM", "SPEED"]
        
        # Test
        response = self.client.post("/stream/start?commands=RPM&commands=SPEED&interval=0.5")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["commands"], ["RPM", "SPEED"])
        self.mock_data_stream.add_commands.assert_called_once()
        self.mock_data_stream.start.assert_called_once()
        
    def test_stream_stop_endpoint(self):
        """Test /stream/stop endpoint."""
        # Setup
        self.mock_data_stream.streaming = True
        self.mock_data_stream.stop = Mock()
        
        # Test
        response = self.client.post("/stream/stop")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.mock_data_stream.stop.assert_called_once()
        
    def test_stream_status_endpoint(self):
        """Test /stream/status endpoint."""
        # Setup
        self.mock_data_stream.streaming = True
        self.mock_data_stream.commands = ["RPM", "SPEED"]
        self.mock_data_stream.interval = 0.5
        self.mock_websocket_streamer.active_connections = set([1, 2, 3])  # Mock 3 connections
        
        # Test
        response = self.client.get("/stream/status")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["active"])
        self.assertEqual(data["commands"], ["RPM", "SPEED"])
        self.assertEqual(data["interval"], 0.5)
        self.assertEqual(data["connections"], 3)
        
    def test_stream_commands_endpoint(self):
        """Test /stream/commands endpoint."""
        # Setup
        self.mock_data_stream.add_commands.return_value = ["RPM"]
        self.mock_data_stream.commands = ["RPM", "SPEED"]
        
        # Test
        response = self.client.post("/stream/commands?commands=RPM&action=add")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["added"], ["RPM"])
        self.assertEqual(data["commands"], ["RPM", "SPEED"])
        
    def test_stream_threshold_endpoint(self):
        """Test /stream/threshold endpoint."""
        # Setup
        self.mock_data_stream.set_threshold.return_value = True
        
        # Test
        response = self.client.post("/stream/threshold?command=RPM&min_value=500&max_value=5000")
        
        # Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["command"], "RPM")
        self.assertEqual(data["threshold"]["min"], 500)
        self.assertEqual(data["threshold"]["max"], 5000)
        self.mock_data_stream.set_threshold.assert_called_once_with("RPM", 500, 5000)


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for the location module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime
import time

from fourpoints.location import LocationTracker, GpsCoordinates, LocationSource, TripData


class TestLocationTracker(unittest.TestCase):
    """Test cases for LocationTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock GPS clients
        self.mock_gpsd_client = Mock()
        self.mock_serial_client = Mock()
        
        # Create location tracker
        self.location_tracker = LocationTracker()
        
        # Replace actual clients with mocks
        self.location_tracker._gpsd_client = self.mock_gpsd_client
        self.location_tracker._serial_client = self.mock_serial_client
        
    def test_init(self):
        """Test initialization."""
        # Verify
        self.assertEqual(self.location_tracker.source, LocationSource.NONE)
        self.assertIsNone(self.location_tracker.current_location)
        self.assertEqual(self.location_tracker.trip_data.distance, 0.0)
        
    def test_start_tracking_gpsd(self):
        """Test starting tracking with GPSD."""
        # Setup
        self.mock_gpsd_client.connect = Mock(return_value=True)
        
        # Test
        result = self.location_tracker.start_tracking(source=LocationSource.GPSD)
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(self.location_tracker.source, LocationSource.GPSD)
        self.mock_gpsd_client.connect.assert_called_once()
        
    def test_start_tracking_serial(self):
        """Test starting tracking with serial GPS."""
        # Setup
        self.mock_serial_client.connect = Mock(return_value=True)
        
        # Test
        result = self.location_tracker.start_tracking(source=LocationSource.SERIAL, port="/dev/ttyUSB0")
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(self.location_tracker.source, LocationSource.SERIAL)
        self.mock_serial_client.connect.assert_called_once_with("/dev/ttyUSB0")
        
    def test_start_tracking_mock(self):
        """Test starting tracking with mock location."""
        # Test
        result = self.location_tracker.start_tracking(source=LocationSource.MOCK)
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(self.location_tracker.source, LocationSource.MOCK)
        
    def test_start_tracking_failure(self):
        """Test starting tracking with failure."""
        # Setup
        self.mock_gpsd_client.connect = Mock(return_value=False)
        
        # Test
        result = self.location_tracker.start_tracking(source=LocationSource.GPSD)
        
        # Verify
        self.assertFalse(result)
        self.assertEqual(self.location_tracker.source, LocationSource.NONE)
        
    def test_stop_tracking(self):
        """Test stopping tracking."""
        # Setup
        self.location_tracker.source = LocationSource.GPSD
        self.mock_gpsd_client.disconnect = Mock()
        
        # Test
        self.location_tracker.stop_tracking()
        
        # Verify
        self.assertEqual(self.location_tracker.source, LocationSource.NONE)
        self.mock_gpsd_client.disconnect.assert_called_once()
        
    def test_get_current_location_gpsd(self):
        """Test getting current location from GPSD."""
        # Setup
        self.location_tracker.source = LocationSource.GPSD
        mock_location = GpsCoordinates(latitude=37.7749, longitude=-122.4194)
        self.mock_gpsd_client.get_current_position = Mock(return_value=mock_location)
        
        # Test
        location = self.location_tracker.get_current_location()
        
        # Verify
        self.assertEqual(location, mock_location)
        self.mock_gpsd_client.get_current_position.assert_called_once()
        
    def test_get_current_location_serial(self):
        """Test getting current location from serial GPS."""
        # Setup
        self.location_tracker.source = LocationSource.SERIAL
        mock_location = GpsCoordinates(latitude=37.7749, longitude=-122.4194)
        self.mock_serial_client.get_current_position = Mock(return_value=mock_location)
        
        # Test
        location = self.location_tracker.get_current_location()
        
        # Verify
        self.assertEqual(location, mock_location)
        self.mock_serial_client.get_current_position.assert_called_once()
        
    def test_get_current_location_mock(self):
        """Test getting current location from mock."""
        # Setup
        self.location_tracker.source = LocationSource.MOCK
        
        # Test
        location = self.location_tracker.get_current_location()
        
        # Verify
        self.assertIsNotNone(location)
        self.assertIsInstance(location, GpsCoordinates)
        
    def test_get_current_location_none(self):
        """Test getting current location when not tracking."""
        # Setup
        self.location_tracker.source = LocationSource.NONE
        
        # Test
        location = self.location_tracker.get_current_location()
        
        # Verify
        self.assertIsNone(location)
        
    def test_update_trip_data(self):
        """Test updating trip data."""
        # Setup
        self.location_tracker.source = LocationSource.MOCK
        self.location_tracker.current_location = GpsCoordinates(latitude=37.7749, longitude=-122.4194)
        new_location = GpsCoordinates(latitude=37.7750, longitude=-122.4195)
        
        # Test
        self.location_tracker._update_trip_data(new_location)
        
        # Verify
        self.assertGreater(self.location_tracker.trip_data.distance, 0.0)
        self.assertEqual(self.location_tracker.current_location, new_location)
        
    def test_calculate_distance(self):
        """Test calculating distance between coordinates."""
        # Setup
        loc1 = GpsCoordinates(latitude=37.7749, longitude=-122.4194)
        loc2 = GpsCoordinates(latitude=37.7750, longitude=-122.4195)
        
        # Test
        distance = self.location_tracker._calculate_distance(loc1, loc2)
        
        # Verify
        self.assertGreater(distance, 0.0)
        
    def test_reset_trip(self):
        """Test resetting trip data."""
        # Setup
        self.location_tracker.trip_data.distance = 100.0
        self.location_tracker.trip_data.start_time = datetime(2023, 1, 1)
        
        # Test
        self.location_tracker.reset_trip()
        
        # Verify
        self.assertEqual(self.location_tracker.trip_data.distance, 0.0)
        self.assertIsNotNone(self.location_tracker.trip_data.start_time)
        self.assertGreaterEqual(self.location_tracker.trip_data.start_time, datetime.now().replace(microsecond=0))
        
    def test_get_trip_data(self):
        """Test getting trip data."""
        # Setup
        self.location_tracker.trip_data.distance = 100.0
        self.location_tracker.trip_data.start_time = datetime(2023, 1, 1)
        
        # Test
        trip_data = self.location_tracker.get_trip_data()
        
        # Verify
        self.assertEqual(trip_data.distance, 100.0)
        self.assertEqual(trip_data.start_time, datetime(2023, 1, 1))
        
    def test_get_average_speed(self):
        """Test getting average speed."""
        # Setup
        self.location_tracker.trip_data.distance = 100.0  # 100 km
        self.location_tracker.trip_data.start_time = datetime.now().replace(microsecond=0)
        time.sleep(0.1)  # Small delay
        
        # Test
        avg_speed = self.location_tracker.get_average_speed()
        
        # Verify
        self.assertGreater(avg_speed, 0.0)
        
    def test_get_average_speed_no_distance(self):
        """Test getting average speed with no distance."""
        # Setup
        self.location_tracker.trip_data.distance = 0.0
        
        # Test
        avg_speed = self.location_tracker.get_average_speed()
        
        # Verify
        self.assertEqual(avg_speed, 0.0)


class TestGpsCoordinates(unittest.TestCase):
    """Test cases for GpsCoordinates."""
    
    def test_init(self):
        """Test initialization."""
        # Test
        coords = GpsCoordinates(latitude=37.7749, longitude=-122.4194, altitude=10.0, speed=60.0, timestamp=datetime.now())
        
        # Verify
        self.assertEqual(coords.latitude, 37.7749)
        self.assertEqual(coords.longitude, -122.4194)
        self.assertEqual(coords.altitude, 10.0)
        self.assertEqual(coords.speed, 60.0)
        self.assertIsNotNone(coords.timestamp)
        
    def test_to_dict(self):
        """Test to_dict method."""
        # Setup
        timestamp = datetime.now()
        coords = GpsCoordinates(latitude=37.7749, longitude=-122.4194, altitude=10.0, speed=60.0, timestamp=timestamp)
        
        # Test
        data = coords.to_dict()
        
        # Verify
        self.assertEqual(data["latitude"], 37.7749)
        self.assertEqual(data["longitude"], -122.4194)
        self.assertEqual(data["altitude"], 10.0)
        self.assertEqual(data["speed"], 60.0)
        self.assertEqual(data["timestamp"], timestamp.isoformat())
        
    def test_from_dict(self):
        """Test from_dict method."""
        # Setup
        timestamp = datetime.now()
        data = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "altitude": 10.0,
            "speed": 60.0,
            "timestamp": timestamp.isoformat()
        }
        
        # Test
        coords = GpsCoordinates.from_dict(data)
        
        # Verify
        self.assertEqual(coords.latitude, 37.7749)
        self.assertEqual(coords.longitude, -122.4194)
        self.assertEqual(coords.altitude, 10.0)
        self.assertEqual(coords.speed, 60.0)
        self.assertEqual(coords.timestamp.isoformat(), timestamp.isoformat())
        
    def test_str(self):
        """Test string representation."""
        # Setup
        coords = GpsCoordinates(latitude=37.7749, longitude=-122.4194)
        
        # Test
        string = str(coords)
        
        # Verify
        self.assertIn("37.7749", string)
        self.assertIn("-122.4194", string)


if __name__ == '__main__':
    unittest.main()

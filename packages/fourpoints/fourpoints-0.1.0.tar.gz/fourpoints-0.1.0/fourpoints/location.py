"""
Location Module for FourPoints.

This module provides GPS and location-related functionality for vehicle tracking
and geospatial analysis.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import threading
import datetime

logger = logging.getLogger(__name__)

@dataclass
class GpsCoordinates:
    """Data class for GPS coordinates."""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    timestamp: Optional[datetime.datetime] = None
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class LocationTracker:
    """
    Tracks and manages vehicle location data.
    """
    
    def __init__(self, gps_device: Optional[str] = None):
        """
        Initialize the location tracker.
        
        Args:
            gps_device: Path to GPS device (e.g., '/dev/ttyUSB1')
        """
        self.gps_device = gps_device
        self.current_location = None
        self.location_history = []
        self.max_history_size = 1000  # Maximum number of location points to store
        self.tracking = False
        self._tracking_thread = None
        self._lock = threading.Lock()
        
        # Try to import GPS libraries
        try:
            import gpsd
            self.gpsd = gpsd
            self.gpsd_available = True
        except ImportError:
            logger.warning("gpsd-py3 library not installed. Install with 'pip install gpsd-py3' for GPS support.")
            self.gpsd = None
            self.gpsd_available = False
            
        try:
            import pynmea2
            self.pynmea2 = pynmea2
            self.pynmea2_available = True
        except ImportError:
            logger.warning("pynmea2 library not installed. Install with 'pip install pynmea2' for NMEA parsing.")
            self.pynmea2 = None
            self.pynmea2_available = False
            
    def connect_gpsd(self, host: str = "localhost", port: int = 2947) -> bool:
        """
        Connect to GPSD daemon.
        
        Args:
            host: GPSD host
            port: GPSD port
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.gpsd_available:
            logger.error("gpsd-py3 library not available")
            return False
            
        try:
            self.gpsd.connect(host=host, port=port)
            logger.info(f"Connected to GPSD at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to GPSD: {str(e)}")
            return False
            
    def connect_serial(self, port: str, baudrate: int = 9600) -> bool:
        """
        Connect to GPS device via serial port.
        
        Args:
            port: Serial port
            baudrate: Baud rate
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.pynmea2_available:
            logger.error("pynmea2 library not available")
            return False
            
        try:
            import serial
            self.serial_port = serial.Serial(port, baudrate)
            self.gps_device = port
            logger.info(f"Connected to GPS device at {port}")
            return True
        except ImportError:
            logger.error("pyserial library not installed. Install with 'pip install pyserial'")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to GPS device: {str(e)}")
            return False
            
    def get_current_location(self) -> Optional[GpsCoordinates]:
        """
        Get the current GPS location.
        
        Returns:
            Optional[GpsCoordinates]: Current GPS coordinates or None if not available
        """
        if self.gpsd_available:
            try:
                self.gpsd.get_current()
                packet = self.gpsd.get_current()
                
                if packet.mode >= 2:  # 2D or 3D fix
                    coords = GpsCoordinates(
                        latitude=packet.lat,
                        longitude=packet.lon,
                        altitude=packet.alt if packet.mode >= 3 else None,
                        timestamp=datetime.datetime.now()
                    )
                    
                    with self._lock:
                        self.current_location = coords
                        self.location_history.append(coords)
                        if len(self.location_history) > self.max_history_size:
                            self.location_history.pop(0)
                            
                    return coords
                else:
                    logger.warning("No GPS fix available")
                    return None
                    
            except Exception as e:
                logger.error(f"Error getting GPS location from GPSD: {str(e)}")
                return None
                
        elif self.pynmea2_available and hasattr(self, 'serial_port'):
            try:
                line = self.serial_port.readline().decode('ascii', errors='replace')
                if line.startswith('$'):
                    try:
                        msg = self.pynmea2.parse(line)
                        if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                            coords = GpsCoordinates(
                                latitude=msg.latitude,
                                longitude=msg.longitude,
                                altitude=msg.altitude if hasattr(msg, 'altitude') else None,
                                timestamp=datetime.datetime.now()
                            )
                            
                            with self._lock:
                                self.current_location = coords
                                self.location_history.append(coords)
                                if len(self.location_history) > self.max_history_size:
                                    self.location_history.pop(0)
                                    
                            return coords
                    except Exception as e:
                        logger.debug(f"Error parsing NMEA sentence: {str(e)}")
                        
                return None
                
            except Exception as e:
                logger.error(f"Error reading from GPS device: {str(e)}")
                return None
                
        else:
            logger.error("No GPS connection available")
            return None
            
    def start_tracking(self, interval: float = 1.0) -> bool:
        """
        Start continuous location tracking.
        
        Args:
            interval: Interval between location updates in seconds
            
        Returns:
            bool: True if tracking started successfully, False otherwise
        """
        if self.tracking:
            logger.warning("Location tracking already active")
            return True
            
        if not (self.gpsd_available or (self.pynmea2_available and hasattr(self, 'serial_port'))):
            logger.error("No GPS connection available")
            return False
            
        self.tracking = True
        self._tracking_thread = threading.Thread(
            target=self._tracking_loop,
            args=(interval,),
            daemon=True
        )
        self._tracking_thread.start()
        logger.info(f"Location tracking started with interval {interval}s")
        return True
        
    def stop_tracking(self) -> None:
        """Stop continuous location tracking."""
        self.tracking = False
        if self._tracking_thread:
            self._tracking_thread.join(timeout=2.0)
            logger.info("Location tracking stopped")
            
    def _tracking_loop(self, interval: float) -> None:
        """
        Background thread for continuous location tracking.
        
        Args:
            interval: Interval between location updates in seconds
        """
        while self.tracking:
            try:
                self.get_current_location()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in location tracking loop: {str(e)}")
                time.sleep(interval)
                
    def get_location_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get location history.
        
        Args:
            limit: Maximum number of history points to return
            
        Returns:
            List[Dict[str, Any]]: List of location history points
        """
        with self._lock:
            history = self.location_history.copy()
            
        if limit is not None and limit > 0:
            history = history[-limit:]
            
        return [loc.to_dict() for loc in history]
        
    def calculate_distance(self, coord1: GpsCoordinates, coord2: GpsCoordinates) -> float:
        """
        Calculate distance between two GPS coordinates in kilometers.
        
        Args:
            coord1: First GPS coordinate
            coord2: Second GPS coordinate
            
        Returns:
            float: Distance in kilometers
        """
        import math
        
        # Haversine formula
        R = 6371.0  # Earth radius in kilometers
        
        lat1_rad = math.radians(coord1.latitude)
        lon1_rad = math.radians(coord1.longitude)
        lat2_rad = math.radians(coord2.latitude)
        lon2_rad = math.radians(coord2.longitude)
        
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
        
    def calculate_trip_distance(self) -> float:
        """
        Calculate total trip distance in kilometers.
        
        Returns:
            float: Total trip distance in kilometers
        """
        with self._lock:
            history = self.location_history.copy()
            
        if len(history) < 2:
            return 0.0
            
        total_distance = 0.0
        for i in range(1, len(history)):
            total_distance += self.calculate_distance(history[i-1], history[i])
            
        return total_distance
        
    def get_location_data(self) -> Dict[str, Any]:
        """
        Get comprehensive location data.
        
        Returns:
            Dict[str, Any]: Location data including current position and trip statistics
        """
        current = self.current_location.to_dict() if self.current_location else None
        trip_distance = self.calculate_trip_distance()
        
        return {
            "current_location": current,
            "trip_distance_km": trip_distance,
            "tracking_active": self.tracking,
            "history_points": len(self.location_history),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    def mock_location(self, latitude: float, longitude: float, altitude: Optional[float] = None) -> None:
        """
        Set a mock location for testing purposes.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            altitude: Altitude (optional)
        """
        coords = GpsCoordinates(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            timestamp=datetime.datetime.now()
        )
        
        with self._lock:
            self.current_location = coords
            self.location_history.append(coords)
            if len(self.location_history) > self.max_history_size:
                self.location_history.pop(0)
                
        logger.info(f"Mock location set: {latitude}, {longitude}")
        
    def mock_trip(self, coordinates: List[Tuple[float, float, Optional[float]]]) -> None:
        """
        Set a mock trip for testing purposes.
        
        Args:
            coordinates: List of (latitude, longitude, altitude) tuples
        """
        with self._lock:
            self.location_history = []
            
            for lat, lon, alt in coordinates:
                coords = GpsCoordinates(
                    latitude=lat,
                    longitude=lon,
                    altitude=alt,
                    timestamp=datetime.datetime.now()
                )
                self.location_history.append(coords)
                
            if self.location_history:
                self.current_location = self.location_history[-1]
                
        logger.info(f"Mock trip set with {len(coordinates)} points")

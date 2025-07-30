"""
OBD-II Client Module for FourPoints.

This module handles communication with OBD-II adapters (ELM327) via USB and Bluetooth.
It provides functionality for connecting to the vehicle, reading real-time data,
and retrieving diagnostic trouble codes.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
import obd
from obd import OBDStatus, OBDCommand
from obd.protocols import ECU
from obd.utils import BitArray

logger = logging.getLogger(__name__)

class OBDClient:
    """
    Client for communicating with OBD-II adapters (ELM327).
    Supports both USB and Bluetooth connections.
    """
    
    def __init__(self, connection_type: str = "auto", port: Optional[str] = None, 
                 baudrate: int = 38400, timeout: float = 30, fast: bool = True):
        """
        Initialize the OBD client.
        
        Args:
            connection_type: Type of connection ('auto', 'usb', 'bluetooth')
            port: Port to connect to (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Baud rate for serial communication
            timeout: Connection timeout in seconds
            fast: Whether to use fast mode (skips the search for unused PIDs)
        """
        self.connection_type = connection_type
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.fast = fast
        self.connection = None
        self.is_connected = False
        self.supported_commands = {}
        
    def connect(self) -> bool:
        """
        Connect to the OBD-II adapter.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # If port is not specified, auto-detect
            if self.port is None:
                ports = obd.scan_serial()
                if not ports:
                    logger.error("No OBD-II adapters found")
                    return False
                self.port = ports[0]
                
            # Connect to the adapter
            self.connection = obd.OBD(
                portstr=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                fast=self.fast
            )
            
            # Check if connection is successful
            if self.connection.status() == OBDStatus.CAR_CONNECTED:
                self.is_connected = True
                logger.info(f"Connected to OBD-II adapter at {self.port}")
                self._cache_supported_commands()
                return True
            else:
                logger.error(f"Failed to connect to vehicle: {self.connection.status()}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to OBD-II adapter: {str(e)}")
            return False
            
    def disconnect(self) -> None:
        """Disconnect from the OBD-II adapter."""
        if self.connection:
            self.connection.close()
            self.is_connected = False
            logger.info("Disconnected from OBD-II adapter")
            
    def _cache_supported_commands(self) -> None:
        """Cache the supported OBD commands for faster access."""
        if not self.is_connected:
            return
            
        self.supported_commands = {}
        for command in self.connection.supported_commands:
            self.supported_commands[command.name] = command
            
    def get_supported_commands(self) -> List[str]:
        """
        Get a list of supported OBD commands.
        
        Returns:
            List[str]: List of supported command names
        """
        return list(self.supported_commands.keys())
        
    def query(self, command_name: str) -> Optional[obd.OBDResponse]:
        """
        Query a specific OBD command.
        
        Args:
            command_name: Name of the OBD command to query
            
        Returns:
            Optional[obd.OBDResponse]: Response from the OBD adapter or None if command not supported
        """
        if not self.is_connected:
            logger.error("Not connected to OBD-II adapter")
            return None
            
        if command_name in self.supported_commands:
            cmd = self.supported_commands[command_name]
            return self.connection.query(cmd)
        else:
            logger.warning(f"Command '{command_name}' not supported by vehicle")
            return None
            
    def get_dtcs(self) -> List[str]:
        """
        Get Diagnostic Trouble Codes (DTCs) from the vehicle.
        
        Returns:
            List[str]: List of DTCs
        """
        if not self.is_connected:
            logger.error("Not connected to OBD-II adapter")
            return []
            
        response = self.connection.query(obd.commands.GET_DTC)
        if response.is_null():
            return []
        return response.value
        
    def clear_dtcs(self) -> bool:
        """
        Clear Diagnostic Trouble Codes (DTCs) and Check Engine Light (CEL).
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected:
            logger.error("Not connected to OBD-II adapter")
            return False
            
        response = self.connection.query(obd.commands.CLEAR_DTC)
        return not response.is_null()
        
    def get_real_time_data(self) -> Dict[str, Any]:
        """
        Get real-time data from the vehicle.
        
        Returns:
            Dict[str, Any]: Dictionary of real-time data
        """
        if not self.is_connected:
            logger.error("Not connected to OBD-II adapter")
            return {}
            
        data = {}
        important_commands = [
            "RPM", "SPEED", "THROTTLE_POS", "ENGINE_LOAD", "COOLANT_TEMP",
            "INTAKE_TEMP", "MAF", "FUEL_LEVEL", "FUEL_PRESSURE", "OIL_TEMP",
            "BAROMETRIC_PRESSURE", "AMBIANT_AIR_TEMP", "FUEL_RATE"
        ]
        
        for cmd_name in important_commands:
            if cmd_name in self.supported_commands:
                response = self.query(cmd_name)
                if response and not response.is_null():
                    data[cmd_name] = {
                        "value": response.value.magnitude if hasattr(response.value, "magnitude") else response.value,
                        "unit": response.value.units if hasattr(response.value, "units") else None
                    }
                    
        return data
        
    def get_sensor_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of key sensors.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of sensor statuses
        """
        if not self.is_connected:
            logger.error("Not connected to OBD-II adapter")
            return {}
            
        sensor_commands = [
            "O2_SENSORS", "O2_B1S1", "O2_B1S2", "O2_B2S1", "O2_B2S2",
            "CATALYST_TEMP_B1S1", "CATALYST_TEMP_B2S1", "CONTROL_MODULE_VOLTAGE",
            "FUEL_RAIL_PRESSURE_ABS", "FUEL_RAIL_PRESSURE_VAC", "FUEL_RAIL_TEMP",
            "INTAKE_PRESSURE", "TIMING_ADVANCE", "EGR_ERROR"
        ]
        
        sensors = {}
        for cmd_name in sensor_commands:
            if cmd_name in self.supported_commands:
                response = self.query(cmd_name)
                if response and not response.is_null():
                    sensors[cmd_name] = {
                        "value": response.value.magnitude if hasattr(response.value, "magnitude") else response.value,
                        "unit": response.value.units if hasattr(response.value, "units") else None,
                        "status": "OK"  # Default status, will be analyzed in analytics module
                    }
                    
        return sensors

    async def stream_data(self, command_names: List[str], callback, interval: float = 0.1):
        """
        Stream real-time data asynchronously.
        
        Args:
            command_names: List of OBD command names to stream
            callback: Callback function to process the data
            interval: Interval between queries in seconds
        """
        if not self.is_connected:
            logger.error("Not connected to OBD-II adapter")
            return
            
        commands = []
        for cmd_name in command_names:
            if cmd_name in self.supported_commands:
                commands.append(self.supported_commands[cmd_name])
            else:
                logger.warning(f"Command '{cmd_name}' not supported by vehicle")
                
        if not commands:
            logger.error("No supported commands to stream")
            return
            
        try:
            while True:
                data = {}
                for cmd in commands:
                    response = self.connection.query(cmd)
                    if not response.is_null():
                        data[cmd.name] = {
                            "value": response.value.magnitude if hasattr(response.value, "magnitude") else response.value,
                            "unit": response.value.units if hasattr(response.value, "units") else None
                        }
                        
                await callback(data)
                await asyncio.sleep(interval)
                
        except asyncio.CancelledError:
            logger.info("Data streaming cancelled")
        except Exception as e:
            logger.error(f"Error during data streaming: {str(e)}")


class BluetoothLEClient:
    """
    Client for communicating with OBD-II adapters via Bluetooth Low Energy (BLE).
    This is a bonus implementation for BLE compatibility.
    """
    
    def __init__(self, device_name: Optional[str] = None, device_address: Optional[str] = None):
        """
        Initialize the BLE client.
        
        Args:
            device_name: Name of the BLE device to connect to
            device_address: MAC address of the BLE device
        """
        self.device_name = device_name
        self.device_address = device_address
        self.client = None
        self.is_connected = False
        
        # Import BLE library only when needed
        try:
            import bleak
            self.bleak = bleak
        except ImportError:
            logger.error("Bleak library not installed. Install with 'pip install bleak' for BLE support.")
            self.bleak = None
            
    async def scan_for_devices(self, timeout: float = 5.0) -> List[Dict[str, Any]]:
        """
        Scan for available BLE devices.
        
        Args:
            timeout: Scan timeout in seconds
            
        Returns:
            List[Dict[str, Any]]: List of discovered devices with name and address
        """
        if not self.bleak:
            logger.error("Bleak library not available")
            return []
            
        try:
            devices = await self.bleak.BleakScanner.discover(timeout=timeout)
            return [{"name": d.name, "address": d.address} for d in devices if d.name]
        except Exception as e:
            logger.error(f"Error scanning for BLE devices: {str(e)}")
            return []
            
    async def connect(self) -> bool:
        """
        Connect to the BLE OBD-II adapter.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.bleak:
            logger.error("Bleak library not available")
            return False
            
        try:
            # If no device specified, scan for devices
            if not self.device_address:
                devices = await self.scan_for_devices()
                if not devices:
                    logger.error("No BLE devices found")
                    return False
                    
                # Try to find a device that looks like an OBD adapter
                obd_devices = [d for d in devices if any(x in d["name"].lower() for x in ["obd", "elm", "car", "auto"])]
                if obd_devices:
                    self.device_address = obd_devices[0]["address"]
                    self.device_name = obd_devices[0]["name"]
                else:
                    self.device_address = devices[0]["address"]
                    self.device_name = devices[0]["name"]
                    
            # Connect to the device
            self.client = self.bleak.BleakClient(self.device_address)
            await self.client.connect()
            self.is_connected = self.client.is_connected
            
            if self.is_connected:
                logger.info(f"Connected to BLE device: {self.device_name} ({self.device_address})")
                return True
            else:
                logger.error("Failed to connect to BLE device")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to BLE device: {str(e)}")
            return False
            
    async def disconnect(self) -> None:
        """Disconnect from the BLE device."""
        if self.client and self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            logger.info(f"Disconnected from BLE device: {self.device_name}")
            
    # Additional BLE-specific methods would be implemented here
    # This is a placeholder for the bonus BLE compatibility feature

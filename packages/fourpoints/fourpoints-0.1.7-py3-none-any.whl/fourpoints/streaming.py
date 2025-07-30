"""
Streaming Module for FourPoints.

This module provides asyncio support for real-time data streaming from the vehicle.
It allows for continuous monitoring of vehicle telemetry with event-based callbacks.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union, Set
import time
import json
from datetime import datetime
from functools import partial

from .obd_client import OBDClient

logger = logging.getLogger(__name__)

class DataStreamEvent:
    """Event types for data streaming."""
    DATA_RECEIVED = "data_received"
    STREAM_STARTED = "stream_started"
    STREAM_STOPPED = "stream_stopped"
    ERROR = "error"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    CONNECTION_LOST = "connection_lost"
    CONNECTION_RESTORED = "connection_restored"


class DataPoint:
    """Class representing a single data point from the vehicle."""
    
    def __init__(self, command_name: str, value: Any, unit: Optional[str] = None, 
                 timestamp: Optional[datetime] = None):
        """
        Initialize a data point.
        
        Args:
            command_name: Name of the OBD command
            value: Value of the data point
            unit: Unit of measurement
            timestamp: Timestamp of the data point
        """
        self.command_name = command_name
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command": self.command_name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat()
        }
        
    def __str__(self) -> str:
        """String representation."""
        return f"{self.command_name}: {self.value} {self.unit or ''} @ {self.timestamp.isoformat()}"


class DataStream:
    """
    Class for streaming real-time data from the vehicle using asyncio.
    """
    
    def __init__(self, obd_client: OBDClient):
        """
        Initialize the data stream.
        
        Args:
            obd_client: OBD client instance
        """
        self.obd_client = obd_client
        self.streaming = False
        self.commands = []
        self.interval = 0.1  # Default interval in seconds
        self.event_handlers = {
            DataStreamEvent.DATA_RECEIVED: [],
            DataStreamEvent.STREAM_STARTED: [],
            DataStreamEvent.STREAM_STOPPED: [],
            DataStreamEvent.ERROR: [],
            DataStreamEvent.THRESHOLD_EXCEEDED: [],
            DataStreamEvent.CONNECTION_LOST: [],
            DataStreamEvent.CONNECTION_RESTORED: []
        }
        self.thresholds = {}  # {command_name: {"min": value, "max": value}}
        self._stream_task = None
        self._connection_monitor_task = None
        self._last_connection_status = False
        
    def add_command(self, command_name: str) -> bool:
        """
        Add a command to the stream.
        
        Args:
            command_name: Name of the OBD command
            
        Returns:
            bool: True if command was added, False otherwise
        """
        if not self.obd_client.is_connected:
            logger.error("Cannot add command: OBD client not connected")
            return False
            
        if command_name in self.obd_client.supported_commands:
            if command_name not in self.commands:
                self.commands.append(command_name)
                logger.debug(f"Added command to stream: {command_name}")
            return True
        else:
            logger.warning(f"Command not supported by vehicle: {command_name}")
            return False
            
    def add_commands(self, command_names: List[str]) -> List[str]:
        """
        Add multiple commands to the stream.
        
        Args:
            command_names: List of OBD command names
            
        Returns:
            List[str]: List of commands that were successfully added
        """
        added = []
        for cmd in command_names:
            if self.add_command(cmd):
                added.append(cmd)
        return added
        
    def remove_command(self, command_name: str) -> bool:
        """
        Remove a command from the stream.
        
        Args:
            command_name: Name of the OBD command
            
        Returns:
            bool: True if command was removed, False otherwise
        """
        if command_name in self.commands:
            self.commands.remove(command_name)
            logger.debug(f"Removed command from stream: {command_name}")
            return True
        return False
        
    def set_threshold(self, command_name: str, min_value: Optional[float] = None, 
                     max_value: Optional[float] = None) -> bool:
        """
        Set a threshold for a command.
        
        Args:
            command_name: Name of the OBD command
            min_value: Minimum threshold value
            max_value: Maximum threshold value
            
        Returns:
            bool: True if threshold was set, False otherwise
        """
        if command_name not in self.obd_client.supported_commands:
            logger.warning(f"Cannot set threshold: Command not supported: {command_name}")
            return False
            
        if min_value is None and max_value is None:
            logger.warning("Cannot set threshold: Both min and max values are None")
            return False
            
        if command_name not in self.thresholds:
            self.thresholds[command_name] = {}
            
        if min_value is not None:
            self.thresholds[command_name]["min"] = min_value
            
        if max_value is not None:
            self.thresholds[command_name]["max"] = max_value
            
        logger.debug(f"Set threshold for {command_name}: min={min_value}, max={max_value}")
        return True
        
    def remove_threshold(self, command_name: str) -> bool:
        """
        Remove a threshold for a command.
        
        Args:
            command_name: Name of the OBD command
            
        Returns:
            bool: True if threshold was removed, False otherwise
        """
        if command_name in self.thresholds:
            del self.thresholds[command_name]
            logger.debug(f"Removed threshold for {command_name}")
            return True
        return False
        
    def on(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler.
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
            logger.debug(f"Registered handler for event: {event_type}")
        else:
            logger.warning(f"Unknown event type: {event_type}")
            
    def off(self, event_type: str, handler: Optional[Callable] = None) -> None:
        """
        Unregister an event handler.
        
        Args:
            event_type: Type of event
            handler: Event handler function (if None, all handlers for the event are removed)
        """
        if event_type in self.event_handlers:
            if handler is None:
                self.event_handlers[event_type] = []
                logger.debug(f"Removed all handlers for event: {event_type}")
            elif handler in self.event_handlers[event_type]:
                self.event_handlers[event_type].remove(handler)
                logger.debug(f"Removed handler for event: {event_type}")
        else:
            logger.warning(f"Unknown event type: {event_type}")
            
    def _emit(self, event_type: str, data: Any = None) -> None:
        """
        Emit an event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if data is not None:
                        handler(data)
                    else:
                        handler()
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {str(e)}")
                    
    def _check_thresholds(self, data_point: DataPoint) -> None:
        """
        Check if a data point exceeds any thresholds.
        
        Args:
            data_point: Data point to check
        """
        command_name = data_point.command_name
        if command_name in self.thresholds:
            threshold = self.thresholds[command_name]
            value = data_point.value
            
            if isinstance(value, (int, float)):
                min_exceeded = "min" in threshold and value < threshold["min"]
                max_exceeded = "max" in threshold and value > threshold["max"]
                
                if min_exceeded or max_exceeded:
                    self._emit(DataStreamEvent.THRESHOLD_EXCEEDED, {
                        "data_point": data_point,
                        "threshold": threshold,
                        "min_exceeded": min_exceeded,
                        "max_exceeded": max_exceeded
                    })
                    
    async def _stream_data(self) -> None:
        """Stream data from the vehicle."""
        if not self.commands:
            logger.warning("No commands to stream")
            return
            
        logger.info(f"Starting data stream with {len(self.commands)} commands")
        self._emit(DataStreamEvent.STREAM_STARTED)
        
        try:
            while self.streaming:
                data_points = []
                
                for cmd_name in self.commands:
                    try:
                        response = self.obd_client.query(cmd_name)
                        if response and not response.is_null():
                            value = response.value.magnitude if hasattr(response.value, "magnitude") else response.value
                            unit = response.value.units if hasattr(response.value, "units") else None
                            
                            data_point = DataPoint(cmd_name, value, unit)
                            data_points.append(data_point)
                            
                            # Check thresholds
                            self._check_thresholds(data_point)
                    except Exception as e:
                        logger.error(f"Error querying {cmd_name}: {str(e)}")
                        
                if data_points:
                    self._emit(DataStreamEvent.DATA_RECEIVED, data_points)
                    
                await asyncio.sleep(self.interval)
                
        except asyncio.CancelledError:
            logger.info("Data stream cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in data stream: {str(e)}")
            self._emit(DataStreamEvent.ERROR, str(e))
        finally:
            self._emit(DataStreamEvent.STREAM_STOPPED)
            
    async def _monitor_connection(self) -> None:
        """Monitor the OBD connection status."""
        try:
            while self.streaming:
                current_status = self.obd_client.is_connected
                
                if current_status != self._last_connection_status:
                    if current_status:
                        logger.info("OBD connection restored")
                        self._emit(DataStreamEvent.CONNECTION_RESTORED)
                    else:
                        logger.warning("OBD connection lost")
                        self._emit(DataStreamEvent.CONNECTION_LOST)
                        
                    self._last_connection_status = current_status
                    
                await asyncio.sleep(1.0)  # Check connection every second
                
        except asyncio.CancelledError:
            logger.debug("Connection monitor cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in connection monitor: {str(e)}")
            
    async def start(self, interval: float = 0.1) -> bool:
        """
        Start streaming data.
        
        Args:
            interval: Interval between queries in seconds
            
        Returns:
            bool: True if stream started successfully, False otherwise
        """
        if self.streaming:
            logger.warning("Data stream already active")
            return True
            
        if not self.obd_client.is_connected:
            connected = self.obd_client.connect()
            if not connected:
                logger.error("Failed to connect to vehicle")
                return False
                
        if not self.commands:
            logger.warning("No commands to stream")
            return False
            
        self.interval = interval
        self.streaming = True
        self._last_connection_status = self.obd_client.is_connected
        
        # Start streaming task
        self._stream_task = asyncio.create_task(self._stream_data())
        
        # Start connection monitor
        self._connection_monitor_task = asyncio.create_task(self._monitor_connection())
        
        return True
        
    async def stop(self) -> None:
        """Stop streaming data."""
        if not self.streaming:
            return
            
        self.streaming = False
        
        # Cancel tasks
        if self._stream_task:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass
            self._stream_task = None
            
        if self._connection_monitor_task:
            self._connection_monitor_task.cancel()
            try:
                await self._connection_monitor_task
            except asyncio.CancelledError:
                pass
            self._connection_monitor_task = None
            
        logger.info("Data stream stopped")


class WebSocketStreamer:
    """
    Class for streaming data over WebSocket using FastAPI and websockets.
    """
    
    def __init__(self, data_stream: DataStream):
        """
        Initialize the WebSocket streamer.
        
        Args:
            data_stream: DataStream instance
        """
        self.data_stream = data_stream
        self.active_connections = set()
        
    async def register(self, websocket) -> None:
        """
        Register a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
        """
        self.active_connections.add(websocket)
        
    async def unregister(self, websocket) -> None:
        """
        Unregister a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
        """
        self.active_connections.remove(websocket)
        
    async def send_data(self, data_points: List[DataPoint]) -> None:
        """
        Send data points to all active WebSocket connections.
        
        Args:
            data_points: List of data points
        """
        if not self.active_connections:
            return
            
        # Convert data points to JSON
        data = {
            "timestamp": datetime.now().isoformat(),
            "data": [dp.to_dict() for dp in data_points]
        }
        
        message = json.dumps(data)
        
        # Send to all connections
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending data to WebSocket: {str(e)}")
                await self.unregister(connection)
                
    async def send_event(self, event_type: str, data: Any = None) -> None:
        """
        Send an event to all active WebSocket connections.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if not self.active_connections:
            return
            
        # Create event message
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if data is not None:
            if isinstance(data, list) and all(isinstance(dp, DataPoint) for dp in data):
                event["data"] = [dp.to_dict() for dp in data]
            elif isinstance(data, dict):
                event["data"] = data
            else:
                event["data"] = str(data)
                
        message = json.dumps(event)
        
        # Send to all connections
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending event to WebSocket: {str(e)}")
                await self.unregister(connection)
                
    def setup_handlers(self) -> None:
        """Set up event handlers for the data stream."""
        # Set up handlers for data stream events
        self.data_stream.on(DataStreamEvent.DATA_RECEIVED, 
                          lambda data: asyncio.create_task(self.send_data(data)))
                          
        self.data_stream.on(DataStreamEvent.STREAM_STARTED,
                          lambda: asyncio.create_task(self.send_event(DataStreamEvent.STREAM_STARTED)))
                          
        self.data_stream.on(DataStreamEvent.STREAM_STOPPED,
                          lambda: asyncio.create_task(self.send_event(DataStreamEvent.STREAM_STOPPED)))
                          
        self.data_stream.on(DataStreamEvent.ERROR,
                          lambda data: asyncio.create_task(self.send_event(DataStreamEvent.ERROR, data)))
                          
        self.data_stream.on(DataStreamEvent.THRESHOLD_EXCEEDED,
                          lambda data: asyncio.create_task(self.send_event(DataStreamEvent.THRESHOLD_EXCEEDED, data)))
                          
        self.data_stream.on(DataStreamEvent.CONNECTION_LOST,
                          lambda: asyncio.create_task(self.send_event(DataStreamEvent.CONNECTION_LOST)))
                          
        self.data_stream.on(DataStreamEvent.CONNECTION_RESTORED,
                          lambda: asyncio.create_task(self.send_event(DataStreamEvent.CONNECTION_RESTORED)))
                          
    async def websocket_endpoint(self, websocket) -> None:
        """
        WebSocket endpoint for FastAPI.
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        await self.register(websocket)
        
        try:
            # Send initial event
            await self.send_event("connected", {
                "message": "Connected to FourPoints data stream",
                "available_commands": self.data_stream.obd_client.get_supported_commands()
            })
            
            # Handle incoming messages
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    await self.handle_message(message, websocket)
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
                    
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
        finally:
            await self.unregister(websocket)
            
    async def handle_message(self, message: Dict[str, Any], websocket) -> None:
        """
        Handle a message from a WebSocket client.
        
        Args:
            message: Message from client
            websocket: WebSocket connection
        """
        if not isinstance(message, dict) or "type" not in message:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Invalid message format"
            }))
            return
            
        msg_type = message.get("type")
        
        if msg_type == "subscribe":
            # Subscribe to commands
            commands = message.get("commands", [])
            if commands:
                added = self.data_stream.add_commands(commands)
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "commands": added
                }))
                
        elif msg_type == "unsubscribe":
            # Unsubscribe from commands
            commands = message.get("commands", [])
            removed = []
            for cmd in commands:
                if self.data_stream.remove_command(cmd):
                    removed.append(cmd)
                    
            await websocket.send_text(json.dumps({
                "type": "unsubscribed",
                "commands": removed
            }))
            
        elif msg_type == "set_threshold":
            # Set threshold for a command
            command = message.get("command")
            min_value = message.get("min")
            max_value = message.get("max")
            
            if command:
                success = self.data_stream.set_threshold(command, min_value, max_value)
                await websocket.send_text(json.dumps({
                    "type": "threshold_set",
                    "command": command,
                    "success": success
                }))
                
        elif msg_type == "remove_threshold":
            # Remove threshold for a command
            command = message.get("command")
            
            if command:
                success = self.data_stream.remove_threshold(command)
                await websocket.send_text(json.dumps({
                    "type": "threshold_removed",
                    "command": command,
                    "success": success
                }))
                
        elif msg_type == "get_supported_commands":
            # Get supported commands
            commands = self.data_stream.obd_client.get_supported_commands()
            await websocket.send_text(json.dumps({
                "type": "supported_commands",
                "commands": commands
            }))
            
        else:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Unknown message type: {msg_type}"
            }))

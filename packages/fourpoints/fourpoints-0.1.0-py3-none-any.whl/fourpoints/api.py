"""
API Module for FourPoints.

This module provides FastAPI endpoints for accessing vehicle telemetry,
diagnostics, health, maintenance, and report generation.
"""

import logging
import os
import json
import base64
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from enum import Enum

import fastapi
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Response, File, UploadFile, WebSocket
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel, Field

# Handle imports for both direct execution and module import
import sys
import os
from pathlib import Path

# Add parent directory to path for direct execution
if __name__ == "__main__":
    # Get the parent directory of the current file's directory
    parent_dir = str(Path(__file__).resolve().parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    # Use absolute imports when running as script
    from fourpoints.obd_client import OBDClient
    from fourpoints.analytics import Analytics
    from fourpoints.gemini_client import GeminiClient
    from fourpoints.location import LocationTracker
    from fourpoints.reports import ReportGenerator
    from fourpoints.streaming import DataStream, WebSocketStreamer
else:
    # Use relative imports when imported as a module
    from .obd_client import OBDClient
    from .analytics import Analytics
    from .gemini_client import GeminiClient
    from .location import LocationTracker
    from .reports import ReportGenerator
    from .streaming import DataStream, WebSocketStreamer

logger = logging.getLogger(__name__)

# Pydantic models for request/response
class VehicleInfo(BaseModel):
    """Vehicle information model."""
    vin: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    engine: Optional[str] = None
    odometer: Optional[float] = None
    odometer_unit: Optional[str] = "km"

class TelemetryData(BaseModel):
    """Telemetry data model."""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = {}

class DiagnosticTroubleCode(BaseModel):
    """Diagnostic trouble code model."""
    code: str
    description: str
    possible_causes: str
    severity: str

class DTCResponse(BaseModel):
    """DTC response model."""
    dtcs: List[DiagnosticTroubleCode] = []
    count: int = 0
    status: str = "Good"

class HealthResponse(BaseModel):
    """Health response model."""
    status: str
    issues: List[str] = []
    metrics: Dict[str, Any] = {}
    dtcs: List[str] = []
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class MaintenanceRecommendation(BaseModel):
    """Maintenance recommendation model."""
    component: str
    issue: str
    confidence: float
    recommendation: str

class MaintenanceResponse(BaseModel):
    """Maintenance response model."""
    recommendations: List[MaintenanceRecommendation] = []
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class SensorStatus(BaseModel):
    """Sensor status model."""
    value: Any
    unit: Optional[str] = None
    status: str
    message: str

class SensorsResponse(BaseModel):
    """Sensors response model."""
    sensors: Dict[str, SensorStatus] = {}
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ReportFormat(str, Enum):
    """Report format enum."""
    PDF = "pdf"
    HTML = "html"

class ReportResponse(BaseModel):
    """Report response model."""
    report_path: str
    format: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class APIConfig:
    """API configuration."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000,
                 obd_port: Optional[str] = None, obd_baudrate: int = 38400, obd_timeout: float = 30.0,
                 gemini_api_key: Optional[str] = None, gemini_model: str = "gemini-pro",
                 reports_dir: str = "reports", cors_origins: List[str] = None,
                 enable_websocket: bool = True, stream_interval: float = 0.1,
                 mock_obd: bool = False):
        """
        Initialize API configuration.
        
        Args:
            host: Host to bind the API server to
            port: Port to bind the API server to
            obd_port: OBD port (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)
            obd_baudrate: OBD baudrate
            obd_timeout: OBD connection timeout in seconds
            gemini_api_key: Gemini API key
            gemini_model: Gemini model name
            reports_dir: Directory to store reports
            cors_origins: List of allowed CORS origins
            enable_websocket: Enable WebSocket streaming
            stream_interval: Default interval for data streaming in seconds
            mock_obd: Whether to use mock OBD data instead of real connection
        """
        self.host = host
        self.port = port
        self.obd_port = obd_port
        self.obd_baudrate = obd_baudrate
        self.obd_timeout = obd_timeout
        self.gemini_api_key = gemini_api_key
        self.gemini_model = gemini_model
        self.reports_dir = reports_dir
        self.cors_origins = cors_origins or ["*"]
        self.enable_websocket = enable_websocket
        self.stream_interval = stream_interval
        self.mock_obd = mock_obd

class FourPointsAPI:
    """
    FastAPI application for FourPoints vehicle telemetry and diagnostics.
    """
    
    def __init__(self, config: APIConfig = None):
        """
        Initialize the API.
        
        Args:
            config: API configuration
        """
        self.config = config or APIConfig()
        self.app = FastAPI(
            title="FourPoints API",
            description="API for vehicle telemetry, diagnostics, and maintenance",
            version="0.1.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
            
        # Initialize components
        self.obd_client = None
        self.analytics = None
        self.gemini_client = None
        self.location_tracker = None
        self.report_generator = None
        self.data_stream = None
        self.websocket_streamer = None
        self.vehicle_info = VehicleInfo()
        
        # Initialize components if OBD port is specified
        if self.config.obd_port:
            self._initialize_components()
        
        # Cache for telemetry data
        self.telemetry_cache = {}
        self.dtcs_cache = []
        
        # Setup routes
        self._setup_routes()
        
    def _initialize_components(self):
        """Initialize API components."""
        # Initialize OBD client
        self.obd_client = OBDClient(
            port=self.config.obd_port,
            baudrate=self.config.obd_baudrate,
            timeout=self.config.obd_timeout
        )
        
        # Initialize analytics
        self.analytics = VehicleAnalytics(self.obd_client)
        
        # Initialize Gemini client
        self.gemini_client = GeminiClient(
            api_key=self.config.gemini_api_key,
            model=self.config.gemini_model
        )
        
        # Initialize location tracker
        self.location_tracker = LocationTracker()
        
        # Initialize report generator
        self.report_generator = ReportGenerator(self.config.reports_dir)
        
        # Initialize data streaming components if WebSocket is enabled
        if self.config.enable_websocket:
            self.data_stream = DataStream(self.obd_client)
            self.websocket_streamer = WebSocketStreamer(self.data_stream)
            self.websocket_streamer.setup_handlers()
            
    def _setup_routes(self):
        """Set up API routes."""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize components on startup."""
            # Initialize OBD client
            if self.obd_client:
                self.obd_client.connect()
                
            # Initialize location tracker
            if self.location_tracker:
                self.location_tracker.start_tracking()
                
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Clean up on shutdown."""
            if self.obd_client:
                self.obd_client.disconnect()
                
            if self.location_tracker:
                self.location_tracker.stop_tracking()
                
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """Root endpoint with API information."""
            return """
            <html>
                <head>
                    <title>FourPoints API</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            max-width: 800px;
                            margin: 0 auto;
                            padding: 20px;
                        }
                        h1 {
                            color: #2c3e50;
                        }
                        .endpoint {
                            margin-bottom: 20px;
                            padding: 10px;
                            background-color: #f9f9f9;
                            border-radius: 5px;
                        }
                        .endpoint h2 {
                            margin-top: 0;
                            color: #2980b9;
                        }
                        code {
                            background-color: #f2f2f2;
                            padding: 2px 5px;
                            border-radius: 3px;
                        }
                    </style>
                </head>
                <body>
                    <h1>FourPoints Vehicle Telemetry API</h1>
                    <p>API for vehicle telemetry, diagnostics, and maintenance</p>
                    
                    <div class="endpoint">
                        <h2>GET /realtime</h2>
                        <p>Get real-time vehicle telemetry data</p>
                    </div>
                    
                    <div class="endpoint">
                        <h2>GET /dtcs</h2>
                        <p>Get diagnostic trouble codes with explanations</p>
                    </div>
                    
                    <div class="endpoint">
                        <h2>POST /clear_cel</h2>
                        <p>Clear check engine light and trouble codes</p>
                    </div>
                    
                    <div class="endpoint">
                        <h2>GET /health</h2>
                        <p>Get vehicle health diagnostics</p>
                    </div>
                    
                    <div class="endpoint">
                        <h2>GET /maintenance</h2>
                        <p>Get predictive maintenance recommendations</p>
                    </div>
                    
                    <div class="endpoint">
                        <h2>GET /sensors</h2>
                        <p>Get real-time sensor status</p>
                    </div>
                    
                    <div class="endpoint">
                        <h2>GET /report</h2>
                        <p>Generate a vehicle health and diagnostics report</p>
                        <p>Query parameters:</p>
                        <ul>
                            <li><code>format</code>: Report format (pdf or html, default: pdf)</li>
                        </ul>
                    </div>
                    
                    <p>For API documentation, visit <a href="/docs">/docs</a></p>
                </body>
            </html>
            """
            
        @self.app.get("/realtime", response_model=TelemetryData)
        async def get_realtime_data():
            """
            Get real-time vehicle telemetry data.
            
            Returns:
                TelemetryData: Current telemetry data
            """
            if not self.obd_client:
                raise HTTPException(status_code=503, detail="OBD client not initialized")
                
            if not self.obd_client.is_connected:
                connected = self.obd_client.connect()
                if not connected:
                    raise HTTPException(status_code=503, detail="Failed to connect to vehicle")
                    
            telemetry_data = self.obd_client.get_real_time_data()
            self.telemetry_cache = telemetry_data  # Cache for other endpoints
            
            return TelemetryData(
                timestamp=datetime.datetime.now().isoformat(),
                data=telemetry_data
            )
            
        @self.app.get("/dtcs", response_model=DTCResponse)
        async def get_dtcs():
            """
            Get diagnostic trouble codes with explanations.
            
            Returns:
                DTCResponse: DTCs with explanations
            """
            if not self.obd_client:
                raise HTTPException(status_code=503, detail="OBD client not initialized")
                
            if not self.obd_client.is_connected:
                connected = self.obd_client.connect()
                if not connected:
                    raise HTTPException(status_code=503, detail="Failed to connect to vehicle")
                    
            dtcs = self.obd_client.get_dtcs()
            self.dtcs_cache = dtcs  # Cache for other endpoints
            
            dtc_analysis = self.analytics.analyze_dtcs(dtcs)
            
            # Get explanations from Gemini if available
            dtc_explanations = {}
            if self.gemini_client and self.gemini_client.initialized:
                dtc_explanations = self.gemini_client.explain_dtcs(dtcs)
            else:
                # Use local database
                for dtc in dtcs:
                    if dtc in self.gemini_client.dtc_database:
                        dtc_explanations[dtc] = self.gemini_client.dtc_database[dtc]
                    else:
                        dtc_explanations[dtc] = {
                            "description": f"Code {dtc}",
                            "possible_causes": "Unknown",
                            "severity": "Unknown"
                        }
                        
            # Build response
            dtc_list = []
            for dtc in dtcs:
                explanation = dtc_explanations.get(dtc, {})
                dtc_list.append(DiagnosticTroubleCode(
                    code=dtc,
                    description=explanation.get("description", f"Code {dtc}"),
                    possible_causes=explanation.get("possible_causes", "Unknown"),
                    severity=explanation.get("severity", "Unknown")
                ))
                
            return DTCResponse(
                dtcs=dtc_list,
                count=len(dtcs),
                status=dtc_analysis["severity"]
            )
            
        @self.app.post("/clear_cel", response_model=dict)
        async def clear_cel():
            """
            Clear check engine light and trouble codes.
            
            Returns:
                dict: Status of the operation
            """
            if not self.obd_client:
                raise HTTPException(status_code=503, detail="OBD client not initialized")
                
            if not self.obd_client.is_connected:
                connected = self.obd_client.connect()
                if not connected:
                    raise HTTPException(status_code=503, detail="Failed to connect to vehicle")
                    
            success = self.obd_client.clear_dtcs()
            
            if success:
                self.dtcs_cache = []  # Clear the cache
                return {"success": True, "message": "Check engine light and trouble codes cleared"}
            else:
                raise HTTPException(status_code=500, detail="Failed to clear trouble codes")
                
        @self.app.get("/health", response_model=HealthResponse)
        async def get_health():
            """
            Get vehicle health diagnostics.
            
            Returns:
                HealthResponse: Vehicle health diagnostics
            """
            if not self.obd_client:
                raise HTTPException(status_code=503, detail="OBD client not initialized")
                
            # Get telemetry data if not cached
            if not self.telemetry_cache:
                if not self.obd_client.is_connected:
                    connected = self.obd_client.connect()
                    if not connected:
                        raise HTTPException(status_code=503, detail="Failed to connect to vehicle")
                        
                self.telemetry_cache = self.obd_client.get_real_time_data()
                
            # Get DTCs if not cached
            if not self.dtcs_cache and self.obd_client.is_connected:
                self.dtcs_cache = self.obd_client.get_dtcs()
                
            # Analyze health
            health_data = self.analytics.analyze_vehicle_health(
                self.telemetry_cache,
                self.dtcs_cache
            )
            
            return HealthResponse(
                status=health_data["status"],
                issues=health_data["issues"],
                metrics=health_data["metrics_analysis"],
                dtcs=self.dtcs_cache,
                timestamp=health_data["timestamp"]
            )
            
        @self.app.get("/maintenance", response_model=MaintenanceResponse)
        async def get_maintenance():
            """
            Get predictive maintenance recommendations.
            
            Returns:
                MaintenanceResponse: Maintenance recommendations
            """
            # Get telemetry data if not cached
            if not self.telemetry_cache and self.obd_client:
                if not self.obd_client.is_connected:
                    connected = self.obd_client.connect()
                    if not connected:
                        logger.warning("Failed to connect to vehicle, using cached data only")
                    else:
                        self.telemetry_cache = self.obd_client.get_real_time_data()
                        
            # Get maintenance predictions from analytics
            maintenance_data = self.analytics.predict_maintenance()
            
            # Get AI-powered recommendations if Gemini is available
            if self.gemini_client and self.gemini_client.initialized:
                # Prepare vehicle data for Gemini
                vehicle_data = {
                    "telemetry": self.telemetry_cache,
                    "dtcs": self.dtcs_cache,
                    "vehicle_info": self.vehicle_info.dict()
                }
                
                gemini_advice = self.gemini_client.get_maintenance_advice(vehicle_data)
                
                # Combine analytics predictions with Gemini recommendations
                recommendations = []
                
                # Add analytics predictions
                for pred in maintenance_data["predictions"]:
                    recommendations.append(MaintenanceRecommendation(
                        component=pred["component"],
                        issue=pred["issue"],
                        confidence=pred["confidence"],
                        recommendation=pred["recommendation"]
                    ))
                    
                # Add Gemini recommendations if available
                if "recommendations" in gemini_advice:
                    for rec in gemini_advice["recommendations"]:
                        # Convert estimated_cost to string if present
                        estimated_cost = rec.get("estimated_cost", "")
                        recommendation = rec["description"]
                        if estimated_cost:
                            recommendation += f" (Est. cost: {estimated_cost})"
                            
                        recommendations.append(MaintenanceRecommendation(
                            component=rec["title"].split(":")[0] if ":" in rec["title"] else rec["title"],
                            issue=rec["title"],
                            confidence=0.8 if rec["priority"].lower() == "high" else 0.6,
                            recommendation=recommendation
                        ))
                        
                return MaintenanceResponse(
                    recommendations=recommendations,
                    timestamp=maintenance_data["timestamp"]
                )
            else:
                # Use only analytics predictions
                recommendations = []
                for pred in maintenance_data["predictions"]:
                    recommendations.append(MaintenanceRecommendation(
                        component=pred["component"],
                        issue=pred["issue"],
                        confidence=pred["confidence"],
                        recommendation=pred["recommendation"]
                    ))
                    
                return MaintenanceResponse(
                    recommendations=recommendations,
                    timestamp=maintenance_data["timestamp"]
                )
                
        @self.app.get("/sensors", response_model=SensorsResponse)
        async def get_sensors():
            """
            Get real-time sensor status.
            
            Returns:
                SensorsResponse: Sensor status
            """
            if not self.obd_client:
                raise HTTPException(status_code=503, detail="OBD client not initialized")
                
            if not self.obd_client.is_connected:
                connected = self.obd_client.connect()
                if not connected:
                    raise HTTPException(status_code=503, detail="Failed to connect to vehicle")
                    
            # Get sensor data
            sensor_data = self.obd_client.get_sensor_status()
            
            # Analyze sensor status
            analyzed_sensors = self.analytics.analyze_sensor_status(sensor_data)
            
            # Build response
            sensors_dict = {}
            for sensor_name, data in analyzed_sensors.items():
                sensors_dict[sensor_name] = SensorStatus(
                    value=data["value"],
                    unit=data["unit"],
                    status=data["status"],
                    message=data["message"]
                )
                
            return SensorsResponse(
                sensors=sensors_dict,
                timestamp=datetime.datetime.now().isoformat()
            )
            
        @self.app.get("/report")
        async def get_report(
            format: ReportFormat = ReportFormat.PDF,
            background_tasks: BackgroundTasks = None
        ):
            """
            Generate a vehicle health and diagnostics report.
            
            Args:
                format: Report format (pdf or html)
                background_tasks: FastAPI background tasks
                
            Returns:
                FileResponse: Report file
            """
            # Get telemetry data if not cached
            if not self.telemetry_cache and self.obd_client:
                if not self.obd_client.is_connected:
                    connected = self.obd_client.connect()
                    if not connected:
                        logger.warning("Failed to connect to vehicle, using cached data only")
                    else:
                        self.telemetry_cache = self.obd_client.get_real_time_data()
                        
            # Get DTCs if not cached
            if not self.dtcs_cache and self.obd_client and self.obd_client.is_connected:
                self.dtcs_cache = self.obd_client.get_dtcs()
                
            # Get health data
            health_data = self.analytics.analyze_vehicle_health(
                self.telemetry_cache,
                self.dtcs_cache
            )
            
            # Get maintenance data
            maintenance_data = self.analytics.predict_maintenance()
            
            # Get DTC explanations
            dtc_explanations = {}
            if self.gemini_client:
                dtc_explanations = self.gemini_client.explain_dtcs(self.dtcs_cache)
                
            # Get Gemini insights if available
            gemini_insights = None
            if self.gemini_client and self.gemini_client.initialized:
                gemini_insights = self.gemini_client.get_health_insights(health_data)
                
            # Prepare report data
            report_data = {
                "title": "Vehicle Health Report",
                "vehicle_info": self.vehicle_info.dict(),
                "health_data": health_data,
                "maintenance_data": maintenance_data,
                "telemetry_data": self.telemetry_cache,
                "dtc_explanations": dtc_explanations,
                "gemini_insights": gemini_insights
            }
            
            # Generate report
            report_path = self.report_generator.generate_report(
                report_data,
                report_type='health',
                format=format.value
            )
            
            if not report_path:
                raise HTTPException(status_code=500, detail="Failed to generate report")
                
            # Clean up old reports in background
            if background_tasks:
                background_tasks.add_task(self._cleanup_old_reports)
                
            # Return file
            return FileResponse(
                path=report_path,
                filename=os.path.basename(report_path),
                media_type="application/pdf" if format == ReportFormat.PDF else "text/html"
            )
            
        @self.app.put("/vehicle_info", response_model=VehicleInfo)
        async def update_vehicle_info(info: VehicleInfo):
            """
            Update vehicle information.
            
            Args:
                info: Vehicle information
                
            Returns:
                VehicleInfo: Updated vehicle information
            """
            self.vehicle_info = info
            return self.vehicle_info
            
        @self.app.get("/vehicle_info", response_model=VehicleInfo)
        async def get_vehicle_info():
            """
            Get vehicle information.
            
            Returns:
                VehicleInfo: Vehicle information
            """
            return self.vehicle_info
            
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """
            WebSocket endpoint for real-time data streaming.
            
            Args:
                websocket: WebSocket connection
            """
            if not self.config.enable_websocket or not self.websocket_streamer:
                await websocket.close(code=1000, reason="WebSocket streaming not enabled")
                return
                
            try:
                await self.websocket_streamer.websocket_endpoint(websocket)
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                
        @self.app.post("/stream/start")
        async def start_stream(commands: List[str] = Query(None), interval: float = Query(None)):
            """
            Start streaming data.
            
            Args:
                commands: List of OBD commands to stream
                interval: Interval between queries in seconds
                
            Returns:
                dict: Status of the operation
            """
            if not self.config.enable_websocket or not self.data_stream:
                raise HTTPException(status_code=503, detail="WebSocket streaming not enabled")
                
            if not self.obd_client:
                raise HTTPException(status_code=503, detail="OBD client not initialized")
                
            if not self.obd_client.is_connected:
                connected = self.obd_client.connect()
                if not connected:
                    raise HTTPException(status_code=503, detail="Failed to connect to vehicle")
                    
            # Add commands to stream
            if commands:
                self.data_stream.add_commands(commands)
            else:
                # Add default commands if none specified
                default_commands = [
                    "RPM", "SPEED", "THROTTLE_POS", "ENGINE_LOAD", "COOLANT_TEMP",
                    "INTAKE_TEMP", "MAF", "FUEL_LEVEL"
                ]
                self.data_stream.add_commands(default_commands)
                
            # Set interval
            stream_interval = interval if interval is not None else self.config.stream_interval
            
            # Start streaming
            if self.data_stream.streaming:
                return {"success": True, "message": "Stream already active", "commands": self.data_stream.commands}
                
            success = await self.data_stream.start(interval=stream_interval)
            
            if success:
                return {
                    "success": True,
                    "message": "Stream started",
                    "commands": self.data_stream.commands,
                    "interval": stream_interval
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to start stream")
                
        @self.app.post("/stream/stop")
        async def stop_stream():
            """
            Stop streaming data.
            
            Returns:
                dict: Status of the operation
            """
            if not self.config.enable_websocket or not self.data_stream:
                raise HTTPException(status_code=503, detail="WebSocket streaming not enabled")
                
            if not self.data_stream.streaming:
                return {"success": True, "message": "Stream not active"}
                
            await self.data_stream.stop()
            return {"success": True, "message": "Stream stopped"}
            
        @self.app.get("/stream/status")
        async def get_stream_status():
            """
            Get stream status.
            
            Returns:
                dict: Stream status
            """
            if not self.config.enable_websocket or not self.data_stream:
                raise HTTPException(status_code=503, detail="WebSocket streaming not enabled")
                
            return {
                "active": self.data_stream.streaming,
                "commands": self.data_stream.commands,
                "interval": self.data_stream.interval,
                "connections": len(self.websocket_streamer.active_connections) if self.websocket_streamer else 0
            }
            
        @self.app.post("/stream/commands")
        async def update_stream_commands(commands: List[str] = Query(None), action: str = Query("add")):
            """
            Update stream commands.
            
            Args:
                commands: List of OBD commands
                action: Action to perform ('add' or 'remove')
                
            Returns:
                dict: Status of the operation
            """
            if not self.config.enable_websocket or not self.data_stream:
                raise HTTPException(status_code=503, detail="WebSocket streaming not enabled")
                
            if not commands:
                raise HTTPException(status_code=400, detail="No commands specified")
                
            if action.lower() == "add":
                added = self.data_stream.add_commands(commands)
                return {"success": True, "added": added, "commands": self.data_stream.commands}
            elif action.lower() == "remove":
                removed = []
                for cmd in commands:
                    if self.data_stream.remove_command(cmd):
                        removed.append(cmd)
                return {"success": True, "removed": removed, "commands": self.data_stream.commands}
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
                
        @self.app.post("/stream/threshold")
        async def set_threshold(command: str = Query(...), min_value: Optional[float] = Query(None), 
                              max_value: Optional[float] = Query(None)):
            """
            Set a threshold for a command.
            
            Args:
                command: OBD command name
                min_value: Minimum threshold value
                max_value: Maximum threshold value
                
            Returns:
                dict: Status of the operation
            """
            if not self.config.enable_websocket or not self.data_stream:
                raise HTTPException(status_code=503, detail="WebSocket streaming not enabled")
                
            if min_value is None and max_value is None:
                raise HTTPException(status_code=400, detail="Either min_value or max_value must be specified")
                
            success = self.data_stream.set_threshold(command, min_value, max_value)
            
            if success:
                return {
                    "success": True,
                    "command": command,
                    "threshold": {
                        "min": min_value,
                        "max": max_value
                    }
                }
            else:
                raise HTTPException(status_code=400, detail=f"Failed to set threshold for command: {command}")
                
        @self.app.delete("/stream/threshold/{command}")
        async def remove_threshold(command: str):
            """
            Remove a threshold for a command.
            
            Args:
                command: OBD command name
                
            Returns:
                dict: Status of the operation
            """
            if not self.config.enable_websocket or not self.data_stream:
                raise HTTPException(status_code=503, detail="WebSocket streaming not enabled")
                
            success = self.data_stream.remove_threshold(command)
            
            if success:
                return {"success": True, "command": command}
            else:
                raise HTTPException(status_code=404, detail=f"No threshold found for command: {command}")
            
    async def _cleanup_old_reports(self, max_age_days: int = 7):
        """
        Clean up old reports.
        
        Args:
            max_age_days: Maximum age of reports to keep in days
        """
        if not self.config.reports_dir:
            return
            
        try:
            now = datetime.datetime.now()
            report_dir = Path(self.config.reports_dir)
            
            for file_path in report_dir.glob("*_report_*.?*"):
                if not file_path.is_file():
                    continue
                    
                file_age = now - datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.days > max_age_days:
                    try:
                        file_path.unlink()
                        logger.info(f"Deleted old report: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to delete old report {file_path}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up old reports: {str(e)}")
            
    def get_app(self):
        """
        Get the FastAPI application.
        
        Returns:
            FastAPI: FastAPI application
        """
        return self.app


# Direct execution entry point
if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run FourPoints API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--mock", action="store_true", help="Use mock OBD connection")
    parser.add_argument("--obd-port", help="OBD connection port (default: auto-detect)")
    parser.add_argument("--gemini-key", help="Gemini API key")
    parser.add_argument("--websocket", action="store_true", help="Enable WebSocket streaming")
    args = parser.parse_args()
    
    # Configure API
    config = APIConfig(
        host=args.host,
        port=args.port,
        obd_port=args.obd_port,
        mock_obd=args.mock,
        gemini_api_key=args.gemini_key or os.environ.get("GEMINI_API_KEY"),
        enable_websocket=args.websocket
    )
    
    # Print configuration
    print(f"Starting FourPoints API Server:")
    print(f"  Host: {config.host}")
    print(f"  Port: {config.port}")
    print(f"  OBD Connection: {'Mock' if args.mock else 'Real'}")
    if config.obd_port:
        print(f"  OBD Port: {config.obd_port}")
    print(f"  Gemini API: {'Enabled' if config.gemini_api_key else 'Disabled'}")
    print(f"  WebSocket: {'Enabled' if config.enable_websocket else 'Disabled'}")
    
    # Create and start API
    api = FourPointsAPI(config)
    app = api.get_app()
    
    # Run the server
    uvicorn.run(app, host=config.host, port=config.port)

# FourPoints

A production-grade Python library for real-time vehicle telemetry and diagnostics.

## Features

- **OBD-II Communication**: Connect to vehicle ECUs via USB or Bluetooth (including BLE)
- **Real-time Telemetry**: Stream vehicle data in real-time with asyncio support
- **Advanced Analytics**: Health diagnostics, predictive maintenance, and sensor status monitoring
- **AI-Powered Insights**: Gemini API integration for DTC explanations and maintenance advice
- **Location Tracking**: GPS integration for location data and trip statistics
- **Report Generation**: Create PDF/HTML reports with charts and vehicle data
- **FastAPI Endpoints**: RESTful API and WebSocket streaming for easy integration
- **Comprehensive Testing**: Unit tests with pytest and mocked OBD responses

## Installation

```bash
# Basic installation
pip install fourpoints

# With development tools
pip install fourpoints[dev]

# With documentation tools
pip install fourpoints[docs]

# Full installation with all dependencies
pip install fourpoints[all]
```

### Dependencies

FourPoints requires the `obd` package for OBD-II communication. This dependency is automatically installed with the basic installation.

### Gemini API Key

For AI-powered features (DTC explanations, maintenance advice, health insights), you'll need a Google Gemini API key:

1. Get your API key from [Google AI Studio](https://ai.google.dev/)
2. Set it as an environment variable:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
   
   Or on Windows:
   ```powershell
   $env:GEMINI_API_KEY="your_api_key_here"
   ```
3. Alternatively, provide it directly when initializing the `GeminiClient` or in the `APIConfig`

## Quick Start

```python
from fourpoints.obd_client import OBDClient
from fourpoints.analytics import VehicleAnalytics

# Connect to vehicle
client = OBDClient()
client.connect()

# Get real-time telemetry
telemetry = client.get_telemetry()
print(f"RPM: {telemetry.get('RPM')}")
print(f"Speed: {telemetry.get('SPEED')} km/h")

# Check vehicle health
analytics = VehicleAnalytics(client)
health = analytics.get_health_status()
print(f"Health Score: {health['score']}/100")
```

## API Server

Start the API server to expose vehicle data via REST API and WebSocket:

```python
from fourpoints.api import FourPointsAPI, APIConfig

config = APIConfig(
    host="localhost",
    port=8000,
    obd_port="/dev/ttyUSB0",  # or auto-detect
    enable_websocket=True,
    gemini_api_key="YOUR_API_KEY"  # For AI features
)

api = FourPointsAPI(config)
api.start()
```

## Real-time Streaming

Stream vehicle data in real-time with asyncio:

```python
import asyncio
from fourpoints.obd_client import OBDClient
from fourpoints.streaming import DataStream

async def main():
    client = OBDClient()
    client.connect()
    
    stream = DataStream(client)
    stream.add_commands(["RPM", "SPEED", "ENGINE_LOAD"])
    
    # Set up event handlers
    stream.on_data = lambda data: print(f"Data: {data}")
    stream.on_threshold = lambda violations: print(f"Alert: {violations}")
    
    # Set thresholds
    stream.set_threshold("RPM", min_value=500, max_value=3000)
    
    # Start streaming
    stream.start()
    
    # Run for 60 seconds
    await asyncio.sleep(60)
    
    # Stop streaming
    stream.stop()

asyncio.run(main())
```

## WebSocket Streaming

Connect to the WebSocket endpoint to receive real-time data:

```javascript
// Browser JavaScript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  // Subscribe to commands
  ws.send(JSON.stringify({
    action: 'subscribe',
    commands: ['RPM', 'SPEED', 'ENGINE_LOAD']
  }));
  
  // Set threshold
  ws.send(JSON.stringify({
    action: 'set_threshold',
    command: 'RPM',
    min: 500,
    max: 3000
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'data') {
    console.log('Data:', message.data);
  } else if (message.type === 'threshold') {
    console.log('Threshold Alert:', message.violations);
  }
};
```

## Example Script

Check out the [demo script](examples/demo.py) for a comprehensive example of using FourPoints.

## API Documentation

### OBD Client

```python
from fourpoints.obd_client import OBDClient, ConnectionType

# Create client
client = OBDClient(
    port=None,  # Auto-detect
    connection_type=ConnectionType.AUTO,  # AUTO, USB, BLUETOOTH, BLE, MOCK
    timeout=2.0
)

# Connect to vehicle
client.connect()

# Get supported commands
commands = client.get_supported_commands()

# Query specific command
rpm = client.query_command("RPM")

# Get all telemetry
telemetry = client.get_telemetry()

# Get DTCs
dtcs = client.get_dtcs()

# Clear DTCs
client.clear_dtcs()

# Disconnect
client.disconnect()
```

### Analytics

```python
from fourpoints.analytics import VehicleAnalytics

# Create analytics
analytics = VehicleAnalytics(obd_client)

# Get health status
health = analytics.get_health_status()

# Get maintenance recommendations
maintenance = analytics.get_maintenance_recommendations()

# Get sensor status
sensors = analytics.get_sensor_status()

# Predict failures
predictions = analytics.predict_failures()

# Calculate health score
score = analytics.calculate_health_score()
```

### Gemini AI Integration

```python
from fourpoints.gemini_client import GeminiClient

# Create client with explicit API key
gemini = GeminiClient(api_key="YOUR_API_KEY")

# Or use environment variable (recommended)
# export GEMINI_API_KEY="your_api_key_here"
gemini = GeminiClient()  # Will use GEMINI_API_KEY environment variable

# Get DTC explanation
explanation = gemini.explain_dtc("P0123")

# Get maintenance advice
advice = gemini.get_maintenance_advice(
    dtcs=["P0123"],
    telemetry={"RPM": 1500, "ENGINE_LOAD": 40}
)

# Get health insights
insights = gemini.get_health_insights(
    telemetry={"RPM": 1500, "ENGINE_LOAD": 40}
)
```

### Location Tracking

```python
from fourpoints.location import LocationTracker, LocationSource

# Create tracker
tracker = LocationTracker()

# Start tracking
tracker.start_tracking(
    source=LocationSource.GPSD,  # GPSD, SERIAL, MOCK
    port="/dev/ttyUSB1"  # For SERIAL source
)

# Get current location
location = tracker.get_current_location()
print(f"Lat: {location.latitude}, Lon: {location.longitude}")

# Get trip data
trip = tracker.get_trip_data()
print(f"Distance: {trip.distance} km")

# Reset trip
tracker.reset_trip()

# Stop tracking
tracker.stop_tracking()
```

### Report Generation

```python
from fourpoints.reports import ReportGenerator, ReportFormat

# Create generator
generator = ReportGenerator(output_dir="reports")

# Generate report
report_path = generator.generate_report(
    format=ReportFormat.PDF,  # PDF, HTML
    telemetry=telemetry,
    dtcs=dtcs,
    health_status=health,
    maintenance=maintenance,
    location=location.to_dict(),
    trip_data=trip.__dict__,
    vehicle_info={"make": "Toyota", "model": "Camry", "year": 2020}
)

# Get all reports
reports = generator.get_all_reports()

# Clean up old reports
generator.cleanup_old_reports(max_age_days=30)
```

## License

MIT License

#!/usr/bin/env python3
"""
FourPoints Library Demo Script

This script demonstrates the key features of the FourPoints vehicle telemetry library,
including OBD-II communication, vehicle analytics, Gemini AI integration, location tracking,
report generation, and real-time data streaming.

Usage:
    python demo.py [--mock] [--port PORT] [--gemini-key KEY]

Options:
    --mock          Use mock OBD connection instead of real hardware
    --port PORT     Specify OBD connection port (default: auto-detect)
    --gemini-key KEY  Specify Gemini API key (default: from environment variable GEMINI_API_KEY)
                      Get your key from https://ai.google.dev/
"""

import argparse
import asyncio
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import fourpoints
sys.path.insert(0, str(Path(__file__).parent.parent))

from fourpoints.obd_client import OBDClient, ConnectionType
from fourpoints.analytics import VehicleAnalytics
from fourpoints.gemini_client import GeminiClient
from fourpoints.location import LocationTracker, LocationSource
from fourpoints.reports import ReportGenerator, ReportFormat
from fourpoints.streaming import DataStream, StreamEvent, StreamEventType


class FourPointsDemo:
    """Demo class for FourPoints library."""

    def __init__(self, use_mock=False, port=None, gemini_key=None):
        """Initialize the demo."""
        self.use_mock = use_mock
        self.port = port
        self.gemini_key = gemini_key or os.environ.get("GEMINI_API_KEY")
        
        # Initialize components
        self.obd_client = None
        self.analytics = None
        self.gemini_client = None
        self.location_tracker = None
        self.report_generator = None
        self.data_stream = None
        
        # Create output directory
        self.output_dir = Path("demo_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)
        
    def setup(self):
        """Set up all components."""
        print("\n=== Setting up FourPoints components ===")
        
        # Initialize OBD client
        print("Initializing OBD client...")
        if self.use_mock:
            print("Using mock OBD connection")
            self.obd_client = OBDClient(connection_type=ConnectionType.MOCK)
        else:
            print(f"Connecting to OBD adapter on port: {self.port or 'auto-detect'}")
            self.obd_client = OBDClient(port=self.port)
        
        # Connect to vehicle
        print("Connecting to vehicle...")
        if not self.obd_client.connect():
            print("Failed to connect to vehicle. Using mock connection instead.")
            self.obd_client = OBDClient(connection_type=ConnectionType.MOCK)
            self.obd_client.connect()
        
        # Initialize analytics
        print("Initializing vehicle analytics...")
        self.analytics = VehicleAnalytics(self.obd_client)
        
        # Initialize Gemini client if API key is provided
        if self.gemini_key:
            print("Initializing Gemini AI client with provided API key...")
            self.gemini_client = GeminiClient(api_key=self.gemini_key)
        elif os.environ.get("GEMINI_API_KEY"):
            print("Initializing Gemini AI client with API key from environment variable...")
            self.gemini_client = GeminiClient()
        else:
            print("⚠️ No Gemini API key provided. AI features will be limited.")
            print("   To enable AI features, get a key from https://ai.google.dev/")
            print("   and set the GEMINI_API_KEY environment variable or use --gemini-key")
            self.gemini_client = None
        
        # Initialize location tracker
        print("Initializing location tracker...")
        self.location_tracker = LocationTracker()
        self.location_tracker.start_tracking(source=LocationSource.MOCK)
        
        # Initialize report generator
        print("Initializing report generator...")
        self.report_generator = ReportGenerator(output_dir=self.output_dir)
        
        # Initialize data stream
        print("Initializing data stream...")
        self.data_stream = DataStream(self.obd_client)
        self.data_stream.on_data = self.handle_stream_data
        self.data_stream.on_error = self.handle_stream_error
        self.data_stream.on_threshold = self.handle_stream_threshold
        
        print("Setup complete!\n")
        
    def run_basic_demo(self):
        """Run basic demo showcasing core features."""
        print("\n=== Running Basic Demo ===")
        
        # Get supported commands
        print("\n--- Supported OBD Commands ---")
        commands = self.obd_client.get_supported_commands()
        print(f"Vehicle supports {len(commands)} commands:")
        for i, cmd in enumerate(commands[:10], 1):
            print(f"  {i}. {cmd}")
        if len(commands) > 10:
            print(f"  ... and {len(commands) - 10} more")
        
        # Get current telemetry
        print("\n--- Current Vehicle Telemetry ---")
        telemetry = self.obd_client.get_telemetry()
        for key, value in telemetry.items():
            print(f"  {key}: {value}")
        
        # Get DTCs
        print("\n--- Diagnostic Trouble Codes ---")
        dtcs = self.obd_client.get_dtcs()
        if dtcs:
            print(f"Found {len(dtcs)} DTCs:")
            for dtc in dtcs:
                print(f"  {dtc}")
                if self.gemini_client:
                    explanation = self.gemini_client.explain_dtc(dtc)
                    print(f"    Explanation: {explanation}")
        else:
            print("No DTCs found. Vehicle is running without error codes.")
        
        # Get health status
        print("\n--- Vehicle Health Status ---")
        health = self.analytics.get_health_status()
        print(f"Health Status: {health['status']}")
        print(f"Health Score: {health['score']}/100")
        if health['issues']:
            print("Issues:")
            for issue in health['issues']:
                print(f"  - {issue}")
        else:
            print("No health issues detected.")
        
        # Get maintenance recommendations
        print("\n--- Maintenance Recommendations ---")
        maintenance = self.analytics.get_maintenance_recommendations()
        if maintenance:
            print(f"Found {len(maintenance)} maintenance recommendations:")
            for item in maintenance:
                print(f"  Component: {item['component']}")
                print(f"  Severity: {item['severity']}")
                print(f"  Description: {item['description']}")
                print(f"  Recommendation: {item['recommendation']}")
                print()
        else:
            print("No maintenance recommendations at this time.")
        
        # Get sensor status
        print("\n--- Sensor Status ---")
        sensors = self.analytics.get_sensor_status()
        for sensor in sensors[:5]:
            print(f"  {sensor['name']}: {sensor['value']} - Status: {sensor['status']}")
        if len(sensors) > 5:
            print(f"  ... and {len(sensors) - 5} more sensors")
        
        # Get location
        print("\n--- Current Location ---")
        location = self.location_tracker.get_current_location()
        if location:
            print(f"  Latitude: {location.latitude}")
            print(f"  Longitude: {location.longitude}")
            if location.altitude:
                print(f"  Altitude: {location.altitude} m")
            if location.speed:
                print(f"  Speed: {location.speed} km/h")
        else:
            print("  Location not available")
        
        # Get trip data
        print("\n--- Trip Data ---")
        trip = self.location_tracker.get_trip_data()
        print(f"  Distance: {trip.distance:.2f} km")
        print(f"  Start Time: {trip.start_time}")
        print(f"  Average Speed: {self.location_tracker.get_average_speed():.2f} km/h")
        
        # Generate report
        print("\n--- Generating Reports ---")
        html_report = self.report_generator.generate_report(
            format=ReportFormat.HTML,
            telemetry=telemetry,
            dtcs=dtcs,
            health_status=health,
            maintenance=maintenance,
            location=location.to_dict() if location else None,
            trip_data=trip.__dict__,
            vehicle_info={"make": "Demo", "model": "Vehicle", "year": 2023}
        )
        print(f"HTML report generated: {html_report}")
        
        pdf_report = self.report_generator.generate_report(
            format=ReportFormat.PDF,
            telemetry=telemetry,
            dtcs=dtcs,
            health_status=health,
            maintenance=maintenance,
            location=location.to_dict() if location else None,
            trip_data=trip.__dict__,
            vehicle_info={"make": "Demo", "model": "Vehicle", "year": 2023}
        )
        print(f"PDF report generated: {pdf_report}")
        
    async def run_streaming_demo(self):
        """Run streaming demo showcasing real-time data capabilities."""
        print("\n=== Running Streaming Demo ===")
        print("Starting real-time data stream for 10 seconds...")
        
        # Add commands to stream
        commands = ["RPM", "SPEED", "ENGINE_LOAD", "COOLANT_TEMP"]
        added = self.data_stream.add_commands(commands)
        print(f"Added {len(added)} commands to stream: {', '.join(added)}")
        
        # Set thresholds
        self.data_stream.set_threshold("RPM", 500, 3000)
        self.data_stream.set_threshold("ENGINE_LOAD", 0, 80)
        print("Set thresholds for RPM and ENGINE_LOAD")
        
        # Start streaming
        self.data_stream.start()
        print("Stream started!")
        
        # Run for 10 seconds
        await asyncio.sleep(10)
        
        # Stop streaming
        self.data_stream.stop()
        print("Stream stopped!")
        
    def handle_stream_data(self, data):
        """Handle streaming data events."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] Data: ", end="")
        for key, value in data.items():
            print(f"{key}={value} ", end="")
        print()
        
    def handle_stream_error(self, error):
        """Handle streaming error events."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] Error: {error}")
        
    def handle_stream_threshold(self, violations):
        """Handle streaming threshold violation events."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] Threshold Alert: ", end="")
        for violation in violations:
            print(f"{violation['command']}={violation['value']} (threshold: {violation['threshold']}) ", end="")
        print()
        
    def handle_exit(self, signum, frame):
        """Handle exit signals."""
        print("\nExiting demo...")
        if self.data_stream and self.data_stream.streaming:
            self.data_stream.stop()
        if self.obd_client:
            self.obd_client.disconnect()
        if self.location_tracker:
            self.location_tracker.stop_tracking()
        print("Cleanup complete. Goodbye!")
        sys.exit(0)
        
    async def run(self):
        """Run the full demo."""
        self.setup()
        self.run_basic_demo()
        await self.run_streaming_demo()
        print("\n=== Demo Complete ===")
        print("Thank you for trying FourPoints!")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="FourPoints Library Demo")
    parser.add_argument("--mock", action="store_true", help="Use mock OBD connection")
    parser.add_argument("--port", help="OBD connection port")
    parser.add_argument("--gemini-key", help="Gemini API key (get from https://ai.google.dev/)")
    
    # Print info about Gemini API key requirement
    if not os.environ.get("GEMINI_API_KEY"):
        print("\nNote: For full AI features, provide a Gemini API key with --gemini-key")
        print("or set the GEMINI_API_KEY environment variable.\n")
    args = parser.parse_args()
    
    demo = FourPointsDemo(
        use_mock=args.mock,
        port=args.port,
        gemini_key=args.gemini_key
    )
    
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())

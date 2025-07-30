"""
Analytics Module for FourPoints.

This module provides advanced analytics for vehicle health diagnostics,
predictive maintenance, and sensor status analysis.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import datetime
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    """Enum for vehicle health status."""
    GOOD = "Good"
    WARNING = "Warning"
    CRITICAL = "Critical"


class Analytics:
    """
    Analytics engine for vehicle health diagnostics and predictive maintenance.
    """
    
    def __init__(self):
        """Initialize the analytics engine."""
        self.historical_data = defaultdict(list)
        self.max_history_size = 1000  # Maximum number of data points to store per metric
        self.dtc_severity = self._load_dtc_severity_map()
        
    def _load_dtc_severity_map(self) -> Dict[str, str]:
        """
        Load DTC severity mapping.
        
        Returns:
            Dict[str, str]: Dictionary mapping DTC codes to severity levels
        """
        # This is a simplified mapping. In a real implementation,
        # this would load from a comprehensive database.
        severity_map = {
            # Powertrain (P) codes
            "P0": "WARNING",    # Generic
            "P1": "WARNING",    # Manufacturer-specific
            "P2": "WARNING",    # Generic
            "P3": "WARNING",    # Generic/Manufacturer-specific
            
            # Specific critical codes
            "P0001": "CRITICAL",  # Fuel Volume Regulator Control Circuit/Open
            "P0002": "CRITICAL",  # Fuel Volume Regulator Control Circuit Range/Performance
            "P0106": "WARNING",   # Manifold Absolute Pressure/Barometric Pressure Circuit Range/Performance Problem
            "P0115": "WARNING",   # Engine Coolant Temperature Circuit Malfunction
            "P0117": "CRITICAL",  # Engine Coolant Temperature Circuit Low Input
            "P0118": "CRITICAL",  # Engine Coolant Temperature Circuit High Input
            "P0171": "WARNING",   # System Too Lean (Bank 1)
            "P0172": "WARNING",   # System Too Rich (Bank 1)
            "P0300": "CRITICAL",  # Random/Multiple Cylinder Misfire Detected
            "P0301": "CRITICAL",  # Cylinder 1 Misfire Detected
            "P0302": "CRITICAL",  # Cylinder 2 Misfire Detected
            "P0303": "CRITICAL",  # Cylinder 3 Misfire Detected
            "P0304": "CRITICAL",  # Cylinder 4 Misfire Detected
            "P0401": "WARNING",   # Exhaust Gas Recirculation Flow Insufficient Detected
            "P0420": "WARNING",   # Catalyst System Efficiency Below Threshold (Bank 1)
            "P0440": "WARNING",   # Evaporative Emission Control System Malfunction
            
            # Chassis (C) codes
            "C0": "WARNING",    # Generic
            "C1": "WARNING",    # Manufacturer-specific
            "C2": "WARNING",    # Generic
            "C3": "WARNING",    # Generic/Manufacturer-specific
            
            # Body (B) codes
            "B0": "WARNING",    # Generic
            "B1": "WARNING",    # Manufacturer-specific
            "B2": "WARNING",    # Generic
            "B3": "WARNING",    # Generic/Manufacturer-specific
            
            # Network (U) codes
            "U0": "WARNING",    # Generic
            "U1": "WARNING",    # Manufacturer-specific
            "U2": "WARNING",    # Generic
            "U3": "WARNING",    # Generic/Manufacturer-specific
        }
        return severity_map
        
    def add_data_point(self, metric: str, value: Any, timestamp: Optional[datetime.datetime] = None) -> None:
        """
        Add a data point to the historical data.
        
        Args:
            metric: Name of the metric
            value: Value of the metric
            timestamp: Timestamp of the data point (default: current time)
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        self.historical_data[metric].append({
            "value": value,
            "timestamp": timestamp
        })
        
        # Limit the size of historical data
        if len(self.historical_data[metric]) > self.max_history_size:
            self.historical_data[metric].pop(0)
            
    def add_telemetry_data(self, telemetry_data: Dict[str, Dict[str, Any]]) -> None:
        """
        Add telemetry data to historical data.
        
        Args:
            telemetry_data: Dictionary of telemetry data
        """
        timestamp = datetime.datetime.now()
        for metric, data in telemetry_data.items():
            value = data.get("value")
            if value is not None:
                self.add_data_point(metric, value, timestamp)
                
    def analyze_dtcs(self, dtcs: List[str]) -> Dict[str, Any]:
        """
        Analyze Diagnostic Trouble Codes (DTCs).
        
        Args:
            dtcs: List of DTCs
            
        Returns:
            Dict[str, Any]: Analysis of DTCs including severity and overall health status
        """
        if not dtcs:
            return {
                "count": 0,
                "codes": [],
                "severity": HealthStatus.GOOD,
                "critical_codes": [],
                "warning_codes": []
            }
            
        critical_codes = []
        warning_codes = []
        
        for dtc in dtcs:
            # Check for specific code first
            if dtc in self.dtc_severity:
                severity = self.dtc_severity[dtc]
            # Then check for code family (first 2 characters)
            elif dtc[:2] in self.dtc_severity:
                severity = self.dtc_severity[dtc[:2]]
            # Default to WARNING if unknown
            else:
                severity = "WARNING"
                
            if severity == "CRITICAL":
                critical_codes.append(dtc)
            elif severity == "WARNING":
                warning_codes.append(dtc)
                
        # Determine overall severity
        if critical_codes:
            overall_severity = HealthStatus.CRITICAL
        elif warning_codes:
            overall_severity = HealthStatus.WARNING
        else:
            overall_severity = HealthStatus.GOOD
            
        return {
            "count": len(dtcs),
            "codes": dtcs,
            "severity": overall_severity,
            "critical_codes": critical_codes,
            "warning_codes": warning_codes
        }
        
    def analyze_vehicle_health(self, telemetry_data: Dict[str, Dict[str, Any]], 
                              dtcs: List[str]) -> Dict[str, Any]:
        """
        Analyze overall vehicle health based on telemetry data and DTCs.
        
        Args:
            telemetry_data: Dictionary of telemetry data
            dtcs: List of DTCs
            
        Returns:
            Dict[str, Any]: Vehicle health analysis
        """
        # Add current telemetry data to historical data
        self.add_telemetry_data(telemetry_data)
        
        # Analyze DTCs
        dtc_analysis = self.analyze_dtcs(dtcs)
        
        # Analyze key metrics
        metrics_analysis = {}
        health_issues = []
        
        # Check coolant temperature
        if "COOLANT_TEMP" in telemetry_data:
            coolant_temp = telemetry_data["COOLANT_TEMP"]["value"]
            if coolant_temp > 105:  # Celsius
                metrics_analysis["COOLANT_TEMP"] = {
                    "status": HealthStatus.CRITICAL,
                    "value": coolant_temp,
                    "message": "Engine overheating"
                }
                health_issues.append("Engine overheating")
            elif coolant_temp > 95:
                metrics_analysis["COOLANT_TEMP"] = {
                    "status": HealthStatus.WARNING,
                    "value": coolant_temp,
                    "message": "Engine temperature high"
                }
                health_issues.append("Engine temperature high")
            else:
                metrics_analysis["COOLANT_TEMP"] = {
                    "status": HealthStatus.GOOD,
                    "value": coolant_temp,
                    "message": "Engine temperature normal"
                }
                
        # Check engine load
        if "ENGINE_LOAD" in telemetry_data:
            engine_load = telemetry_data["ENGINE_LOAD"]["value"]
            if engine_load > 90:
                metrics_analysis["ENGINE_LOAD"] = {
                    "status": HealthStatus.WARNING,
                    "value": engine_load,
                    "message": "High engine load"
                }
                health_issues.append("High engine load")
            else:
                metrics_analysis["ENGINE_LOAD"] = {
                    "status": HealthStatus.GOOD,
                    "value": engine_load,
                    "message": "Engine load normal"
                }
                
        # Check fuel level
        if "FUEL_LEVEL" in telemetry_data:
            fuel_level = telemetry_data["FUEL_LEVEL"]["value"]
            if fuel_level < 10:
                metrics_analysis["FUEL_LEVEL"] = {
                    "status": HealthStatus.WARNING,
                    "value": fuel_level,
                    "message": "Low fuel level"
                }
                health_issues.append("Low fuel level")
            else:
                metrics_analysis["FUEL_LEVEL"] = {
                    "status": HealthStatus.GOOD,
                    "value": fuel_level,
                    "message": "Fuel level normal"
                }
                
        # Check oil temperature
        if "OIL_TEMP" in telemetry_data:
            oil_temp = telemetry_data["OIL_TEMP"]["value"]
            if oil_temp > 130:
                metrics_analysis["OIL_TEMP"] = {
                    "status": HealthStatus.CRITICAL,
                    "value": oil_temp,
                    "message": "Oil temperature critically high"
                }
                health_issues.append("Oil temperature critically high")
            elif oil_temp > 110:
                metrics_analysis["OIL_TEMP"] = {
                    "status": HealthStatus.WARNING,
                    "value": oil_temp,
                    "message": "Oil temperature high"
                }
                health_issues.append("Oil temperature high")
            else:
                metrics_analysis["OIL_TEMP"] = {
                    "status": HealthStatus.GOOD,
                    "value": oil_temp,
                    "message": "Oil temperature normal"
                }
                
        # Determine overall health status
        if dtc_analysis["severity"] == HealthStatus.CRITICAL or any(m["status"] == HealthStatus.CRITICAL for m in metrics_analysis.values()):
            overall_status = HealthStatus.CRITICAL
        elif dtc_analysis["severity"] == HealthStatus.WARNING or any(m["status"] == HealthStatus.WARNING for m in metrics_analysis.values()):
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.GOOD
            
        return {
            "status": overall_status,
            "dtc_analysis": dtc_analysis,
            "metrics_analysis": metrics_analysis,
            "issues": health_issues,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    def predict_maintenance(self) -> Dict[str, Any]:
        """
        Predict maintenance needs based on historical data.
        
        Returns:
            Dict[str, Any]: Maintenance predictions
        """
        predictions = []
        
        # Check for coolant temperature trends
        if "COOLANT_TEMP" in self.historical_data and len(self.historical_data["COOLANT_TEMP"]) > 10:
            coolant_temps = [d["value"] for d in self.historical_data["COOLANT_TEMP"]]
            avg_temp = statistics.mean(coolant_temps)
            if avg_temp > 95:
                predictions.append({
                    "component": "Cooling System",
                    "issue": "Potential cooling system issue",
                    "confidence": 0.8 if avg_temp > 100 else 0.6,
                    "recommendation": "Check coolant level and radiator condition"
                })
                
        # Check for engine load trends
        if "ENGINE_LOAD" in self.historical_data and len(self.historical_data["ENGINE_LOAD"]) > 10:
            loads = [d["value"] for d in self.historical_data["ENGINE_LOAD"]]
            avg_load = statistics.mean(loads)
            if avg_load > 80:
                predictions.append({
                    "component": "Engine",
                    "issue": "High average engine load",
                    "confidence": 0.7,
                    "recommendation": "Check for clogged air filter or fuel injector issues"
                })
                
        # Check for MAF sensor trends
        if "MAF" in self.historical_data and len(self.historical_data["MAF"]) > 10:
            maf_values = [d["value"] for d in self.historical_data["MAF"]]
            if statistics.stdev(maf_values) > 5:
                predictions.append({
                    "component": "Mass Air Flow Sensor",
                    "issue": "Inconsistent MAF readings",
                    "confidence": 0.75,
                    "recommendation": "Clean or replace MAF sensor"
                })
                
        # Check for O2 sensor trends
        o2_sensors = ["O2_B1S1", "O2_B1S2", "O2_B2S1", "O2_B2S2"]
        for sensor in o2_sensors:
            if sensor in self.historical_data and len(self.historical_data[sensor]) > 10:
                values = [d["value"] for d in self.historical_data[sensor]]
                if statistics.stdev(values) < 0.05:  # Low variation could indicate a stuck sensor
                    predictions.append({
                        "component": f"Oxygen Sensor ({sensor})",
                        "issue": "Possible stuck oxygen sensor",
                        "confidence": 0.65,
                        "recommendation": f"Inspect or replace {sensor} oxygen sensor"
                    })
                    
        return {
            "predictions": predictions,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    def analyze_sensor_status(self, sensor_data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze the status of vehicle sensors.
        
        Args:
            sensor_data: Dictionary of sensor data
            
        Returns:
            Dict[str, Dict[str, Any]]: Sensor status analysis
        """
        analyzed_sensors = {}
        
        for sensor_name, data in sensor_data.items():
            value = data.get("value")
            if value is None:
                continue
                
            status = HealthStatus.GOOD
            message = "Normal operation"
            
            # Add current data to historical data
            self.add_data_point(sensor_name, value)
            
            # Analyze specific sensors
            if sensor_name.startswith("O2_"):
                # Oxygen sensors should typically vary between 0.1 and 0.9V
                if isinstance(value, (int, float)):
                    if value < 0.1 or value > 0.9:
                        status = HealthStatus.WARNING
                        message = "Out of normal range"
                    # Check for stuck sensor
                    if len(self.historical_data[sensor_name]) > 10:
                        recent_values = [d["value"] for d in self.historical_data[sensor_name][-10:]]
                        if max(recent_values) - min(recent_values) < 0.05:
                            status = HealthStatus.WARNING
                            message = "Sensor may be stuck"
                            
            elif sensor_name == "COOLANT_TEMP":
                if value > 105:
                    status = HealthStatus.CRITICAL
                    message = "Critically high temperature"
                elif value > 95:
                    status = HealthStatus.WARNING
                    message = "High temperature"
                    
            elif sensor_name == "INTAKE_TEMP":
                if value > 60:
                    status = HealthStatus.WARNING
                    message = "High intake temperature"
                    
            elif sensor_name == "MAF":
                # Check for inconsistent MAF readings
                if len(self.historical_data[sensor_name]) > 10:
                    recent_values = [d["value"] for d in self.historical_data[sensor_name][-10:]]
                    if statistics.stdev(recent_values) > 5:
                        status = HealthStatus.WARNING
                        message = "Inconsistent readings"
                        
            elif sensor_name == "FUEL_PRESSURE":
                # Example thresholds - actual values would depend on vehicle specs
                if value < 30:
                    status = HealthStatus.WARNING
                    message = "Low fuel pressure"
                elif value > 70:
                    status = HealthStatus.WARNING
                    message = "High fuel pressure"
                    
            # Add analyzed sensor to result
            analyzed_sensors[sensor_name] = {
                "value": value,
                "unit": data.get("unit"),
                "status": status,
                "message": message
            }
            
        return analyzed_sensors

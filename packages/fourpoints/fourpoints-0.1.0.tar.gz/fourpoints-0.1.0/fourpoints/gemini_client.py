"""
Gemini Client Module for FourPoints.

This module integrates with Google's Gemini API to provide AI-powered insights
for vehicle diagnostics, maintenance recommendations, and DTC explanations.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Client for interacting with Google's Gemini API to provide AI-powered insights.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Google API key for Gemini
            model: Gemini model to use
        """
        self.api_key = api_key
        self.model = model
        self.initialized = False
        self.dtc_database = self._load_dtc_database()
        
        try:
            genai.configure(api_key=api_key)
            self.model_instance = genai.GenerativeModel(model_name=model)
            self.initialized = True
            logger.info(f"Gemini client initialized with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            
    def _load_dtc_database(self) -> Dict[str, Dict[str, str]]:
        """
        Load a basic DTC database with common codes and descriptions.
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary mapping DTC codes to their descriptions
        """
        # This is a simplified database. In a real implementation,
        # this would load from a comprehensive database file or API.
        return {
            "P0001": {
                "description": "Fuel Volume Regulator Control Circuit/Open",
                "possible_causes": "Wiring issue, fuel volume regulator failure, PCM failure",
                "severity": "High"
            },
            "P0002": {
                "description": "Fuel Volume Regulator Control Circuit Range/Performance",
                "possible_causes": "Fuel volume regulator, wiring, PCM",
                "severity": "Medium"
            },
            "P0100": {
                "description": "Mass or Volume Air Flow Circuit Malfunction",
                "possible_causes": "MAF sensor, wiring, air intake leaks",
                "severity": "Medium"
            },
            "P0101": {
                "description": "Mass or Volume Air Flow Circuit Range/Performance Problem",
                "possible_causes": "Dirty MAF sensor, intake leaks, wiring issues",
                "severity": "Medium"
            },
            "P0102": {
                "description": "Mass or Volume Air Flow Circuit Low Input",
                "possible_causes": "MAF sensor failure, wiring short to ground",
                "severity": "Medium"
            },
            "P0106": {
                "description": "Manifold Absolute Pressure/Barometric Pressure Circuit Range/Performance Problem",
                "possible_causes": "MAP sensor, wiring, vacuum leaks",
                "severity": "Medium"
            },
            "P0115": {
                "description": "Engine Coolant Temperature Circuit Malfunction",
                "possible_causes": "ECT sensor, wiring, thermostat",
                "severity": "Medium"
            },
            "P0117": {
                "description": "Engine Coolant Temperature Circuit Low Input",
                "possible_causes": "ECT sensor failure, wiring short to ground",
                "severity": "High"
            },
            "P0118": {
                "description": "Engine Coolant Temperature Circuit High Input",
                "possible_causes": "ECT sensor failure, wiring open circuit",
                "severity": "High"
            },
            "P0171": {
                "description": "System Too Lean (Bank 1)",
                "possible_causes": "Vacuum leaks, fuel pressure low, MAF sensor issue",
                "severity": "Medium"
            },
            "P0172": {
                "description": "System Too Rich (Bank 1)",
                "possible_causes": "Fuel pressure high, leaking injectors, MAF sensor issue",
                "severity": "Medium"
            },
            "P0300": {
                "description": "Random/Multiple Cylinder Misfire Detected",
                "possible_causes": "Ignition issues, fuel delivery, compression problems",
                "severity": "High"
            },
            "P0301": {
                "description": "Cylinder 1 Misfire Detected",
                "possible_causes": "Spark plug, ignition coil, injector, compression",
                "severity": "High"
            },
            "P0420": {
                "description": "Catalyst System Efficiency Below Threshold (Bank 1)",
                "possible_causes": "Catalytic converter failure, exhaust leaks, oxygen sensors",
                "severity": "Medium"
            },
            "P0440": {
                "description": "Evaporative Emission Control System Malfunction",
                "possible_causes": "EVAP system leaks, purge valve, fuel cap",
                "severity": "Low"
            }
        }
        
    def explain_dtc(self, dtc_code: str) -> Dict[str, str]:
        """
        Get explanation for a Diagnostic Trouble Code (DTC).
        
        Args:
            dtc_code: The DTC code to explain
            
        Returns:
            Dict[str, str]: Explanation of the DTC code
        """
        # First check local database
        if dtc_code in self.dtc_database:
            return self.dtc_database[dtc_code]
            
        # If not in local database, use Gemini to get explanation
        if not self.initialized:
            logger.error("Gemini client not initialized")
            return {
                "description": "Unknown code",
                "possible_causes": "Unable to retrieve information (Gemini API not initialized)",
                "severity": "Unknown"
            }
            
        try:
            prompt = f"""
            Provide information about the automotive diagnostic trouble code {dtc_code}.
            Format your response as a JSON object with the following fields:
            - description: A brief description of what the code means
            - possible_causes: Common causes for this code
            - severity: The severity level (Low, Medium, High)
            
            Only respond with the JSON object, no other text.
            """
            
            response = self.model_instance.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    top_p=0.95,
                    top_k=40
                )
            )
            
            try:
                # Extract JSON from response
                response_text = response.text
                # Remove any markdown code block formatting if present
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1]
                if response_text.endswith("```"):
                    response_text = response_text.split("```")[0]
                    
                response_text = response_text.strip()
                explanation = json.loads(response_text)
                
                # Cache the result for future use
                self.dtc_database[dtc_code] = explanation
                return explanation
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Gemini response as JSON: {response.text}")
                return {
                    "description": f"Code {dtc_code}",
                    "possible_causes": "Unable to retrieve detailed information",
                    "severity": "Unknown"
                }
                
        except Exception as e:
            logger.error(f"Error getting DTC explanation from Gemini: {str(e)}")
            return {
                "description": f"Code {dtc_code}",
                "possible_causes": "Error retrieving information",
                "severity": "Unknown"
            }
            
    def explain_dtcs(self, dtc_codes: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Get explanations for multiple Diagnostic Trouble Codes (DTCs).
        
        Args:
            dtc_codes: List of DTC codes to explain
            
        Returns:
            Dict[str, Dict[str, str]]: Dictionary mapping DTC codes to their explanations
        """
        explanations = {}
        for code in dtc_codes:
            explanations[code] = self.explain_dtc(code)
        return explanations
        
    def get_maintenance_advice(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI-powered maintenance advice based on vehicle data.
        
        Args:
            vehicle_data: Dictionary containing vehicle telemetry, DTCs, and other relevant data
            
        Returns:
            Dict[str, Any]: Maintenance advice
        """
        if not self.initialized:
            logger.error("Gemini client not initialized")
            return {
                "recommendations": [
                    {
                        "title": "Unable to generate recommendations",
                        "description": "Gemini API not initialized",
                        "priority": "Unknown"
                    }
                ]
            }
            
        try:
            # Prepare vehicle data for the prompt
            data_str = json.dumps(vehicle_data, indent=2)
            
            prompt = f"""
            Based on the following vehicle data, provide maintenance recommendations.
            
            Vehicle Data:
            {data_str}
            
            Format your response as a JSON object with an array of recommendations.
            Each recommendation should have:
            - title: A brief title for the recommendation
            - description: A detailed description of the recommendation
            - priority: Priority level (Low, Medium, High, Critical)
            - estimated_cost: Estimated cost range for the maintenance (if applicable)
            
            Only respond with the JSON object, no other text.
            """
            
            response = self.model_instance.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    top_p=0.95,
                    top_k=40
                )
            )
            
            try:
                # Extract JSON from response
                response_text = response.text
                # Remove any markdown code block formatting if present
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1]
                if response_text.endswith("```"):
                    response_text = response_text.split("```")[0]
                    
                response_text = response_text.strip()
                advice = json.loads(response_text)
                return advice
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Gemini response as JSON: {response.text}")
                return {
                    "recommendations": [
                        {
                            "title": "Error parsing recommendations",
                            "description": "The system encountered an error while generating recommendations.",
                            "priority": "Unknown"
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error getting maintenance advice from Gemini: {str(e)}")
            return {
                "recommendations": [
                    {
                        "title": "Error generating recommendations",
                        "description": f"Error: {str(e)}",
                        "priority": "Unknown"
                    }
                ]
            }
            
    def get_health_insights(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI-powered insights on vehicle health.
        
        Args:
            health_data: Dictionary containing vehicle health data
            
        Returns:
            Dict[str, Any]: Health insights
        """
        if not self.initialized:
            logger.error("Gemini client not initialized")
            return {
                "summary": "Unable to generate insights (Gemini API not initialized)",
                "insights": []
            }
            
        try:
            # Prepare health data for the prompt
            data_str = json.dumps(health_data, indent=2)
            
            prompt = f"""
            Based on the following vehicle health data, provide insights and recommendations.
            
            Health Data:
            {data_str}
            
            Format your response as a JSON object with:
            - summary: A brief summary of the vehicle's overall health
            - insights: An array of specific insights, each with:
              - title: A brief title for the insight
              - description: A detailed description
              - action_needed: Whether immediate action is needed (true/false)
              - recommendation: What action to take
            
            Only respond with the JSON object, no other text.
            """
            
            response = self.model_instance.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    top_p=0.95,
                    top_k=40
                )
            )
            
            try:
                # Extract JSON from response
                response_text = response.text
                # Remove any markdown code block formatting if present
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1]
                if response_text.endswith("```"):
                    response_text = response_text.split("```")[0]
                    
                response_text = response_text.strip()
                insights = json.loads(response_text)
                return insights
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Gemini response as JSON: {response.text}")
                return {
                    "summary": "Error parsing insights",
                    "insights": [
                        {
                            "title": "Error generating insights",
                            "description": "The system encountered an error while generating insights.",
                            "action_needed": False,
                            "recommendation": "Try again later or contact support."
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error getting health insights from Gemini: {str(e)}")
            return {
                "summary": "Error generating insights",
                "insights": [
                    {
                        "title": "Error",
                        "description": f"Error: {str(e)}",
                        "action_needed": False,
                        "recommendation": "Try again later or contact support."
                    }
                ]
            }

"""
Unit tests for the Gemini client module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
import json
import os
from pathlib import Path

from fourpoints.gemini_client import GeminiClient, GeminiAPIError


class TestGeminiClient(unittest.TestCase):
    """Test cases for GeminiClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the generative AI module
        self.patcher = patch('fourpoints.gemini_client.genai')
        self.mock_genai = self.patcher.start()
        
        # Mock the generative model
        self.mock_model = Mock()
        self.mock_genai.GenerativeModel.return_value = self.mock_model
        
        # Create GeminiClient with mock API key
        self.client = GeminiClient(api_key="mock_api_key", model="gemini-pro")
        
        # Mock the cache directory
        self.mock_cache_dir = patch.object(self.client, 'cache_dir', Path('mock_cache_dir'))
        self.mock_cache_dir.start()
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
        self.mock_cache_dir.stop()
        
    def test_init(self):
        """Test initialization."""
        # Verify
        self.assertEqual(self.client.api_key, "mock_api_key")
        self.assertEqual(self.client.model_name, "gemini-pro")
        self.mock_genai.configure.assert_called_once_with(api_key="mock_api_key")
        self.mock_genai.GenerativeModel.assert_called_once_with("gemini-pro")
        
    def test_explain_dtc_with_api(self):
        """Test explaining DTC with API."""
        # Setup
        mock_response = Mock()
        mock_response.text = "This is a mock explanation for P0123"
        self.mock_model.generate_content.return_value = mock_response
        
        # Test
        explanation = self.client.explain_dtc("P0123")
        
        # Verify
        self.assertEqual(explanation, "This is a mock explanation for P0123")
        self.mock_model.generate_content.assert_called_once()
        
    def test_explain_dtc_with_api_error(self):
        """Test explaining DTC with API error."""
        # Setup
        self.mock_model.generate_content.side_effect = Exception("API Error")
        
        # Mock the local database
        mock_dtc_db = {
            "P0123": {
                "description": "Throttle Position Sensor Circuit High Input",
                "explanation": "The throttle position sensor is showing a value that is higher than expected."
            }
        }
        
        with patch.object(self.client, '_load_local_dtc_database', return_value=mock_dtc_db):
            # Test
            explanation = self.client.explain_dtc("P0123")
            
            # Verify
            self.assertIn("throttle position sensor", explanation.lower())
            
    def test_explain_dtc_with_cache(self):
        """Test explaining DTC with cache."""
        # Setup - Create mock cache
        mock_cache = {
            "P0123": "Cached explanation for P0123"
        }
        
        with patch.object(self.client, '_load_cache', return_value=mock_cache):
            # Test
            explanation = self.client.explain_dtc("P0123")
            
            # Verify
            self.assertEqual(explanation, "Cached explanation for P0123")
            self.mock_model.generate_content.assert_not_called()
            
    def test_explain_dtc_not_found(self):
        """Test explaining DTC not found."""
        # Setup
        self.mock_model.generate_content.side_effect = Exception("API Error")
        
        # Test
        explanation = self.client.explain_dtc("INVALID_DTC")
        
        # Verify
        self.assertIn("could not find", explanation.lower())
        
    def test_get_maintenance_advice(self):
        """Test getting maintenance advice."""
        # Setup
        mock_response = Mock()
        mock_response.text = "This is mock maintenance advice"
        self.mock_model.generate_content.return_value = mock_response
        
        # Test
        advice = self.client.get_maintenance_advice(["P0123"], {"ENGINE_LOAD": 40, "COOLANT_TEMP": 90})
        
        # Verify
        self.assertEqual(advice, "This is mock maintenance advice")
        self.mock_model.generate_content.assert_called_once()
        
    def test_get_maintenance_advice_error(self):
        """Test getting maintenance advice with error."""
        # Setup
        self.mock_model.generate_content.side_effect = Exception("API Error")
        
        # Test
        advice = self.client.get_maintenance_advice(["P0123"], {"ENGINE_LOAD": 40, "COOLANT_TEMP": 90})
        
        # Verify
        self.assertIn("unable to get", advice.lower())
        
    def test_get_health_insights(self):
        """Test getting health insights."""
        # Setup
        mock_response = Mock()
        mock_response.text = "This is mock health insight"
        self.mock_model.generate_content.return_value = mock_response
        
        # Test
        insights = self.client.get_health_insights({"ENGINE_LOAD": 40, "COOLANT_TEMP": 90})
        
        # Verify
        self.assertEqual(insights, "This is mock health insight")
        self.mock_model.generate_content.assert_called_once()
        
    def test_get_health_insights_error(self):
        """Test getting health insights with error."""
        # Setup
        self.mock_model.generate_content.side_effect = Exception("API Error")
        
        # Test
        insights = self.client.get_health_insights({"ENGINE_LOAD": 40, "COOLANT_TEMP": 90})
        
        # Verify
        self.assertIn("unable to get", insights.lower())
        
    def test_save_to_cache(self):
        """Test saving to cache."""
        # Setup
        mock_cache = {}
        
        with patch.object(self.client, '_load_cache', return_value=mock_cache), \
             patch.object(self.client, '_save_cache') as mock_save_cache:
            # Test
            self.client._save_to_cache("P0123", "Test explanation")
            
            # Verify
            mock_save_cache.assert_called_once()
            self.assertEqual(mock_cache["P0123"], "Test explanation")
            
    def test_load_cache(self):
        """Test loading cache."""
        # Setup
        mock_cache = {"P0123": "Cached explanation"}
        
        with patch('json.load', return_value=mock_cache), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', MagicMock()):
            # Test
            cache = self.client._load_cache()
            
            # Verify
            self.assertEqual(cache, mock_cache)
            
    def test_load_cache_not_exists(self):
        """Test loading cache that doesn't exist."""
        # Setup
        with patch('pathlib.Path.exists', return_value=False):
            # Test
            cache = self.client._load_cache()
            
            # Verify
            self.assertEqual(cache, {})
            
    def test_save_cache(self):
        """Test saving cache."""
        # Setup
        mock_cache = {"P0123": "Cached explanation"}
        
        with patch('json.dump') as mock_json_dump, \
             patch('builtins.open', MagicMock()), \
             patch('pathlib.Path.parent.exists', return_value=False), \
             patch('pathlib.Path.parent.mkdir') as mock_mkdir:
            # Test
            self.client._save_cache(mock_cache)
            
            # Verify
            mock_mkdir.assert_called_once()
            mock_json_dump.assert_called_once()
            
    def test_load_local_dtc_database(self):
        """Test loading local DTC database."""
        # Setup
        mock_db = {"P0123": {"description": "Test description"}}
        
        with patch('json.load', return_value=mock_db), \
             patch('builtins.open', MagicMock()), \
             patch('pathlib.Path.exists', return_value=True):
            # Test
            db = self.client._load_local_dtc_database()
            
            # Verify
            self.assertEqual(db, mock_db)
            
    def test_load_local_dtc_database_not_exists(self):
        """Test loading local DTC database that doesn't exist."""
        # Setup
        with patch('pathlib.Path.exists', return_value=False):
            # Test
            db = self.client._load_local_dtc_database()
            
            # Verify
            self.assertEqual(db, {})


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for the OBD client module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
import obd
from obd.OBDResponse import OBDResponse
from obd.commands import OBDCommand
from obd.protocols import ECU
from obd.utils import Unit

from fourpoints.obd_client import OBDClient, OBDConnectionError, OBDCommandError


class TestOBDClient(unittest.TestCase):
    """Test cases for OBDClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = Mock(spec=obd.OBD)
        self.mock_connection.status = Mock(return_value=obd.OBDStatus.CAR_CONNECTED)
        self.mock_connection.is_connected = Mock(return_value=True)
        self.mock_connection.supported_commands = {
            "RPM": True,
            "SPEED": True,
            "ENGINE_LOAD": True,
            "COOLANT_TEMP": True,
        }
        
        # Create a patcher for the obd.OBD class
        self.patcher = patch('obd.OBD', return_value=self.mock_connection)
        self.mock_obd = self.patcher.start()
        
        # Create OBDClient with mocked connection
        self.client = OBDClient(port="mock_port")
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
        
    def test_connect_success(self):
        """Test successful connection."""
        # Test
        result = self.client.connect()
        
        # Verify
        self.assertTrue(result)
        self.assertTrue(self.client.is_connected)
        self.mock_obd.assert_called_once_with(
            portstr="mock_port", 
            baudrate=38400, 
            timeout=30.0, 
            fast=True, 
            interface="auto"
        )
        
    def test_connect_failure(self):
        """Test connection failure."""
        # Setup
        self.mock_connection.is_connected = Mock(return_value=False)
        
        # Test
        result = self.client.connect()
        
        # Verify
        self.assertFalse(result)
        self.assertFalse(self.client.is_connected)
        
    def test_disconnect(self):
        """Test disconnect."""
        # Setup
        self.client.connect()
        
        # Test
        self.client.disconnect()
        
        # Verify
        self.mock_connection.close.assert_called_once()
        self.assertFalse(self.client.is_connected)
        
    def test_query_success(self):
        """Test successful query."""
        # Setup
        mock_response = Mock(spec=OBDResponse)
        mock_response.value = 1500
        mock_response.is_null = Mock(return_value=False)
        self.mock_connection.query = Mock(return_value=mock_response)
        
        # Test
        response = self.client.query("RPM")
        
        # Verify
        self.assertEqual(response.value, 1500)
        self.mock_connection.query.assert_called_once()
        
    def test_query_not_connected(self):
        """Test query when not connected."""
        # Setup
        self.client.disconnect()
        
        # Test & Verify
        with self.assertRaises(OBDConnectionError):
            self.client.query("RPM")
            
    def test_query_command_error(self):
        """Test query with command error."""
        # Setup
        self.mock_connection.query = Mock(side_effect=Exception("Command error"))
        
        # Test & Verify
        with self.assertRaises(OBDCommandError):
            self.client.query("RPM")
            
    def test_get_dtcs(self):
        """Test getting DTCs."""
        # Setup
        mock_response = Mock(spec=OBDResponse)
        mock_response.value = ["P0123", "P0456"]
        mock_response.is_null = Mock(return_value=False)
        self.mock_connection.query = Mock(return_value=mock_response)
        
        # Test
        dtcs = self.client.get_dtcs()
        
        # Verify
        self.assertEqual(dtcs, ["P0123", "P0456"])
        self.mock_connection.query.assert_called_once()
        
    def test_clear_dtcs(self):
        """Test clearing DTCs."""
        # Setup
        mock_response = Mock(spec=OBDResponse)
        mock_response.value = None
        mock_response.is_null = Mock(return_value=False)
        self.mock_connection.query = Mock(return_value=mock_response)
        
        # Test
        result = self.client.clear_dtcs()
        
        # Verify
        self.assertTrue(result)
        self.mock_connection.query.assert_called_once()
        
    def test_get_supported_commands(self):
        """Test getting supported commands."""
        # Test
        commands = self.client.get_supported_commands()
        
        # Verify
        self.assertEqual(set(commands), {"RPM", "SPEED", "ENGINE_LOAD", "COOLANT_TEMP"})
        
    def test_is_command_supported(self):
        """Test checking if a command is supported."""
        # Test & Verify
        self.assertTrue(self.client.is_command_supported("RPM"))
        self.assertTrue(self.client.is_command_supported("SPEED"))
        self.assertFalse(self.client.is_command_supported("UNKNOWN_COMMAND"))


class TestOBDClientAsync(unittest.TestCase):
    """Test cases for OBDClient async methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection = Mock(spec=obd.OBD)
        self.mock_connection.status = Mock(return_value=obd.OBDStatus.CAR_CONNECTED)
        self.mock_connection.is_connected = Mock(return_value=True)
        self.mock_connection.supported_commands = {
            "RPM": True,
            "SPEED": True,
        }
        
        # Create a patcher for the obd.OBD class
        self.patcher = patch('obd.OBD', return_value=self.mock_connection)
        self.mock_obd = self.patcher.start()
        
        # Create OBDClient with mocked connection
        self.client = OBDClient(port="mock_port")
        self.client.connect()
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
        
    @pytest.mark.asyncio
    async def test_async_query(self):
        """Test async query."""
        # Setup
        mock_response = Mock(spec=OBDResponse)
        mock_response.value = 1500
        mock_response.is_null = Mock(return_value=False)
        
        with patch.object(self.client, 'query', return_value=mock_response) as mock_query:
            # Test
            response = await self.client.async_query("RPM")
            
            # Verify
            self.assertEqual(response.value, 1500)
            mock_query.assert_called_once_with("RPM")
            
    @pytest.mark.asyncio
    async def test_async_get_dtcs(self):
        """Test async get DTCs."""
        # Setup
        mock_dtcs = ["P0123", "P0456"]
        
        with patch.object(self.client, 'get_dtcs', return_value=mock_dtcs) as mock_get_dtcs:
            # Test
            dtcs = await self.client.async_get_dtcs()
            
            # Verify
            self.assertEqual(dtcs, mock_dtcs)
            mock_get_dtcs.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_async_clear_dtcs(self):
        """Test async clear DTCs."""
        # Setup
        with patch.object(self.client, 'clear_dtcs', return_value=True) as mock_clear_dtcs:
            # Test
            result = await self.client.async_clear_dtcs()
            
            # Verify
            self.assertTrue(result)
            mock_clear_dtcs.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_async_get_telemetry(self):
        """Test async get telemetry."""
        # Setup
        def mock_query_side_effect(cmd):
            if cmd == "RPM":
                resp = Mock(spec=OBDResponse)
                resp.value = 1500
                resp.is_null = Mock(return_value=False)
                return resp
            elif cmd == "SPEED":
                resp = Mock(spec=OBDResponse)
                resp.value = 60
                resp.is_null = Mock(return_value=False)
                return resp
            return None
            
        with patch.object(self.client, 'query', side_effect=mock_query_side_effect):
            # Test
            telemetry = await self.client.async_get_telemetry(["RPM", "SPEED"])
            
            # Verify
            self.assertEqual(len(telemetry), 2)
            self.assertEqual(telemetry["RPM"], 1500)
            self.assertEqual(telemetry["SPEED"], 60)


if __name__ == '__main__':
    unittest.main()

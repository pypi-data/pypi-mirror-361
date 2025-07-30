"""
Unit tests for the streaming module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest
import asyncio
from fastapi import WebSocket

from fourpoints.streaming import DataStream, WebSocketStreamer, StreamEvent, StreamEventType


class TestDataStream(unittest.TestCase):
    """Test cases for DataStream."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock OBD client
        self.mock_obd_client = Mock()
        
        # Create data stream
        self.data_stream = DataStream(self.mock_obd_client)
        
        # Setup event loop for async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.loop.close()
        
    def test_init(self):
        """Test initialization."""
        # Verify
        self.assertEqual(self.data_stream.obd_client, self.mock_obd_client)
        self.assertFalse(self.data_stream.streaming)
        self.assertEqual(self.data_stream.commands, [])
        self.assertEqual(self.data_stream.thresholds, {})
        self.assertEqual(self.data_stream.interval, 0.1)
        
    def test_add_commands(self):
        """Test adding commands."""
        # Test
        added = self.data_stream.add_commands(["RPM", "SPEED"])
        
        # Verify
        self.assertEqual(added, ["RPM", "SPEED"])
        self.assertEqual(self.data_stream.commands, ["RPM", "SPEED"])
        
        # Test adding duplicate
        added = self.data_stream.add_commands(["RPM", "ENGINE_LOAD"])
        
        # Verify
        self.assertEqual(added, ["ENGINE_LOAD"])
        self.assertEqual(set(self.data_stream.commands), set(["RPM", "SPEED", "ENGINE_LOAD"]))
        
    def test_remove_commands(self):
        """Test removing commands."""
        # Setup
        self.data_stream.commands = ["RPM", "SPEED", "ENGINE_LOAD"]
        
        # Test
        removed = self.data_stream.remove_commands(["RPM", "INVALID"])
        
        # Verify
        self.assertEqual(removed, ["RPM"])
        self.assertEqual(self.data_stream.commands, ["SPEED", "ENGINE_LOAD"])
        
    def test_set_threshold(self):
        """Test setting threshold."""
        # Test
        result = self.data_stream.set_threshold("RPM", 500, 5000)
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(self.data_stream.thresholds["RPM"], {"min": 500, "max": 5000})
        
    def test_remove_threshold(self):
        """Test removing threshold."""
        # Setup
        self.data_stream.thresholds = {
            "RPM": {"min": 500, "max": 5000},
            "SPEED": {"min": 0, "max": 120}
        }
        
        # Test
        result = self.data_stream.remove_threshold("RPM")
        
        # Verify
        self.assertTrue(result)
        self.assertNotIn("RPM", self.data_stream.thresholds)
        self.assertIn("SPEED", self.data_stream.thresholds)
        
        # Test removing non-existent threshold
        result = self.data_stream.remove_threshold("INVALID")
        
        # Verify
        self.assertFalse(result)
        
    def test_check_thresholds(self):
        """Test checking thresholds."""
        # Setup
        self.data_stream.thresholds = {
            "RPM": {"min": 500, "max": 5000},
            "SPEED": {"min": 0, "max": 120}
        }
        
        # Test within thresholds
        data = {"RPM": 1500, "SPEED": 60}
        violations = self.data_stream._check_thresholds(data)
        
        # Verify
        self.assertEqual(violations, [])
        
        # Test threshold violation
        data = {"RPM": 5500, "SPEED": 60}
        violations = self.data_stream._check_thresholds(data)
        
        # Verify
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["command"], "RPM")
        self.assertEqual(violations[0]["value"], 5500)
        self.assertEqual(violations[0]["threshold"], {"min": 500, "max": 5000})
        
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_stream_data(self, mock_sleep):
        """Test streaming data."""
        # Setup
        self.data_stream.commands = ["RPM", "SPEED"]
        self.data_stream.streaming = True
        self.data_stream.interval = 0.1
        
        # Mock query responses
        self.mock_obd_client.query_command.side_effect = [
            {"RPM": 1500},
            {"SPEED": 60}
        ]
        
        # Mock event handlers
        self.data_stream.on_data = Mock()
        self.data_stream.on_error = Mock()
        
        # Create a mock task that will be cancelled after one iteration
        async def cancel_after_delay():
            await asyncio.sleep(0.05)
            self.data_stream.streaming = False
            
        # Run the stream_data method and cancel_after_delay concurrently
        await asyncio.gather(
            self.data_stream._stream_data(),
            cancel_after_delay()
        )
        
        # Verify
        self.mock_obd_client.query_command.assert_called()
        self.data_stream.on_data.assert_called()
        mock_sleep.assert_called_with(0.1)
        
    @patch.object(DataStream, '_stream_data')
    def test_start(self, mock_stream_data):
        """Test starting the stream."""
        # Setup
        self.data_stream.commands = ["RPM", "SPEED"]
        mock_stream_data.return_value = asyncio.Future()
        mock_stream_data.return_value.set_result(None)
        
        # Test
        result = self.data_stream.start()
        
        # Verify
        self.assertTrue(result)
        self.assertTrue(self.data_stream.streaming)
        mock_stream_data.assert_called_once()
        
    def test_start_no_commands(self):
        """Test starting the stream with no commands."""
        # Test
        result = self.data_stream.start()
        
        # Verify
        self.assertFalse(result)
        self.assertFalse(self.data_stream.streaming)
        
    def test_stop(self):
        """Test stopping the stream."""
        # Setup
        self.data_stream.streaming = True
        
        # Test
        self.data_stream.stop()
        
        # Verify
        self.assertFalse(self.data_stream.streaming)


class TestWebSocketStreamer(unittest.TestCase):
    """Test cases for WebSocketStreamer."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock data stream
        self.mock_data_stream = Mock()
        
        # Create websocket streamer
        self.streamer = WebSocketStreamer(self.mock_data_stream)
        
        # Setup event loop for async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.loop.close()
        
    def test_init(self):
        """Test initialization."""
        # Verify
        self.assertEqual(self.streamer.data_stream, self.mock_data_stream)
        self.assertEqual(self.streamer.active_connections, set())
        
        # Verify event handlers are set
        self.assertEqual(self.mock_data_stream.on_data, self.streamer.handle_data_event)
        self.assertEqual(self.mock_data_stream.on_error, self.streamer.handle_error_event)
        self.assertEqual(self.mock_data_stream.on_connection, self.streamer.handle_connection_event)
        self.assertEqual(self.mock_data_stream.on_threshold, self.streamer.handle_threshold_event)
        
    @patch('json.dumps', return_value='{"type":"data","data":{"RPM":1500}}')
    async def test_handle_data_event(self, mock_dumps):
        """Test handling data event."""
        # Setup
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        self.streamer.active_connections = {mock_websocket1, mock_websocket2}
        
        # Test
        await self.streamer.handle_data_event({"RPM": 1500})
        
        # Verify
        mock_websocket1.send_text.assert_called_once_with('{"type":"data","data":{"RPM":1500}}')
        mock_websocket2.send_text.assert_called_once_with('{"type":"data","data":{"RPM":1500}}')
        
    @patch('json.dumps', return_value='{"type":"error","message":"Test error"}')
    async def test_handle_error_event(self, mock_dumps):
        """Test handling error event."""
        # Setup
        mock_websocket = AsyncMock()
        self.streamer.active_connections = {mock_websocket}
        
        # Test
        await self.streamer.handle_error_event("Test error")
        
        # Verify
        mock_websocket.send_text.assert_called_once_with('{"type":"error","message":"Test error"}')
        
    @patch('json.dumps', return_value='{"type":"connection","status":"connected"}')
    async def test_handle_connection_event(self, mock_dumps):
        """Test handling connection event."""
        # Setup
        mock_websocket = AsyncMock()
        self.streamer.active_connections = {mock_websocket}
        
        # Test
        await self.streamer.handle_connection_event(True)
        
        # Verify
        mock_websocket.send_text.assert_called_once_with('{"type":"connection","status":"connected"}')
        
    @patch('json.dumps', return_value='{"type":"threshold","violations":[{"command":"RPM","value":5500}]}')
    async def test_handle_threshold_event(self, mock_dumps):
        """Test handling threshold event."""
        # Setup
        mock_websocket = AsyncMock()
        self.streamer.active_connections = {mock_websocket}
        
        # Test
        await self.streamer.handle_threshold_event([{"command": "RPM", "value": 5500}])
        
        # Verify
        mock_websocket.send_text.assert_called_once_with('{"type":"threshold","violations":[{"command":"RPM","value":5500}]}')
        
    async def test_connect(self):
        """Test connecting a websocket."""
        # Setup
        mock_websocket = AsyncMock()
        
        # Test
        await self.streamer.connect(mock_websocket)
        
        # Verify
        self.assertIn(mock_websocket, self.streamer.active_connections)
        mock_websocket.accept.assert_called_once()
        
    async def test_disconnect(self):
        """Test disconnecting a websocket."""
        # Setup
        mock_websocket = AsyncMock()
        self.streamer.active_connections = {mock_websocket}
        
        # Test
        await self.streamer.disconnect(mock_websocket)
        
        # Verify
        self.assertNotIn(mock_websocket, self.streamer.active_connections)
        
    @patch('json.loads', return_value={"action": "subscribe", "commands": ["RPM", "SPEED"]})
    async def test_handle_message_subscribe(self, mock_loads):
        """Test handling subscribe message."""
        # Setup
        self.mock_data_stream.add_commands.return_value = ["RPM", "SPEED"]
        mock_websocket = AsyncMock()
        
        # Test
        await self.streamer.handle_message(mock_websocket, '{"action":"subscribe","commands":["RPM","SPEED"]}')
        
        # Verify
        self.mock_data_stream.add_commands.assert_called_once_with(["RPM", "SPEED"])
        mock_websocket.send_text.assert_called_once()
        
    @patch('json.loads', return_value={"action": "unsubscribe", "commands": ["RPM"]})
    async def test_handle_message_unsubscribe(self, mock_loads):
        """Test handling unsubscribe message."""
        # Setup
        self.mock_data_stream.remove_commands.return_value = ["RPM"]
        mock_websocket = AsyncMock()
        
        # Test
        await self.streamer.handle_message(mock_websocket, '{"action":"unsubscribe","commands":["RPM"]}')
        
        # Verify
        self.mock_data_stream.remove_commands.assert_called_once_with(["RPM"])
        mock_websocket.send_text.assert_called_once()
        
    @patch('json.loads', return_value={"action": "set_threshold", "command": "RPM", "min": 500, "max": 5000})
    async def test_handle_message_set_threshold(self, mock_loads):
        """Test handling set_threshold message."""
        # Setup
        self.mock_data_stream.set_threshold.return_value = True
        mock_websocket = AsyncMock()
        
        # Test
        await self.streamer.handle_message(mock_websocket, '{"action":"set_threshold","command":"RPM","min":500,"max":5000}')
        
        # Verify
        self.mock_data_stream.set_threshold.assert_called_once_with("RPM", 500, 5000)
        mock_websocket.send_text.assert_called_once()
        
    @patch('json.loads', return_value={"action": "remove_threshold", "command": "RPM"})
    async def test_handle_message_remove_threshold(self, mock_loads):
        """Test handling remove_threshold message."""
        # Setup
        self.mock_data_stream.remove_threshold.return_value = True
        mock_websocket = AsyncMock()
        
        # Test
        await self.streamer.handle_message(mock_websocket, '{"action":"remove_threshold","command":"RPM"}')
        
        # Verify
        self.mock_data_stream.remove_threshold.assert_called_once_with("RPM")
        mock_websocket.send_text.assert_called_once()
        
    @patch('json.loads', return_value={"action": "unknown"})
    async def test_handle_message_unknown(self, mock_loads):
        """Test handling unknown message."""
        # Setup
        mock_websocket = AsyncMock()
        
        # Test
        await self.streamer.handle_message(mock_websocket, '{"action":"unknown"}')
        
        # Verify
        mock_websocket.send_text.assert_called_once()
        # Verify error message
        args = mock_websocket.send_text.call_args[0][0]
        self.assertIn("error", args.lower())
        self.assertIn("unknown action", args.lower())


if __name__ == '__main__':
    unittest.main()

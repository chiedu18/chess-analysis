import json
import unittest
from unittest.mock import Mock, patch, AsyncMock
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path
from ..consumers import AnalysisConsumer
from ..routing import websocket_urlpatterns

class TestAnalysisConsumer(unittest.TestCase):
    
    def setUp(self):
        self.sample_pgn = """[Event "Test Game"]
[Site "Test Site"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O O-O 5. d3 d6 6. Nc3 Nf6 7. Bg5 h6 8. Bh4 g5 9. Bg3 Nh5 10. Nxe5 Nxe5 11. d4 Bxd4 12. Qxd4 Nc6 13. Qh4 Nf6 14. Bxf7+ Rxf7 15. Qxf6 Qe7 16. Qxe7+ Nxe7 17. Nxd6 cxd6 18. Rfe1 Be6 19. Rxe6 Nc6 20. Rae1 Rf8 21. Rxc6 bxc6 22. Rxe7 1-0"""
    
    @patch('core.consumers.sync_to_async')
    async def test_connect(self, mock_sync_to_async):
        """Test WebSocket connection"""
        communicator = WebsocketCommunicator(
            AnalysisConsumer.as_asgi(),
            "/ws/analysis/test-pgn-id/"
        )
        communicator.scope["url_route"] = {"kwargs": {"pgn_id": "test-pgn-id"}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Check initial status message
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "status")
        self.assertIn("Connected", response["message"])
        
        await communicator.disconnect()
    
    @patch('core.consumers.sync_to_async')
    async def test_start_analysis_success(self, mock_sync_to_async):
        """Test successful analysis start"""
        # Mock the analysis result
        mock_analysis = [
            {"eval": {"type": "cp", "value": 34}, "lines": [{"Move": "e4", "Centipawn": 34}]},
            {"eval": {"type": "cp", "value": 12}, "lines": [{"Move": "e5", "Centipawn": 12}]}
        ]
        mock_sync_to_async.return_value = AsyncMock(return_value=mock_analysis)
        
        communicator = WebsocketCommunicator(
            AnalysisConsumer.as_asgi(),
            "/ws/analysis/test-pgn-id/"
        )
        communicator.scope["url_route"] = {"kwargs": {"pgn_id": "test-pgn-id"}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send start analysis message
        await communicator.send_json_to({
            "type": "start_analysis",
            "pgn": self.sample_pgn
        })
        
        # Check analysis messages
        for i in range(len(mock_analysis)):
            response = await communicator.receive_json_from()
            self.assertEqual(response["type"], "analysis")
            self.assertEqual(response["ply"], i)
            self.assertEqual(response["eval"], mock_analysis[i]["eval"])
            self.assertEqual(response["lines"], mock_analysis[i]["lines"])
        
        # Check completion message
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "complete")
        
        await communicator.disconnect()
    
    @patch('core.consumers.sync_to_async')
    async def test_start_analysis_no_pgn(self, mock_sync_to_async):
        """Test analysis start without PGN"""
        communicator = WebsocketCommunicator(
            AnalysisConsumer.as_asgi(),
            "/ws/analysis/test-pgn-id/"
        )
        communicator.scope["url_route"] = {"kwargs": {"pgn_id": "test-pgn-id"}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send start analysis message without PGN
        await communicator.send_json_to({
            "type": "start_analysis"
        })
        
        # Check error message
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "error")
        self.assertIn("No PGN provided", response["message"])
        
        await communicator.disconnect()
    
    @patch('core.consumers.sync_to_async')
    async def test_start_analysis_failure(self, mock_sync_to_async):
        """Test analysis start when analysis fails"""
        mock_sync_to_async.return_value = AsyncMock(return_value=[])
        
        communicator = WebsocketCommunicator(
            AnalysisConsumer.as_asgi(),
            "/ws/analysis/test-pgn-id/"
        )
        communicator.scope["url_route"] = {"kwargs": {"pgn_id": "test-pgn-id"}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send start analysis message
        await communicator.send_json_to({
            "type": "start_analysis",
            "pgn": self.sample_pgn
        })
        
        # Check error message
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "error")
        self.assertIn("Failed to analyze", response["message"])
        
        await communicator.disconnect()
    
    async def test_unknown_message_type(self):
        """Test handling of unknown message types"""
        communicator = WebsocketCommunicator(
            AnalysisConsumer.as_asgi(),
            "/ws/analysis/test-pgn-id/"
        )
        communicator.scope["url_route"] = {"kwargs": {"pgn_id": "test-pgn-id"}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send unknown message type
        await communicator.send_json_to({
            "type": "unknown_type"
        })
        
        # Check error message
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "error")
        self.assertIn("Unknown message type", response["message"])
        
        await communicator.disconnect()

if __name__ == '__main__':
    unittest.main() 
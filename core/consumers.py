import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .services.engine import analyse_pgn
import asyncio

logger = logging.getLogger(__name__)

class AnalysisConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for streaming chess analysis
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.pgn_id = self.scope["url_route"]["kwargs"]["pgn_id"]
        self.room_group_name = f"analysis_{self.pgn_id}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected for analysis {self.pgn_id}")
        
        # Send initial status
        await self.send_json({
            "type": "status",
            "message": "Connected, starting analysis..."
        })
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected for analysis {self.pgn_id}")
    
    async def receive_json(self, content):
        """Handle incoming JSON messages"""
        message_type = content.get("type")
        
        if message_type == "start_analysis":
            pgn_text = content.get("pgn")
            if pgn_text:
                await self.start_analysis(pgn_text)
            else:
                await self.send_json({
                    "type": "error",
                    "message": "No PGN provided"
                })
        else:
            await self.send_json({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            })
    
    async def start_analysis(self, pgn_text):
        """Start the analysis process"""
        try:
            # Run analysis in a thread to avoid blocking
            analysis = await sync_to_async(analyse_pgn)(pgn_text)
            
            if not analysis:
                await self.send_json({
                    "type": "error",
                    "message": "Failed to analyze game"
                })
                return
            
            # Send analysis results
            for ply, data in enumerate(analysis):
                await self.send_json({
                    "type": "analysis",
                    "ply": ply,
                    "eval": data.get("eval", {}),
                    "lines": data.get("lines", [])
                })
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.1)
            
            # Send completion message
            await self.send_json({
                "type": "complete",
                "message": f"Analysis complete - {len(analysis)} positions analyzed"
            })
            
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            await self.send_json({
                "type": "error",
                "message": f"Analysis error: {str(e)}"
            })
    
    async def analysis_message(self, event):
        """Send analysis message to WebSocket"""
        await self.send_json(event) 
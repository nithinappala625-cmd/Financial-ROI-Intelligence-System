import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

router = APIRouter(prefix="/ws", tags=["websocket"])
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and broadcasts Real-Time Kafka event streams"""
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New WebSocket connection accepted.")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("WebSocket connection disconnected.")

    async def broadcast_financial_update(self, message: dict):
        """Simulates Kafka event pushing live updates to the dashboard"""
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@router.websocket("/live-financials")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We keep sending simulated Kafka financial metrics streaming
            # Or waiting for client messages if needed
            data = await websocket.receive_text()
            logger.info(f"Received from client: {data}")
            # Mocking push back
            await manager.broadcast_financial_update({
                "type": "KafkaEvent",
                "topic": "financial_roi_stream",
                "data": {
                    "event": "BUDGET_UPDATE",
                    "details": "Kafka streamed real-time project metric change."
                }
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)

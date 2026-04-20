"""
F048: WebSocket endpoint — WS /ws/dashboard.
Streams live ROI, new alerts, expense updates, AI predictions to clients.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.api.ws.manager import ws_manager
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/dashboard")
async def websocket_dashboard(
    websocket: WebSocket,
    tenant_id: int = Query(default=None),
):
    """
    Real-time dashboard WebSocket stream.
    
    Clients connect and receive push notifications for:
    - expense.created: new expense logged
    - alert.triggered: new alert fired
    - project.updated: project data changed
    - ai.prediction.ready: AI prediction completed
    - employee.flagged: employee flagged as underperforming
    
    Query params:
        tenant_id: optional tenant filter
    """
    await ws_manager.connect(websocket, tenant_id=tenant_id)

    try:
        while True:
            # Keep connection alive; handle incoming client messages
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type", "")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                elif msg_type == "subscribe":
                    # Future: topic-level subscriptions
                    await websocket.send_json({
                        "type": "subscribed",
                        "topics": msg.get("topics", ["all"]),
                    })
                else:
                    await websocket.send_json({"type": "ack", "received": msg_type})
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, tenant_id=tenant_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket, tenant_id=tenant_id)


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """Dedicated alert stream WebSocket."""
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

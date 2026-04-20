"""
F048: WebSocket Dashboard Stream Manager.
WS /ws/dashboard — pushes live ROI, new alerts, expense updates, AI predictions.
"""

import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time dashboard updates."""

    def __init__(self):
        # tenant_id -> set of WebSocket connections
        self._connections: Dict[int, Set[WebSocket]] = {}
        # Global connections (no tenant filter)
        self._global_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, tenant_id: int = None):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        if tenant_id:
            if tenant_id not in self._connections:
                self._connections[tenant_id] = set()
            self._connections[tenant_id].add(websocket)
        else:
            self._global_connections.add(websocket)
        logger.info(f"WebSocket connected (tenant={tenant_id}), total={self.connection_count}")

    def disconnect(self, websocket: WebSocket, tenant_id: int = None):
        """Remove a WebSocket connection."""
        if tenant_id and tenant_id in self._connections:
            self._connections[tenant_id].discard(websocket)
            if not self._connections[tenant_id]:
                del self._connections[tenant_id]
        else:
            self._global_connections.discard(websocket)
        logger.info(f"WebSocket disconnected (tenant={tenant_id}), total={self.connection_count}")

    @property
    def connection_count(self) -> int:
        total = len(self._global_connections)
        for conns in self._connections.values():
            total += len(conns)
        return total

    async def send_to_tenant(self, tenant_id: int, message: dict):
        """Send a message to all connections for a specific tenant."""
        dead = set()
        for ws in self._connections.get(tenant_id, set()):
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections.get(tenant_id, set()).discard(ws)

    async def broadcast(self, message: dict):
        """Broadcast a message to ALL connected clients."""
        dead = set()

        # Global connections
        for ws in self._global_connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._global_connections.discard(ws)

        # Tenant connections
        for tenant_id, connections in self._connections.items():
            dead_tenant = set()
            for ws in connections:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_tenant.add(ws)
            for ws in dead_tenant:
                connections.discard(ws)


# Singleton manager instance
ws_manager = ConnectionManager()


async def broadcast_event(topic: str, data: dict):
    """Broadcast a Kafka-style event to all WebSocket clients."""
    message = {
        "type": "event",
        "topic": topic,
        "data": data,
    }
    await ws_manager.broadcast(message)

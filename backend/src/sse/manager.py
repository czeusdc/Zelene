"""Module: Server-Sent Events connection manager.

This module manages SSE subscriptions and broadcasts for intelligence
deployments. Each deployment gets its own set of client connections,
and events are fanned out with timestamps to all active subscribers.
"""

import asyncio
import uuid
from datetime import datetime, timezone


class Connection:
    """A single SSE client connection with a message queue."""

    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.active = True

    async def send(self, event_type: str, data: dict):
        """Enqueue an event for this client."""
        await self.queue.put((event_type, data))

    async def close(self):
        """Deactivate and signal the client to disconnect."""
        self.active = False
        await self.queue.put(None)


class SSEManager:
    """Manages SSE subscriptions and broadcasts per deployment."""

    def __init__(self):
        self._connections: dict[str, list[Connection]] = {}
        self._speed: float = 1.0

    def create_deployment(self) -> str:
        """Create a deployment tracking entry and return its ID."""
        deployment_id = str(uuid.uuid4())
        self._connections[deployment_id] = []
        return deployment_id

    def subscribe(self, deployment_id: str) -> Connection:
        """Register a new SSE client connection for a deployment."""
        conn = Connection()
        self._connections.setdefault(deployment_id, []).append(conn)
        return conn

    def unsubscribe(self, deployment_id: str, conn: Connection):
        """Remove a disconnected client from a deployment."""
        if deployment_id in self._connections and conn in self._connections[deployment_id]:
            self._connections[deployment_id].remove(conn)

    async def broadcast(self, deployment_id: str, event_type: str, data: dict):
        """Send an event with timestamp to all active subscribers of a deployment."""
        full = {**data, "timestamp": datetime.now(timezone.utc).isoformat()}
        for conn in self._connections.get(deployment_id, [])[:]:
            if conn.active:
                try:
                    await conn.send(event_type, full)
                except Exception:
                    conn.active = False


sse_manager = SSEManager()

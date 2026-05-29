"""Module: Server-Sent Events connection manager.

This module manages SSE subscriptions and broadcasts for intelligence
deployments. Each deployment gets its own set of client connections,
and events are fanned out with timestamps to all active subscribers.

Events broadcast before any client subscribes are buffered per deployment
and replayed when the first client connects, preventing data loss from the
race between graph execution and SSE subscription.
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
    """Manages SSE subscriptions and broadcasts per deployment.

    Maintains an event buffer per deployment so that events emitted before
    any client subscribes are not lost — they are replayed on first connect.
    """

    def __init__(self):
        self._connections: dict[str, list[Connection]] = {}
        self._buffers: dict[str, list[tuple[str, dict]]] = {}
        self._speed: float = 1.0

    @property
    def speed(self) -> float:
        """Return the simulation speed, guarded against division by zero."""
        return self._speed if self._speed > 0 else 0.1

    def create_deployment(self) -> str:
        """Create a deployment tracking entry and return its ID."""
        deployment_id = str(uuid.uuid4())
        self._connections[deployment_id] = []
        self._buffers[deployment_id] = []
        return deployment_id

    def subscribe(self, deployment_id: str) -> Connection:
        """Register a new SSE client connection and replay any buffered events."""
        conn = Connection()
        self._connections.setdefault(deployment_id, []).append(conn)
        # Replay buffered events to the newly connected client
        buffer = self._buffers.get(deployment_id, [])
        for event_type, data in buffer:
            conn.queue.put_nowait((event_type, data))
        # Clear buffer once the first client has replayed it
        if buffer:
            self._buffers[deployment_id] = []
        return conn

    def unsubscribe(self, deployment_id: str, conn: Connection):
        """Remove a disconnected client from a deployment."""
        if deployment_id in self._connections and conn in self._connections[deployment_id]:
            self._connections[deployment_id].remove(conn)

    async def broadcast(self, deployment_id: str, event_type: str, data: dict):
        """Send an event with timestamp to all active subscribers of a deployment.

        If no subscribers are connected yet, the event is buffered and will be
        replayed when the first client subscribes.
        """
        full = {**data, "timestamp": datetime.now(timezone.utc).isoformat()}
        connections = self._connections.get(deployment_id, [])
        if not connections:
            # No client yet — buffer for later replay
            self._buffers.setdefault(deployment_id, []).append((event_type, full))
            return
        for conn in connections[:]:
            if conn.active:
                try:
                    await conn.send(event_type, full)
                except Exception:
                    conn.active = False

    def cleanup(self, deployment_id: str):
        """Remove all connections and buffer for a deployment."""
        self._connections.pop(deployment_id, None)
        self._buffers.pop(deployment_id, None)


sse_manager = SSEManager()

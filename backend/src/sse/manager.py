import asyncio
import uuid
from datetime import datetime, timezone

class Connection:
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.active = True

    async def send(self, event_type: str, data: dict):
        await self.queue.put((event_type, data))

    async def close(self):
        self.active = False
        await self.queue.put(None)

class SSEManager:
    def __init__(self):
        self._connections: dict[str, list[Connection]] = {}
        self._speed: float = 1.0

    def create_deployment(self) -> str:
        deployment_id = str(uuid.uuid4())
        self._connections[deployment_id] = []
        return deployment_id

    def subscribe(self, deployment_id: str) -> Connection:
        conn = Connection()
        self._connections.setdefault(deployment_id, []).append(conn)
        return conn

    def unsubscribe(self, deployment_id: str, conn: Connection):
        if deployment_id in self._connections and conn in self._connections[deployment_id]:
            self._connections[deployment_id].remove(conn)

    async def broadcast(self, deployment_id: str, event_type: str, data: dict):
        full = {**data, "timestamp": datetime.now(timezone.utc).isoformat()}
        for conn in self._connections.get(deployment_id, [])[:]:
            if conn.active:
                await conn.send(event_type, full)

sse_manager = SSEManager()

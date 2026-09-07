from fastapi import WebSocket


class ConnectionManager:
    """
    Keeps track of connected frontend WebSocket clients and broadcasts
    messages to all of them. Single Responsibility: connection bookkeeping
    only - it knows nothing about Redis, AI, or chat logic.
    """

    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, data: dict) -> None:
        dead_connections = []
        for connection in self._connections:
            try:
                await connection.send_json(data)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)

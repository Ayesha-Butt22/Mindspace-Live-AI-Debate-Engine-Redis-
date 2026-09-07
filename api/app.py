import asyncio
import os
import queue
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.connection_manager import ConnectionManager
from api.conversation_manager import ConversationManager
from controllers import message_controller

# Comma-separated list of allowed frontend origins, e.g.
# "https://your-app.vercel.app,https://your-app.netlify.app". Defaults to
# "*" (any origin) for local development.
ALLOWED_ORIGINS = os.environ.get("FRONTEND_ORIGINS", "*").split(",")

broadcast_queue: "queue.Queue" = queue.Queue()
connection_manager = ConnectionManager()
conversation_manager = ConversationManager(broadcast_queue)


async def _drain_broadcast_queue() -> None:
    """Moves messages from the background Redis listener threads onto the
    asyncio event loop so they can be sent to WebSocket clients."""
    loop = asyncio.get_event_loop()
    while True:
        message = await loop.run_in_executor(None, broadcast_queue.get)
        await connection_manager.broadcast(message)


@asynccontextmanager
async def lifespan(app: FastAPI):
    conversation_manager.start_listeners()
    drain_task = asyncio.create_task(_drain_broadcast_queue())
    yield
    drain_task.cancel()


app = FastAPI(title="Mindspace API", lifespan=lifespan)

# The frontend is deployed on a different domain, so it needs CORS enabled
# to call this API. Set FRONTEND_ORIGINS in production instead of relying
# on the "*" default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartConversationRequest(BaseModel):
    topic: str


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/start")
def start_conversation(request: StartConversationRequest):
    conversation_manager.start_conversation(request.topic)
    return {"status": "started", "topic": request.topic}


@app.get("/api/history")
def get_history():
    # Reuses the same controller/repository every chat mode (CLI and web)
    # already writes to - no new persistence logic here.
    rows = message_controller.list_messages()
    return [
        {"id": row[0], "sender": row[1], "content": row[2], "timestamp": row[3]}
        for row in rows
    ]


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            # This endpoint only pushes messages out; it still needs to
            # await something so it notices the client disconnecting.
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

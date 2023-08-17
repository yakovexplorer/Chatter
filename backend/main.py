from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    name: str
    content: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.messages: List[Message] = []
        self.active_users: List[str] = []

    async def connect(self, websocket: WebSocket, name: str):
        if not name or name.lower() in ["null", "undefined"] or name.lower() in [user.lower() for user in self.active_users]:
            await websocket.close(code=4000)
            return
        await websocket.accept()
        self.active_connections.append(websocket)
        self.active_users.append(name)
        message = Message(name="System", content=f"{name} has joined the chat.")
        self.messages.append(message)
        await self.broadcast({"type": "join", "name": name}, exclude=websocket)
        for message in self.messages:
            await websocket.send_json({"type": "message", "message": message.dict()})
        await self.broadcast_active_users()

    def disconnect(self, websocket: WebSocket, name: str):
        self.active_connections.remove(websocket)
        self.active_users.remove(name)
        message = Message(name="System", content=f"{name} has left the chat.")
        self.messages.append(message)
        self.broadcast({"type": "leave", "name": name})
        self.broadcast_active_users()

    async def broadcast(self, data: dict, exclude=None):
        for connection in self.active_connections:
            if connection == exclude:
                continue
            await connection.send_json(data)

    async def broadcast_active_users(self):
        await self.broadcast({"type": "active_users", "users": self.active_users})

manager = ConnectionManager()

@app.websocket("/ws/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    await manager.connect(websocket, name)
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "message":
                message = Message(**data["message"])
                manager.messages.append(message)
                await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, name)

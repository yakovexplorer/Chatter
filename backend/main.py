from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
import secrets

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
        self.csrf_tokens: dict = {}
        self.connection_status: dict = {}

    async def connect(self, websocket: WebSocket, name: str):
        if not name or name.lower() in ["null", "undefined"] or name.lower() in [user.lower() for user in
                                                                                 self.active_users]:
            await websocket.close(code=4000)
            return
        await websocket.accept()
        self.active_connections.append(websocket)
        self.active_users.append(name)
        csrf_token = secrets.token_hex(16)
        self.csrf_tokens[name] = csrf_token
        message = Message(name="System", content=f"{name} has joined the chat.")
        self.messages.append(message)
        await self.broadcast({"type": "join", "name": name}, exclude=websocket)
        for message in self.messages:
            await websocket.send_json({"type": "message", "message": message.dict()})
        await websocket.send_json({"type": "csrf_token", "csrf_token": csrf_token})
        await self.broadcast_active_users()
        self.connection_status[name] = True

    def disconnect(self, websocket: WebSocket, name: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.active_users.remove(name)
            del self.csrf_tokens[name]
            message = Message(name="System", content=f"{name} has left the chat.")
            self.messages.append(message)
            self.broadcast({"type": "leave", "name": name})
            self.broadcast_active_users()
            del self.connection_status[name]

    async def broadcast(self, data: dict, exclude=None):
        for connection in self.active_connections:
            if connection == exclude:
                continue
            await connection.send_json(data)

    async def broadcast_active_users(self):
        await self.broadcast({"type": "active_users", "users": self.active_users})

    async def check_connection_status(self, background_tasks: BackgroundTasks):
        for name, status in list(self.connection_status.items()):
            if not status:
                websocket = next(ws for ws in self.active_connections if ws == ws)
                self.disconnect(websocket, name)
                continue
            index = self.active_users.index(name)
            websocket = self.active_connections[index]
            try:
                await websocket.send_json({"type": "ping"})
                self.connection_status[name] = False
            except:
                pass
        background_tasks.add_task(self.check_connection_status, background_tasks)


manager = ConnectionManager()


@app.websocket("/ws/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str, background_tasks: BackgroundTasks):
    await manager.connect(websocket, name)
    background_tasks.add_task(manager.check_connection_status)
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "message":
                if data.get("csrf_token") != manager.csrf_tokens.get(name):
                    await websocket.close(code=4001)
                    return
                message = Message(**data["message"])
                manager.messages.append(message)
                await manager.broadcast(data)
            elif data["type"] == "leave":
                manager.disconnect(websocket, name)
                break
            elif data["type"] == "pong":
                manager.connection_status[name] = True
    except WebSocketDisconnect:
        manager.disconnect(websocket, name)

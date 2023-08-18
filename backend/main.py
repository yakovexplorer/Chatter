from functools import partial

import bleach
from bleach.linkifier import LinkifyFilter
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import secrets

from bleach import Cleaner
from markdown import Markdown

md = Markdown(output_format="html")

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
        name = bleach.clean(name)
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

    async def disconnect(self, websocket: WebSocket, name: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.active_users.remove(name)
            del self.csrf_tokens[name]
            message = Message(name="System", content=f"{name} has left the chat.")
            self.messages.append(message)
            await self.broadcast({"type": "leave", "name": name})
            await self.broadcast_active_users()
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
                await self.disconnect(websocket, name)
                continue
            index = self.active_users.index(name)
            websocket = self.active_connections[index]
            try:
                await websocket.send_json({"type": "ping"})
                self.connection_status[name] = False
            except WebSocketDisconnect:
                pass
        background_tasks.add_task(self.check_connection_status, background_tasks)


manager = ConnectionManager()

# List of allowed HTML tags
ALLOWED_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6", "hr",
    "ul", "ol", "li", "p", "br",
    "pre", "code", "blockquote",
    "strong", "em", "a", "img", "b", "i",
    "table", "thead", "tbody", "tr", "th", "td",
    "div", "span"
]

# A map of HTML tags to allowed attributes
# If a tag isn't here, then no attributes are allowed
ALLOWED_ATTRIBUTES = {
    "h1": ["id"], "h2": ["id"], "h3": ["id"], "h4": ["id"],
    "a": ["href", "title"],
    "img": ["src", "title", "alt"],
}

# Allowed protocols in links.
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def render_markdown(source):
    html = md.convert(source)

    cleaner = Cleaner(
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        filters=[partial(LinkifyFilter, callbacks=bleach.linkifier.DEFAULT_CALLBACKS)])

    return cleaner.clean(html)


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
                message_data = data["message"]
                message_data["name"] = bleach.clean(message_data["name"])
                message_data["content"] = render_markdown(message_data["content"])
                message = Message(**message_data)
                manager.messages.append(message)
                await manager.broadcast(data)
            elif data["type"] == "leave":
                await manager.disconnect(websocket, name)
                break
            elif data["type"] == "pong":
                manager.connection_status[name] = True
    except WebSocketDisconnect:
        await manager.disconnect(websocket, name)

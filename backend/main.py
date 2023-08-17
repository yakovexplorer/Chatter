from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class Message(BaseModel):
    name: str
    content: str

class Msgs(BaseModel):
    name: str

messages = []
active_users = []

@app.get("/messages")
async def get_messages():
    return messages

@app.post("/messages")
@limiter.limit("1/second")
async def create_message(request: Request, message: Message):
    messages.append(message.dict())
    return message

def validate_username(name: str):
    if name.lower() == "null" or name.lower() == "undefined":
        raise HTTPException(
            400,
            "The username passed is null, which is blacklisted!"
        )
    if len(name) < 1 or len(name) > 20:
        raise HTTPException(
            400,
            "The username must be between 1 and 20 characters long!"
        )
    if not all(c.isalnum() for c in name):
        raise HTTPException(
            400,
            "The username must only contain letters and numbers!"
        )

@app.post("/join/{name}")
@limiter.limit("1/second")
async def join(request: Request, name: str):
    validate_username(name)
    if name not in active_users:
        active_users.append(name)
    else:
        raise HTTPException(
            400,
            "The username passed is already in use!"
        )
    messages.append({"name": "System", "content": f"{name} has joined the chat."})
    return {}

@app.post("/leave/{name}")
@limiter.limit("1/second")
async def leave(request: Request, name: str):
    validate_username(name)
    if name in active_users:
        active_users.remove(name)
    messages.append({"name": "System", "content": f"{name} has left the chat."})
    return {}

@app.get("/active_users")
async def get_active_users():
    return active_users

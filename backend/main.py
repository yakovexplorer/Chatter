from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from fastapi_limiter import FastAPILimiter
# from fastapi_limiter.depends import RateLimiter

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

class Msgs(BaseModel):
    name: str

messages = []
active_users = []

# @app.on_event("startup")
# async def startup():
#    rediss = await redis.Redis(port=5500,host="127.0.0.1")
#    await FastAPILimiter.init(rediss)

@app.get("/messages")
async def get_messages():
    return messages

@app.post("/messages")
async def create_message(message: Message):
    messages.append(message.dict())
    return message

@app.post("/join/{name}")
async def join(name: str):
    if name.lower() == "null" or name.lower() == "undefined":
        raise HTTPException(
            400,
            "The username passed is null, which is blacklisted!"
        )
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
async def leave(name: str):
    if name.lower() == "null" or name.lower() == "undefined":
        raise HTTPException(
            400,
            "The username passed is null, which is blacklisted!"
        )
    if name in active_users:
        active_users.remove(name)
    messages.append({"name": "System", "content": f"{name} has left the chat."})
    return {}

@app.get("/active_users")
async def get_active_users():
    return active_users

import os
from features.encryption import AES256Encryptor
from uuid import uuid4
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
#from features.encryption import encrypt_message, decrypt_message
from ultrachatapp.database_client import DatabaseClient
from ultrachatapp.database_client import DatabaseClient
from ultrachatapp.database_client import users_collection # ✅ MongoDB client
from features.esa256 import encrypt_message, decrypt_message
import json
import uvicorn
from typing import List
from pathlib import Path
from fastapi import Query
from rapidfuzz import process, fuzz
from features.encryption import encrypt_message, decrypt_message
from features.esa256 import encrypt_message, decrypt_message    
from features.search_text import Search, fuzzy_search
from features.status_management import StatusManagement
from features.room_management import RoomManagement
from features.read_receipts import ReadReceipts
from features.authentication import Authentication
from features.chat_analytics import ChatAnalytics
from features.message_handling import WebSocketManager
from features.file_upload import S3Uploader
from features.notifications import Notification
from features.moderation import Moderation
from features.presence import Presence
from features.encryption import encrypt_message, decrypt_message
from features.session import Session
from features.reactions import Message as ChatMessage
from .models import MessageRequest, MessageResponse
from ultrachatapp.constants import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_REGION
from fastapi.middleware.cors import CORSMiddleware
from features.authentication import Authentication
auth_manager = Authentication()




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory stores
messages = {}
active_sessions = {}
user_presence = {}

# Services

read_receipts = ReadReceipts()
search_text = Search(messages)
room_management = RoomManagement()
auth_manager = Authentication()
chat_analytics = ChatAnalytics()
websocket_manager = WebSocketManager()
s3_uploader = S3Uploader(
    aws_access_key=AWS_ACCESS_KEY_ID,
    aws_secret_key=AWS_SECRET_ACCESS_KEY,
    bucket_name=AWS_S3_BUCKET_NAME,
    region=AWS_REGION
)
notify = Notification()
moderator = Moderation(["spam", "abuse", "hate"])

# Schemas
class ReadRequest(BaseModel):
    message_id: str
    user_id: str

class CheckReadRequest(BaseModel):
    message_id: str
    user_id: str

class MessageIDRequest(BaseModel):
    message_id: str

class MessageCreate(BaseModel):
    sender_id: str
    content: str

class ReactionAdd(BaseModel):
    message_id: str
    user_id: str
    reactions: list

class UserID(BaseModel):
    user_id: str

class UserCredentials(BaseModel):
    username: str
    password: str

class RoomRequest(BaseModel):
    room_name: str

class UserRequest(BaseModel):
    room_name: str
    user: str

class UserStatusRequest(BaseModel):
    user_id: str

class AES256Encryptor(BaseModel):
    key: bytes
    

# Routes
@app.post("/register")
async def register(user: UserCredentials):
    return auth_manager.register(user.username, user.password)

@app.post("/login")
async def login(user: UserCredentials):
    return auth_manager.login(user.username, user.password)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.send_message("Ayush", user_id, f"{user_id}: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)

@app.post("/send-message/", response_model=MessageResponse)
async def send_message(message: MessageRequest):
    if not message.sender_id or not message.receiver_id:
        raise HTTPException(status_code=400, detail="Sender ID and Receiver ID are required")
    
    if not moderator.is_message_allowed(message.message):
        raise HTTPException(status_code=403, detail="Message contains banned content.")

    if message.sender_id not in active_sessions:
        active_sessions[message.sender_id] = Session(message.sender_id, f"session_{message.sender_id}", datetime.utcnow())

    if message.receiver_id not in active_sessions:
        active_sessions[message.receiver_id] = Session(message.receiver_id, f"session_{message.receiver_id}", datetime.utcnow())

    sender_session = active_sessions[message.sender_id]
    receiver_session = active_sessions[message.receiver_id]

    encrypted = encrypt_message(message.message)
    message_id = str(uuid4())
    timestamp = datetime.utcnow().isoformat()

    data = {
        "sender_id": message.sender_id,
        "receiver_id": message.receiver_id,
        "sender_session_id": sender_session.session_id,
        "receiver_session_id": receiver_session.session_id,
        "timestamp": timestamp,
        "encryption": {
            "algorithm": "SHA256",
            "key_id": "key1",
            "encrypted_message": encrypted
        }
    }

    save_message_to_file(message_id, data)

    await websocket_manager.send_message(
        message.receiver_id,
        message.sender_id,
        f"{message.sender_id}: {message.message}"
    )

    return MessageResponse(
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        sender_session_id=sender_session.session_id,
        receiver_session_id=receiver_session.session_id,
        message=message.message,
        timestamp=timestamp,
        encryption=data["encryption"]
    )


@app.get("/messages")
def load_messages_from_file():
    try:
        with open("data.json", "r") as f:
            data = json.load(f)

            if isinstance(data, list):
                print("⚠️ Warning: data.json was a list, converting to dict")
                converted = {}
                for idx, item in enumerate(data):
                    msg_id = f"msg_{idx+1}"  # Example: msg_1, msg_2, etc.
                    converted[msg_id] = item
                return converted

            elif isinstance(data, dict):
                return data

            else:
                print("⚠️ Unknown format, returning empty dict")
                return {}

    except Exception as e:
        print(f"⚠️ Failed to load data: {e}")
        return {}

@app.post("/create-message")
def create_message(data: MessageCreate):
    msg = ChatMessage(sender_id=data.sender_id, content=data.content)
    messages[msg.message_id] = msg
    return {"message_id": msg.message_id}

@app.post("/reaction")
def add_reaction(react: ReactionAdd):
    message = messages.get(react.message_id)
    if not message:
        print("⚠️ Message ID not found:", react.message_id)
        raise HTTPException(status_code=404, detail="Message not found")

    message.add_reaction(react.user_id, react.reactions)
    return {
        "message": "Reaction added/updated",
        "data": message.to_dict()
    }



@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_url = s3_uploader.upload_file_object(file.file, file.filename, file.content_type)
    return {"message": "Uploaded", "url": file_url} if file_url else {"message": "Failed"}

@app.post("/mark-as-read")
def mark_as_read(data: ReadRequest):
    read_receipts.mark_as_read(data.message_id, data.user_id)
    return {"status": "marked as read"}

@app.post("/has-been-read")
def has_been_read(data: CheckReadRequest):
    result = read_receipts.has_been_read_by(data.message_id, data.user_id)
    return {"has_been_read": result}

@app.post("/get-read-by")
def get_read_by_users(data: MessageIDRequest):
    return {"read_by_users": read_receipts.get_read_by_users(data.message_id)}

@app.post("/set_online/")
def set_user_online(request: UserStatusRequest):
    user = user_presence.get(request.user_id, Presence(request.user_id))
    user.set_online()
    user_presence[request.user_id] = user
    return {"message": "User is now online."}

@app.post("/set_offline/")
def set_user_offline(request: UserStatusRequest):
    user = user_presence.get(request.user_id, Presence(request.user_id))
    user.set_offline(datetime.utcnow())
    user_presence[request.user_id] = user
    return {"message": "User is now offline."}

@app.get("/status/{user_id}")
def get_user_status(user_id: str):
    user = user_presence.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user.get_status()

@app.post("/rooms/")
def create_room(req: RoomRequest):
    room_management.create_room(req.room_name)
    return {"message": f"Room '{req.room_name}' created."}

@app.delete("/rooms/{room_name}")
def delete_room(room_name: str):
    room_management.delete_room(room_name)
    return {"message": f"Room '{room_name}' deleted."}

@app.post("/rooms/add-user")
def add_user(req: UserRequest):
    room_management.add_user_to_room(req.room_name, req.user)
    return {"message": f"User '{req.user}' added to room '{req.room_name}'."}

@app.post("/rooms/remove-user")
def remove_user(req: UserRequest):
    room_management.remove_user_from_room(req.room_name, req.user)
    return {"message": f"User '{req.user}' removed from room '{req.room_name}'."}

@app.get("/rooms/", response_model=List[str])
def list_rooms():
    return room_management.list_rooms()

@app.get("/rooms/{room_name}/users", response_model=List[str])
def list_users(room_name: str):
    return room_management.list_users_in_room(room_name)

@app.get("/search/keyword")
def search_keyword(keyword: str = Query(..., min_length=1)):
    dummy_data = [
        "apple juice", "banana smoothie", "chocolate cake", 
        "vanilla ice cream", "grape soda", "mango lassi", "orange juice"
    ]
    return {"results": fuzzy_search(keyword, dummy_data)}



# Root JSON file
DATA_FILE = Path("data.json")

def load_messages_from_file():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as file:
            try:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
                elif isinstance(data, list):
                    print("⚠️ Warning: data.json was a list, converting to dict format")
                    converted = {}
                    for idx, item in enumerate(data):
                        message_id = f"msg_{idx+1}"
                        converted[message_id] = item
                    with open(DATA_FILE, "w") as fixfile:
                        json.dump(converted, fixfile, indent=4)
                    return converted
                else:
                    print("⚠️ Unknown format, resetting to empty dict")
                    return {}
            except json.JSONDecodeError as e:
                print("⚠️ JSON decode error:", e)
                return {}
    return {}



def save_message_to_file(message_id: str, message_data: dict):
    all_messages = load_messages_from_file()
    
    # Make sure it's always a dict
    if not isinstance(all_messages, dict):
        print("⚠️ Overwriting invalid message store")
        all_messages = {}

    all_messages[message_id] = message_data

    with open(DATA_FILE, "w") as file:
        json.dump(all_messages, file, indent=4)




# Entry point
def main():
    import uvicorn
    uvicorn.run("ultrachatapp.main:app", host="0.0.0.0", port=8000, reload=True)





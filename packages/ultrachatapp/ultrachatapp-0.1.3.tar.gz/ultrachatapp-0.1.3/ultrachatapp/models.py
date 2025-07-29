

from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    sender_id: str
    receiver_id: str
    message: str


# Response model for the message data
# Response model for the message data
class MessageResponse(BaseModel):
    # message_id: str
    sender_id: str
    receiver_id: str
    message: str
    timestamp: str
    encryption: Optional[dict] = None


# MessageRequest model for incoming message data


class MessageRequest(BaseModel):
    sender_id: str  # ID of the sender
    receiver_id: str  # ID of the receiver
    message: str  # The actual message
    # Optional timestamp of when the message was sent
    timestamp: Optional[str] = None
    # Optional encryption information (e.g., algorithm, key_id, encrypted_message)
    encryption: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "sender_id": "user1",
                "receiver_id": "user2",
                "message": "Hello, how are you?",
                "timestamp": "2025-04-01T12:00:00",
                "encryption": {
                    "algorithm": "AES-256",
                    "key_id": "key1",
                    "encrypted_message": "U2FsdGVkX1+abcd1234..."
                }
            }
        }

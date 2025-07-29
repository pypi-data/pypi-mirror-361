# features/reactions.py

import uuid
from typing import List, Dict


# Message reactions (like, love, etc.)
class Reaction:
    def __init__(self, user_id: str, reactions: List[str]):
        self.user_id = user_id
        self.reactions = reactions

    def __repr__(self):
        return f"Reaction(user_id={self.user_id}, reactions={self.reactions})"

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "reactions": self.reactions
        }


# Class to represent a message with sender, content, and reactions (with unique message_id)
class Message:
    def __init__(self, sender_id: str, content: str):
        self.message_id = str(uuid.uuid4())
        self.sender_id = sender_id
        self.content = content
        self.reactions = []  # ✅ Corrected

    def add_reaction(self, user_id: str, reactions: List[str]):
        self.reactions = [r for r in self.reactions if r.user_id != user_id]
        self.reactions.append(Reaction(user_id, reactions))


    def __repr__(self):
        return (
            f"Message(message_id={self.message_id}, sender_id={self.sender_id}, "
            f"content='{self.content}', reactions={self.reactions})"
        )

    def to_dict(self) -> Dict:
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "reactions": [r.to_dict() for r in self.reactions]
        }

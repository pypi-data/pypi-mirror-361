# features/authentication.py
from fastapi import HTTPException
from uuid import uuid4
from ultrachatapp.database_client import users_collection

class Authentication:
    def register(self, username: str, password: str):
        if users_collection.find_one({"username": username}):
            raise HTTPException(status_code=400, detail="Username already exists")
        users_collection.insert_one({
            "username": username,
            "password": password  # In real app, use hashed password
        })
        return {"message": "User registered successfully"}

    def login(self, username: str, password: str):
        user = users_collection.find_one({"username": username})
        if not user or user["password"] != password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        session_id = str(uuid4())
        return {"session_id": session_id, "username": username}

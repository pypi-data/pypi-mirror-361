# ultrachatapp/config.py
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# .env file को load करो
load_dotenv()

# Environment से values लाओ
FERNET_KEY = os.getenv("FERNET_KEY")  # Must be 32-byte base64 string
SECRET_KEY = os.getenv("SECRET_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/whatsapp_clone")

# Fernet encryptor initialize करो
fernet = Fernet(FERNET_KEY.encode())

# Config class बनाओ
class Config:
    MONGO_URI = MONGO_URI
    SECRET_KEY = SECRET_KEY

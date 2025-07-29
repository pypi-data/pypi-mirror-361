import os
from cryptography.fernet import Fernet
from cryptography.fernet import Fernet

# Function to generate and save the key if it doesn't exist
def generate_key():
    return Fernet.generate_key()

def save_key(key: bytes):
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    # Check if the key file exists
    if not os.path.exists("secret.key"):
        print("Key file not found. Generating and saving a new key.")
        key = generate_key()  # Generate a new key
        save_key(key)  # Save the new key to the file
    else:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    return key

# Load the key
key = load_key()

cipher = Fernet(key)

def encrypt_message(message: str) -> str:
    return cipher.encrypt(message.encode()).decode()
  
def decrypt_message(token: str) -> str:
    return cipher.decrypt(token.encode()).decode()

   

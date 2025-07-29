# features/encryption.py
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


class AES256Encryptor:
    """
    A class to perform AES-256 encryption and decryption using CBC mode.
    """

    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256.")
        self.key = key

    def encrypt(self, plaintext: str) -> str:
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + ciphertext).decode()
       
        decrypted = encryptor.decrypt(encrypted)
        print("Decrypted:", decrypted)
    def decrypt(self, b64_ciphertext: str) -> str:
        data = base64.b64decode(b64_ciphertext)
        iv = data[:16]
        ciphertext = data[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext.decode()


# ------------------- Fernet key loading & encryption -------------------

FERNET_KEY_PATH = "secret.key"

def generate_key():
    return Fernet.generate_key()

def save_key(key: bytes):
    with open(FERNET_KEY_PATH, "wb") as key_file:
        key_file.write(key)

def load_key():
    if not os.path.exists(FERNET_KEY_PATH):
        print("Key file not found. Generating and saving a new key.")
        key = generate_key()
        save_key(key)
    else:
        with open(FERNET_KEY_PATH, "rb") as key_file:
            key = key_file.read()
    return key

# Load or create the Fernet cipher
cipher = Fernet(load_key())

def encrypt_message(message: str) -> str:
    return cipher.encrypt(message.encode()).decode()

def decrypt_message(token: str) -> str:
    return cipher.decrypt(token.encode()).decode()


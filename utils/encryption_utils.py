from cryptography.fernet import Fernet
import os

# Always load the same key from secret.key
def load_key():
    key_path = "secret.key"
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
    with open(key_path, "rb") as key_file:
        return key_file.read()

fernet = Fernet(load_key())

def encrypt(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt(token):
    return fernet.decrypt(token.encode()).decode()

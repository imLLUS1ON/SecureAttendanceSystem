from cryptography.fernet import Fernet
import os

# Always load the same key from secret.key
def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()

fernet = Fernet(load_key())

def encrypt(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt(token):
    return fernet.decrypt(token.encode()).decode()

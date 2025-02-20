# key_generator.py
import os
import base64

def generate_key(length=16):
    """Generate a random key of specified length."""
    return os.urandom(length)

def encode_key(key):
    """Encode key in Base64 for safe storage and transmission."""
    return base64.b64encode(key).decode()

def decode_key(encoded_key):
    """Decode a Base64-encoded key."""
    return base64.b64decode(encoded_key)

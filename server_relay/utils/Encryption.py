from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

def encrypt_data(data, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # PKCS7 padding logic
    pad_length = 16 - (len(data) % 16)
    pad_length = pad_length if pad_length != 0 else 16  # Ensure 1-16 bytes
    padded_data = data + bytes([pad_length] * pad_length)
    
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data  # IV (16B) + ciphertext

def decrypt_data(encrypted_data, key):
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove PKCS7 padding
    pad_length = decrypted_padded[-1]
    decrypted_data = decrypted_padded[:-pad_length]
    
    return decrypted_data

# Example usage
key = os.urandom(32)  # 256-bit key for AES-256
data = b"Hello, World!"

encrypted = encrypt_data(data, key)
print("Encrypted:", encrypted)

decrypted = decrypt_data(encrypted, key)
print("Decrypted:", decrypted.decode())


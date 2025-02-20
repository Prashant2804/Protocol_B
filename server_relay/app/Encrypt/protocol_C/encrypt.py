
# encryption.py
def xor_encrypt(data: bytes, key: bytes) -> bytes:
    """XOR-based encryption."""
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])


def shift_encrypt(data: bytes, shift: int = 3) -> bytes:
    """Shift-based encryption (Caesar cipher-like)."""
    return bytes([(b + shift) % 256 for b in data])


def shift_decrypt(data: bytes, shift: int = 3) -> bytes:
    """Shift-based decryption."""
    return bytes([(b - shift) % 256 for b in data])

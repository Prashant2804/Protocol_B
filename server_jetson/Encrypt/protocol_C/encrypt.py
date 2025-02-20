
# encryption.py
def xor_encrypt(data, key):
    """XOR-based encryption."""
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])


def shift_encrypt(data, shift):
    """Shift-based encryption (Caesar cipher-like)."""
    return bytes([(b + shift) % 256 for b in data])


def shift_decrypt(data, shift):
    """Shift-based decryption."""
    return bytes([(b - shift) % 256 for b in data])

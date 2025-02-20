
# integrity.py
import hashlib


def generate_hash(data: bytes) -> str:
    """Generate a SHA-256 hash of the data for integrity checking."""
    return hashlib.sha256(data).hexdigest()


def verify_hash(data: bytes, expected_hash: str) -> bool:
    """Verify data integrity by comparing hashes."""
    return generate_hash(data) == expected_hash

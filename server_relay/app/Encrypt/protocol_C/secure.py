from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import os


def generate_dh_parameters():
    return dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())


def generate_dh_key_pair(parameters):
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def deserialize_public_key(peer_bytes):
    return serialization.load_pem_public_key(peer_bytes, backend=default_backend())


def derive_shared_key(private_key, peer_public_key, length=32):
    shared_secret = private_key.exchange(peer_public_key)
    return HKDF(
        algorithm=hashes.SHA256(), length=length,
        salt=None, info=b'handshake data', backend=default_backend()
    ).derive(shared_secret)


def aes_encrypt(plaintext, key):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext


def aes_decrypt(ciphertext, key):
    aesgcm = AESGCM(key)
    nonce = ciphertext[:12]
    ct = ciphertext[12:]
    return aesgcm.decrypt(nonce, ct, None)


def perform_key_exchange(sock, is_client=False):
    params = generate_dh_parameters()
    priv, pub = generate_dh_key_pair(params)
    pub_bytes = serialize_public_key(pub)
    if is_client:
        sock.send(pub_bytes)
        peer_bytes = sock.recv(4096)
    else:
        peer_bytes = sock.recv(4096)
        sock.send(pub_bytes)
    peer_pub = deserialize_public_key(peer_bytes)
    return derive_shared_key(priv, peer_pub)

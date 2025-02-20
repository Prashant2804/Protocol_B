# main.py (Example Usage)
if __name__ == "__main__":
    from gen import generate_key, encode_key, decode_key
    from encrypt import xor_encrypt, shift_encrypt, shift_decrypt
    from integrity import generate_hash, verify_hash

    # Generate and encode a key
    key = generate_key()
    encoded_key = encode_key(key)
    print("Encoded Key:", encoded_key)

    # Encrypt data
    message = b"Hello, Secure World!"
    encrypted_xor = xor_encrypt(message, key)
    encrypted_shift = shift_encrypt(encrypted_xor)

    # Generate hash
    data_hash = generate_hash(encrypted_shift)
    print("Data Hash:", data_hash)

    # Decrypt data
    decrypted_shift = shift_decrypt(encrypted_shift)
    decrypted_xor = xor_encrypt(decrypted_shift, key)  # XOR reverses itself

    # Verify integrity
    if verify_hash(encrypted_shift, data_hash):
        print("Integrity Verified!")
    else:
        print("Data Tampered!")

    print("Decrypted Message:", decrypted_xor.decode())

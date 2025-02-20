import cv2
import numpy as np
from byte_convertor import int_to_bytes 
from config import SERVER_IP, SERVER_PORT, CHUNK_SIZE, ENCRYPTION_KEY
from camera import initialize_camera
from compression import compress_frame, decompress_frame
from Encrypt.protocol_C.gen import generate_key, encode_key, decode_key
from Encrypt.protocol_C.encrypt import xor_encrypt, shift_encrypt, shift_decrypt
from Encrypt.protocol_C.integrity import generate_hash, verify_hash

from network import initialize_socket
import socket

def main():
    cap = None
    client_socket = None
    
    try:
        # Initialize camera
        cap = initialize_camera()
        
        # Network connection with retry
        while True:
            try:
                client_socket = initialize_socket(SERVER_IP, SERVER_PORT)
                print("Connected to server")
                break
            except socket.error as e:  # Handle connection errors
                if e.args and e.args[0] == 111:  # 111 = ECONNREFUSED
                    print("Connection refused. Retrying in 5 seconds...")
                else:
                    print("Socket error: %s" % str(e))  # Corrected string formatting
                cv2.waitKey(5000)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Preprocess frame
            frame = cv2.resize(frame, (320, 240))

            # Compression and Encryption
	    key = generate_key()
            encoded_key = encode_key(key)
            compressed_data = compress_frame(frame)
	    byte_representation = int_to_bytes(compressed_data)

		
	    #chunking + convesion to bytes
            encrypted_xor = xor_encrypt(byte_representation, key)
            encrypted_shift = shift_encrypt(encrypted_xor)

            # Generate hash
            data_hash = generate_hash(encrypted_shift)
            print("Data Hash:", data_hash)

            encrypted_data= data_hash
            # Send data with size header
            try:
                # Send frame size
                client_socket.sendall(struct.pack("!I", len(encrypted_data)))
                # Send encrypted data in chunks
                bytes_sent = 0
                while bytes_sent < len(encrypted_data):
                    chunk = encrypted_data[bytes_sent:bytes_sent+CHUNK_SIZE]
                    client_socket.sendall(chunk)
                    bytes_sent += len(chunk)
            except socket.error as e:  # Handle broken pipe or other socket errors
                if e.args and e.args[0] == 32:  # 32 = EPIPE (Broken Pipe)
                    print("Connection lost. Reconnecting...")
                    client_socket = initialize_socket(SERVER_IP, SERVER_PORT)
                    continue
                else:
                    raise  # Re-raise unexpected errors

            # Receive processed frame
            try:
                # Get response size
                size_header = client_socket.recv(4)
                if not size_header:
                    raise socket.error("No header received")
                response_size = struct.unpack("!I", size_header)[0]
                
                # Receive response data
                received_data = b''
                while len(received_data) < response_size:
                    chunk = client_socket.recv(min(CHUNK_SIZE, response_size - len(received_data)))
                    if not chunk:
                        raise socket.error("Incomplete data received")
                    received_data += chunk

                # Decryption and Decompression
                decrypted_response = decrypt_data(received_data, ENCRYPTION_KEY)
                processed_frame = decompress_frame(decrypted_response)

                # Display result
                if processed_frame is not None:
                    cv2.imshow("Processed Feed", processed_frame)

            except socket.error as e:  # Handle network errors
                print("Network error: %s" % str(e))  # Corrected string formatting
                client_socket.close()
                client_socket = initialize_socket(SERVER_IP, SERVER_PORT)
                continue

            # Exit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if cap and cap.isOpened():
            cap.release()
        if client_socket:
            client_socket.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

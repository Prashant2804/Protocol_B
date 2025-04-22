import socket
import struct
import os
import sys
# Ensure server_relay config is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import STREAM_CREDENTIALS
from .Encrypt.protocol_C.secure import perform_key_exchange, aes_encrypt, aes_decrypt
from utils.compression import Compressor
from utils.fragmentation import Fragmenter

class SocketHandler:
    def __init__(self, server_ip, server_port, buffer_size):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = buffer_size
        # Shared key will be established after client connects
        self.shared_key = None
        self.server_socket = None
        self.client_socket = None
        self.client_address = None

    def start_server(self):
        """
        Start the TCP server.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(1)
        print(f"Server started at {self.server_ip}:{self.server_port}")

    def wait_for_client(self):
        """
        Wait for a client connection.
        """
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"Client connected from {self.client_address}")
        # Authenticate client via stream_id and password
        creds_line = b''
        while b'\n' not in creds_line:
            chunk = self.client_socket.recv(1)
            if not chunk:
                raise RuntimeError("Connection closed during authentication")
            creds_line += chunk
        try:
            stream_id, password = creds_line.strip().decode().split(':', 1)
        except Exception:
            self.client_socket.send(b'ER')
            self.client_socket.close()
            raise RuntimeError("Invalid authentication format")
        if STREAM_CREDENTIALS.get(stream_id) != password:
            self.client_socket.send(b'ER')
            self.client_socket.close()
            raise RuntimeError("Invalid credentials")
        # Send acknowledgement
        self.client_socket.send(b'OK')
        # Perform Diffie-Hellman key exchange to derive shared AES key
        self.shared_key = perform_key_exchange(self.client_socket, is_client=False)

    def receive_frame(self):
        """
        Receive and process a frame.
        """
        # Receive frame size
        size_header = self.client_socket.recv(4)
        if not size_header:
            return None
        frame_size = struct.unpack("!I", size_header)[0]

        # Receive the full frame data
        received_data = b''
        while len(received_data) < frame_size:
            chunk = self.client_socket.recv(min(self.buffer_size, frame_size - len(received_data)))
            if not chunk:
                break
            received_data += chunk

        # Decrypt and decompress the data
        plaintext = aes_decrypt(received_data, self.shared_key)
        return Compressor.decompress(plaintext)

    def send_frame(self, data):
        """
        Encrypt, compress, and send a frame.
        """
        # Compress and encrypt the data
        compressed = Compressor.compress(data)
        encrypted_data = aes_encrypt(compressed, self.shared_key)
        frame_size = struct.pack("!I", len(encrypted_data))

        # Send the frame size first
        self.client_socket.sendall(frame_size)
        # Send the actual frame data
        self.client_socket.sendall(encrypted_data)

    def close_connection(self):
        """
        Close the client socket.
        """
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        print("Client connection closed.")

    def stop_server(self):
        """
        Stop the server.
        """
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        print("Server stopped.")

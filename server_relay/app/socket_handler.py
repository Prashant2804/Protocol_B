import socket
import struct
from .Encrypt.protocol_C.gen import generate_key, encode_key, decode_key
from .Encrypt.protocol_C.encrypt import xor_encrypt, shift_encrypt, shift_decrypt
from .Encrypt.protocol_C.integrity import generate_hash, verify_hash
from utils.compression import Compressor
from utils.fragmentation import Fragmenter

class SocketHandler:
    def __init__(self, server_ip, server_port, buffer_size,aaa):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = buffer_size
        number = 12
        byte_representation = number.to_bytes((number.bit_length() + 7) // 8, byteorder='big')
        key = generate_key()
        encoded_key = encode_key(key)
        encrypted_xor = xor_encrypt(byte_representation, key)
        encrypted_shift = shift_encrypt(encrypted_xor)

        # Generate hash
        data_hash = generate_hash(encrypted_shift)
        print("Data Hash:", data_hash)

        self.encryptor = data_hash
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
        data = self.encryptor.decrypt_data(received_data, encryption_key)
        return Compressor.decompress(data)

    def send_frame(self, data):
        """
        Encrypt, compress, and send a frame.
        """
        compressed_data = Compressor.compress(data)
        key = generate_key()
        encoded_key = encode_key(key)
        encrypted_xor = xor_encrypt(compressed_data, key)
        encrypted_shift = shift_encrypt(encrypted_xor)

        # Generate hash
        data_hash = generate_hash(encrypted_shift)
        print("Data Hash:", data_hash)

        encrypted_data = data_hash
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

import socket


def initialize_socket(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    return client_socket


def send_data_in_chunks(socket, data, chunk_size):
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    for chunk in chunks:
        socket.sendall(chunk)
    socket.sendall(b"EOF")  # End-of-file signal

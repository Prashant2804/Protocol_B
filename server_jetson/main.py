import cv2
import argparse
from config import SERVER_IP, SERVER_PORT, CHUNK_SIZE
from camera import initialize_camera
from compression import compress_frame
from Encrypt.protocol_C.secure import perform_key_exchange, aes_encrypt
from utils.network import initialize_socket, send_data_in_chunks
from forks import ForkManager


def main():
    parser = argparse.ArgumentParser(description='Drone Video Stream Client')
    # Authentication and broker
    parser.add_argument('--stream-id', required=True, help='Stream number')
    parser.add_argument('--password', required=True, help='Stream password')
    parser.add_argument('--broker', action='store_true', help='Enable sending to broker server')
    # Broker connection
    parser.add_argument('--server-ip', default=SERVER_IP)
    parser.add_argument('--server-port', type=int, default=SERVER_PORT)
    parser.add_argument('--chunk-size', type=int, default=CHUNK_SIZE)
    # Fork options
    parser.add_argument('--store', action='store_true', help='Enable onboard storage')
    parser.add_argument('--display', action='store_true', help='Enable local display')
    parser.add_argument('--analyze', action='store_true', help='Enable onboard analysis')
    parser.add_argument('--relay-host', help='Direct SRT relay host')
    parser.add_argument('--relay-port', type=int, help='Direct SRT relay port')
    parser.add_argument('--peer', action='append', help='Direct SRT peer URIs')
    args = parser.parse_args()

    # Initialize camera with retry in case of open failures
    cap = None
    while True:
        try:
            cap = initialize_camera()
            print("Camera opened successfully.")
            break
        except Exception as e:
            print("Camera open error:", e)
            print("Retrying camera open in 5 seconds...")
            cv2.waitKey(5000)

    # Initialize broker socket if needed
    client_socket = None
    if args.broker:
        client_socket = initialize_socket(args.server_ip, args.server_port)
        # Authenticate
        creds = f"{args.stream_id}:{args.password}\n".encode()
        client_socket.sendall(creds)
        resp = client_socket.recv(2)
        if resp != b'OK':
            raise RuntimeError('Authentication failed')
        # Key exchange
        shared_key = perform_key_exchange(client_socket, is_client=True)

    # Instantiate forks
    forks = ForkManager(
        store=args.store,
        display=args.display,
        analyze=args.analyze,
        relay=bool(args.relay_host and args.relay_port),
        relay_host=args.relay_host,
        relay_port=args.relay_port,
        peers=args.peer
    )
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Process forks
            forks.process(frame)
            # Send to broker
            if args.broker:
                compressed = compress_frame(frame)
                encrypted = aes_encrypt(compressed, shared_key)
                send_data_in_chunks(client_socket, encrypted, args.chunk_size)
    except KeyboardInterrupt:
        pass
    finally:
        forks.close()
        cap.release()
        if args.display:
            cv2.destroyAllWindows()
        if args.broker and client_socket:
            client_socket.close()


if __name__ == '__main__':
    main()

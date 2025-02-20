# app/server.py

from config import (
    SERVER_IP, SERVER_PORT, BUFFER_SIZE, FLAME_MODEL_PATH, SMOKE_MODEL_PATH
)
from app.frame_processor import FrameProcessor
from app.socket_handler import SocketHandler


def main():
    encryption_key =  b'ThisIsAValid32ByteKeyForAES256!!'  # Replace with a secure key
    frame_processor = FrameProcessor(FLAME_MODEL_PATH, SMOKE_MODEL_PATH)
    socket_handler = SocketHandler(
        SERVER_IP, SERVER_PORT, BUFFER_SIZE, encryption_key)

    try:
        socket_handler.start_server()
        socket_handler.wait_for_client()

        while True:
            # Receive frame
            frame = socket_handler.receive_frame()
            if frame is None:
                print("No frame received. Closing connection.")
                break

            # Process frame
            processed_frame = frame_processor.detect_and_draw(frame)

            # Send processed frame
            socket_handler.send_frame(processed_frame)

    except KeyboardInterrupt:
        print("\nServer shutting down...")

    finally:
        socket_handler.close_connection()
        print("Resources released. Server stopped.")


if __name__ == "__main__":
    main()

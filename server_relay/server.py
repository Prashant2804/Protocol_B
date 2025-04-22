# app/server.py

from config import (
    SERVER_IP, SERVER_PORT, BUFFER_SIZE, FLAME_MODEL_PATH, SMOKE_MODEL_PATH, HTTP_HOST, HTTP_PORT
)
import threading
from app.frame_processor import FrameProcessor
from app.socket_handler import SocketHandler
from app.web_stream import run as run_web, set_frame


def main():
    # Launch web portal for MJPEG streaming
    web_thread = threading.Thread(target=run_web, kwargs={'host': HTTP_HOST, 'port': HTTP_PORT}, daemon=True)
    web_thread.start()
    # Initialize frame processor and socket handler
    frame_processor = FrameProcessor(FLAME_MODEL_PATH, SMOKE_MODEL_PATH)
    socket_handler = SocketHandler(SERVER_IP, SERVER_PORT, BUFFER_SIZE)

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
            # Update web stream frame
            set_frame(processed_frame)

            # Send processed frame
            socket_handler.send_frame(processed_frame)

    except KeyboardInterrupt:
        print("\nServer shutting down...")

    finally:
        socket_handler.close_connection()
        print("Resources released. Server stopped.")


if __name__ == "__main__":
    main()

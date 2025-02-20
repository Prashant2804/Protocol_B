import cv2
from config import SERVER_IP, SERVER_PORT, CHUNK_SIZE, ENCRYPTION_KEY
from camera import initialize_camera
from compression import compress_frame, decompress_frame
from encryption import encrypt_data, decrypt_data
from fragmentation import fragment_data, reassemble_data
from utils.network import initialize_socket, send_data_in_chunks


def main():
    try:
        # Initialize camera and socket
        cap = initialize_camera()
        client_socket = initialize_socket(SERVER_IP, SERVER_PORT)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            # Resize frame
            frame = cv2.resize(frame, (320, 240))

            # Compress, encrypt, and fragment the frame
            compressed_data = compress_frame(frame)
            encrypted_data = encrypt_data(compressed_data, ENCRYPTION_KEY)
            send_data_in_chunks(client_socket, encrypted_data, CHUNK_SIZE)

            # Receive and process the server's response
            response_chunks = []
            while True:
                chunk = client_socket.recv(CHUNK_SIZE)
                if chunk == b"EOF":
                    break
                response_chunks.append(chunk)

            # Reassemble, decrypt, and decompress the server's response
            encrypted_response = reassemble_data(response_chunks)
            decrypted_response = decrypt_data(
                encrypted_response, ENCRYPTION_KEY)
            processed_frame = decompress_frame(decrypted_response)

            # Display the processed frame
            if processed_frame is not None:
                cv2.imshow("Processed Frame", processed_frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        client_socket.close()


if __name__ == "__main__":
    main()

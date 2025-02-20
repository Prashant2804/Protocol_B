# server.py
from flask import Flask, Response
from socket_handler import SocketHandler
from queue import Queue
import threading

app = Flask(__name__)
frame_queue = Queue()

# Initialize SocketHandler with your encryption key and server details
KEY = b'your-encryption-key'  # Must match the relay client's key
SERVER_IP = '0.0.0.0'
SERVER_PORT = 5001
BUFFER_SIZE = 4096

def tcp_server():
    server = SocketHandler(SERVER_IP, SERVER_PORT, BUFFER_SIZE, KEY)
    server.start_server()
    server.wait_for_client()
    
    while True:
        frame = server.receive_frame()  # Get decrypted/decompressed frame
        frame_queue.put(frame)

# Start TCP server in a background thread
threading.Thread(target=tcp_server, daemon=True).start()

@app.route('/stream')
def video_stream():
    def generate():
        while True:
            frame = frame_queue.get()
            yield (b'--frame\r\n'
                   b'Content-Type: video/mp4\r\n\r\n' + frame + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return open('app.html').read()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
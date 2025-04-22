SERVER_IP = '0.0.0.0'
SERVER_PORT = 8000
BUFFER_SIZE = 65535  # TCP buffer size
FLAME_MODEL_PATH = "Weights/best (1).onnx"  # Use ONNX model to avoid PT deserialization errors
SMOKE_MODEL_PATH = "Weights/smoke1.pt"

HTTP_HOST = '0.0.0.0'
HTTP_PORT = 5000

STREAM_CREDENTIALS = {
    '1': 'password1',  # stream_id: password mapping
}

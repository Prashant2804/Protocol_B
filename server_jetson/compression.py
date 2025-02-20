import cv2
import zlib


def compress_frame(frame):
    _, buffer = cv2.imencode(
        '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    compressed_data = zlib.compress(buffer.tobytes())
    return compressed_data


def decompress_frame(compressed_data):
    decompressed_data = zlib.decompress(compressed_data)
    frame = cv2.imdecode(np.frombuffer(
        decompressed_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    return frame

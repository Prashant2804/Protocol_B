import cv2
import zlib
import numpy as np


def compress_frame(frame):
    _, buffer = cv2.imencode(
        '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    compressed_data = zlib.compress(buffer.tobytes())
    return compressed_data


def decompress_frame(compressed_data):
    decompressed_data = zlib.decompress(compressed_data)
    arr = np.frombuffer(decompressed_data, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return frame

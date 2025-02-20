# app/utils/compression.py

import gzip
import io


class Compressor:
    @staticmethod
    def compress(data: bytes) -> bytes:
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb") as f:
            f.write(data)
        return buffer.getvalue()

    @staticmethod
    def decompress(data: bytes) -> bytes:
        buffer = io.BytesIO(data)
        with gzip.GzipFile(fileobj=buffer, mode="rb") as f:
            return f.read()

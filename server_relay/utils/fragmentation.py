# app/utils/fragmentation.py

class Fragmenter:
    @staticmethod
    def fragment(data: bytes, chunk_size: int) -> list:
        """
        Splits data into chunks of specified size.
        """
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    @staticmethod
    def defragment(chunks: list) -> bytes:
        """
        Reassembles data from chunks.
        """
        return b"".join(chunks)

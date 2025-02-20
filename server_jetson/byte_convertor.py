import struct

def int_to_bytes(compressed_data):
    """
    Convert an integer to its byte representation using struct packing.
    Supports variable-length packing for Python 2.7 compatibility.

    :param compressed_data: Integer to be converted to bytes
    :return: Byte representation of the integer
    """
    # Ensure compressed_data is an integer
    compressed_data = int(compressed_data)

    # Calculate required bytes dynamically
    num_bytes = (compressed_data.bit_length() + 7) // 8 or 1  # Ensure at least 1 byte

    # Pack using struct (handling different byte sizes)
    if num_bytes == 1:
        return struct.pack('!B', compressed_data)  # Unsigned 1-byte integer
    elif num_bytes == 2:
        return struct.pack('!H', compressed_data)  # Unsigned 2-byte integer
    elif num_bytes <= 4:
        return struct.pack('!I', compressed_data)  # Unsigned 4-byte integer
    elif num_bytes <= 8:
        return struct.pack('!Q', compressed_data)  # Unsigned 8-byte integer
    else:
        # For larger numbers, manually convert to bytes
        byte_representation = b""
        while compressed_data:
            byte_representation = struct.pack('!B', compressed_data & 0xFF) + byte_representation
            compressed_data >>= 8  # Shift 8 bits to the right
        return byte_representation


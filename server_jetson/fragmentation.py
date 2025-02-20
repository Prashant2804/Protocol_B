def fragment_data(data, chunk_size):
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    return chunks


def reassemble_data(chunks):
    return b''.join(chunks)

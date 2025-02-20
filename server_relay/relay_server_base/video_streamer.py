def video_stream_generator(video_path):
    """Generates video data in chunks."""
    with open(video_path, 'rb') as video_file:
        while chunk := video_file.read(1024 * 1024):  # Read 1 MB chunks
            yield chunk

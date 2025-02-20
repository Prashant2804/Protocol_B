import os


class Config:
    VIDEO_FILE_PATH = os.getenv("VIDEO_FILE_PATH", "/path/to/video.mp4")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

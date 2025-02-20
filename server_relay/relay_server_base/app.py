from flask import Flask, Response
from video_streamer.py import video_stream_generator
from config import Config

app = Flask(__name__)


@app.route('/stream', methods=['GET'])
def stream_video():
    """Stream video file to the client."""
    return Response(
        video_stream_generator(Config.VIDEO_FILE_PATH),
        content_type='video/mp4'
    )


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT)

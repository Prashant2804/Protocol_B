import os
import cv2
import subprocess
from datetime import datetime

class ForkManager:
    def __init__(self, store=False, display=False, analyze=False,
                 relay=False, relay_host=None, relay_port=None,
                 peers=None, width=640, height=480, fps=30):
        self.store = store
        self.display = display
        self.analyze = analyze
        self.relay = relay
        self.relay_host = relay_host
        self.relay_port = relay_port
        self.peers = peers or []
        self.width = width
        self.height = height
        self.fps = fps

        # Initialize storage
        if self.store:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"drone_record_{timestamp}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.writer = cv2.VideoWriter(fname, fourcc, fps, (width, height))
        # Initialize display
        if self.display:
            cv2.namedWindow('Local Display', cv2.WINDOW_AUTOSIZE)
        # Initialize analysis
        if self.analyze:
            from analysis import analyze_frame
            self.analyze_frame = analyze_frame
        # Initialize relay GStreamer pipeline
        if self.relay:
            # Use gst-launch-1.0 to send SRT stream
            pipeline = (
                f"appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=5000 "
                f"speed-preset=superfast ! mpegtsmux ! srtsink uri=srt://{self.relay_host}:{self.relay_port}?mode=caller"
            )
            self.relay_proc = subprocess.Popen([
                'gst-launch-1.0', '-v', 'appsrc', 'format=3', 'is-live=true',
                f'caps=video/x-raw,format=BGR,width={width},height={height},framerate={fps}/1',
                '!', 'videoconvert', '!', 'x264enc', 'tune=zerolatency', 'bitrate=5000',
                'speed-preset=superfast', '!', 'mpegtsmux', '!',
                f'srtsink uri=srt://{self.relay_host}:{self.relay_port}?mode=caller'
            ], stdin=subprocess.PIPE)
        # Initialize peer pipelines dict
        self.peer_procs = {}
        for peer in self.peers:
            proc = subprocess.Popen([
                'gst-launch-1.0', '-v', 'appsrc', 'format=3', 'is-live=true',
                f'caps=video/x-raw,format=BGR,width={width},height={height},framerate={fps}/1',
                '!', 'videoconvert', '!', 'x264enc', 'tune=zerolatency', 'bitrate=5000',
                'speed-preset=superfast', '!', 'mpegtsmux', '!',
                f'srtsink uri=srt://{peer}?mode=caller'
            ], stdin=subprocess.PIPE)
            self.peer_procs[peer] = proc

    def process(self, frame):
        # Optionally store
        if self.store:
            self.writer.write(frame)
        # Optionally display
        if self.display:
            cv2.imshow('Local Display', frame)
            cv2.waitKey(1)
        # Optionally analyze
        if self.analyze:
            self.analyze_frame(frame)
        # Optionally relay
        if self.relay:
            try:
                self.relay_proc.stdin.write(frame.tobytes())
            except BrokenPipeError:
                pass
        # Optionally send to peers
        for peer, proc in self.peer_procs.items():
            try:
                proc.stdin.write(frame.tobytes())
            except BrokenPipeError:
                pass

    def close(self):
        if self.store:
            self.writer.release()
        if self.display:
            cv2.destroyAllWindows()
        if self.relay:
            self.relay_proc.stdin.close()
            self.relay_proc.terminate()
        for proc in self.peer_procs.values():
            proc.stdin.close()
            proc.terminate()
# app/frame_processor.py

import cv2
from ultralytics import YOLO


class FrameProcessor:
    def __init__(self, flame_model_path, smoke_model_path):
        # Load YOLO models
        self.model_flame = YOLO(flame_model_path)
        self.model_smoke = YOLO(smoke_model_path)

    def detect_and_draw(self, frame):
        """
        Perform flame and smoke detection on a frame and annotate it.
        """
        # YOLO flame detection
        results_flame = self.model_flame(frame)
        for result in results_flame:
            self._annotate_frame(frame, result, (0, 255, 0))  # Green for flame

        # YOLO smoke detection
        results_smoke = self.model_smoke(frame)
        for result in results_smoke:
            self._annotate_frame(frame, result, (255, 0, 0))  # Blue for smoke

        return frame

    def _annotate_frame(self, frame, result, color):
        """
        Annotates the frame with detection results.
        """
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())
            label = f"{self.model_flame.names[cls]}: {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

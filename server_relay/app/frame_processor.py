# app/frame_processor.py

import cv2
from ultralytics import YOLO


class FrameProcessor:
    def __init__(self, flame_model_path, smoke_model_path):
        # Load YOLO models with fallback on error
        try:
            self.model_flame = YOLO(flame_model_path)
        except Exception as e:
            print(f"Warning: could not load flame model: {e}")
            self.model_flame = None
        try:
            self.model_smoke = YOLO(smoke_model_path)
        except Exception as e:
            print(f"Warning: could not load smoke model: {e}")
            self.model_smoke = None

    def detect_and_draw(self, frame):
        """
        Perform flame and smoke detection on a frame and annotate it.
        """
        # YOLO flame detection
        if self.model_flame:
            results_flame = self.model_flame(frame)
            for result in results_flame:
                self._annotate_frame(frame, result, (0, 255, 0))  # Green for flame

        # YOLO smoke detection
        if self.model_smoke:
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

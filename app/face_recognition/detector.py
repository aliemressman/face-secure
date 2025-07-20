# Yeni HAFIF FaceDetector (mediapipe) versiyonu

import cv2
import mediapipe as mp

class FaceDetector:
    def __init__(self, confidence=0.6):
        self.detector = mp.solutions.face_detection.FaceDetection(
            model_selection=0,  # 0: yakın yüzler
            min_detection_confidence=confidence
        )

    def detect_face(self, frame):
        boxes = []
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.detector.process(rgb)
            if results.detections:
                h, w, _ = frame.shape
                for det in results.detections:
                    box = det.location_data.relative_bounding_box
                    x = int(box.xmin * w)
                    y = int(box.ymin * h)
                    w_box = int(box.width * w)
                    h_box = int(box.height * h)
                    boxes.append((x, y, w_box, h_box))
        except Exception as e:
            print(f"[HATA - Mediapipe]: {e}")
        return boxes

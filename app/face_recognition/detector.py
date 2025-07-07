"""
Kamera ile Gerçek Zamanlı Yüz Algılama (Mediapipe)
"""

import cv2
import mediapipe as mp

# Yüz algılama sınıfı tanımlanıyor
class FaceDetector:
    def __init__(self, confidence = 0.6):
        # Mediapipe'in yüz algılama özelliği kullanılıyor
        self.face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection = 1, # 1: daha uzak yüzler için model
            min_detection_confidence = confidence # Minimum algılama doğruluğu
        )

    def detect_face(self, frame):
        """Yüzleri tespit eder ve bounding box (kutu) döner"""

        # OpenCV ile alınan görüntü RGB formatına çevrilir
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Mediapipe ile yüz algılama yapılır
        results = self.face_detection.process(rgb)

        # Algılanan yüzlerin kutularını tutacak liste
        boxes = []

        # Eğer yüz algılandıysa
        if results.detections:
            for det in results.detections:
                # Bounding box bilgilerini al 
                box = det.location_data.relative_bounding_box

                # Çerçeve boyutlarını al
                h, w, _ = frame.shape

                # Oransal koordinatları piksel cinsine çevir
                x = int(box.xmin * w)
                y = int(box.ymin * h)
                w_box = int(box.width * w)
                h_box = int(box.height * h)

                # Sonucu listeye ekle
                boxes.append((x, y, w_box, h_box))

        return boxes

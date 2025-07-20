""" Kamerayı açar, yüz tespit eder ve ekrana gösterir """

import cv2
from app.face_recognition.detector import FaceDetector 
from app.face_recognition.embedding import get_embedding
from app.face_recognition.matcher import find_best_match
from app.services.user_management import get_all_user_embeddings, log_login_attempt
from models.model import get_facenet_model

SIMILARITY_THRESHOLD = 0.65
IP_ADDRESS = "127.0.0.1"
FRAME_SKIP = 3  # Her 3 karede bir işlem yap
RESIZE_SCALE = 0.5  # Görüntü işleme yükünü azaltmak için küçültme oranı

def run_camera_auth():
    model = get_facenet_model()
    known_users = get_all_user_embeddings()

    if not known_users:
        print("[UYARI] Sistemde kullanıcı yok.")
        return

    detector = FaceDetector(confidence=0.6)
    cap = cv2.VideoCapture(0)
    print("[INFO] Kamera açıldı. 'q' ile çıkış yapabilirsin.")

    frame_count = 0
    text = "Yüz bekleniyor..."
    color = (255, 255, 0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        display = frame.copy()

        if frame_count % FRAME_SKIP == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=RESIZE_SCALE, fy=RESIZE_SCALE)
            boxes = detector.detect_face(small_frame)

            if boxes:
                x, y, w, h = boxes[0]
                # Orijinal boyuta göre çevir
                x, y, w, h = [int(coord / RESIZE_SCALE) for coord in (x, y, w, h)]
                face_img = frame[y:y+h, x:x+w]

                embedding = get_embedding(model, face_img)
                matched_user, similarity = find_best_match(embedding, known_users, threshold=SIMILARITY_THRESHOLD)

                if matched_user != "Unknown":
                    text = f"{matched_user} ({similarity:.2f}) - Giriş Başarılı"
                    color = (0, 255, 0)
                    log_login_attempt(matched_user, True, IP_ADDRESS)
                else:
                    text = f"Erisim Reddedildi ({similarity:.2f})"
                    color = (0, 0, 255)
                    log_login_attempt("Unknown", False, IP_ADDRESS)
            else:
                text = "Yüz algılanamadı"
                color = (0, 0, 255)

        cv2.putText(display, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.imshow("FaceSecure", display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



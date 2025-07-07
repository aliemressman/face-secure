""" Kamerayı açar, yüz tespit eder ve ekrana gösterir """

import cv2
from app.face_recognition.detector import FaceDetector 
from app.face_recognition.embedding import get_embedding
from app.face_recognition.matcher import find_best_match
from app.services.user_management import get_all_user_embeddings, log_login_attempt
from models.model import get_facenet_model

SIMILARITY_THRESHOLD = 0.65
IP_ADDRESS = "127.0.0.1"

def run_camera_auth():
    model = get_facenet_model()
    known_users = get_all_user_embeddings()
    
    if not known_users:
        print("[UYARI] Sistemde kullanıcı yok.")
        return
    
    detector = FaceDetector(confidence=0.6)  # confidence isteğe bağlı
    cap = cv2.VideoCapture(0)
    print("[INFO] Kamera açıldı. 'q' ile çıkış yapabilirsin.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        boxes = detector.detect_face(frame)  # Yüz koordinatlarını al
        face_img = None
        if boxes:
            # İlk bulunan yüzü crop et (x,y,w,h)
            x, y, w, h = boxes[0]
            face_img = frame[y:y+h, x:x+w]
        
        display = frame.copy()
        if face_img is not None:
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
            text = "Yuz algilanamadi"
            color = (0, 0, 255)
            
        cv2.putText(display, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.imshow("FaceSecure", display)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()




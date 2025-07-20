import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import cv2
import re
from app.services.user_management import save_user_embedding
from app.face_recognition.embedding import get_embedding
from models.model import get_facenet_model

# === Augmented görsellerin bulunduğu klasör ===
IMAGE_DIR = "data/images_augmented"

# === Dosya adından kullanıcı ismini çıkar ===
def normalize_username(raw_name):
    base = os.path.splitext(os.path.basename(raw_name))[0]
    base = re.sub(r'_aug\d+$', '', base)         # _augX kaldır
    base = re.sub(r'\d+$', '', base)             # sondaki rakamları kaldır
    base = re.sub(r'[^a-zA-Z]', '', base)         # sadece harfler
    return base.lower()

def process_images():
    if not os.path.exists(IMAGE_DIR):
        print(f"[HATA] {IMAGE_DIR} klasörü bulunamadı.")
        return

    model = get_facenet_model()

    for file in os.listdir(IMAGE_DIR):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(IMAGE_DIR, file)
            img = cv2.imread(path)
            if img is None:
                print(f"[HATA] Görüntü okunamadı: {path}")
                continue

            username = normalize_username(file)
            embedding = get_embedding(model, img)
            save_user_embedding(username, embedding)
            print(f"[✓] {username} → embedding kaydedildi: {file}")

if __name__ == "__main__":
    process_images()
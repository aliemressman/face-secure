import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import cv2
from app.services.user_management import save_user_embedding
from app.face_recognition.embedding import get_embedding
import re

IMAGE_DIR = "data/images"

def normalize_username(raw_name):
    base = os.path.splitext(os.path.basename(raw_name))[0]
    cleaned = re.sub(r'[^a-zA-Z]', '', base)  # sadece harfler
    return cleaned.lower()

def process_images():
    for file in os.listdir(IMAGE_DIR):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(IMAGE_DIR, file)
            img = cv2.imread(path)
            if img is None:
                print(f"[HATA] görüntü okunamadı: {path}")
                continue

            username = normalize_username(file)
            embedding = get_embedding(None, img)
            save_user_embedding(username, embedding)
            print(f"[OK] {username} → embedding eklendi.")

if __name__ == "__main__":
    process_images()

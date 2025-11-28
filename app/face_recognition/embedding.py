import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

"""
DeepFace ile Yüz Embedding Çıkarma
"""

from deepface import DeepFace
import cv2

def get_embedding(_, face_img):
    face_img = cv2.resize(face_img, (160, 160))
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    embedding = DeepFace.represent(face_img, model_name="Facenet", enforce_detection=False)
    return embedding[0]["embedding"]


"""
Hem görsel dosyasından okunan img ile, hem de canlı kamera görüntüsünden gelen face_img için kullanılır.
"""
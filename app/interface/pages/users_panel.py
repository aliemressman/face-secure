import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import cv2
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# Gerekli servisler
from app.face_recognition.embedding import get_embedding
from app.face_recognition.detector import FaceDetector
from app.face_recognition.matcher import find_best_match
from app.services.user_management import get_all_user_embeddings, log_login_attempt

# --------------------------- Sayfa Ayarları ---------------------------
st.set_page_config(page_title="FaceSecure - Kullanıcı Girişi", layout="wide",initial_sidebar_state="collapsed")
st.sidebar.markdown("## 👤 Kullanıcı Girişi")
st.sidebar.info("Yüz tanıma ile sisteme giriş yapın.")

# --------------------------- Global Kaynaklar ---------------------------
@st.cache_resource(show_spinner=False)
def load_detector():
    return FaceDetector()

# @st.cache_resource(show_spinner=False) streamlit'i terminalden calistirmak icin gerekli
def load_known_users():
    return get_all_user_embeddings()

DETECTOR = load_detector()
KNOWN_USERS = load_known_users()

# --------------------------- Kamera Sınıfı ---------------------------
class LiveProcessor(VideoTransformerBase):
    def __init__(self):
        self.box_color = (0, 0, 255)
        self.text = "Yüz algılanıyor..."
        self.similarity = 0.0
        self.user = "Unknown"
        self.latest_frame = None

    def transform(self, frame):
        image = frame.to_ndarray(format="bgr24")
        boxes = DETECTOR.detect_face(image)
        self.latest_frame = frame

        if len(boxes) > 1:
            self.text = "⚠️ Birden fazla yüz algılandı!"
            self.box_color = (0, 255, 255)
            for (x, y, w, h) in boxes:
                cv2.rectangle(image, (x, y), (x + w, y + h), self.box_color, 2)
                cv2.putText(image, self.text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.box_color, 2)
                self.user = "TooManyFaces"
                return image

        elif len(boxes) == 1:
            x, y, w, h = boxes[0]
            face_img = image[y:y + h, x:x + w]
            if face_img.size == 0:
                return image

            embedding = get_embedding(None, face_img)
            matched_user, similarity = find_best_match(embedding, KNOWN_USERS, threshold=0.65)

            self.user = matched_user
            self.similarity = similarity

            self.text = f"{matched_user} ({similarity:.2f})" if matched_user != "Unknown" else f"Tanınmadı ({similarity:.2f})"
            self.box_color = (0, 255, 0) if matched_user != "Unknown" else (0, 0, 255)

            cv2.rectangle(image, (x, y), (x + w, y + h), self.box_color, 2)
            cv2.putText(image, self.text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.box_color, 2)

        return image


# --------------------------- Arayüz ---------------------------
def show_login_ui():
    st.markdown("### 🎥 Kameradan Giriş Yap")
    ctx = webrtc_streamer(key="user-login", video_processor_factory=LiveProcessor)

    if ctx.video_transformer:
        st.markdown("---")
        st.markdown(f"**🎯 Tespit Edilen Kişi:** `{ctx.video_transformer.user}` | **Benzerlik:** `{ctx.video_transformer.similarity:.2f}`")

        if st.button("🧬 Girişi Onayla"):
            if ctx.video_transformer.user == "TooManyFaces":
                st.warning("⚠️ Lütfen sadece bir kişi kamerada olacak şekilde tekrar deneyin.")
                return
            frame = ctx.video_transformer.latest_frame

            if frame is not None:
                image = frame.to_ndarray(format="bgr24")
                boxes = DETECTOR.detect_face(image)

                if boxes:
                    x, y, w, h = boxes[0]
                    face_img = image[y:y + h, x:x + w]

                    if face_img.size > 0:
                        embedding = get_embedding(None, face_img)
                        matched_user, similarity = find_best_match(embedding, KNOWN_USERS)

                        if matched_user != "Unknown":
                            st.success(f"✅ Giriş Başarılı: {matched_user} ({similarity:.2f})")
                            log_login_attempt(matched_user, True, "127.0.0.1")
                        else:
                            st.error(f"❌ Giriş Reddedildi ({similarity:.2f})")
                            log_login_attempt("Unknown", False, "127.0.0.1")
                    else:
                        st.warning("Yüz bulundu ancak görüntü alınamadı.")
                else:
                    st.warning("Kamerada yüz algılanmadı.")

# --------------------------- Çalıştır ---------------------------
show_login_ui()

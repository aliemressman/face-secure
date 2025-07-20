import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import cv2
import numpy as np
import re
import albumentations as A

from app.services.user_management import get_usernames, delete_user, get_all_logs, save_user_embedding
from app.auth.admin_auth import check_admin_login
from app.face_recognition.embedding import get_embedding
from models.model import get_facenet_model

# --- Sayfa Ayarları ---
st.set_page_config(page_title="Admin Panel - FaceSecure", layout="wide", initial_sidebar_state="collapsed")
st.sidebar.markdown("## 🛠️ Admin Paneli")
st.sidebar.info("Kullanıcı yönetimi, kayıt ve log işlemleri")

st.markdown("<h1 style='text-align: center;'>🔐 Admin Yönetim Paneli</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Kullanıcı kayıt, silme ve sistem loglarını yönetin.</p>", unsafe_allow_html=True)
st.markdown("---")

if not check_admin_login():
    st.stop()

# --- Yardımcı Fonksiyon ---
def normalize_username(raw_name):
    return re.sub(r'[^a-zA-Z]', '', raw_name).lower()

# --- Albumentations Pipeline ---
augment = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.5),
    A.Rotate(limit=15, p=0.7),
    A.GaussNoise(var_limit=(10, 30), p=0.4),
    A.Blur(blur_limit=3, p=0.3),
])

# --- Kullanıcı Kayıt ---
with st.expander("➕ Yeni Kullanıcı Kaydı", expanded=False):
    st.markdown("Yüz görsellerini yükleyerek kullanıcıyı kaydedin.")
    name = st.text_input("👤 Kullanıcı Adı (aynı kişi için aynı ad!)")
    uploaded_files = st.file_uploader("📷 Yüz Görsellerini Yükleyin (10+ önerilir)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if st.button("📥 Kaydet") and name and uploaded_files:
        username = normalize_username(name)
        model = get_facenet_model()
        count = 0

        for file in uploaded_files:
            img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                st.warning(f"❌ '{file.name}' okunamadı.")
                continue

            for i in range(6):  # 1 orijinal + 5 augment
                input_img = img if i == 0 else augment(image=img)["image"]
                embedding = get_embedding(model, input_img)
                save_user_embedding(username, embedding)
                count += 1

        st.success(f"✅ {username} için toplam {count} görsel (aug dahil) kaydedildi." if count else "❌ Hiçbir görsel işlenemedi.")

st.markdown("---")

# --- Kullanıcı Silme ---
st.subheader("🗑️ Kullanıcıları Yönet")
user_list = get_usernames()

if user_list:
    selected_user = st.selectbox("Silmek istediğiniz kullanıcıyı seçin:", user_list)
    if st.button("❌ Kullanıcıyı Sil"):
        if delete_user(selected_user):
            st.success(f"✅ {selected_user} silindi.")
            st.rerun()
        else:
            st.error("❌ Silme başarısız.")
else:
    st.info("📭 Kayıtlı kullanıcı yok.")

st.markdown("---")

# --- Giriş Logları ---
logs = get_all_logs()

with st.expander("📜 Giriş Loglarını Göster"):
    if st.button("🔄 Logları Yenile"):
        logs = get_all_logs()
        st.rerun()

    if logs:
        for log in logs:
            durum = "✅ Başarılı" if log["success"] else "❌ Başarısız"
            st.markdown(f"""
            - 👤 Kullanıcı: `{log['username']}`
            - 🕒 Zaman: `{log['timestamp'].strftime("%Y-%m-%d %H:%M:%S")}`
            - 🌐 IP: `{log['ip']}`
            - 📌 Durum: {durum}
            ---
            """)
    else:
        st.info("Henüz giriş log'u yok.")
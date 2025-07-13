import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import cv2
import numpy as np
import re

from app.services.user_management import (get_usernames, delete_user, get_all_logs, save_user_embedding)
from app.auth.admin_auth import check_admin_login
from app.face_recognition.embedding import get_embedding

# ---------------- Sayfa Ayarları ----------------
st.set_page_config(page_title="Admin Panel - FaceSecure", layout="wide",initial_sidebar_state="collapsed")
st.sidebar.markdown("## 🛠️ Admin Paneli")
st.sidebar.info("Kullanıcı yönetimi, kayıt ve log işlemleri")

st.markdown("<h1 style='text-align: center;'>🔐 Admin Yönetim Paneli</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Kullanıcı kayıt, silme ve sistem loglarını yönetin.</p>", unsafe_allow_html=True)
st.markdown("---")
if not check_admin_login():
    st.stop()
    

# ---------------- Yardımcı Fonksiyon ----------------
def normalize_username(raw_name):
    cleaned = re.sub(r'[^a-zA-Z]', '', raw_name)
    return cleaned.lower()

# ---------------- Kullanıcı Kayıt Bölümü ----------------
with st.expander("➕ Yeni Kullanıcı Kaydı", expanded=False):
    st.markdown("Yüz görsellerini yükleyerek kullanıcıyı kaydedin.")
    name = st.text_input("👤 Kullanıcı Adı (aynı kişi için aynı ad!)")
    uploaded_files = st.file_uploader(
        "📷 Yüz Görsellerini Yükleyin (10+ önerilir)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if st.button("📥 Kaydet") and name and uploaded_files:
        username = normalize_username(name)
        success_count = 0

        for uploaded_file in uploaded_files:
            img = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                st.warning(f"❌ '{uploaded_file.name}' okunamadı.")
                continue

            embedding = get_embedding(None, img)
            save_user_embedding(username, embedding)
            success_count += 1

        if success_count > 0:
            st.success(f"✅ {username} için {success_count} görsel başarıyla kaydedildi.")
        else:
            st.error("❌ Hiçbir görsel başarıyla işlenemedi.")

st.markdown("---")

# ---------------- Kullanıcı Silme Bölümü ----------------
st.subheader("🗑️ Kullanıcıları Yönet")

user_list = get_usernames()
if user_list:
    selected_user = st.selectbox("Silmek istediğiniz kullanıcıyı seçin:", user_list)
    if st.button("❌ Kullanıcıyı Sil"):
        success = delete_user(selected_user)
        if success:
            st.success(f"✅ {selected_user} başarıyla silindi.")
            st.rerun()
        else:
            st.error("❌ Kullanıcı silinemedi.")
else:
    st.info("📭 Kayıtlı kullanıcı bulunamadı.")

st.markdown("---")

# ---------------- Giriş Logları ----------------

# Giriş sonrası logları direkt çekiyoruz (cache yok)
logs = get_all_logs()

with st.expander("📜 Giriş Loglarını Göster"):
    if st.button("🔄 Logları Yenile"):
        logs = get_all_logs()  # Yeniden çek
        st.rerun()  # Sayfayı yenile

    if logs:
        for log in logs:
            status = "✅ Başarılı" if log["success"] else "❌ Başarısız"
            st.markdown(f"""
            - 👤 Kullanıcı: `{log['username']}`
            - 🕒 Zaman: `{log['timestamp'].strftime("%Y-%m-%d %H:%M:%S")}`
            - 🌐 IP: `{log['ip']}`
            - 📌 Durum: {status}
            ---
            """)
    else:
        st.info("Henüz giriş log'u yok.")
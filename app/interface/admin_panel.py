import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from app.services.user_management import get_usernames, delete_user, get_all_logs, save_user_embedding
from app.face_recognition.embedding import get_embedding
import cv2
import numpy as np
import re

# ---------------- Sayfa Ayarları ----------------
st.set_page_config(page_title="Admin Panel - FaceSecure", layout="wide")
st.title("🛠️ Admin Paneli")

st.markdown("""
Yüz tanıma sistemine ait kullanıcıları yönetebilir, kayıt ekleyebilir ve giriş loglarını inceleyebilirsiniz.
""")

# ---------------- Yardımcı Fonksiyon ----------------
def normalize_username(raw_name):
    cleaned = re.sub(r'[^a-zA-Z]', '', raw_name)
    return cleaned.lower()

# ---------------- Kullanıcı Kayıt ----------------
st.subheader("➕ Yeni Kullanıcı Ekle")

with st.expander("📥 Kullanıcı Kaydı Formu", expanded=False):
    name = st.text_input("Kullanıcı Adı (aynı kişi için aynı ad!)")
    uploaded_files = st.file_uploader(
        "Bir veya birden fazla yüz fotoğrafı yükleyin",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if st.button("✅ Kaydet") and name and uploaded_files:
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
            st.success(f"✅ {username} için {success_count} adet görsel başarıyla kaydedildi.")
        else:
            st.error("❌ Hiçbir görsel başarıyla işlenemedi.")

# ---------------- Kullanıcı Listesi ----------------
st.subheader("👤 Kayıtlı Kullanıcılar")

user_list = get_usernames()

if user_list:
    selected_user = st.selectbox("Silmek için bir kullanıcı seçin", user_list)

    if st.button("❌ Kullanıcıyı Sil"):
        success = delete_user(selected_user)
        if success:
            st.success(f"✅ {selected_user} başarıyla silindi.")
            st.rerun()
        else:
            st.error("❌ Silme işlemi başarısız oldu.")
else:
    st.info("📭 Sistemde kayıtlı kullanıcı bulunmamaktadır.")

# ---------------- Giriş Logları ----------------
st.subheader("📜 Giriş Logları")

if st.button("📂 Logları Göster"):
    logs = get_all_logs()

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
        st.info("Henüz hiç giriş log'u bulunamadı.")

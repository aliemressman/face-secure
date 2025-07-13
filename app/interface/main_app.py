import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st

# ------------------ Sayfa Ayarları ------------------
st.set_page_config(
    page_title="FaceSecure Giriş",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------ Stil ------------------
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .centered { text-align: center; }
    .stButton>button {
        width: 100%;
        padding: 0.75em;
        font-weight: bold;
        border-radius: 10px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ Başlık ------------------
st.markdown("<h1 class='centered'>🔐 FaceSecure'e Hoşgeldiniz ! </h1>", unsafe_allow_html=True)
st.markdown("<p class='centered'>Lütfen giriş türünü seçin</p>", unsafe_allow_html=True)

# ------------------ Seçenek Kartları ------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/3064/3064197.png", width=80)
    st.write("### 👤 Kullanıcı Girişi")
    if st.button("➡️ Kullanıcı Paneline Git"):
        st.switch_page("pages/users_panel.py")

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/1828/1828490.png", width=80)
    st.write("### 🔐 Admin Paneli")
    if st.button("➡️ Admin Paneline Git"):
        st.switch_page("pages/admin_panel.py")

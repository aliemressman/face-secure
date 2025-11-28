# --- PYTHONPATH sabitleyici (kökü otomatik bulur) ---
import sys
from pathlib import Path

# Bu dosyanın konumu: .../app/interface/pages/<dosya>.py
# parents[3] => proje kökü ("Face Secure")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# -----------------------------------------------------

import os
import streamlit as st

# Styles klasörünün path'ini ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)  # app klasörüne git
styles_dir = os.path.join(app_dir, 'styles')
sys.path.append(app_dir)  # app klasörünü Python path'ine ekle

# Şimdi import edebiliriz
from styles.main_style_loader import load_css, load_html_component

# ------------------ Sayfa Ayarları ------------------
st.set_page_config(
    page_title="FaceSecure Giriş",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------ Stilleri Yükle ------------------
# CSS ve HTML dosyalarının tam path'lerini belirle
css_path = os.path.join(styles_dir, "main_styles.css")
html_path = os.path.join(styles_dir, "main_styles.html")

# CSS dosyasını yükle
load_css(css_path)

# HTML componentlerini yükle
html_components = load_html_component(html_path)

# Arka plan parçacıkları ve ana başlık
st.markdown(html_components, unsafe_allow_html=True)

# ------------------ Kartlar ve Butonlar ------------------
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("""
        <div class="option-card">
            <div class="card-icon">
                <img src="https://cdn-icons-png.flaticon.com/512/3064/3064197.png" alt="Kullanıcı">
            </div>
            <h3 class="card-title">Kullanıcı Girişi</h3>
            <p class="card-description">Yüz tanıma teknolojisi ile hızlı ve güvenli giriş yapın</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Kullanıcı Paneline Git", key="user_btn"):
        st.switch_page("pages/users_panel.py")

with col2:
    st.markdown("""
        <div class="option-card">
            <div class="card-icon">
                <img src="https://cdn-icons-png.flaticon.com/512/1828/1828490.png" alt="Admin">
            </div>
            <h3 class="card-title">Admin Paneli</h3>
            <p class="card-description">Sistem yönetimi ve kullanıcı kontrolü için admin paneli</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("⚙️ Admin Paneline Git", key="admin_btn"):
        st.switch_page("pages/admin_panel.py")
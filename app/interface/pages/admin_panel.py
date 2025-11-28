# --- PYTHONPATH sabitleyici (kökü otomatik bulur) ---
import sys
from pathlib import Path

# Bu dosyanın konumu: .../app/interface/pages/<dosya>.py
# parents[3] => proje kökü ("Face Secure")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# -----------------------------------------------------

import streamlit as st
import cv2
import numpy as np
import re
import albumentations as A
from app.services.user_management import get_usernames, delete_user, get_all_logs, save_user_embedding
from app.auth.admin_auth import check_admin_login
from app.face_recognition.embedding import get_embedding
from models.model import get_facenet_model

# --------------------------- Sayfa Ayarları ---------------------------
st.set_page_config(
    page_title="FaceSecure - Admin Panel", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------- Modern Stil ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Streamlit Header'ı Gizle */
header[data-testid="stHeader"] {
    background: #0d1117;
    height: 0px;
    visibility: hidden;
}

[data-testid="stSidebar"] {
    display: none;
}

/* Ana Background */
.stApp {
    background: linear-gradient(135deg, #1a1f2e 0%, #2d3748 25%, #4a5568 50%, #5a6478 100%);
    min-height: 100vh;
}

/* Main Container */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 1200px;
    margin: 0 auto;
}

body {
    font-family: 'Poppins', sans-serif;
    margin: 0;
    padding: 0;
}

/* Home Button */
.home-button-container {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 9999;
}

.home-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(45, 55, 72, 0.95);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(88, 166, 255, 0.3);
    color: #58a6ff;
    padding: 0.7rem 1rem;
    border-radius: 50px;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 500;
    font-family: 'Poppins', sans-serif;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
    cursor: pointer;
}

.home-button:hover {
    background: rgba(88, 166, 255, 0.1);
    border-color: #58a6ff;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(88, 166, 255, 0.4);
}

/* Header Section */
.header-section {
    background: rgba(45, 55, 72, 0.8);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.page-title {
    font-size: 2rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0 0 0.3rem 0;
    background: linear-gradient(135deg, #58a6ff 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.page-subtitle {
    font-size: 0.95rem;
    color: rgba(255,255,255,0.7);
    margin: 0;
    font-weight: 400;
}

/* Content Grid */
.content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

/* Section Cards */
.section-card {
    background: rgba(45, 55, 72, 0.9);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
    position: relative;
    height: fit-content;
}

.section-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #58a6ff 0%, #7c3aed 100%);
    border-radius: 16px 16px 0 0;
}

.section-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Full Width Cards */
.full-width-card {
    background: rgba(45, 55, 72, 0.9);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
    position: relative;
    margin-bottom: 1.5rem;
}

.full-width-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #58a6ff 0%, #7c3aed 100%);
    border-radius: 16px 16px 0 0;
}

/* Form Elements */
.stTextInput > div > div > input {
    background: rgba(26, 31, 46, 0.8);
    border: 1px solid rgba(88, 166, 255, 0.3);
    border-radius: 10px;
    color: #ffffff;
    padding: 0.7rem 1rem;
    font-family: 'Poppins', sans-serif;
    font-size: 0.9rem;
}

.stTextInput > div > div > input:focus {
    border-color: #58a6ff;
    box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.2);
}

.stSelectbox > div > div {
    background: rgba(26, 31, 46, 0.8);
    border: 1px solid rgba(88, 166, 255, 0.3);
    border-radius: 10px;
}

.stSelectbox > div > div > div {
    color: #ffffff;
    background: rgba(26, 31, 46, 0.8);
}

/* File Uploader */
.stFileUploader > div {
    background: rgba(26, 31, 46, 0.8);
    border: 2px dashed rgba(88, 166, 255, 0.5);
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
}

.stFileUploader > div:hover {
    border-color: #58a6ff;
    background: rgba(88, 166, 255, 0.05);
}

.stFileUploader label {
    color: #ffffff !important;
    font-size: 0.9rem;
}

/* Buttons */
.stButton > button {
    width: 100%;
    padding: 0.7rem 1.2rem;
    font-size: 0.9rem;
    font-weight: 600;
    border-radius: 10px;
    border: none;
    color: #ffffff;
    background: linear-gradient(135deg, #58a6ff 0%, #7c3aed 100%);
    box-shadow: 0 3px 12px rgba(88, 166, 255, 0.4);
    transition: all 0.3s ease;
    cursor: pointer;
    font-family: 'Poppins', sans-serif;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 5px 20px rgba(88, 166, 255, 0.6);
    background: linear-gradient(135deg, #6cb6ff 0%, #8b5cf6 100%);
}

/* Delete Button */
.delete-button > button {
    background: linear-gradient(135deg, #f85149 0%, #dc2626 100%);
    box-shadow: 0 3px 12px rgba(248, 81, 73, 0.4);
}

.delete-button > button:hover {
    box-shadow: 0 5px 20px rgba(248, 81, 73, 0.6);
    background: linear-gradient(135deg, #ff6b6b 0%, #ef4444 100%);
}

/* Info Cards */
.info-card {
    background: rgba(88, 166, 255, 0.1);
    border: 1px solid rgba(88, 166, 255, 0.3);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

.info-label {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 0.3rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.info-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
}

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.stat-card {
    background: rgba(88, 166, 255, 0.1);
    border: 1px solid rgba(88, 166, 255, 0.3);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}

.stat-number {
    font-size: 1.8rem;
    font-weight: 700;
    color: #58a6ff;
    margin-bottom: 0.3rem;
}

.stat-label {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.6);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Log Entry */
.log-entry {
    background: rgba(26, 31, 46, 0.8);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    border-left: 4px solid transparent;
    transition: all 0.3s ease;
}

.log-entry.success {
    border-left-color: #3fb950;
    background: rgba(63, 185, 80, 0.1);
}

.log-entry.failed {
    border-left-color: #f85149;
    background: rgba(248, 81, 73, 0.1);
}

.log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.log-user {
    font-weight: 600;
    color: #ffffff;
    font-size: 0.95rem;
}

.log-status {
    font-size: 0.8rem;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-weight: 500;
}

.log-status.success {
    background: rgba(63, 185, 80, 0.2);
    color: #3fb950;
}

.log-status.failed {
    background: rgba(248, 81, 73, 0.2);
    color: #f85149;
}

.log-details {
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.7);
    display: flex;
    gap: 1rem;
}

/* Instructions */
.instruction-panel {
    background: rgba(88, 166, 255, 0.05);
    border: 1px solid rgba(88, 166, 255, 0.15);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.instruction-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin-bottom: 0.8rem;
    color: rgba(255, 255, 255, 0.75);
    font-size: 0.85rem;
    line-height: 1.3;
}

.instruction-item:last-child {
    margin-bottom: 0;
}

.instruction-icon {
    background: #58a6ff;
    color: white;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    font-weight: bold;
    flex-shrink: 0;
    margin-top: 1px;
}

/* Progress Indicator */
.progress-container {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    height: 8px;
    margin: 1rem 0;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #58a6ff 0%, #7c3aed 100%);
    border-radius: 8px;
    transition: width 0.3s ease;
}

/* Alert Styles */
.stAlert {
    background: rgba(33, 38, 45, 0.9) !important;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 10px !important;
    color: white !important;
}

.stAlert > div {
    background: transparent !important;
}

/* Responsive */
@media (max-width: 1024px) {
    .content-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
}

@media (max-width: 768px) {
    .page-title {
        font-size: 1.7rem;
    }
    
    .header-section {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .section-card, .full-width-card {
        padding: 1rem;
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .home-button-container {
        position: relative;
        top: 0;
        left: 0;
        margin-bottom: 1rem;
    }
}

/* Expandable sections - Custom styling for Streamlit expander */
.stExpander {
    background: rgba(45, 55, 72, 0.9) !important;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 16px !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2) !important;
    position: relative;
}

.stExpander::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #58a6ff 0%, #7c3aed 100%);
    border-radius: 16px 16px 0 0;
}

.stExpander > div:first-child {
    background: transparent !important;
    border: none !important;
}

.stExpander > div:first-child > div {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 1.3rem !important;
    font-family: 'Poppins', sans-serif !important;
    padding: 1rem 1.5rem !important;
}

.stExpander > div:last-child {
    background: transparent !important;
    border: none !important;
    padding: 0 1.5rem 1.5rem 1.5rem !important;
}

.stExpander > div:last-child > div {
    background: transparent !important;
}

/* Loading Animation */
.processing {
    position: relative;
}

.processing::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20px;
    height: 20px;
    margin: -10px 0 0 -10px;
    border: 2px solid rgba(88, 166, 255, 0.3);
    border-radius: 50%;
    border-top-color: #58a6ff;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>
""", unsafe_allow_html=True)

# --------------------------- Yardımcı Fonksiyonlar ---------------------------
def normalize_username(raw_name):
    return re.sub(r'[^a-zA-Z]', '', raw_name).lower()

# --------------------------- Albumentations Pipeline ---------------------------
augment = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.5),
    A.Rotate(limit=15, p=0.7),
    A.GaussNoise(var_limit=(10, 30), p=0.4),
    A.Blur(blur_limit=3, p=0.3),
])

# --------------------------- Admin Kontrolü ---------------------------
if not check_admin_login():
    st.stop()

# --------------------------- Ana Sayfaya Dönüş Butonu ---------------------------
st.markdown("""
<div class="home-button-container">
    <a href="/" class="home-button">
        🏠 Ana Sayfa
    </a>
</div>
""", unsafe_allow_html=True)

# --------------------------- Ana Arayüz ---------------------------
# Header
st.markdown("""
<div class="header-section">
    <h1 class="page-title">
        🔐 Admin Yönetim Paneli
    </h1>
    <p class="page-subtitle">Kullanıcı kayıt, silme ve sistem loglarını yönetin</p>
</div>
""", unsafe_allow_html=True)

# İstatistikler
user_list = get_usernames()
logs = get_all_logs()
success_count = len([log for log in logs if log["success"]])
failed_count = len(logs) - success_count

st.markdown(f"""
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">{len(user_list)}</div>
        <div class="stat-label">Kayıtlı Kullanıcı</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{len(logs)}</div>
        <div class="stat-label">Toplam Giriş</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{success_count}</div>
        <div class="stat-label">Başarılı Giriş</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{failed_count}</div>
        <div class="stat-label">Başarısız Giriş</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Ana İçerik Grid
st.markdown('<div class="content-grid">', unsafe_allow_html=True)

# Sol Kolon - Kullanıcı Kaydı (Collapsible)
with st.container():
    with st.expander("➕ Yeni Kullanıcı Kaydı", expanded=False):
        st.markdown("""
        <div class="instruction-panel">
            <div class="instruction-item">
                <div class="instruction-icon">1</div>
                <div>Kullanıcı adını girin (aynı kişi için aynı ad kullanın)</div>
            </div>
            <div class="instruction-item">
                <div class="instruction-icon">2</div>
                <div>En az 10 farklı yüz görselini yükleyin</div>
            </div>
            <div class="instruction-item">
                <div class="instruction-icon">3</div>
                <div>Sistem otomatik olarak augmentasyon uygulayacak</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("👤 Kullanıcı Adı", placeholder="Kullanıcı adını girin...")
        uploaded_files = st.file_uploader(
            "📷 Yüz Görsellerini Yükleyin", 
            type=["jpg", "jpeg", "png"], 
            accept_multiple_files=True,
            help="En az 10 farklı görsel yüklemeniz önerilir"
        )
        
        if uploaded_files:
            st.markdown(f"""
            <div class="info-card">
                <div class="info-label">Yüklenen Görsel Sayısı</div>
                <div class="info-value">{len(uploaded_files)} dosya</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("📥 Kullanıcıyı Kaydet", key="register_user"):
            if name and uploaded_files:
                username = normalize_username(name)
                model = get_facenet_model()
                count = 0
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, file in enumerate(uploaded_files):
                    status_text.text(f"İşleniyor: {file.name}")
                    
                    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
                    if img is None:
                        st.warning(f"❌ '{file.name}' okunamadı.")
                        continue
                    
                    # Orijinal + 5 augmented version
                    for i in range(6):
                        input_img = img if i == 0 else augment(image=img)["image"]
                        embedding = get_embedding(model, input_img)
                        save_user_embedding(username, embedding)
                        count += 1
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                status_text.empty()
                progress_bar.empty()
                
                if count > 0:
                    st.success(f"✅ {username} için toplam {count} görsel (augmentasyon dahil) kaydedildi.")
                else:
                    st.error("❌ Hiçbir görsel işlenemedi.")
            else:
                st.warning("⚠️ Lütfen kullanıcı adı girin ve görsel yükleyin.")

# Sağ Kolon - Kullanıcı Yönetimi (Collapsible)
with st.container():
    with st.expander("🗑️ Kullanıcı Yönetimi", expanded=False):
        if user_list:
            st.markdown(f"""
            <div class="info-card">
                <div class="info-label">Toplam Kayıtlı Kullanıcı</div>
                <div class="info-value">{len(user_list)} kişi</div>
            </div>
            """, unsafe_allow_html=True)
            
            selected_user = st.selectbox(
                "Silmek istediğiniz kullanıcıyı seçin:", 
                user_list,
                help="Bu işlem geri alınamaz!"
            )
            
            if selected_user:
                st.markdown(f"""
                <div class="info-card">
                    <div class="info-label">Seçili Kullanıcı</div>
                    <div class="info-value">{selected_user}</div>
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Listeyi Yenile", key="refresh_users"):
                    st.rerun()
            
            with col2:
                if st.button("❌ Kullanıcıyı Sil", key="delete_user"):
                    if delete_user(selected_user):
                        st.success(f"✅ {selected_user} başarıyla silindi.")
                        st.rerun()
                    else:
                            st.error("❌ Kullanıcı silinirken hata oluştu.")
        else:
            st.markdown("""
            <div class="info-card">
                <div class="info-label">Durum</div>
                <div class="info-value">📭 Kayıtlı kullanıcı yok</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Giriş Logları - Collapsible
with st.expander("📜 Giriş Logları", expanded=False):
    if st.button("🔄 Logları Yenile", key="refresh_logs"):
        st.rerun()

    if logs:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Log İstatistikleri</div>
            <div class="info-value">
                Toplam: {len(logs)} | 
                Başarılı: <span style="color: #3fb950;">{success_count}</span> | 
                Başarısız: <span style="color: #f85149;">{failed_count}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Son 10 log göster
        recent_logs = logs[:10]  # En yeni 10 log zaten listenin başında
        
        for log in recent_logs:
            status_class = "success" if log["success"] else "failed"
            status_text = "✅ Başarılı" if log["success"] else "❌ Başarısız"
            
            st.markdown(f"""
            <div class="log-entry {status_class}">
                <div class="log-header">
                    <div class="log-user">👤 {log['username']}</div>
                    <div class="log-status {status_class}">{status_text}</div>
                </div>
                <div class="log-details">
                    <span>🕒 {log['timestamp'].strftime("%Y-%m-%d %H:%M:%S")}</span>
                    <span>🌐 {log['ip']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-card">
            <div class="info-label">Durum</div>
            <div class="info-value">📭 Henüz giriş log'u yok</div>
        </div>
        """, unsafe_allow_html=True)
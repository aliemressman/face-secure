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
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration

# Gerekli servisler
from app.face_recognition.embedding import get_embedding
from app.face_recognition.detector import FaceDetector
from app.face_recognition.matcher import find_best_match
from app.services.user_management import get_all_user_embeddings, log_login_attempt
from models.model import get_facenet_model
from app.services.voice_greeting import say

# --------------------------- Sayfa Ayarları ---------------------------
st.set_page_config(
    page_title="FaceSecure - Kullanıcı Girişi", 
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

/* Kompakt Header */
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

/* Kompakt Grid Layout */
.content-grid {
    display: grid;
    grid-template-columns: 1fr 350px;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

/* Kamera Bölümü - Sadeleştirilmiş */
.camera-section {
    background: rgba(45, 55, 72, 0.9);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
    position: relative;
}

.camera-section::before {
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

/* Info Panel - Kompakt */
.info-panel {
    background: rgba(45, 55, 72, 0.9);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
    height: fit-content;
}

.status-card {
    background: rgba(88, 166, 255, 0.1);
    border: 1px solid rgba(88, 166, 255, 0.3);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

.status-label {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 0.3rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
}

.status-value.success {
    color: #3fb950;
}

.status-value.warning {
    color: #d29922;
}

.status-value.error {
    color: #f85149;
}

/* Dinamik Tanıma Göstergesi */
.recognition-meter {
    background: rgba(26, 31, 46, 0.8);
    border-radius: 12px;
    padding: 1rem;
    margin: 1rem 0;
    border: 1px solid rgba(88, 166, 255, 0.3);
    position: relative;
    overflow: hidden;
}

.recognition-meter::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    background: linear-gradient(90deg, 
        rgba(248, 81, 73, 0.2) 0%, 
        rgba(63, 185, 80, 0.2) 50%, 
        rgba(63, 185, 80, 0.3) 100%);
    border-radius: 12px;
    transition: width 0.3s ease;
    z-index: 1;
}

.recognition-content {
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.recognition-text {
    color: #ffffff;
    font-size: 1rem;
    font-weight: 500;
    margin: 0;
}

.recognition-percentage {
    color: #58a6ff;
    font-size: 1.1rem;
    font-weight: 700;
}

.similarity-progress {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    margin-top: 0.5rem;
    overflow: hidden;
    position: relative;
}

.similarity-fill {
    height: 100%;
    background: linear-gradient(90deg, #f85149 0%, #3fb950 50%, #58a6ff 100%);
    border-radius: 4px;
    transition: width 0.5s ease;
    position: relative;
}

.similarity-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

/* Kompakt Stats */
.detection-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.8rem;
    margin-bottom: 1rem;
}

.stat-item {
    background: rgba(88, 166, 255, 0.1);
    border-radius: 8px;
    padding: 0.8rem;
    text-align: center;
    border: 1px solid rgba(88, 166, 255, 0.2);
}

.stat-number {
    font-size: 1.3rem;
    font-weight: 700;
    color: #58a6ff;
    margin-bottom: 0.2rem;
}

.stat-label {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.6);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Kompakt Butonlar */
.action-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    margin-top: 1rem;
}

.stButton {
    width: 100%;
}

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

/* Kompakt Talimatlar */
.instructions-panel {
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
    
    .camera-section, .info-panel {
        padding: 1rem;
    }
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

/* Pulse Animation for Active Recognition */
.active-recognition {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { 
        border-color: rgba(88, 166, 255, 0.3);
        box-shadow: 0 0 0 0 rgba(88, 166, 255, 0.4);
    }
    50% { 
        border-color: rgba(88, 166, 255, 0.6);
        box-shadow: 0 0 0 8px rgba(88, 166, 255, 0);
    }
}

/* Loading States */
.processing {
    position: relative;
}

.processing::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 30px;
    height: 30px;
    margin: -15px 0 0 -15px;
    border: 3px solid rgba(88, 166, 255, 0.3);
    border-radius: 50%;
    border-top-color: #58a6ff;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>
""", unsafe_allow_html=True)

# --------------------------- Global Kaynaklar ---------------------------
# @st.cache_resource(show_spinner=False)
def load_detector():
    return FaceDetector()

# @st.cache_resource(show_spinner=False)
def load_model():
    return get_facenet_model()

# @st.cache_resource(show_spinner=False)
def load_known_users():
    return get_all_user_embeddings()

DETECTOR = load_detector()
MODEL = load_model()
KNOWN_USERS = load_known_users()

# WebRTC Configuration
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

# --------------------------- Kamera Sınıfı ---------------------------
class LiveProcessor(VideoTransformerBase):
    def __init__(self):
        self.box_color = (0, 0, 255)
        self.text = "Yüz algılanıyor..."
        self.similarity = 0.0
        self.user = "Unknown"
        self.latest_frame = None
        self.face_count = 0

    def transform(self, frame):
        image = frame.to_ndarray(format="bgr24")
        boxes = DETECTOR.detect_face(image)
        self.latest_frame = frame
        self.face_count = len(boxes)

        if len(boxes) > 1:
            self.text = "⚠️ Birden fazla yüz algılandı!"
            self.box_color = (0, 255, 255)
            for (x, y, w, h) in boxes:
                cv2.rectangle(image, (x, y), (x + w, y + h), self.box_color, 2)
                cv2.putText(image, "Coklu Yuz", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.box_color, 2)
            self.user = "TooManyFaces"
            self.similarity = 0.0
            return image

        elif len(boxes) == 1:
            x, y, w, h = boxes[0]
            face_img = image[y:y + h, x:x + w]
            if face_img.size == 0:
                return image

            embedding = get_embedding(MODEL, face_img)
            matched_user, similarity = find_best_match(embedding, KNOWN_USERS, threshold=0.65)

            self.user = matched_user
            self.similarity = similarity

            self.text = f"{matched_user}" if matched_user != "Unknown" else "Taninmadi"
            
            # Benzerlik oranına göre renk
            if similarity > 0.8:
                self.box_color = (0, 255, 0)  # Yeşil - Yüksek benzerlik
            elif similarity > 0.6:
                self.box_color = (0, 200, 0)  # Açık yeşil - Orta benzerlik
            else:
                self.box_color = (0, 0, 255)  # Kırmızı - Düşük benzerlik

            # Modern çerçeve çizimi
            thickness = 2 + int(similarity * 2)  # Benzerlik arttıkça kalınlık artar
            cv2.rectangle(image, (x, y), (x + w, y + h), self.box_color, thickness)
            
            # Üst bilgi kutusu
            text_size = cv2.getTextSize(self.text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(image, (x, y - 30), (x + text_size[0] + 10, y), self.box_color, -1)
            cv2.putText(image, self.text, (x + 5, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Alt bilgi kutusu (similarity)
            similarity_text = f"{similarity:.1%}"
            cv2.putText(image, similarity_text, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.box_color, 2)
        
        else:
            self.user = "NoFace"
            self.similarity = 0.0
            self.text = "Yüz bulunamadı"

        return image

# --------------------------- Ana Arayüz ---------------------------
def show_login_ui():
    # Header
    st.markdown("""
    <div class="header-section">
        <h1 class="page-title">
            👤 Yüz Tanıma Girişi
        </h1>
        <p class="page-subtitle">Güvenli ve hızlı kimlik doğrulama sistemi</p>
    </div>
    """, unsafe_allow_html=True)

    # Ana içerik
    st.markdown('<div class="content-grid">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="camera-section">
            <h3 class="section-title">📷 Kamera Görüntüsü</h3>
        """, unsafe_allow_html=True)
        
        # WebRTC Streamer - sadece component
        ctx = webrtc_streamer(
            key="user-login", 
            video_processor_factory=LiveProcessor,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={"video": {"width": 640, "height": 480}, "audio": False},
            async_processing=True
        )
        
        if ctx.video_transformer:
            st.session_state.video_transformer = ctx.video_transformer
            # Live detection display with dynamic progress
            user = ctx.video_transformer.user
            similarity = ctx.video_transformer.similarity
            
            status_color = "success" if user not in ["Unknown", "TooManyFaces", "NoFace"] else "error"
            if user == "TooManyFaces":
                status_text = "⚠️ Çoklu yüz algılandı"
                status_color = "warning"
            elif user == "NoFace":
                status_text = "👁️ Yüz bekleniyor..."
                status_color = "warning"
            elif user == "Unknown":
                status_text = "❌ Tanınmayan kişi"
            else:
                status_text = f"✅ {user} tanındı"
            
            # Dynamic recognition meter
            meter_width = min(max(similarity * 100, 5), 100)  # Min %5, Max %100
            
            st.markdown(f"""
            <div class="recognition-meter" style="--progress-width: {meter_width}%;">
                <div class="recognition-meter::before" style="width: {meter_width}%;"></div>
                <div class="recognition-content">
                    <span class="recognition-text">{status_text}</span>
                    <span class="recognition-percentage">{similarity:.1%}</span>
                </div>
                <div class="similarity-progress">
                    <div class="similarity-fill" style="width: {meter_width}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-panel">
            <h3 class="section-title">✨ Giriş Bilgileri</h3>
        """, unsafe_allow_html=True)
        
        if ctx and ctx.video_transformer:
            user = ctx.video_transformer.user
            similarity = ctx.video_transformer.similarity
            face_count = ctx.video_transformer.face_count
            
            # Status cards
            st.markdown(f"""
            <div class="status-card">
                <div class="status-label">Kimlik Durumu</div>
                <div class="status-value {'success' if user not in ['Unknown', 'TooManyFaces', 'NoFace'] else 'error' if user in ['Unknown', 'NoFace'] else 'warning'}">
                    {user if user not in ['TooManyFaces', 'NoFace'] else 'Yüz Tespit Edilemiyor' if user == 'NoFace' else 'Birden Fazla Kişi'}
                </div>
            </div>
            
            <div class="status-card">
                <div class="status-label">Eşleşme Oranı</div>
                <div class="status-value {'success' if similarity > 0.8 else 'warning' if similarity > 0.6 else 'error'}">{similarity:.1%}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Detection stats
            st.markdown(f"""
            <div class="detection-stats">
                <div class="stat-item">
                    <div class="stat-number">{face_count}</div>
                    <div class="stat-label">Tespit Edilen</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(KNOWN_USERS)}</div>
                    <div class="stat-label">Kayıtlı Kişi</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Instructions
            st.markdown("""
            <div class="instructions-panel">
                <div class="instruction-item">
                    <div class="instruction-icon">1</div>
                    <div>Kameraya doğru bakın ve yüzünüzü net tutun</div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-icon">2</div>
                    <div>Sistem tanıyana kadar bekleyin (yeşil çerçeve)</div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-icon">3</div>
                    <div>Giriş onayı için butona tıklayın</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
            
            if st.button("🔓 Girişi Onayla", key="confirm_login"):
                if user == "TooManyFaces":
                    st.warning("⚠️ Lütfen sadece bir kişi kamerada olacak şekilde tekrar deneyin.")
                elif user == "NoFace":
                    st.warning("⚠️ Kamerada yüz algılanmadı. Lütfen kameranın karşısına geçin.")
                elif user == "Unknown" or similarity < 0.65:
                    st.error(f"❌ Giriş Reddedildi - Kimlik doğrulanamadı (Eşleşme: {similarity:.1%})")
                    log_login_attempt("Unknown", False, "127.0.0.1")
                else:
                    st.success(f"✅ Hoş Geldiniz {user}! (Eşleşme: {similarity:.1%})")
                    try:
                        say(f"Welcome {user}")
                    except:
                        pass  # Ses sistemi yoksa devam et
                    log_login_attempt(user, True, "127.0.0.1")
            
            if st.button("🔄 Yeniden Dene", key="refresh"):
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------- Çalıştır ---------------------------
show_login_ui()
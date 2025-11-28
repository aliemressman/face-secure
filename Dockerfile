# Python tabanlı bir image kullan
FROM python:3.9-slim

# Gerekli sistem paketlerini kur
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*


# Çalışma dizinini ayarla
WORKDIR /app

# Proje dosyalarını kopyala
COPY . .

# Bağımlılıkları yükle
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Streamlit portunu aç
EXPOSE 8501

# Uygulamayı başlat
CMD ["streamlit", "run", "app/interface/main_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
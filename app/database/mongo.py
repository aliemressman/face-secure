"""
MongoDB bağlantısı ve koleksiyon referansları
"""

from pymongo import MongoClient
import os

# Ortam değişkeninden Mongo URI'yi al, yoksa localhost kullan
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Bağlantıyı kur
client = MongoClient(MONGO_URI)

# Veritabanı ismi
db = client["face_secure"]

# Koleksiyonlar
users_collection = db["users"]         # Yüz verisi ve kullanıcı bilgileri
logs_collection = db["logs"]           # Giriş logları

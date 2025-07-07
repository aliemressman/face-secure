from pymongo import MongoClient
from datetime import datetime
import numpy as np

# MongoDB bağlantısı
client = MongoClient("mongodb://localhost:27017/")
db = client["face_secure"]
users_collection = db["users"]
logs_collection = db["logs"]

# Dummy embedding (örnek 128 boyutlu rastgele veri)
dummy_embedding = np.random.rand(128).tolist()

# Kullanıcı verisi ekle
users_collection.replace_one(
    {
        "username": "ferhat",
        "embedding": dummy_embedding,
        "created_at": datetime.now()
    },
    upsert=True
)

# Log örneği ekle
logs_collection.insert_one({
    "username": "etem",
    "success": True,
    "ip": "127.0.0.1",
    "timestamp": datetime.now()
})

print("✅ Test verileri başarıyla eklendi.")

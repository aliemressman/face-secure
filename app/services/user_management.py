"""
Kullanıcı yönetimi ve giriş loglama işlemleri
"""

from datetime import datetime
from app.database.mongo import users_collection, logs_collection

# ---------------- Kullanıcı EMBEDDING KAYIT ----------------

def save_user_embedding(username: str, new_embedding: list):
    """
    Kullanıcının embedding bilgisini kaydeder.
    Aynı kullanıcı varsa 'embeddings' listesine eklenir,
    yoksa yeni kullanıcı olarak eklenir.
    """
    user = users_collection.find_one({"username": username})
    if user:
        users_collection.update_one(
            {"username": username},
            {"$push": {"embeddings": new_embedding}}
        )
    else:
        users_collection.insert_one({
            "username": username,
            "embeddings": [new_embedding],
            "created_at": datetime.now()
        })


# ---------------- KULLANICILARI GETİR ----------------

def get_all_user_embeddings():
    """
    Tüm kullanıcı embeddinglerini döner.
    """
    return list(users_collection.find({}, {"_id": 0, "username": 1, "embeddings": 1}))


def get_usernames():
    """
    Sadece kullanıcı isimlerini liste olarak döner.
    """
    return [doc["username"] for doc in users_collection.find({}, {"_id": 0, "username": 1})]


# ---------------- KULLANICI SİLME ----------------

def delete_user(username: str):
    """
    Belirli bir kullanıcıyı siler. Başarıyla silinirse True döner.
    """
    result = users_collection.delete_one({"username": username})
    return result.deleted_count > 0


# ---------------- GİRİŞ LOG'LAMASI ----------------

def log_login_attempt(username: str, success: bool, ip_address: str):
    """
    Giriş denemesi loglanır. Başarılı/başarısız ayrımı yapılır.
    """
    logs_collection.insert_one({
        "username": username,
        "success": success,
        "ip": ip_address,
        "timestamp": datetime.now()
    })


def get_all_logs():
    """
    Giriş loglarını (en son giriş en üstte olacak şekilde) döner.
    """
    return list(
        logs_collection.find({}, {"_id": 0}).sort("timestamp", -1)
    )
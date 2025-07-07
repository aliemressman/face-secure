"""
Karşılaştırma (Kosinus Karsilastirmasi)
"""

from numpy import dot # İki vektörün noktasal çarpımını (dot product) alır.
from numpy.linalg import norm # Bir vektörün uzunluğunu (vektör normu) hesaplar.

def cosine_similarity(a, b):
    """İki embedding arasındaki benzerliği hesaplar"""
    return dot(a,b) / (norm(a) * norm(b))

    
def find_best_match(embedding, known_users, threshold=0.65):
    best_user = "Unknown"
    best_score = -1

    for user in known_users:
        embeddings = user.get("embeddings", [])  # 👈 Doğru olan bu
        for emb in embeddings:
            similarity = cosine_similarity(embedding, emb)
            if similarity >= threshold and similarity > best_score:
                best_score = similarity
                best_user = user["username"]

    return best_user, best_score

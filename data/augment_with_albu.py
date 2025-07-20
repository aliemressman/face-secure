import os
import cv2
import albumentations as A

# === Klasör Ayarları ===
INPUT_FOLDER = "C:/Users/aliem/Documents/Face Secure/data/images"               # Orijinal yüz görselleri
OUTPUT_FOLDER = "C:/Users/aliem/Documents/Face Secure/data/images_augmented"     # Yeni üretilecek varyasyonlar
AUG_PER_IMAGE = 5                           # Her görselden kaç tane?

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Albumentations pipeline (dönüşümler) ===
transform = A.Compose([
    A.HorizontalFlip(p=0.5),                     # Aynalama
    A.RandomBrightnessContrast(p=0.5),           # Işık ve kontrast
    A.Rotate(limit=15, p=0.7),                   # Açısal dönüş
    A.GaussNoise(var_limit=(10, 30), p=0.4),     # Gürültü
    A.Blur(blur_limit=3, p=0.3),                 # Bulanıklık
])

# === Tüm görselleri işle ===
for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(INPUT_FOLDER, filename)
        image = cv2.imread(img_path)
        if image is None:
            print(f"[!] Görsel açılamadı: {filename}")
            continue

        name, ext = os.path.splitext(filename)
        for i in range(AUG_PER_IMAGE):
            augmented = transform(image=image)['image']
            new_name = f"{name}{i+1}{ext}"
            new_path = os.path.join(OUTPUT_FOLDER, new_name)
            cv2.imwrite(new_path, augmented)

        print(f"[✓] {filename} için {AUG_PER_IMAGE} varyasyon üretildi.")

print("\n✅ Tüm veri artırımı tamamlandı.")

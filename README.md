# 🚀 FaceSecure – Kolay Kurulum ve Çalıştırma Rehberi

FaceSecure, Docker ile paketlenmiş bir yüz tanıma tabanlı güvenlik uygulamasıdır.
Kurulum için yalnızca 2 komut çalıştırmanız yeterlidir — herhangi bir ek yazılım kurmanız gerekmez.

## ✅ 1. Gereksinimler
Uygulamayı çalıştırmak için bilgisayarınızda Docker Desktop kurulu olmalıdır.

👉 İndirme: https://www.docker.com/products/docker-desktop/
Kurulumdan sonra Docker Desktop’ı açın ve çalışır durumda olduğundan emin olun.

## ✅ 2. Proje Dosyalarını Hazırlayın
Size verilen proje klasörünü (örneğin: Face Secure) bilgisayarınıza çıkarın.
Klasör içinde şu dosyalar bulunmalıdır:

Dockerfile
docker-compose.yml
requirements.txt
app/
.env
data/   (varsa)

## 📌 .env Dosyası
Bu dosya projeye dahil edilmiştir ve düzenlemenize gerek yoktur:

ADMIN_USERNAME = admin 
ADMIN_PASSWORD_HASH = $2b$12$4eBAikPrNgNacj1NeH9TPOXKrZMdY58zIqjW9yG6GM8HstROzFVI2
MONGO_URI = mongodb://localhost:27017/

## ✅ 3. Proje Klasörüne Girin

Terminal veya PowerShell açıp proje klasörüne geçin:
cd "Face Secure"
Klasör adında boşluk olduğu için tırnak içinde yazıyoruz.

## ✅ 4. Docker Image Oluşturun

Aşağıdaki komutu çalıştırın:
docker compose build --no-cache

Bu işlem:
Python ortamını kurar
Gerekli kütüphaneleri yükler
Uygulamayı Docker içine aktarır
İlk seferde 1–5 dakika sürebilir.

## ✅ 5. Uygulamayı Başlatın

docker compose up -d
Bu komut:
Konteyneri başlatır
Uygulamayı otomatik olarak 8501 portuna yönlendirir

## ✅ 6. Tarayıcıdan Uygulamaya Girin

Tarayıcıya şu adresi yazın:

👉 http://localhost:8501

🔐 Admin Girişi

Admin paneline erişmek için: 

Kullanıcı adı : admin
Parola : admin

📷 Kamera Çalışmazsa

Tarayıcı kamera izni istemiş olabilir.
Tarayıcı adres çubuğundaki kamera ikonuna tıklayıp:
İzin ver → Kamera
seçeneğini aktif edin.

🛑 Uygulamayı Durdurmak İçin
docker compose down


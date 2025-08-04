# 🐳 FAZ3.x DOCKER KURULUM VE KULLANIM REHBERİ

## 📋 Docker Desktop ile Kurulum ve Görüntüleme

### 1. 🚀 HIZLI BAŞLANGIÇ

#### Docker Desktop Üzerinden:
1. **Docker Desktop'ı açın**
2. **Images** sekmesine gidin
3. **Build** butonuna tıklayın
4. Bu klasörü seçin: `/Users/kaan/Desktop/Blackjack/V3_0`
5. **Build** butonuna tıklayın

#### Terminal'den Hızlı Kurulum:
```bash
# Development ortamını başlat
docker-compose -f docker-compose-dev.yml up -d

# Veya production ortamı için
docker-compose up -d
```

### 2. 📊 GÖRÜNTÜLEME ARAÇLARI

#### Web Arayüzleri (Docker çalıştırıldıktan sonra):
- **Jupyter Lab:** http://localhost:8888 (AI geliştirme)
- **TensorBoard:** http://localhost:6006 (Model görselleştirme)
- **Grafana:** http://localhost:3000 (Performans monitörü)
- **Dash Dashboard:** http://localhost:8050 (Real-time analitik)

#### Docker Desktop'ta Görüntüleme:
1. **Containers** sekmesinde aktif servisler
2. **Logs** sekmesinde real-time loglar
3. **Stats** sekmesinde kaynak kullanımı

### 3. 🔧 DOCKER MANAGER KULLANIMI

```bash
# Sistem durumunu kontrol et
python scripts/docker_manager.py status

# Ortamı başlat
python scripts/docker_manager.py start dev

# Sağlık kontrolü
python scripts/docker_manager.py health

# Logları görüntüle
python scripts/docker_manager.py logs

# Ortamı durdur
python scripts/docker_manager.py stop
```

### 4. 🎯 ORTAM TÜRLERİ

#### Development Ortamı:
```bash
docker-compose -f docker-compose-dev.yml up -d
```
**İçerir:** Jupyter, TensorBoard, Grafana, PostgreSQL, Redis

#### Production Ortamı:
```bash
docker-compose up -d
```
**İçerir:** AI Training, Model Serving, Monitoring

### 5. 📈 MONİTÖRİNG VE ANALİTİK

#### TensorBoard (Model Eğitimi):
- http://localhost:6006
- Model loss grafikleri
- Training metrikleri
- Hyperparameter tuning

#### Grafana Dashboard:
- http://localhost:3000
- Login: admin/admin
- Real-time performans
- Resource utilization

#### Jupyter Lab (Geliştirme):
- http://localhost:8888
- Token: `blackjack-dev-token`
- Interactive development
- Model experimentation

### 6. 🗂️ DOCKER VOLUME YÖNETİMİ

```bash
# Model checkpoints
docker volume ls | grep blackjack

# Backup model
docker run --rm -v blackjack_models:/backup alpine tar czf - /backup

# Restore model
docker run --rm -v blackjack_models:/restore alpine tar xzf - -C /restore
```

### 7. 🔍 TROUBLESHOOTING

#### Container Durumu Kontrolü:
```bash
docker ps -a | grep blackjack
```

#### Log İnceleme:
```bash
docker logs blackjack-ai-dev
```

#### Resource Kullanımı:
```bash
docker stats blackjack-ai-dev
```

#### Container İçine Giriş:
```bash
docker exec -it blackjack-ai-dev /bin/bash
```

### 8. 🎮 HIZLI TEST KOMUTLARI

```bash
# AI modelini test et
docker exec blackjack-ai-dev python test_f3_integration.py

# Kritik testleri çalıştır
docker exec blackjack-ai-dev python faz3_kritik_sorunlar_cozum_plani.py

# Performance analizi
docker exec blackjack-ai-dev python comprehensive_ai_analysis.py
```

### 9. 📊 DOCKER DESKTOP'TA GÖRÜNTÜLEME

#### Images Sekmesi:
- `blackjack-ai:latest` - Ana imaj
- Boyut: ~2.5GB
- Build durumu ve tarih

#### Containers Sekmesi:
- `blackjack-ai-dev` - Development container
- `blackjack-postgres` - Database
- `blackjack-redis` - Cache
- `blackjack-grafana` - Monitoring

#### Volumes Sekmesi:
- `blackjack_models` - AI model storage
- `blackjack_data` - Training data
- `blackjack_logs` - Application logs

### 10. 🚀 PRODUCTION DEPLOYMENT

```bash
# Production build
docker build -t blackjack-ai:prod .

# Scaled deployment
docker-compose up -d --scale ai-worker=3

# Health check
curl http://localhost:8080/health
```

### 11. 📱 MOBILE MONITORING

#### Docker Desktop Mobile App:
- iOS/Android uygulaması ile remote monitoring
- Container status
- Resource alerts
- Quick actions

### 12. 🔐 SECURITY & BACKUP

```bash
# Backup tüm sistem
docker-compose down
docker save blackjack-ai:latest | gzip > blackjack-backup.tar.gz

# Restore
gunzip -c blackjack-backup.tar.gz | docker load
```

## 🎯 ÖNERİLEN İŞ AKIŞI

1. **Docker Desktop'ı aç**
2. **Development ortamını başlat:** `docker-compose -f docker-compose-dev.yml up -d`
3. **Jupyter Lab'ı aç:** http://localhost:8888
4. **TensorBoard'u izle:** http://localhost:6006
5. **Testleri çalıştır:** Docker Manager ile
6. **Sonuçları Grafana'da gör:** http://localhost:3000

## 🆘 DESTEK

Herhangi bir sorun yaşarsanız:
```bash
python scripts/docker_manager.py health
python scripts/docker_manager.py logs
```

Bu komutlar detaylı durum raporu verecektir. 
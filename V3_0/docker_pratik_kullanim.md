# 🐳 DOCKER İMAJI PRATİK KULLANIM

## ✅ **MEVCUT DURUM**
- ✅ Docker imajı hazır: `blackjack-ai:latest` (2.98GB)
- ✅ Tüm Faz3.x geliştirmeleri dahil
- ✅ AI modelleri ve araçlar entegre

## 🚀 **HEMEN YAPILABILECEKLER**

### 1. **DOCKER DESKTOP'TA GÖRÜNTÜLEYİN**

Docker Desktop uygulamasını açıp şunları görebilirsiniz:

**Images sekmesi:**
- `blackjack-ai:latest` (2.98GB)
- Build tarihi: Az önce
- Tüm layers'lar ve boyutlar

**İşlemler:**
- ▶️ **Run** butonuna tıklayın
- Port ayarları: `8888:8888, 6006:6006, 8050:8050`
- **Start** butonuna basın

### 2. **TEK KOMUTLA ÇALIŞTIRIN**

Terminal'de:

```bash
# Basit başlatma
docker run -it --rm -p 8888:8888 blackjack-ai:latest bash

# Sonra container içinde:
cd /app
python test_f3_integration.py
```

### 3. **DOCKER DESKTOP ÜZERİNDEN ÇALIŞTIRIN**

1. **Docker Desktop** açın
2. **Images** → `blackjack-ai:latest`
3. **Run** butonuna tıklayın
4. **Optional settings** kısmında:
   - **Container name:** `blackjack-ai-test`
   - **Ports:** `8888:8888`
5. **Run** butonuna basın
6. **Containers** sekmesinde container'ı göreceksiniz
7. **Terminal** ikonuna tıklayın

### 4. **ANALİZ VE TESTLER**

Container çalıştıktan sonra:

```bash
# F3.x entegrasyon testleri
python test_f3_integration.py

# Kritik sorunlar çözümü
python faz3_kritik_sorunlar_cozum_plani.py

# AI analizi
python comprehensive_ai_analysis.py

# Model eğitimi
python scripts/train_play_agent.py
```

### 5. **WEB ARAYÜZLERE ERİŞİM**

Container çalıştıktan sonra:

- **Jupyter Notebook:** http://localhost:8888
- **TensorBoard:** http://localhost:6006
- **AI Dashboard:** http://localhost:8050

### 6. **VERİ VE SONUÇLARI GETİRİN**

```bash
# Container'dan dosyaları kopyalayın
docker cp container_name:/app/runs ./runs_backup
docker cp container_name:/app/models ./models_backup
```

### 7. **DOCKER COMPOSE ALTERNATİFİ**

Eğer compose kullanmak isterseniz:

```bash
# Sadece AI servisi
docker run -d --name blackjack-ai \
  -p 8888:8888 -p 6006:6006 \
  blackjack-ai:latest python -m jupyter lab \
  --ip=0.0.0.0 --allow-root --no-browser
```

### 8. **HIZLI PROBLEM ÇÖZME**

```bash
# Container durumu
docker ps -a

# Logları görüntüle
docker logs container_name

# Container'ı yeniden başlat
docker restart container_name

# Container temizle
docker rm -f container_name
```

## 🎯 **ÖNERİLEN BAŞLANGIÇ**

**EN KOLAY YOL:**

1. **Docker Desktop açın**
2. **Images** → `blackjack-ai:latest` → **Run**
3. **Ports:** `8888:8888` ekleyin
4. **Run** basın
5. **Containers** → **Terminal** açın
6. **Test çalıştırın:** `python test_f3_integration.py`

**Terminal YOL:**

```bash
docker run -it --rm -p 8888:8888 blackjack-ai:latest bash
```

## 📊 **NELERİ GÖREBİLİRSİNİZ**

- ✅ Faz3.x test sonuçları
- ✅ AI model performansı  
- ✅ Adaptasyon algoritması sonuçları
- ✅ HPC altyapı durumu
- ✅ Player profiling accuracy
- ✅ Comprehensive analysis raporları
- ✅ Model eğitim grafikleri
- ✅ Real-time blackjack simulations

---

**🎉 SONUÇ:** Docker imajınız hazır ve çalışır durumda. Tek tıkla veya tek komutla tüm Faz3.x sistemini test edebilir ve geliştirebilirsiniz! 
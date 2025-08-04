# 🚀 DOCKER İMAJI HIZLI KULLANIM REHBERİ

## ✅ **HAZIR DOCKER İMAJI: blackjack-ai:latest (2.98GB)**

### 1. 🎯 **TEK KOMUTLA BAŞLATABİLİRSİNİZ**

```bash
# AI Container'ını çalıştır
docker run -it --name blackjack-ai-container \
  -p 8888:8888 -p 6006:6006 -p 8050:8050 \
  -v $(pwd):/app/workspace \
  blackjack-ai:latest
```

**Bu size verir:**
- ✅ Jupyter Lab (http://localhost:8888)
- ✅ TensorBoard (http://localhost:6006)  
- ✅ Dash Dashboard (http://localhost:8050)
- ✅ Tüm AI modelleri ve araçları

### 2. 🧪 **HIZLI TESTLERİ ÇALIŞTIRABİLİRSİNİZ**

```bash
# Container içinde testleri çalıştır
docker exec -it blackjack-ai-container python test_f3_integration.py

# Kritik sorunları çöz
docker exec -it blackjack-ai-container python faz3_kritik_sorunlar_cozum_plani.py

# AI performansını analiz et
docker exec -it blackjack-ai-container python comprehensive_ai_analysis.py
```

### 3. 📊 **DOCKER DESKTOP'TA GÖRÜNTÜLEYEBİLİRSİNİZ**

**Docker Desktop'ı açın ve şunları görebilirsiniz:**

1. **Images sekmesi:**
   - `blackjack-ai:latest` (2.98GB)
   - Build tarihi ve detayları

2. **Containers sekmesi:**
   - Container durumu (Running/Stopped)
   - Real-time loglar
   - Resource kullanımı

3. **Quick Actions:**
   - ▶️ Start/Stop container
   - 📋 View logs
   - 💻 Open terminal
   - 🔍 Inspect

### 4. 🎮 **İNTERAKTİF KULLANIM**

```bash
# Container'a bağlan
docker exec -it blackjack-ai-container bash

# Jupyter Lab başlat
jupyter lab --ip=0.0.0.0 --allow-root --no-browser

# Model eğit
python scripts/train_play_agent.py

# Sonuçları analiz et
python scripts/visualize_policy.py
```

### 5. 🔧 **DOCKER MANAGER İLE YÖNETİM**

```bash
# Sistem durumu
python scripts/docker_manager.py status

# Container başlat
python scripts/docker_manager.py start

# Sağlık kontrolü
python scripts/docker_manager.py health

# Logları görüntüle
python scripts/docker_manager.py logs
```

### 6. 💾 **VERİ YEDEKLEMESİ**

```bash
# Model checkpoints'leri yedekle
docker cp blackjack-ai-container:/app/models ./backup_models

# Tüm sonuçları yedekle
docker cp blackjack-ai-container:/app/runs ./backup_runs

# Container'ı imaj olarak kaydet
docker commit blackjack-ai-container blackjack-ai:backup
```

### 7. 🌐 **WEB ARAYÜZLER**

Container çalıştıktan sonra şu adreslere gidebilirsiniz:

- **Jupyter Lab:** http://localhost:8888
  - Token: `blackjack-dev-token`
  - AI model geliştirme
  - Interaktif analiz

- **TensorBoard:** http://localhost:6006
  - Model eğitim grafikleri
  - Loss/reward curves
  - Hyperparameter tracking

- **Dash Dashboard:** http://localhost:8050
  - Real-time performans
  - AI strategi görselleştirme
  - Live blackjack simulation

### 8. 🎯 **ÖNERİLEN İŞ AKIŞI**

```bash
# 1. Container'ı başlat
docker run -d --name blackjack-ai \
  -p 8888:8888 -p 6006:6006 -p 8050:8050 \
  blackjack-ai:latest

# 2. Web arayüzleri aç
open http://localhost:8888  # Jupyter
open http://localhost:6006  # TensorBoard
open http://localhost:8050  # Dashboard

# 3. Testleri çalıştır
docker exec blackjack-ai python test_f3_integration.py

# 4. AI'yı eğit
docker exec blackjack-ai python scripts/train_play_agent.py

# 5. Sonuçları analiz et
docker exec blackjack-ai python comprehensive_ai_analysis.py
```

### 9. 🔍 **TROUBLESHOOTING**

```bash
# Container durumu
docker ps -a | grep blackjack

# Container logları
docker logs blackjack-ai

# Resource kullanımı
docker stats blackjack-ai

# Container restart
docker restart blackjack-ai

# Container temizle
docker rm -f blackjack-ai
```

### 10. 🚀 **PRODUCTION READY**

```bash
# Production modunda çalıştır
docker run -d --name blackjack-ai-prod \
  --restart=always \
  -p 8080:8080 \
  -e ENV=production \
  blackjack-ai:latest

# Auto-scaling için
docker-compose up -d --scale ai-worker=3

# Health check
curl http://localhost:8080/health
```

---

## 🎉 **ÖZET**

✅ **Hazır AI sistemi:** blackjack-ai:latest (2.98GB)
✅ **Web arayüzleri:** Jupyter, TensorBoard, Dashboard
✅ **Kolay yönetim:** Docker Desktop + komutlar
✅ **Production ready:** Auto-scaling + monitoring
✅ **Tam entegre:** Tüm Faz3.x geliştirmeleri dahil

**Tek komutla başlayın:**
```bash
docker run -it -p 8888:8888 -p 6006:6006 -p 8050:8050 blackjack-ai:latest
``` 
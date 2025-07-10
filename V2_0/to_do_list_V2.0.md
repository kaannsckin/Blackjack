# Blackjack Simülasyonu - To Do List

## 1. Kod Refactoring ve Temizlik

- [ ] Magic numbers yerine sabit (constant) değişkenler kullan
    - Ör. BLACKJACK = 21, DEALER_STAND_SOFT = 17
- [ ] print() yerine logging modülünü entegre et
- [ ] El değerleme ve yüzde hesaplama hatasını düzelt
    - int/int bölmesinden kaynaklanan hataları kontrol et
- [ ] Kodda tekrar eden blokları fonksiyonlaştır (ör. action seçimleri için dictionary dispatch)
- [ ] Penetration kontrolünü koda ekle
    - Örn. deste bitişine yaklaşınca reshuffle tetikle

---

## 2. Kart Sayma Sistemi Entegrasyonu

- [ ] Kart sayma sistemi için CardCounter class’ını oluştur
    - Running Count hesapla
    - True Count hesapla
- [ ] Hi-Lo sistemi değer tablolarını ekle
    - Kartlara değer (+1, 0, -1) ataması yap
- [ ] Omega II ve Wong Halves sistemlerini ileride eklenebilir şekilde tasarla (opsiyonel)

---

## 3. Bahis Stratejisi Entegrasyonu

- [ ] True Count’a göre bahis spread fonksiyonunu yaz
    - TC ≤ 1 → min bet
    - TC = 2 → 2× bet
    - TC = 3 → 4× bet
    - TC ≥ 4 → 6-8× bet
- [ ] Kelly Criterion bazlı bahis fonksiyonunu ekle (opsiyonel)

---

## 4. Temel Strateji ve Deviation Logic

- [ ] Temel strateji tablosunu modül olarak oluştur
- [ ] Deviations (Index Plays) için kontrol mekanizması ekle
    - Ör. 16 vs 10 → Stand (TC ≥ 0)
- [ ] Deviation logic’ini ayrı bir fonksiyon içinde tut

---

## 5. Simülasyon Senaryolarını Tasarla

- [ ] Simülasyon parametre kombinasyonlarını belirle:
    - Deste sayısı: 1, 2, 6, 8
    - Dealer rule: S17, H17
    - Penetration: %50, %65, %75
    - DAS: var/yok
    - Surrender: var/yok
- [ ] itertools.product kullanarak tüm senaryoları oluştur
- [ ] Simülasyonu parametre bazlı çalıştıracak fonksiyon yaz

---
| No | Özellik | Detay |
|----|---------|--------|
| 1 | RTP & EV | `win_rate_pN`, `ev_pN`, `rtp_pN` sütunları - her oyuncu için ayrı. |
| 2 | Çok-oyunculu destek | Sütun adları otomatik `p1`, `p2`, ... ; hesaplama döngüsel. |
| 3 | DB kaydı | `--db sqlite:///results.db` (veya herhangi bir SQLAlchemy URL) ile `scenario_results` tablosuna `to_sql()` append. |

python batch_simulation.py \
  --hands 20000 \
  --db sqlite:///results.db \
  --csv scenario_results.csv



## 6. İstatistiksel Ölçümler ve Raporlama

- [ ] RTP (Return To Player) hesaplamasını ekle
- [ ] Toplam kazanç/kayıp ölçümlerini tut
- [ ] Ortalama kar/zarar (per session) hesapla
- [ ] Risk of Ruin (RoR) hesaplaması ekle (opsiyonel)
- [ ] Volatilite (standart sapma) hesapla
- [ ] Max Drawdown ölçümü ekle
- [ ] Sonuçları pandas DataFrame’e kaydet ve raporla

---

## 7. Test ve Validasyon

- [ ] Küçük test simülasyonları ile sistemin stabil çalıştığını doğrula
- [ ] Yüzdelik hatasının düzeldiğini test et
- [ ] Penetration kontrolünün doğru çalıştığını test et
- [ ] Kart sayma ve bahis spread entegrasyonunu test et
- [ ] Farklı stratejilerle uzun vadeli simülasyonlar yap

---

## 8. İleri Düzey Geliştirmeler (Opsiyonel)

- [ ] GUI veya web arayüzü ile görselleştirme (Streamlit, Dash vb.)
- [ ] Simülasyon hızlandırma (multiprocessing)
- [ ] Daha karmaşık kart sayma sistemlerini ekle
- [ ] Session bazlı sonuç raporlaması





| Dosya                     | Ana Rol                           | Önemli Sınıf/Fonksiyonlar                                                        |
| ------------------------- | --------------------------------- | -------------------------------------------------------------------------------- |
| **`basic_strategy.py`**   | JSON’suz temel strateji kuralları | `BasicStrategy.action()` – hard/soft/split karar ağacı.                          |
| **`counting_systems.py`** | Kart sayma modelleri              | `CardCounter` (running/true count).                                              |
| **`deviations.py`**       | Index-play (sapma) kuralları      | `DeviationRule`, `DeviationEngine`, `load_index_plays()`.                        |
| **`counting.py`**         | Strateji motoru                   | `StrategyEngine` – basic + deviation + Hi-Lo entegrasyonu.                       |
| **`betting.py`**          | Bahis algoritmaları               | `BETTING_FUNCTIONS` – “flat”, “spread”, “kelly”.                                 |
| **`blackjack_engine.py`** | Oyun mekaniği                     | `Card`, `Deck`, `Hand`, `Player`, `Dealer`, `BlackjackGame`.                     |
| **`simulation.py`**       | Çoklu tur simülatörü              | `BlackjackSimulation` ve opsiyonel `TestSimulation` – sonuçları toplar, özetler. |

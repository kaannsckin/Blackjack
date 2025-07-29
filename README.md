# 🎰 Blackjack AI - Reinforcement Learning Project

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange.svg)]()

---

## 🇹🇷 Türkçe

### 📋 Proje Hakkında

Bu proje, **belirsiz gelecek içeren süreçlerde risk değerlendirmesi ve bütçe optimizasyonu yapabilen evrensel bir AI asistan** geliştirmeyi amaçlamaktadır. Blackjack oyunu, bu AI asistanın yeteneklerini test etmek ve geliştirmek için kullanılan ideal bir test ortamıdır.

#### 🎯 Ana Vizyon

**Evrensel Risk-Bütçe AI Asistanı:**
- **Stokastik Süreç Analizi**: Belirsiz gelecek içeren herhangi bir süreçte risk değerlendirmesi
- **Dinamik Bütçe Optimizasyonu**: Risk seviyesine göre kaynak dağılımı ve bütçe yönetimi
- **Adaptif Karar Verme**: Çevre değişikliklerine göre strateji güncelleme
- **Gerçek Zamanlı Öğrenme**: Sürekli deneyim birikimi ile performans iyileştirme

**Blackjack Test Ortamı:**
- **Kontrol Edilebilir Belirsizlik**: Kart dağılımı ile simüle edilen gerçek dünya belirsizlikleri
- **Çoklu Risk Faktörleri**: Oyuncu eli, dealer kartı, kart sayımı, masa dinamikleri
- **Anında Geri Bildirim**: Her hamle sonrası kazanç/kayıp ile öğrenme
- **Portfolio Yönetimi**: Çoklu el ve split durumlarında bütçe dağılımı

#### 🧠 AI Asistanın Öğrenme Süreci

Bu AI asistan, herhangi bir stokastik süreçte risk değerlendirmesi ve bütçe optimizasyonu yapmayı öğrenir:

1. **Durum Analizi**: Mevcut durumun tüm faktörlerini değerlendirme
2. **Risk Hesaplama**: Belirsizlik seviyesini ve potansiyel riskleri hesaplama
3. **Bütçe Optimizasyonu**: Risk seviyesine göre optimal kaynak dağılımı
4. **Aksiyon Seçimi**: Risk-bütçe dengesine göre en uygun kararı verme
5. **Sürekli Öğrenme**: Her deneyimden öğrenerek stratejiyi güncelleme

#### 🌍 Gerçek Dünya Uygulama Alanları

Bu AI asistan, Blackjack test ortamında geliştirilen yeteneklerle şu alanlarda uygulanabilir:

**Finansal Sektör:**
- **Portfolio Yönetimi**: Risk-bazlı varlık dağılımı
- **Trading Stratejileri**: Dinamik risk yönetimi ile alım-satım kararları
- **Kredi Risk Analizi**: Borçluluk riski değerlendirmesi

**İşletme Yönetimi:**
- **Proje Yönetimi**: Belirsizlik altında kaynak optimizasyonu
- **Tedarik Zinciri**: Stokastik talep altında envanter yönetimi
- **Pazarlama Stratejileri**: Dinamik pazar koşullarında bütçe dağılımı

**Sağlık Sektörü:**
- **Tedavi Planlaması**: Risk-bazlı tedavi stratejileri
- **Kaynak Dağılımı**: Hastane kaynaklarının optimizasyonu

**Enerji Sektörü:**
- **Enerji Trading**: Dinamik fiyat ortamında risk yönetimi
- **Grid Yönetimi**: Belirsiz talep altında enerji dağılımı

#### 🎰 Blackjack Test Ortamının Avantajları

Blackjack, AI asistanın yeteneklerini test etmek için ideal bir ortam sağlar:
- **Kontrol Edilebilir Belirsizlik**: Kart dağılımı ile simüle edilen gerçek dünya belirsizlikleri
- **Çoklu Risk Faktörleri**: Oyuncu eli, dealer kartı, kart sayımı, masa dinamikleri
- **Anında Geri Bildirim**: Her hamle sonrası kazanç/kayıp ile öğrenme
- **Portfolio Yönetimi**: Çoklu el ve split durumlarında bütçe dağılımı

### 🎯 Ana Özellikler

- **Reinforcement Learning**: DQN (Deep Q-Network) tabanlı AI eğitimi
- **Temel Strateji Entegrasyonu**: Klasik blackjack stratejileri ile karşılaştırma
- **Hiperparametre Optimizasyonu**: Optuna ile otomatik parametre ayarlama
- **Performans Analizi**: Kapsamlı metrikler ve görselleştirmeler
- **Çok Oyunculu Destek**: Dinamik masa ortamları (FAZ 4.0)
- **Gerçek Zamanlı Takip**: Weights & Biases entegrasyonu

### 🏗️ Proje Yapısı

```
Blackjack/
├── V3_0/                          # Ana proje dizini
│   ├── rl_environment.py          # RL ortamı
│   ├── utils/                     # Yardımcı modüller
│   │   ├── ai_strategy.py        # AI strateji sınıfları
│   │   ├── basic_strategy.py     # Temel blackjack stratejisi
│   │   ├── performance_metrics.py # Performans ölçümleri
│   │   └── tracking.py           # W&B entegrasyonu
│   ├── scripts/                   # Eğitim ve değerlendirme scriptleri
│   │   ├── train_play_agent.py   # AI eğitimi
│   │   ├── evaluate_play_agent.py # Model değerlendirme
│   │   ├── optimize_hyperparameters.py # HPO
│   │   └── visualize_policy.py   # Politika görselleştirme
│   ├── config/                    # Konfigürasyon dosyaları
│   ├── tests/                     # Test dosyaları
│   └── reports/                   # Raporlar ve analizler
├── V2_0/                          # Önceki versiyon
└── V1.0/                          # İlk versiyon
```

### 🚀 Kurulum

1. **Gereksinimleri Yükleyin:**
```bash
cd V3_0
pip install -r requirements.txt
```

2. **Ortamı Hazırlayın:**
```bash
# Weights & Biases kurulumu (opsiyonel)
wandb login
```

### 📊 Kullanım

#### 1. AI Eğitimi
```bash
cd V3_0
python scripts/train_play_agent.py
```

#### 2. Model Değerlendirme
```bash
python scripts/evaluate_play_agent.py --model-path runs/phase1/models/final_model.zip
```

#### 3. Hiperparametre Optimizasyonu
```bash
python scripts/optimize_hyperparameters.py
```

#### 4. Politika Görselleştirme
```bash
python scripts/visualize_policy.py --model-path runs/phase1/models/final_model.zip
```

### 🎮 Oyun Özellikleri

- **Kart Sayımı**: Hi-Lo sistemi ile gerçek zamanlı sayım
- **Split Desteği**: Çoklu el yönetimi
- **Double Down**: Uygun durumlarda çift bahis
- **Dealer Kuralları**: S17/H17 desteği
- **Çoklu Destek**: 1-8 deste desteği

### 📈 Performans Metrikleri

- **Win Rate**: Kazanma oranı
- **Expected Value**: Beklenen değer
- **Risk Metrics**: Risk ölçümleri
- **Strategy Comparison**: Temel strateji ile karşılaştırma

### 🔬 Gelişmiş Özellikler

#### FAZ 4.0 - Çok Oyunculu Dinamik AI
- **Oyuncu Davranış Analizi**: Conservative, Aggressive, Basic Strategy, Card Counter, Random, Superstitious
- **Real-time Classification**: Gerçek zamanlı oyuncu kategorizasyonu
- **Adaptive Strategy**: Dinamik strateji değişimi
- **Multi-Player Environment**: Çoklu oyuncu desteği

### 📝 Raporlar

Proje kapsamında oluşturulan raporlar:
- `reports/phase_1_final_report.md`: FAZ 1 sonuçları
- `reports/engine_validation.md`: Motor doğrulama raporu
- `runs/integration_test/`: Entegrasyon test sonuçları

---

## 🇺🇸 English

### 📋 About the Project

This project aims to develop a **universal AI assistant capable of risk assessment and budget optimization in processes containing uncertain futures**. The Blackjack game serves as an ideal test environment to develop and test this AI assistant's capabilities.

#### 🎯 Main Vision

**Universal Risk-Budget AI Assistant:**
- **Stochastic Process Analysis**: Risk assessment in any process containing uncertain futures
- **Dynamic Budget Optimization**: Resource allocation and budget management based on risk level
- **Adaptive Decision Making**: Strategy updates based on environmental changes
- **Real-time Learning**: Performance improvement through continuous experience accumulation

**Blackjack Test Environment:**
- **Controllable Uncertainty**: Real-world uncertainties simulated through card distribution
- **Multiple Risk Factors**: Player hand, dealer card, card count, table dynamics
- **Instant Feedback**: Learning through gain/loss after each move
- **Portfolio Management**: Budget allocation in multiple hands and split situations

#### 🧠 AI Assistant Learning Process

This AI assistant learns to perform risk assessment and budget optimization in any stochastic process:

1. **State Analysis**: Evaluating all factors of the current situation
2. **Risk Calculation**: Calculating uncertainty level and potential risks
3. **Budget Optimization**: Optimal resource allocation based on risk level
4. **Action Selection**: Making the most appropriate decision based on risk-budget balance
5. **Continuous Learning**: Updating strategy by learning from each experience

#### 🌍 Real-World Application Areas

This AI assistant, developed through the Blackjack test environment, can be applied in the following areas:

**Financial Sector:**
- **Portfolio Management**: Risk-based asset allocation
- **Trading Strategies**: Buy-sell decisions with dynamic risk management
- **Credit Risk Analysis**: Creditworthiness risk assessment

**Business Management:**
- **Project Management**: Resource optimization under uncertainty
- **Supply Chain**: Inventory management under stochastic demand
- **Marketing Strategies**: Budget allocation under dynamic market conditions

**Healthcare Sector:**
- **Treatment Planning**: Risk-based treatment strategies
- **Resource Allocation**: Hospital resource optimization

**Energy Sector:**
- **Energy Trading**: Risk management in dynamic price environments
- **Grid Management**: Energy distribution under uncertain demand

#### 🎰 Advantages of Blackjack Test Environment

Blackjack provides an ideal environment to test the AI assistant's capabilities:
- **Controllable Uncertainty**: Real-world uncertainties simulated through card distribution
- **Multiple Risk Factors**: Player hand, dealer card, card count, table dynamics
- **Instant Feedback**: Learning through gain/loss after each move
- **Portfolio Management**: Budget allocation in multiple hands and split situations

### 🎯 Key Features

- **Reinforcement Learning**: DQN (Deep Q-Network) based AI training
- **Basic Strategy Integration**: Comparison with classical blackjack strategies
- **Hyperparameter Optimization**: Automatic parameter tuning with Optuna
- **Performance Analysis**: Comprehensive metrics and visualizations
- **Multi-Player Support**: Dynamic table environments (PHASE 4.0)
- **Real-time Tracking**: Weights & Biases integration

### 🏗️ Project Structure

```
Blackjack/
├── V3_0/                          # Main project directory
│   ├── rl_environment.py          # RL environment
│   ├── utils/                     # Utility modules
│   │   ├── ai_strategy.py        # AI strategy classes
│   │   ├── basic_strategy.py     # Basic blackjack strategy
│   │   ├── performance_metrics.py # Performance measurements
│   │   └── tracking.py           # W&B integration
│   ├── scripts/                   # Training and evaluation scripts
│   │   ├── train_play_agent.py   # AI training
│   │   ├── evaluate_play_agent.py # Model evaluation
│   │   ├── optimize_hyperparameters.py # HPO
│   │   └── visualize_policy.py   # Policy visualization
│   ├── config/                    # Configuration files
│   ├── tests/                     # Test files
│   └── reports/                   # Reports and analyses
├── V2_0/                          # Previous version
└── V1.0/                          # Initial version
```

### 🚀 Installation

1. **Install Requirements:**
```bash
cd V3_0
pip install -r requirements.txt
```

2. **Setup Environment:**
```bash
# Weights & Biases setup (optional)
wandb login
```

### 📊 Usage

#### 1. AI Training
```bash
cd V3_0
python scripts/train_play_agent.py
```

#### 2. Model Evaluation
```bash
python scripts/evaluate_play_agent.py --model-path runs/phase1/models/final_model.zip
```

#### 3. Hyperparameter Optimization
```bash
python scripts/optimize_hyperparameters.py
```

#### 4. Policy Visualization
```bash
python scripts/visualize_policy.py --model-path runs/phase1/models/final_model.zip
```

### 🎮 Game Features

- **Card Counting**: Real-time counting with Hi-Lo system
- **Split Support**: Multiple hand management
- **Double Down**: Double betting in appropriate situations
- **Dealer Rules**: S17/H17 support
- **Multiple Decks**: 1-8 deck support

### 📈 Performance Metrics

- **Win Rate**: Winning percentage
- **Expected Value**: Expected value calculations
- **Risk Metrics**: Risk measurements
- **Strategy Comparison**: Comparison with basic strategy

### 🔬 Advanced Features

#### PHASE 4.0 - Multi-Player Dynamic AI
- **Player Behavior Analysis**: Conservative, Aggressive, Basic Strategy, Card Counter, Random, Superstitious
- **Real-time Classification**: Real-time player categorization
- **Adaptive Strategy**: Dynamic strategy changes
- **Multi-Player Environment**: Multi-player support

### 📝 Reports

Reports generated within the project scope:
- `reports/phase_1_final_report.md`: PHASE 1 results
- `reports/engine_validation.md`: Engine validation report
- `runs/integration_test/`: Integration test results

---

## 🛠️ Technical Details

### Dependencies

Core dependencies include:
- `stable-baselines3>=2.2.1`: RL algorithms
- `gymnasium==0.29.0`: Environment framework
- `optuna>=3.4`: Hyperparameter optimization
- `wandb>=0.17`: Experiment tracking
- `matplotlib>=3.7`: Visualization
- `pandas>=2.1`: Data analysis

### Environment Features

- **Observation Space**: `(player_total, dealer_upcard, usable_ace, true_count)`
- **Action Space**: `{stand, hit, double, split}`
- **Reward System**: Win/Loss/Tie based rewards
- **Card Counting**: Hi-Lo system integration

### Training Configuration

- **Algorithm**: DQN (Deep Q-Network)
- **Network Architecture**: Custom neural network
- **Training Episodes**: Configurable (default: 100,000)
- **Evaluation**: Regular performance assessment

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<<<<<<< HEAD
---

## 📞 Contact

For questions and support:
- **Email**: [Your Email]
- **GitHub**: [Your GitHub Profile]
- **Project**: [Repository URL]
=======
>>>>>>> 33d6c815dbdf81f7a17d47b2a4457c15a0f21adb

---

## 🙏 Acknowledgments

- **Stable-Baselines3**: RL algorithms implementation
- **Gymnasium**: Environment framework
- **Weights & Biases**: Experiment tracking
- **Optuna**: Hyperparameter optimization

---

<<<<<<< HEAD
*Bu proje, belirsiz gelecek içeren süreçlerde risk değerlendirmesi ve bütçe optimizasyonu yapabilen evrensel bir AI asistan geliştirmeyi amaçlamaktadır. Blackjack test ortamında geliştirilen bu asistan, finans, işletme yönetimi, sağlık ve enerji sektörlerinde uygulanabilir hale getirilmektedir.*

*This project aims to develop a universal AI assistant capable of risk assessment and budget optimization in processes containing uncertain futures. This assistant, developed through the Blackjack test environment, is being made applicable in finance, business management, healthcare, and energy sectors.* 
=======
*Bu proje, belirsiz gelecek içeren süreçlerde risk değerlendirmesi ve bütçe optimizasyonu yapabilen evrensel bir AI asistan geliştirmeyi amaçlamaktadır. Blackjack test ortamında geliştirilen bu asistan, finans, işletme yönetimi, sağlık ve enerji sektörlerinde uygulanabilir hale getirilebilir Blackjack sadece temsilidir.*

*This project aims to develop a universal AI assistant capable of risk assessment and budget optimization in processes containing uncertain futures. This assistant, developed through the Blackjack test environment, is being made applicable in finance, business management, healthcare, and energy sectors.* 
>>>>>>> 33d6c815dbdf81f7a17d47b2a4457c15a0f21adb

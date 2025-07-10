# 🎰 Blackjack AI - Reinforcement Learning Project

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange.svg)]()

---

## 🇹🇷 Türkçe

### 📋 Proje Hakkında

Bu proje, Reinforcement Learning (RL) kullanarak Blackjack oyununda uzmanlaşmış bir yapay zeka sistemi geliştirmeyi amaçlamaktadır. Proje, temel strateji optimizasyonundan başlayarak, çok oyunculu dinamik ortamlara kadar geniş bir yelpazede AI stratejileri geliştirmektedir.

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

This project aims to develop an artificial intelligence system specialized in Blackjack using Reinforcement Learning (RL). The project develops AI strategies across a broad spectrum, from basic strategy optimization to multi-player dynamic environments.

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

---

## 📞 Contact

For questions and support:
- **Email**: [Your Email]
- **GitHub**: [Your GitHub Profile]
- **Project**: [Repository URL]

---

## 🙏 Acknowledgments

- **Stable-Baselines3**: RL algorithms implementation
- **Gymnasium**: Environment framework
- **Weights & Biases**: Experiment tracking
- **Optuna**: Hyperparameter optimization

---

*Bu proje, Reinforcement Learning ve Blackjack stratejilerini birleştiren kapsamlı bir AI sistemi geliştirmeyi amaçlamaktadır. Sürekli geliştirme ve iyileştirme ile gerçek dünya casino ortamlarında kullanılabilir hale getirilmektedir.*

*This project aims to develop a comprehensive AI system that combines Reinforcement Learning and Blackjack strategies. Through continuous development and improvement, it is being made suitable for real-world casino environments.* 
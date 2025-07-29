# 🚀 **PHASE 2 YOL HARİTASI: Betting Strategy RL Agent Development**

**Başlangıç Tarihi:** Aralık 2024  
**Durum:** 🔄 IN PROGRESS  
**Ana Hedef:** Dynamik betting stratejisi öğrenen RL agent geliştirme  

---

## 📋 **PHASE 2 GÖREV ÖZETİ**

| Görev ID | Görev Adı | Açıklama | Öncelik | Durum |
|----------|-----------|----------|---------|-------|
| **F2.1** | **Bankroll Ödülü** | Ödül = net kazanılan birim sistemi | **Kritik** | 🔄 Next |
| **F2.2** | **Bahis Aksiyon Uzayı** | `{play_action, bet_index}` veya continuous bet | **Kritik** | ⏳ Pending |
| **F2.3** | **Env Güncellemesi** | Gözleme bankroll, önceki sonuç, TC ekleme | Yüksek | ⏳ Pending |
| **F2.4** | **`train_bet_agent.py`** | PPO/TD3, 10M el, lr scheduler | Yüksek | ⏳ Pending |
| **F2.5** | **Motor Entegrasyonu** | `Player.wager` "ai_bet" stratejisi | Yüksek | ⏳ Pending |
| **F2.6** | **Kombine Ajan** | Bahis → Oynama zinciri veya ortak NN | Orta | ⏳ Pending |
| **F2.7** | **Risk & Güvenlik** | Max-bet sınırı, Risk-of-Ruin ≤1% | **Kritik** | ⏳ Pending |
| **F2.8** | **Politika Görselleştirme** | TC ↔ bet dağılımı, Sharpe trendi | Orta | ⏳ Pending |

---

## 🎯 **HAFTALIK PLAN (2-4 Hafta)**

### **🗓️ Hafta 2: Core Betting Framework (F2.1-F2.3)**
**Hedef:** Betting environment ve reward system temellerini atmak

#### **Gün 1-2: Bankroll Reward System (F2.1)**
- [ ] Net kazanç bazlı reward function tasarımı
- [ ] Unit-based betting sistemi implementasyonu
- [ ] Reward calculation validation testleri

#### **Gün 3-4: Betting Action Space (F2.2)**
- [ ] Discrete bet sizing options (1, 2, 5, 10 units)
- [ ] Continuous betting space alternatifi
- [ ] Action space validation ve testing

#### **Gün 5-7: Environment Enhancement (F2.3)**
- [ ] Bankroll observation ekleme
- [ ] Previous result tracking
- [ ] True Count integration
- [ ] Enhanced observation space testing

### **🗓️ Hafta 3: RL Training & Integration (F2.4-F2.6)**

#### **Gün 1-3: Betting Agent Training (F2.4)**
- [ ] PPO/TD3 betting agent implementation
- [ ] 10M episode training pipeline
- [ ] Learning rate scheduler
- [ ] Training monitoring ve logging

#### **Gün 4-5: Engine Integration (F2.5)**
- [ ] `Player.wager` "ai_bet" strategy integration
- [ ] Betting decision flow implementation
- [ ] Integration testing

#### **Gün 6-7: Combined Agent (F2.6)**
- [ ] Play + Betting agent combination
- [ ] Sequential decision making pipeline
- [ ] Performance optimization

### **🗓️ Hafta 4: Risk Management & Visualization (F2.7-F2.8)**

#### **Gün 1-3: Risk Analysis (F2.7)**
- [ ] Maximum bet limits implementation
- [ ] Risk-of-Ruin calculation (≤1%)
- [ ] Stress testing scenarios
- [ ] Risk metrics validation

#### **Gün 4-5: Policy Visualization (F2.8)**
- [ ] True Count ↔ Bet distribution plots
- [ ] Sharpe ratio trending
- [ ] Policy heatmaps
- [ ] Performance dashboards

#### **Gün 6-7: Phase 2 Completion**
- [ ] Final testing ve validation
- [ ] Performance report
- [ ] Phase 3 hazırlık

---

## 🔧 **TEKNİK MİMARİ**

### **1. Enhanced Environment (F2.3)**
```python
class BettingBlackjackEnv:
    def __init__(self):
        # Enhanced observation space
        self.observation_space = spaces.Box(
            low=-1, high=1,
            shape=(ORIGINAL_OBS + 3,),  # +bankroll, +prev_result, +true_count
            dtype=np.float32
        )
        
        # Betting action space
        self.action_space = spaces.Box(
            low=np.array([0, 1]),     # [play_action, bet_amount]
            high=np.array([3, 10]),   # [max_play, max_bet]
            dtype=np.float32
        )
```

### **2. Reward Function (F2.1)**
```python
def calculate_betting_reward(net_units_won, risk_penalty=0.1):
    base_reward = net_units_won
    risk_adjustment = -risk_penalty * abs(net_units_won)
    return base_reward + risk_adjustment
```

### **3. Combined Agent Architecture (F2.6)**
```python
class CombinedBlackjackAgent:
    def __init__(self):
        self.play_agent = DQN.load("models/play_agent.zip")
        self.bet_agent = PPO.load("models/bet_agent.zip")
    
    def get_action(self, observation):
        bet_size = self.bet_agent.predict(observation)[0]
        play_action = self.play_agent.predict(observation)[0]
        return {"bet": bet_size, "play": play_action}
```

---

## 📊 **BAŞARI KRİTERLERİ**

### **Teknik Başarı Ölçütleri**
- ✅ **Functional Betting Agent:** PPO/TD3 agent successfully trained
- ✅ **Risk Management:** Risk-of-Ruin ≤ 1%
- ✅ **Engine Integration:** Seamless betting integration
- ✅ **Performance Improvement:** Combined agent > baseline

### **Performans Hedefleri**
| Metric | Phase 1 Baseline | Phase 2 Target | Stretch Goal |
|--------|------------------|----------------|--------------|
| **Expected Value** | +0.021 | +0.040 | +0.060 |
| **Sharpe Ratio** | - | >1.5 | >2.0 |
| **Risk-of-Ruin** | - | <1% | <0.5% |
| **Max Drawdown** | - | <10% | <5% |

---

## 🚀 **İLK ADIM: F2.1 Bankroll Reward System**

Hemen Phase 2'nin ilk kririk görevi olan **F2.1: Bankroll Ödülü** ile başlayalım!

**Yapacakları:**
1. ✅ Net unit bazlı reward function tasarımı
2. ✅ Bankroll tracking sistemi
3. ✅ Risk-adjusted reward calculation
4. ✅ Unit testing ve validation

**Estimated Time:** 1-2 gün

---

## 🎯 **Phase 2 Vizyon**

Phase 2 sonunda:
- **🤖 Smart Betting AI:** True Count'a göre optimal bet sizing
- **⚖️ Risk Management:** Responsible AI with controlled risk
- **📈 Performance Boost:** Play + Betting combination superiority
- **📊 Comprehensive Analysis:** Detailed performance metrics & visualization

**Hazır mısınız Phase 2'ye başlamaya?** 🚀 
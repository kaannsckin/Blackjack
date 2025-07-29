from __future__ import annotations

"""
================================================================================
BLACKJACK REINFORCEMENT LEARNING ENVIRONMENT (V3.0)
================================================================================

📋 **AMAÇ:**
   Blackjack oyunu için Gymnasium uyumlu RL ortamı. Hit/Stand/Double/Split 
   kararlarını öğrenen AI ajanlar için temel simülasyon motoru.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 0 (F0.2): Temel RL environment kurulumu
   • FAZ 1 (F1.1-F1.2): Oynama stratejisi için observation/action space
   • FAZ 2 (F2.3): Bahis stratejisi için environment genişletmesi
   • FAZ 3 (F3.1-F3.2): Çoklu kural seti desteği ve dinamik reset

🏗️ **TEKNİK ÖZELLİKLER:**
   • Observation Space: [player_total, dealer_up, usable_ace, true_count]
   • Action Space: Discrete(4) - [Stand, Hit, Double, Split]
   • Reward System: Win:+1, Push:0, Loss:-1
   • Multi-hand Support: Split işlemleri için çoklu el yönetimi
   • Card Counting: Hi-Lo sistemli true count hesaplama
   • Rule Variations: S17/H17, DAS, penetration ayarları

🔄 **GÜNCELLEMELER:**
   • 2025-07-29: Terminal observation fix, split handling improvements
   • 2025-07-10: Split action tam implementasyonu
   • 2025-07-09: İlk sürüm, basic hit/stand/double

📊 **KULLANIM:**
   ```python
   env = BlackjackEnv(rules={"num_decks": 6, "dealer_rule": "S17"})
   obs, info = env.reset()
   obs, reward, done, truncated, info = env.step(action)
   ```

================================================================================
""" 
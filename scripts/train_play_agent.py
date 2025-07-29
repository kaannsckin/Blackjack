#!/usr/bin/env python3
"""
================================================================================
BLACKJACK PLAYING STRATEGY TRAINING SCRIPT (V3.0)
================================================================================

📋 **AMAÇ:**
   DQN tabanlı blackjack oynama stratejisi eğitimi. Hit/Stand/Double/Split
   kararlarını öğrenen AI ajan geliştirir.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 1 (F1.3): Ana DQN eğitim script'i
   • FAZ 1 (F1.6): Hyperparameter tuning entegrasyonu
   • 2025-07-29: Kritik hyperparameter düzeltmeleri uygulandı

🏗️ **EĞİTİM PARAMETRELERİ:**
   • Algorithm: Deep Q-Network (DQN)
   • Network: MLP [256, 256] layers
   • Optimizer: Adam with linear LR schedule
   • Exploration: ε-greedy with decay (0.3 → 0.05)
   • Gamma: 0.99 (fixed from 1.0)
   • Buffer Size: 100K experiences
   • Batch Size: 1024 (optimized from 2048)

🔧 **DÜZELTMELER (2025-07-29):**
   • gamma: 1.0 → 0.99 (kritik!)
   • exploration_fraction: 0.08 → 0.3 (3x daha fazla keşif)
   • learning_rate: artırıldı
   • train_freq: 32 → 4 (daha sık training)

📊 **KULLANIM:**
   ```bash
   python scripts/train_play_agent.py --total-steps 5000000 --log-dir runs/phase1
   ```

⚡ **BEKLENEN ÇIKTILAR:**
   • Eğitilmiş DQN model (.zip)
   • TensorBoard/W&B logları
   • Performance metrics
   • Model checkpoints

================================================================================
"""
"""
Train a DQN "play-agent" for Blackjack (FAZ 1 – F1.3). 
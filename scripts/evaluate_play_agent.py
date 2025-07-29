#!/usr/bin/env python3
"""
================================================================================
BLACKJACK PLAYING AGENT EVALUATION SCRIPT (V3.0)
================================================================================

📋 **AMAÇ:**
   Eğitilmiş DQN modelinin performansını değerlendirme ve benchmark analizi.
   Basic strategy ile karşılaştırma ve detaylı metrik hesaplama.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 1 (F1.4): Model evaluation ve benchmark
   • FAZ 1 (F1.7): Policy comparison ve visualization
   • Performance validation: Her model eğitimi sonrası

🏗️ **DEĞERLENDİRME METRİKLERİ:**
   • Expected Value (EV)
   • Return to Player (RTP)
   • Win Rate & Agreement Rate
   • Action Distribution Analysis
   • Statistical Significance Tests
   • Volatility & Risk Metrics

📊 **KARŞILAŞTIRMA:**
   • AI Agent vs Basic Strategy
   • Policy agreement analysis
   • Decision boundary comparison
   • Action frequency distribution

⚡ **KULLANIM:**
   ```bash
   python scripts/evaluate_play_agent.py --model-path models/best_model.zip
   ```

🎯 **ÇIKTILAR:**
   • Performance report (JSON/CSV)
   • Comparison plots
   • Statistical analysis
   • Recommendation summary

================================================================================
""" 
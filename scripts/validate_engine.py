#!/usr/bin/env python3
"""
================================================================================
SIMULATION ENGINE VALIDATION SCRIPT (V3.0)
================================================================================

📋 **AMAÇ:**
   Blackjack simülasyon motorunun doğruluğunu validate eder.
   House edge hesaplama ve matematik doğrulama.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 0 (F0.5): Simülasyon motoru doğrulama
   • Pre-training: Engine accuracy verification
   • Quality assurance: Mathematical correctness

🏗️ **VALIDATION TESLERİ:**
   • House edge calculation (target: ~0.5%)
   • Basic strategy RTP verification
   • Large sample validation (1M+ hands)
   • Rule variant testing (S17/H17, DAS)
   • Statistical significance checks

📊 **KULLANIM:**
   ```bash
   python scripts/validate_engine.py --hands 1000000 --rules S17
   ```

⚡ **ÇIKTILAR:**
   • Calculated house edge
   • Statistical confidence intervals
   • Validation report
   • Recommendation summary

================================================================================
""" 
"""
================================================================================
BLACKJACK BASIC STRATEGY IMPLEMENTATION (V3.0)
================================================================================

📋 **AMAÇ:**
   Matematiksel olarak optimal blackjack basic strategy implementasyonu.
   AI modellerinin benchmark'ı ve fallback strategy'si olarak kullanılır.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 0 (F0.5): Simülasyon motoru doğrulaması
   • FAZ 1 (F1.4): AI model benchmark ve comparison
   • All phases: Fallback strategy ve reference implementation

🏗️ **STRATEJİ KAPSAMI:**
   • Hard totals (5-21) strategy
   • Soft totals (A2-A10) strategy  
   • Pair splitting strategy
   • Double down decisions
   • Surrender options (H17/S17)

📊 **KURAL VARYASYONLARİ:**
   • S17 vs H17 (dealer stands/hits soft 17)
   • DAS (Double After Split) support
   • Surrender availability
   • Number of decks consideration

⚡ **KULLANIM:**
   ```python
   strategy = BasicStrategy(rules={"dealer_rule": "S17", "das": True})
   action = strategy.get_action(player_total=16, dealer_up=10, usable_ace=False)
   ```

🎯 **PERFORMANS:**
   • House edge: ~0.5% (optimal play)
   • Expected RTP: ~99.5%
   • Benchmark standard: All AI models compared against this

================================================================================
""" 
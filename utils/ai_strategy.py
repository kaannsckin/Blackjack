"""
================================================================================
AI STRATEGY WRAPPER & INTERFACE (V3.0)
================================================================================

📋 **AMAÇ:**
   Eğitilmiş RL modellerini simülasyon engine'inde kullanmak için wrapper.
   Model loading, prediction ve fallback handling sağlar.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 1 (F1.5): AI model engine integration
   • Production deployment: Model serving infrastructure
   • Runtime: Real-time decision making

🏗️ **WRAPPER ÖZELLİKLERİ:**
   • Model loading ve validation
   • Observation preprocessing
   • Action mapping (index → string)
   • Error handling ve fallback
   • Performance monitoring

🔧 **FALLBACK MECHANISM:**
   • Primary: Trained DQN model
   • Fallback: Basic strategy (model failure)
   • Emergency: Random strategy (complete failure)
   • Logging: All fallback events tracked

📊 **KULLANIM:**
   ```python
   ai_strategy = AIStrategy(model_path="models/best_model.zip")
   action = ai_strategy.get_action(player_total=16, dealer_up=10, usable_ace=False)
   ```

⚡ **ENTEGRASYON:**
   • Compatible with existing engine
   • Drop-in replacement for basic strategy
   • Minimal performance overhead
   • Production-ready error handling

================================================================================
""" 
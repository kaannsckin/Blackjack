"""
================================================================================
TRAINING CALLBACKS & MODEL CHECKPOINTING (V3.0)
================================================================================

📋 **AMAÇ:**
   RL model eğitimi sırasında callback functions. Model checkpointing,
   evaluation tracking ve best model saving.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 1 (F1.3): Training callbacks ve model saving
   • All training: Automatic best model checkpointing
   • Monitoring: Performance tracking during training

🏗️ **CALLBACK ÖZELLİKLERİ:**
   • SaveBestModelCallback: En iyi modeli otomatik kaydetme
   • Evaluation tracking: Periyodik performance değerlendirme
   • Early stopping: Performance degradation detection
   • Logging integration: W&B ve TensorBoard compatibility

📊 **KULLANIM:**
   ```python
   callback = SaveBestModelCallback(
       eval_env=eval_env,
       eval_freq=50000,
       save_path="models/"
   )
   model.learn(total_timesteps=5000000, callback=callback)
   ```

⚡ **ÖZELLİKLER:**
   • Best model auto-save
   • Performance monitoring
   • Resource optimization
   • Training stability

================================================================================
""" 
"""
================================================================================
EXPERIMENT TRACKING & MONITORING UTILITIES (V3.0)
================================================================================

📋 **AMAÇ:**
   W&B ve TensorBoard entegrasyonu. Eğitim sürecini izleme, 
   experiment logging ve model versioning.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 0 (F0.4): Deney izleme altyapısı
   • FAZ 1+: Tüm eğitim süreçlerinde monitoring
   • 2025-07-29: Optional TensorBoard support eklendi

🏗️ **TRACKING ÖZELLİKLERİ:**
   • W&B integration (primary)
   • TensorBoard support (optional)
   • Hyperparameter logging
   • Model metrics tracking
   • Artifact management

🔧 **DÜZELTMELER (2025-07-29):**
   • TensorBoard import made optional
   • Graceful fallback when dependencies missing
   • Error handling improvements

📊 **KULLANIM:**
   ```python
   run = init_wandb(project="blackjack_phase1", config=params)
   tb_writer = get_tb_writer(log_dir="runs/experiment")
   ```

⚡ **ENTEGRASYON:**
   • Auto-detection of available tools
   • Minimal setup requirements
   • Production-ready logging
   • Dashboard integration

================================================================================
""" 
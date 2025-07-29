#!/usr/bin/env python3
"""
================================================================================
HYPERPARAMETER OPTIMIZATION SCRIPT (V3.0)
================================================================================

📋 **AMAÇ:**
   Optuna tabanlı hyperparameter tuning. DQN modelinin optimal 
   parametrelerini systematik arama ile bulur.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 1 (F1.6): Hyperparameter tuning ve optimization
   • Model improvement: Performans optimizasyonu
   • Research: En iyi parametre kombinasyonları

🔬 **OPTİMİZE EDİLEN PARAMETRELER:**
   • Learning Rate (1e-5 to 1e-3)
   • Buffer Size (10K to 1M)
   • Exploration parameters (eps_frac, eps_final)
   • Gamma (0.9 to 1.0)
   • Network architecture (layer sizes)
   • Batch size (256 to 4096)

🏗️ **OPTİMİZASYON STRATEJİSİ:**
   • Algorithm: TPE (Tree-structured Parzen Estimator)
   • Objective: Mean episode reward maximization
   • Multi-seed evaluation için robust results
   • Early stopping: underperforming trials

📊 **KULLANIM:**
   ```bash
   python scripts/optimize_hyperparameters.py --n-trials 50 --study-name blackjack_hpo
   ```

⚡ **ÇIKTILAR:**
   • best_params.json
   • Optimized model checkpoints
   • Optimization history plots
   • Parameter importance analysis

================================================================================
""" 
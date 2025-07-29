#!/usr/bin/env python3
"""
================================================================================
POLICY VISUALIZATION & ANALYSIS SCRIPT (V3.0)
================================================================================

📋 **AMAÇ:**
   Eğitilmiş AI modelinin karar alma politikasını görselleştirme.
   Q-value heatmaps, policy comparison ve decision boundary analizi.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 1 (F1.7): Policy visualization ve heatmaps
   • Model analysis: Her eğitim sonrası görsel analiz
   • 2025-07-29: Q-value extraction düzeltmesi uygulandı

🎨 **GÖRSELLEŞTİRME TÜRLERİ:**
   • Q-value Heatmaps (Usable Ace / No Usable Ace)
   • Policy Comparison (AI vs Basic Strategy)
   • Action Distribution Charts
   • Decision Boundary Analysis
   • Agreement Rate Visualization

🔧 **DÜZELTMELER (2025-07-29):**
   • Q-value extraction: model.q_net.forward() → proper method
   • PyTorch tensor handling düzeltildi
   • Heatmap generation stabilized

📊 **KULLANIM:**
   ```bash
   python scripts/visualize_policy.py --model-path models/best_model.zip 
                                      --output-dir runs/visualization
   ```

⚡ **ÇIKTILAR:**
   • Q-value heatmaps (PNG)
   • Policy comparison plots
   • Action distribution charts
   • HTML report dashboard

================================================================================
"""
"""
Policy Visualization Script (FAZ 1 – F1.7)
"""
import sys
from pathlib import Path

# Add V3_0/scripts to sys.path to import the real implementation
sys.path.insert(0, str(Path(__file__).parent.parent / "V3_0" / "scripts"))

from visualize_policy import main

if __name__ == "__main__":
    main() 
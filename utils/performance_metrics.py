"""
================================================================================
PERFORMANCE METRICS & ANALYSIS UTILITIES (V3.0)
================================================================================

📋 **AMAÇ:**
   AI model ve strategy performansını ölçmek için kapsamlı metrik hesaplama.
   Statistical analysis, risk assessment ve comparison utilities.

🎯 **FAZ KAPSAMINDA:**
   • FAZ 1 (F1.4): Model evaluation ve performance analysis
   • All phases: Continuous performance monitoring
   • Research: Statistical significance testing

📊 **HESAPLANAN METRİKLER:**
   • Expected Value (EV) - Ortalama getiri
   • Return to Player (RTP) - Oyuncu dönüş oranı  
   • Win Rate - Kazanma oranı
   • Agreement Rate - Basic strategy ile uyum
   • Volatility - Risk ölçümü
   • Sharpe Ratio - Risk-adjusted return

🔬 **İSTATİSTİKSEL ANALİZ:**
   • T-test significance testing
   • Confidence intervals
   • Standard error calculation
   • Sample size sufficiency
   • Distribution analysis

⚡ **KULLANIM:**
   ```python
   metrics = calculate_performance_metrics(results_df)
   comparison = compare_strategies(ai_results, basic_results)
   report = generate_performance_report(metrics)
   ```

🎯 **ÇIKTILAR:**
   • JSON/CSV performance reports
   • Statistical comparison tables
   • Recommendation summaries
   • Risk assessment reports

================================================================================
""" 
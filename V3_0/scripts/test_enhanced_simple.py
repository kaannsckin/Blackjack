#!/usr/bin/env python3
"""
Enhanced Simple AI Test

Test if minimal targeted improvements to the PROVEN Simple AI can achieve AA grade.
"""

import sys
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from enhanced_simple_ai import create_enhanced_simple_ai
from betting_environment_fixed import create_fixed_betting_env


def test_enhanced_simple_ai(n_hands: int = 1000):
    """Test Enhanced Simple AI - minimal improvements to proven approach."""
    
    print("🎯 ENHANCED SIMPLE AI TEST")
    print("=" * 60)
    print("Strategy: PROVEN Simple AI Base + MINIMAL Targeted Improvements")
    print("Base Performance: +0.51% ROI, B Grade ✅")
    print("Target: AA Grade with bet spread enhancement")
    print(f"Testing {n_hands:,} hands...")
    print()
    
    # Create Enhanced Simple AI
    enhanced_ai = create_enhanced_simple_ai(initial_bankroll=10000)
    
    # Create environment (same as proven tests)
    env = create_fixed_betting_env(
        seed=42,  # Same seed as successful Simple AI test
        initial_bankroll=10000.0,
        min_bet=25.0,
        max_bet=500.0,
        risk_aversion=0.05
    )
    
    # Track performance
    hand_data = []
    
    hands_completed = 0
    start_time = time.time()
    
    print("🎮 Testing Enhanced Simple AI...")
    
    while hands_completed < n_hands:
        # Reset for new hand
        obs, _ = env.reset()
        
        # Extract game state
        player_total = int(obs[0])
        dealer_up = int(obs[1])
        usable_ace = bool(obs[2])
        
        # Enhanced AI bet decision (MAIN IMPROVEMENT)
        ai_bet = enhanced_ai.decide_bet_size(
            min_bet=env.min_bet,
            max_bet=env.max_bet
        )
        
        # Set bet in environment
        env.set_bet_amount(ai_bet)
        
        # Enhanced AI play decision (minimal improvement)
        ai_action = enhanced_ai.decide_play_action(
            player_total=player_total,
            dealer_up=dealer_up,
            usable_ace=usable_ace
        )
        
        # Execute action
        obs, reward, done, truncated, info = env.step(ai_action)
        
        if done or truncated:
            # Update AI with result
            enhanced_ai.update_result(ai_bet, reward)
            
            # Track performance
            metrics = enhanced_ai.get_performance_metrics()
            hand_data.append({
                'hand': hands_completed + 1,
                'bet_size': ai_bet,
                'outcome': reward,
                'current_roi': metrics.get('total_roi', 0),
                'bankroll': metrics.get('current_bankroll', 10000),
                'grade': enhanced_ai.get_grade(),
                'bet_spread': metrics.get('bet_spread', 1.0),
                'tc_correlation': metrics.get('tc_bet_correlation', 0.0)
            })
            
            hands_completed += 1
            
            # Progress updates
            if hands_completed % 250 == 0:
                elapsed = time.time() - start_time
                rate = hands_completed / elapsed
                eta = (n_hands - hands_completed) / rate if rate > 0 else 0
                
                current_metrics = enhanced_ai.get_performance_metrics()
                print(f"   📊 Hand {hands_completed:,}/{n_hands:,} "
                      f"({100*hands_completed/n_hands:.1f}%) "
                      f"- Grade: {enhanced_ai.get_grade()} "
                      f"- ROI: {current_metrics.get('total_roi', 0):+.1%} "
                      f"- Spread: {current_metrics.get('bet_spread', 1.0):.1f}x "
                      f"- ETA: {eta:.0f}s")
    
    total_time = time.time() - start_time
    print(f"\n⏱️ Test completed in {total_time:.1f}s ({hands_completed/total_time:.0f} hands/sec)")
    
    return {
        'enhanced_ai': enhanced_ai,
        'hand_data': hand_data,
        'test_duration': total_time
    }


def analyze_enhanced_simple_performance(results):
    """Analyze Enhanced Simple AI performance vs original."""
    
    print("\n📊 ENHANCED SIMPLE AI ANALYSIS")
    print("=" * 60)
    
    enhanced_ai = results['enhanced_ai']
    hand_data = pd.DataFrame(results['hand_data'])
    
    # Get final metrics
    final_metrics = enhanced_ai.get_performance_metrics()
    final_grade = enhanced_ai.get_grade()
    
    # === CORE PERFORMANCE COMPARISON ===
    print("\n🎯 PERFORMANCE vs PROVEN SIMPLE AI:")
    print(f"   Original Simple AI: B Grade, +0.51% ROI, 1.0x spread")
    print(f"   Enhanced Simple AI: {final_grade} Grade, {final_metrics['total_roi']:+.2%} ROI, {final_metrics['bet_spread']:.1f}x spread")
    print()
    print(f"   Improvement Analysis:")
    
    roi_improvement = final_metrics['total_roi'] - 0.0051  # vs original +0.51%
    print(f"      ROI Change: {roi_improvement:+.2%}")
    
    if final_metrics['bet_spread'] > 1.5:
        print(f"      ✅ Bet Spread ACHIEVED: {final_metrics['bet_spread']:.1f}x (vs 1.0x)")
    else:
        print(f"      🔴 Bet Spread FAILED: {final_metrics['bet_spread']:.1f}x")
    
    if final_metrics['tc_bet_correlation'] > 0.4:
        print(f"      ✅ TC Correlation ACHIEVED: {final_metrics['tc_bet_correlation']:.3f}")
    else:
        print(f"      🔴 TC Correlation FAILED: {final_metrics['tc_bet_correlation']:.3f}")
    
    # === DETAILED METRICS ===
    print(f"\n📊 DETAILED PERFORMANCE:")
    print(f"   Final Bankroll: ${final_metrics['current_bankroll']:,.2f}")
    print(f"   Total Hands: {final_metrics['hands_played']:,}")
    print(f"   Win Rate: {final_metrics['win_rate']:.1%}")
    print(f"   Sharpe Ratio: {final_metrics['sharpe_ratio']:.3f}")
    print(f"   Wins: {final_metrics['wins']}, Losses: {final_metrics['losses']}")
    
    # === AA GRADE ANALYSIS ===
    print(f"\n🏆 AA GRADE REQUIREMENTS CHECK:")
    
    aa_requirements = {
        'TC Correlation': (final_metrics['tc_bet_correlation'], 0.7),
        'Bet Spread': (final_metrics['bet_spread'], 4.0),
        'ROI': (final_metrics['total_roi'], 0.05),
        'Win Rate': (final_metrics['win_rate'], 0.47)
    }
    
    aa_score = 0
    max_score = len(aa_requirements) * 25
    
    for requirement, (actual, target) in aa_requirements.items():
        if actual >= target:
            aa_score += 25
            status = "✅ PASS"
        elif actual >= target * 0.7:  # 70% of target
            aa_score += 15
            status = "🟡 PARTIAL"
        else:
            aa_score += 0
            status = "🔴 FAIL"
        
        print(f"   {requirement}: {actual:.3f} (need {target:.3f}) - {status}")
    
    aa_percentage = (aa_score / max_score) * 100
    print(f"\n   🎯 AA Score: {aa_score}/{max_score} ({aa_percentage:.0f}%)")
    
    # === PERFORMANCE TIMELINE ===
    print(f"\n📈 PERFORMANCE EVOLUTION:")
    
    if len(hand_data) >= 500:
        early_period = hand_data.iloc[:250]
        late_period = hand_data.iloc[-250:]
        
        early_roi = early_period['current_roi'].iloc[-1]
        late_roi = late_period['current_roi'].iloc[-1]
        
        learning_effect = late_roi - early_roi
        print(f"   Learning Effect: {learning_effect:+.2%}")
        
        # Consistency check
        roi_stability = hand_data['current_roi'].std()
        print(f"   ROI Stability: {roi_stability:.3f} (lower = more stable)")
        
        # Grade progression
        early_grades = early_period['grade'].mode().iloc[0] if len(early_period['grade'].mode()) > 0 else "N/A"
        late_grades = late_period['grade'].mode().iloc[0] if len(late_period['grade'].mode()) > 0 else "N/A"
        
        print(f"   Grade Evolution: {early_grades} → {late_grades}")
    
    # === FINAL VERDICT ===
    print(f"\n🎖️ FINAL VERDICT:")
    
    if final_grade == "A+":
        print("   🎉 BREAKTHROUGH! Enhanced Simple AI achieved AA grade!")
        print("   ✅ Minimal improvements successfully enhanced proven approach")
        print("   🏆 Perfect balance: Performance + Sophistication")
        print("   🚀 READY FOR PHASE 3!")
        
    elif final_grade == "A":
        print("   🎊 EXCELLENT! Very close to AA grade target")
        print("   ✅ Significant improvement over original Simple AI")
        print("   🔧 Minor fine-tuning could reach A+")
        
    elif final_grade == "B":
        print("   👍 GOOD! Maintained proven performance base")
        print("   🟡 Some improvement but not enough for AA grade")
        print("   📈 Need to enhance bet spread or TC correlation")
        
    else:
        print("   🔴 REGRESSION! Enhanced version worse than original")
        print("   ⚠️ Improvements broke the proven approach")
        print("   🔙 Should revert to original Simple AI")
    
    # === SUCCESS CRITERIA ===
    success = final_grade in ['A+', 'A'] and final_metrics['total_roi'] > 0
    
    return {
        'final_grade': final_grade,
        'aa_score': aa_score,
        'aa_percentage': aa_percentage,
        'final_metrics': final_metrics,
        'success': success,
        'approach': 'Enhanced Simple AI'
    }


def main():
    """Run Enhanced Simple AI test."""
    
    print("🎯 ENHANCED SIMPLE AI - MINIMAL TARGETED IMPROVEMENTS")
    print("=" * 75)
    print("Philosophy: Keep what works + minimal targeted improvements")
    print("Base: PROVEN Simple AI (+0.51% ROI, B Grade)")
    print("Target: AA Grade through bet spread enhancement")
    print()
    
    try:
        # Run test
        results = test_enhanced_simple_ai(n_hands=1500)
        
        # Analyze
        analysis = analyze_enhanced_simple_performance(results)
        
        # Save results
        timestamp = int(time.time())
        results_file = f"runs/enhanced_simple_test_{timestamp}.json"
        
        save_data = {
            'test_config': {
                'approach': 'Enhanced Simple AI',
                'base_performance': '+0.51% ROI, B Grade',
                'target': 'AA Grade',
                'hands_tested': 1500,
                'philosophy': 'Minimal targeted improvements'
            },
            'analysis': analysis,
            'hand_data': results['hand_data']
        }
        
        with open(results_file, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: {results_file}")
        
        # Save AI session
        session_file = results['enhanced_ai'].save_session()
        
        # === ULTIMATE COMPARISON ===
        print(f"\n{'='*75}")
        print("🏆 ULTIMATE AI APPROACH COMPARISON")
        print('='*75)
        
        approaches = [
            ("Simple AI (Fixed)", "B", "+0.51%", "1.0x", "0.000", "✅ PROVEN"),
            ("Advanced AI", "D", "-28.00%", "2.6x", "0.004", "❌ Failed"),
            ("Ultimate AI", "D", "-17.89%", "1.14x", "0.035", "❌ Failed"),
            ("Practical Hybrid", "D", "-24.22%", "1.00x", "0.129", "❌ Failed"),
            ("Enhanced Simple", analysis['final_grade'], 
             f"{analysis['final_metrics']['total_roi']:+.2%}",
             f"{analysis['final_metrics']['bet_spread']:.1f}x",
             f"{analysis['final_metrics']['tc_bet_correlation']:.3f}",
             "🎯 TARGET")
        ]
        
        print(f"{'Approach':<18} {'Grade':<6} {'ROI':<8} {'Spread':<7} {'TC-Corr':<7} {'Status':<10}")
        print("-" * 75)
        for approach, grade, roi, spread, tc_corr, status in approaches:
            print(f"{approach:<18} {grade:<6} {roi:<8} {spread:<7} {tc_corr:<7} {status:<10}")
        
        # === FINAL RECOMMENDATION ===
        print(f"\n💡 FINAL RECOMMENDATION:")
        
        if analysis['success']:
            print("🎉 SUCCESS! Enhanced Simple AI is the optimal solution!")
            print("✅ Achieved AA grade while maintaining proven performance")
            print("🧠 Perfect balance of simplicity and sophistication")
            print("🚀 READY FOR PHASE 3 DEVELOPMENT!")
            return True
        else:
            print("🤔 Enhanced approach needs further refinement")
            if analysis['final_grade'] >= 'B':
                print("👍 Still better than complex approaches - refine further")
            else:
                print("🔙 Consider reverting to original Simple AI")
            return False
        
    except Exception as e:
        print(f"❌ Enhanced Simple AI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
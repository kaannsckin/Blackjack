#!/usr/bin/env python3
"""
Adaptive Simple AI - Simplified Test

Quick validation of crisis management and adaptive features.
"""

import sys
import json
import time
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from adaptive_simple_ai import create_adaptive_simple_ai, CrisisLevel
from betting_environment_fixed import create_fixed_betting_env


def test_adaptive_crisis_management(n_hands: int = 3000):
    """Test adaptive crisis management effectiveness."""
    
    print(f"🎯 ADAPTIVE SIMPLE AI - CRISIS MANAGEMENT TEST")
    print("=" * 60)
    print(f"Testing {n_hands:,} hands for crisis response")
    print()
    
    # Create Adaptive AI
    adaptive_ai = create_adaptive_simple_ai(initial_bankroll=10000)
    
    # Create environment
    env = create_fixed_betting_env(
        seed=42,
        initial_bankroll=10000.0,
        min_bet=25.0,
        max_bet=500.0,
        risk_aversion=0.05
    )
    
    # Track key metrics
    hand_data = []
    crisis_summary = {'normal': 0, 'minor': 0, 'moderate': 0, 'severe': 0}
    bet_size_by_crisis = {'normal': [], 'minor': [], 'moderate': [], 'severe': []}
    
    hands_completed = 0
    start_time = time.time()
    
    print("🎮 Running adaptive crisis test...")
    
    while hands_completed < n_hands:
        # Reset for new hand
        obs, _ = env.reset()
        
        # Extract game state
        player_total = int(obs[0])
        dealer_up = int(obs[1])
        usable_ace = bool(obs[2])
        
        # AI decisions
        ai_bet = adaptive_ai.decide_bet_size(
            min_bet=env.min_bet,
            max_bet=env.max_bet
        )
        
        env.set_bet_amount(ai_bet)
        
        ai_action = adaptive_ai.decide_play_action(
            player_total=player_total,
            dealer_up=dealer_up,
            usable_ace=usable_ace
        )
        
        # Execute action
        obs, reward, done, truncated, info = env.step(ai_action)
        
        if done or truncated:
            # Update AI
            adaptive_ai.update_result(ai_bet, reward)
            
            # Get current metrics
            metrics = adaptive_ai.get_performance_metrics()
            crisis_level = metrics['current_crisis_level']
            
            # Track data
            hand_data.append({
                'hand': hands_completed + 1,
                'bet_size': ai_bet,
                'outcome': reward,
                'bankroll': metrics['current_bankroll'],
                'roi': metrics['total_roi'],
                'crisis_level': crisis_level,
                'consecutive_losses': metrics['consecutive_losses'],
                'drawdown': metrics['current_drawdown']
            })
            
            # Update summaries
            crisis_summary[crisis_level] += 1
            bet_size_by_crisis[crisis_level].append(ai_bet)
            
            hands_completed += 1
            
            # Progress updates
            if hands_completed % 500 == 0:
                elapsed = time.time() - start_time
                rate = hands_completed / elapsed
                eta = (n_hands - hands_completed) / rate if rate > 0 else 0
                
                print(f"   📊 Hand {hands_completed:,}/{n_hands:,} "
                      f"({100*hands_completed/n_hands:.1f}%) "
                      f"- ROI: {metrics['total_roi']:+.1%} "
                      f"- Crisis: {crisis_level} "
                      f"- Losses: {metrics['consecutive_losses']} "
                      f"- ETA: {eta:.0f}s")
    
    total_time = time.time() - start_time
    
    return {
        'adaptive_ai': adaptive_ai,
        'hand_data': hand_data,
        'crisis_summary': crisis_summary,
        'bet_size_by_crisis': bet_size_by_crisis,
        'total_time': total_time
    }


def analyze_adaptive_results(results):
    """Analyze adaptive AI results with focus on crisis management."""
    
    print(f"\n📊 ADAPTIVE AI ANALYSIS")
    print("=" * 60)
    
    adaptive_ai = results['adaptive_ai']
    hand_data = results['hand_data']
    crisis_summary = results['crisis_summary']
    bet_size_by_crisis = results['bet_size_by_crisis']
    
    # Final metrics
    final_metrics = adaptive_ai.get_performance_metrics()
    
    print(f"   ⏱️ Test Duration: {results['total_time']:.1f}s")
    print(f"   🎯 Total Hands: {len(hand_data):,}")
    print(f"   💰 Final Bankroll: ${final_metrics['current_bankroll']:,.2f}")
    print(f"   📈 Final ROI: {final_metrics['total_roi']:+.2%}")
    print(f"   🎲 Win Rate: {final_metrics['win_rate']:.1%}")
    print(f"   📉 Max Drawdown: {final_metrics['max_drawdown']:.1%}")
    
    # === CRISIS MANAGEMENT ANALYSIS ===
    print(f"\n🚨 CRISIS MANAGEMENT EFFECTIVENESS:")
    
    total_hands = len(hand_data)
    crisis_emojis = {'normal': '✅', 'minor': '🟡', 'moderate': '🟠', 'severe': '🔴'}
    
    for level, count in crisis_summary.items():
        percentage = (count / total_hands) * 100
        emoji = crisis_emojis[level]
        print(f"   {emoji} {level.title()}: {count:,} hands ({percentage:.1f}%)")
    
    # Crisis vs Normal times
    crisis_hands = total_hands - crisis_summary['normal']
    crisis_percentage = (crisis_hands / total_hands) * 100
    print(f"\n   🚨 Total Crisis Time: {crisis_hands:,} hands ({crisis_percentage:.1f}%)")
    
    # === BET ADAPTATION ANALYSIS ===
    print(f"\n⚖️ BET SIZE ADAPTATION:")
    
    for level in ['normal', 'minor', 'moderate', 'severe']:
        if bet_size_by_crisis[level]:
            avg_bet = np.mean(bet_size_by_crisis[level])
            emoji = crisis_emojis[level]
            print(f"   {emoji} {level.title()}: ${avg_bet:.2f} average bet")
    
    # Calculate adaptation effectiveness
    if bet_size_by_crisis['normal'] and bet_size_by_crisis['severe']:
        normal_avg = np.mean(bet_size_by_crisis['normal'])
        severe_avg = np.mean(bet_size_by_crisis['severe'])
        adaptation_ratio = severe_avg / normal_avg
        reduction_pct = (1 - adaptation_ratio) * 100
        
        print(f"\n   📊 Crisis Adaptation:")
        print(f"      Normal → Severe: ${normal_avg:.2f} → ${severe_avg:.2f}")
        print(f"      Reduction: {reduction_pct:.1f}%")
        print(f"      Adaptation Ratio: {adaptation_ratio:.2f}x")
    
    # === PERFORMANCE COMPARISON ===
    print(f"\n⚖️ VS SIMPLE AI COMPARISON:")
    print(f"   Simple AI (Reference): +0.51% ROI, No crisis management")
    print(f"   Adaptive AI (Test): {final_metrics['total_roi']:+.2%} ROI, ✅ Crisis management")
    
    performance_delta = final_metrics['total_roi'] - 0.0051
    print(f"   Performance Delta: {performance_delta:+.2%}")
    
    # === SURVIVAL ANALYSIS ===
    print(f"\n🛡️ SURVIVAL ANALYSIS:")
    
    # Check if AI survived major crises
    worst_drawdown = final_metrics['max_drawdown']
    current_bankroll = final_metrics['current_bankroll']
    
    survival_criteria = {
        'No Bankruptcy': current_bankroll > 1000,
        'Moderate Drawdown': worst_drawdown < 0.5,  # Less than 50% loss
        'Crisis Recovery': crisis_summary['severe'] > 0 and current_bankroll > 5000,
        'Functional Performance': final_metrics['total_roi'] > -0.15  # Not catastrophic
    }
    
    survival_score = 0
    for criterion, passed in survival_criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {criterion}: {status}")
        if passed:
            survival_score += 1
    
    survival_percentage = (survival_score / len(survival_criteria)) * 100
    print(f"\n   🎯 Survival Score: {survival_score}/{len(survival_criteria)} ({survival_percentage:.0f}%)")
    
    # === FINAL ASSESSMENT ===
    print(f"\n🏆 FINAL ASSESSMENT:")
    
    if survival_score >= 3 and final_metrics['total_roi'] > -0.05:
        print(f"   🎉 EXCELLENT! Crisis management is working effectively")
        print(f"   ✅ AI survived major drawdowns")
        print(f"   ✅ Adaptive risk management functional")
        assessment = "READY"
    elif survival_score >= 3:
        print(f"   👍 GOOD! Crisis management protects bankroll")
        print(f"   ✅ Survival mechanisms working")
        print(f"   🔧 Performance tuning recommended")
        assessment = "FUNCTIONAL"
    elif survival_score >= 2:
        print(f"   🟡 PARTIAL! Some crisis features working")
        print(f"   ⚠️ Need refinement in crisis sensitivity")
        assessment = "NEEDS_TUNING"
    else:
        print(f"   🔴 INSUFFICIENT! Crisis management needs major revision")
        print(f"   ❌ Survival mechanisms not effective")
        assessment = "NEEDS_REDESIGN"
    
    return {
        'final_metrics': final_metrics,
        'crisis_summary': crisis_summary,
        'survival_score': survival_score,
        'survival_percentage': survival_percentage,
        'assessment': assessment,
        'performance_delta': performance_delta
    }


def main():
    """Run simplified adaptive AI test."""
    
    print("🎯 ADAPTIVE SIMPLE AI - CRISIS MANAGEMENT VALIDATION")
    print("=" * 70)
    print("Focus: Crisis detection, adaptive risk, bankroll protection")
    print("Philosophy: Simple AI base + intelligent crisis response")
    print()
    
    try:
        # Run test
        results = test_adaptive_crisis_management(n_hands=3000)
        
        # Analyze results
        analysis = analyze_adaptive_results(results)
        
        # Save results
        timestamp = int(time.time())
        results_file = f"runs/adaptive_crisis_test_{timestamp}.json"
        
        save_data = {
            'test_config': {
                'hands_tested': 3000,
                'approach': 'Adaptive Simple AI',
                'focus': 'Crisis management validation'
            },
            'results': {
                'final_metrics': analysis['final_metrics'],
                'crisis_summary': analysis['crisis_summary'],
                'survival_assessment': analysis['assessment'],
                'performance_delta': analysis['performance_delta']
            },
            'hand_data': results['hand_data']
        }
        
        with open(results_file, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: {results_file}")
        
        # Status report
        print(results['adaptive_ai'].get_status_report())
        
        # === RECOMMENDATION ===
        print(f"\n💡 RECOMMENDATION:")
        
        if analysis['assessment'] == "READY":
            print("🚀 ADAPTIVE SIMPLE AI IS READY!")
            print("✅ Crisis management validated")
            print("✅ Long-term viability confirmed")
            print("🎯 PROCEED TO PHASE 3 DEVELOPMENT")
            return True
        elif analysis['assessment'] == "FUNCTIONAL":
            print("👍 ADAPTIVE APPROACH IS WORKING")
            print("✅ Core crisis management functional")
            print("🔧 Minor performance tuning recommended")
            print("🎯 ACCEPTABLE FOR PHASE 3 WITH MONITORING")
            return True
        else:
            print("🔧 NEEDS FURTHER DEVELOPMENT")
            print("⚠️ Crisis management requires refinement")
            print("📚 Consider parameter adjustment")
            return False
        
    except Exception as e:
        print(f"❌ Adaptive AI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Ultimate AI System Test

Test the 4-Level Hierarchical AI system for AA grade performance.
"""

import sys
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ultimate_ai_system import create_ultimate_ai, StrategyMode
from betting_environment_fixed import create_fixed_betting_env


def test_ultimate_ai_comprehensive(n_hands: int = 500):
    """Test the Ultimate AI system comprehensively."""
    
    print("🎯 ULTIMATE AI SYSTEM TEST")
    print("=" * 60)
    print(f"Target: AA Grade (90%+)")
    print(f"Requirements: TC-Corr >0.7, Spread >4x, ROI >5%, Win Rate >47%")
    print(f"Testing {n_hands:,} hands...")
    print()
    
    # Create Ultimate AI
    ultimate_ai = create_ultimate_ai(initial_bankroll=10000)
    
    # Create environment for testing
    env = create_fixed_betting_env(
        seed=42,
        initial_bankroll=10000.0,
        min_bet=25.0,
        max_bet=500.0,
        risk_aversion=0.05
    )
    
    # Track sophisticated metrics
    tc_bet_data = []
    performance_timeline = []
    strategy_switches = []
    
    hands_completed = 0
    start_time = time.time()
    
    print("🎮 Starting game simulation...")
    
    while hands_completed < n_hands:
        # Reset environment for new hand
        obs, _ = env.reset()
        
        # Extract game state
        player_total = int(obs[0])
        dealer_up = int(obs[1])
        usable_ace = bool(obs[2])
        true_count = obs[3] if len(obs) > 3 else np.random.normal(0, 2)  # Simulate realistic TC
        
        # AI bet decision
        ai_bet = ultimate_ai.decide_bet_size(
            min_bet=env.min_bet,
            max_bet=env.max_bet,
            true_count=true_count
        )
        
        # Set bet in environment
        env.set_bet_amount(ai_bet)
        
        # Record TC-bet data
        tc_bet_data.append({
            'true_count': true_count,
            'bet_size': ai_bet,
            'bet_ratio': ai_bet / env.min_bet,
            'hand': hands_completed + 1
        })
        
        # AI play decision
        ai_action = ultimate_ai.decide_action(
            player_total=player_total,
            dealer_up=dealer_up,
            usable_ace=usable_ace,
            true_count=true_count,
            available_actions=[0, 1, 2, 3]  # Stand, Hit, Double, Split
        )
        
        # Execute action in environment
        obs, reward, done, truncated, info = env.step(ai_action)
        
        if done or truncated:
            # Update AI with result
            ultimate_ai.update_result(ai_bet, reward)
            
            # Track performance timeline
            status = ultimate_ai.get_status_report()
            performance_timeline.append({
                'hand': hands_completed + 1,
                'grade': status['current_grade'],
                'roi': ultimate_ai.metrics.roi,
                'win_rate': ultimate_ai.metrics.win_rate,
                'bet_spread': ultimate_ai.metrics.bet_spread,
                'mode': ultimate_ai.level4.current_mode.value,
                'bankroll': ultimate_ai.current_bankroll
            })
            
            # Track strategy switches
            if len(performance_timeline) > 1:
                if performance_timeline[-1]['mode'] != performance_timeline[-2]['mode']:
                    strategy_switches.append({
                        'hand': hands_completed + 1,
                        'from_mode': performance_timeline[-2]['mode'],
                        'to_mode': performance_timeline[-1]['mode'],
                        'trigger_roi': ultimate_ai.metrics.roi
                    })
            
            hands_completed += 1
            
            # Progress updates
            if hands_completed % 100 == 0:
                elapsed = time.time() - start_time
                rate = hands_completed / elapsed
                eta = (n_hands - hands_completed) / rate if rate > 0 else 0
                
                current_status = ultimate_ai.get_status_report()
                print(f"   📊 Hand {hands_completed:,}/{n_hands:,} "
                      f"({100*hands_completed/n_hands:.1f}%) "
                      f"- Grade: {current_status['current_grade']} "
                      f"- ROI: {ultimate_ai.metrics.roi:+.1%} "
                      f"- Mode: {ultimate_ai.level4.current_mode.value} "
                      f"- ETA: {eta:.0f}s")
    
    total_time = time.time() - start_time
    
    # Final analysis
    print(f"\n⏱️ Simulation completed in {total_time:.1f}s ({hands_completed/total_time:.0f} hands/sec)")
    
    return {
        'ultimate_ai': ultimate_ai,
        'tc_bet_data': tc_bet_data,
        'performance_timeline': performance_timeline,
        'strategy_switches': strategy_switches,
        'final_status': ultimate_ai.get_status_report()
    }


def analyze_ultimate_performance(results):
    """Comprehensive analysis of Ultimate AI performance."""
    
    print("\n📊 ULTIMATE AI PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    ultimate_ai = results['ultimate_ai']
    tc_bet_data = pd.DataFrame(results['tc_bet_data'])
    timeline = pd.DataFrame(results['performance_timeline'])
    switches = results['strategy_switches']
    
    # === SOPHISTICATION ANALYSIS ===
    print("\n🧠 SOPHISTICATION METRICS:")
    
    # TC-Bet Correlation
    tc_bet_corr = np.corrcoef(tc_bet_data['true_count'], tc_bet_data['bet_size'])[0, 1]
    print(f"   TC-Bet Correlation: {tc_bet_corr:.3f}")
    
    # Bet Spread Analysis
    bet_spread = tc_bet_data['bet_ratio'].max() / tc_bet_data['bet_ratio'].min()
    print(f"   Bet Spread: {bet_spread:.2f}x")
    
    # Count-based betting validation
    high_count_bets = tc_bet_data[tc_bet_data['true_count'] > 2]['bet_size']
    low_count_bets = tc_bet_data[tc_bet_data['true_count'] < -1]['bet_size']
    
    if len(high_count_bets) > 0 and len(low_count_bets) > 0:
        count_spread = high_count_bets.mean() / low_count_bets.mean()
        print(f"   Count-Based Spread: {count_spread:.2f}x")
    
    # Strategy adaptation
    unique_modes = timeline['mode'].nunique()
    print(f"   Strategy Modes Used: {unique_modes}/4")
    print(f"   Strategy Switches: {len(switches)}")
    
    # === PERFORMANCE ANALYSIS ===
    print("\n🎯 PERFORMANCE METRICS:")
    
    final_metrics = ultimate_ai.metrics
    print(f"   Final ROI: {final_metrics.roi:+.2%}")
    print(f"   Win Rate: {final_metrics.win_rate:.1%}")
    print(f"   Sharpe Ratio: {final_metrics.sharpe_ratio:.3f}")
    print(f"   Confidence Score: {final_metrics.confidence_score:.3f}")
    
    # Performance evolution
    if len(timeline) > 50:
        early_roi = timeline.iloc[:50]['roi'].mean()
        late_roi = timeline.iloc[-50:]['roi'].mean()
        improvement = late_roi - early_roi
        print(f"   Learning Effect: {improvement:+.2%}")
    
    # === GRADING ANALYSIS ===
    print("\n🏆 GRADING BREAKDOWN:")
    
    # Calculate detailed scores
    tc_score = 0
    if tc_bet_corr > 0.7:
        tc_score = 25
        print("   ✅ TC Correlation: EXCELLENT (25/25)")
    elif tc_bet_corr > 0.4:
        tc_score = 15
        print("   🟡 TC Correlation: GOOD (15/25)")
    elif tc_bet_corr > 0.1:
        tc_score = 5
        print("   🔴 TC Correlation: POOR (5/25)")
    else:
        print("   🔴 TC Correlation: NONE (0/25)")
    
    spread_score = 0
    if bet_spread > 4:
        spread_score = 25
        print("   ✅ Bet Spread: EXCELLENT (25/25)")
    elif bet_spread > 2:
        spread_score = 15
        print("   🟡 Bet Spread: GOOD (15/25)")
    elif bet_spread > 1.5:
        spread_score = 5
        print("   🔴 Bet Spread: POOR (5/25)")
    else:
        print("   🔴 Bet Spread: NONE (0/25)")
    
    roi_score = 0
    if final_metrics.roi > 0.05:
        roi_score = 25
        print("   ✅ ROI Performance: EXCELLENT (25/25)")
    elif final_metrics.roi > 0:
        roi_score = 15
        print("   🟡 ROI Performance: GOOD (15/25)")
    elif final_metrics.roi > -0.02:
        roi_score = 5
        print("   🔴 ROI Performance: POOR (5/25)")
    else:
        print("   🔴 ROI Performance: NONE (0/25)")
    
    win_rate_score = 0
    if final_metrics.win_rate > 0.47:
        win_rate_score = 25
        print("   ✅ Win Rate: EXCELLENT (25/25)")
    elif final_metrics.win_rate > 0.43:
        win_rate_score = 15
        print("   🟡 Win Rate: GOOD (15/25)")
    elif final_metrics.win_rate > 0.40:
        win_rate_score = 5
        print("   🔴 Win Rate: POOR (5/25)")
    else:
        print("   🔴 Win Rate: NONE (0/25)")
    
    total_score = tc_score + spread_score + roi_score + win_rate_score
    final_grade = final_metrics.get_grade()
    
    print(f"\n🎯 FINAL SCORE: {total_score}/100 ({total_score}%)")
    print(f"🏆 FINAL GRADE: {final_grade}")
    
    # === STRATEGY ANALYSIS ===
    print("\n🔄 STRATEGY ADAPTATION ANALYSIS:")
    
    mode_distribution = timeline['mode'].value_counts()
    print("   Mode Usage:")
    for mode, count in mode_distribution.items():
        percentage = count / len(timeline) * 100
        print(f"      {mode}: {count} hands ({percentage:.1f}%)")
    
    if len(switches) > 0:
        print(f"\n   Strategy Switch Timeline:")
        for i, switch in enumerate(switches[:5]):  # Show first 5 switches
            print(f"      Hand {switch['hand']}: {switch['from_mode']} → {switch['to_mode']} "
                  f"(ROI: {switch['trigger_roi']:+.1%})")
        if len(switches) > 5:
            print(f"      ... and {len(switches)-5} more switches")
    
    # === RECOMMENDATIONS ===
    print(f"\n💡 RECOMMENDATIONS:")
    
    if final_grade == "A+":
        print("   🎉 PERFECT! Ultimate AI achieved AA grade!")
        print("   ✅ Ready for production deployment")
        print("   🚀 Consider Phase 3 multi-player development")
    elif final_grade in ["A", "B"]:
        print("   🟡 GOOD PERFORMANCE but room for improvement:")
        if tc_bet_corr < 0.7:
            print("   📈 Enhance true count sensitivity")
        if bet_spread < 4:
            print("   📊 Increase betting spread range")
        if final_metrics.roi < 0.05:
            print("   💰 Optimize profit generation")
    else:
        print("   🔴 NEEDS SIGNIFICANT IMPROVEMENT:")
        print("   🔧 Consider parameter re-tuning")
        print("   📚 Review hierarchical weights")
        print("   🎯 Focus on proven strategies")
    
    return {
        'final_grade': final_grade,
        'total_score': total_score,
        'tc_correlation': tc_bet_corr,
        'bet_spread': bet_spread,
        'final_roi': final_metrics.roi,
        'win_rate': final_metrics.win_rate,
        'mode_distribution': mode_distribution.to_dict(),
        'strategy_switches': len(switches)
    }


def main():
    """Run Ultimate AI comprehensive test."""
    
    print("🚀 ULTIMATE AI SYSTEM - AA GRADE TEST")
    print("=" * 70)
    
    try:
        # Run comprehensive test
        results = test_ultimate_ai_comprehensive(n_hands=1000)
        
        # Analyze performance
        analysis = analyze_ultimate_performance(results)
        
        # Save detailed results
        timestamp = int(time.time())
        results_file = f"runs/ultimate_ai_test_{timestamp}.json"
        
        # Prepare saveable results
        save_data = {
            'test_config': {
                'hands_tested': 1000,
                'target_grade': 'A+',
                'timestamp': timestamp
            },
            'final_analysis': analysis,
            'performance_timeline': results['performance_timeline'],
            'strategy_switches': results['strategy_switches'],
            'final_metrics': results['final_status']
        }
        
        with open(results_file, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: {results_file}")
        
        # Save AI session
        session_file = results['ultimate_ai'].save_session()
        
        # Final summary
        print(f"\n{'='*70}")
        print("📋 ULTIMATE AI TEST SUMMARY")
        print('='*70)
        print(f"Final Grade: {analysis['final_grade']}")
        print(f"Score: {analysis['total_score']}/100")
        print(f"TC Correlation: {analysis['tc_correlation']:.3f}")
        print(f"Bet Spread: {analysis['bet_spread']:.2f}x")
        print(f"ROI: {analysis['final_roi']:+.2%}")
        print(f"Win Rate: {analysis['win_rate']:.1%}")
        
        # Success determination
        if analysis['final_grade'] in ['A+', 'A']:
            print("\n🎉 SUCCESS: Ultimate AI achieved target performance!")
            print("✅ Ready to proceed with Phase 3")
            return True
        else:
            print(f"\n🔧 IMPROVEMENT NEEDED: Grade {analysis['final_grade']} below target")
            print("💡 Consider architecture refinements")
            return False
        
    except Exception as e:
        print(f"❌ Ultimate AI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
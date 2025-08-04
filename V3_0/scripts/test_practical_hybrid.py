#!/usr/bin/env python3
"""
Practical Hybrid AI Test

Test the practical approach: proven performance + selective enhancements.
"""

import sys
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from practical_hybrid_ai import create_practical_hybrid_ai
from betting_environment_fixed import create_fixed_betting_env


def test_practical_hybrid_ai(n_hands: int = 1000):
    """Test the Practical Hybrid AI system."""
    
    print("🎯 PRACTICAL HYBRID AI TEST")
    print("=" * 60)
    print(f"Philosophy: Proven Performance + Selective Enhancement")
    print(f"Target: AA Grade (90%+)")
    print(f"Testing {n_hands:,} hands...")
    print()
    
    # Create Practical AI
    hybrid_ai = create_practical_hybrid_ai(initial_bankroll=10000)
    
    # Create environment
    env = create_fixed_betting_env(
        seed=42,
        initial_bankroll=10000.0,
        min_bet=25.0,
        max_bet=500.0,
        risk_aversion=0.05
    )
    
    # Performance tracking
    hand_data = []
    cards_this_shoe = []
    shoe_count = 0
    
    hands_completed = 0
    start_time = time.time()
    
    print("🎮 Starting practical AI simulation...")
    
    while hands_completed < n_hands:
        # Reset for new hand
        obs, _ = env.reset()
        
        # Simulate realistic card tracking
        if hands_completed % 50 == 0:  # New shoe every 50 hands
            cards_this_shoe = []
            shoe_count += 1
            hybrid_ai.card_counter.running_count = 0
            hybrid_ai.card_counter.cards_seen = 0
        
        # Simulate dealt cards (simplified)
        player_total = int(obs[0])
        dealer_up = int(obs[1])
        usable_ace = bool(obs[2])
        
        # Generate realistic true count variation
        if hands_completed % 10 == 0:  # Update count every 10 hands
            # Simulate cards seen
            new_cards = []
            for _ in range(np.random.randint(4, 8)):  # 4-8 cards per update
                card_vals = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
                weights = [1,1,1,1,1,1,1,1,4,1,1,1,1]  # 10-value cards more common
                new_cards.append(np.random.choice(card_vals, p=np.array(weights)/sum(weights)))
            
            cards_this_shoe.extend(new_cards)
            hybrid_ai.update_result(0, 0, new_cards)  # Update count only
        
        # AI bet decision
        ai_bet = hybrid_ai.decide_bet_size(
            min_bet=env.min_bet,
            max_bet=env.max_bet
        )
        
        # Set bet in environment
        env.set_bet_amount(ai_bet)
        
        # AI play decision
        ai_action = hybrid_ai.decide_play_action(
            player_total=player_total,
            dealer_up=dealer_up,
            usable_ace=usable_ace,
            can_double=True,  # Assume doubling available
            can_split=False   # Simplified - no splitting
        )
        
        # Execute action
        obs, reward, done, truncated, info = env.step(ai_action)
        
        if done or truncated:
            # Update AI with result
            hybrid_ai.update_result(ai_bet, reward)
            
            # Track hand data
            metrics = hybrid_ai.get_performance_metrics()
            hand_data.append({
                'hand': hands_completed + 1,
                'bet_size': ai_bet,
                'outcome': reward,
                'true_count': hybrid_ai.card_counter.true_count,
                'count_multiplier': hybrid_ai.card_counter.get_bet_multiplier(),
                'current_roi': metrics.get('total_roi', 0),
                'bankroll': metrics.get('current_bankroll', 10000),
                'grade': hybrid_ai.get_grade()
            })
            
            hands_completed += 1
            
            # Progress updates
            if hands_completed % 200 == 0:
                elapsed = time.time() - start_time
                rate = hands_completed / elapsed
                eta = (n_hands - hands_completed) / rate if rate > 0 else 0
                
                current_metrics = hybrid_ai.get_performance_metrics()
                print(f"   📊 Hand {hands_completed:,}/{n_hands:,} "
                      f"({100*hands_completed/n_hands:.1f}%) "
                      f"- Grade: {hybrid_ai.get_grade()} "
                      f"- ROI: {current_metrics.get('total_roi', 0):+.1%} "
                      f"- TC: {current_metrics.get('true_count', 0):+.1f} "
                      f"- ETA: {eta:.0f}s")
    
    total_time = time.time() - start_time
    print(f"\n⏱️ Simulation completed in {total_time:.1f}s ({hands_completed/total_time:.0f} hands/sec)")
    
    return {
        'hybrid_ai': hybrid_ai,
        'hand_data': hand_data,
        'cards_tracked': len(cards_this_shoe),
        'shoes_played': shoe_count
    }


def analyze_practical_performance(results):
    """Analyze Practical Hybrid AI performance."""
    
    print("\n📊 PRACTICAL HYBRID AI ANALYSIS")
    print("=" * 60)
    
    hybrid_ai = results['hybrid_ai']
    hand_data = pd.DataFrame(results['hand_data'])
    
    # Get final metrics
    final_metrics = hybrid_ai.get_performance_metrics()
    final_grade = hybrid_ai.get_grade()
    
    # === CORE PERFORMANCE ===
    print("\n🎯 CORE PERFORMANCE METRICS:")
    print(f"   Final Grade: {final_grade}")
    print(f"   ROI: {final_metrics['total_roi']:+.2%}")
    print(f"   Win Rate: {final_metrics['win_rate']:.1%}")
    print(f"   Hands Played: {final_metrics['hands_played']:,}")
    print(f"   Final Bankroll: ${final_metrics['current_bankroll']:,.2f}")
    
    # === SOPHISTICATION METRICS ===
    print("\n🧠 SOPHISTICATION ANALYSIS:")
    print(f"   TC-Bet Correlation: {final_metrics['tc_bet_correlation']:.3f}")
    print(f"   Bet Spread: {final_metrics['bet_spread']:.2f}x")
    print(f"   Sharpe Ratio: {final_metrics['sharpe_ratio']:.3f}")
    print(f"   Cards Tracked: {results['cards_tracked']:,}")
    
    # Validate card counting effectiveness
    if len(hand_data) > 100:
        high_count_hands = hand_data[hand_data['true_count'] > 2]
        low_count_hands = hand_data[hand_data['true_count'] < 0]
        
        if len(high_count_hands) > 0 and len(low_count_hands) > 0:
            high_count_avg_bet = high_count_hands['bet_size'].mean()
            low_count_avg_bet = low_count_hands['bet_size'].mean()
            practical_spread = high_count_avg_bet / low_count_avg_bet
            
            print(f"   Practical Count Spread: {practical_spread:.2f}x")
            print(f"   High Count Avg Bet: ${high_count_avg_bet:.2f}")
            print(f"   Low Count Avg Bet: ${low_count_avg_bet:.2f}")
    
    # === GRADING BREAKDOWN ===
    print("\n🏆 DETAILED GRADING:")
    
    score_breakdown = {
        'tc_correlation': 0,
        'bet_spread': 0,
        'roi_performance': 0,
        'win_rate': 0
    }
    
    # TC Correlation scoring
    tc_corr = final_metrics['tc_bet_correlation']
    if tc_corr > 0.7:
        score_breakdown['tc_correlation'] = 25
        print("   ✅ TC Correlation: EXCELLENT (25/25)")
    elif tc_corr > 0.4:
        score_breakdown['tc_correlation'] = 15
        print("   🟡 TC Correlation: GOOD (15/25)")
    elif tc_corr > 0.1:
        score_breakdown['tc_correlation'] = 5
        print("   🔴 TC Correlation: POOR (5/25)")
    else:
        print("   🔴 TC Correlation: NONE (0/25)")
    
    # Bet Spread scoring
    spread = final_metrics['bet_spread']
    if spread > 4:
        score_breakdown['bet_spread'] = 25
        print("   ✅ Bet Spread: EXCELLENT (25/25)")
    elif spread > 2:
        score_breakdown['bet_spread'] = 15
        print("   🟡 Bet Spread: GOOD (15/25)")
    elif spread > 1.5:
        score_breakdown['bet_spread'] = 5
        print("   🔴 Bet Spread: POOR (5/25)")
    else:
        print("   🔴 Bet Spread: NONE (0/25)")
    
    # ROI scoring
    roi = final_metrics['total_roi']
    if roi > 0.05:
        score_breakdown['roi_performance'] = 25
        print("   ✅ ROI: EXCELLENT (25/25)")
    elif roi > 0:
        score_breakdown['roi_performance'] = 15
        print("   🟡 ROI: GOOD (15/25)")
    elif roi > -0.02:
        score_breakdown['roi_performance'] = 5
        print("   🔴 ROI: POOR (5/25)")
    else:
        print("   🔴 ROI: NONE (0/25)")
    
    # Win Rate scoring
    win_rate = final_metrics['win_rate']
    if win_rate > 0.47:
        score_breakdown['win_rate'] = 25
        print("   ✅ Win Rate: EXCELLENT (25/25)")
    elif win_rate > 0.43:
        score_breakdown['win_rate'] = 15
        print("   🟡 Win Rate: GOOD (15/25)")
    elif win_rate > 0.40:
        score_breakdown['win_rate'] = 5
        print("   🔴 Win Rate: POOR (5/25)")
    else:
        print("   🔴 Win Rate: NONE (0/25)")
    
    total_score = sum(score_breakdown.values())
    
    print(f"\n🎯 TOTAL SCORE: {total_score}/100 ({total_score}%)")
    print(f"🏆 COMPUTED GRADE: {final_grade}")
    
    # === PERFORMANCE EVOLUTION ===
    print("\n📈 PERFORMANCE EVOLUTION:")
    
    if len(hand_data) >= 200:
        early_hands = hand_data.iloc[:200]
        late_hands = hand_data.iloc[-200:]
        
        early_roi = early_hands['current_roi'].iloc[-1]
        late_roi = late_hands['current_roi'].iloc[-1]
        
        improvement = late_roi - early_roi
        print(f"   Learning Effect: {improvement:+.2%}")
        
        # Grade progression
        early_grades = early_hands['grade'].value_counts()
        late_grades = late_hands['grade'].value_counts()
        
        print(f"   Early Period Grades: {dict(early_grades)}")
        print(f"   Late Period Grades: {dict(late_grades)}")
    
    # === FINAL VERDICT ===
    print(f"\n🎖️ FINAL VERDICT:")
    
    if final_grade == "A+":
        print("   🎉 OUTSTANDING! Practical AI achieved AA grade!")
        print("   ✅ Perfect balance of performance and sophistication")
        print("   🚀 Ready for production deployment")
    elif final_grade == "A":
        print("   🎊 EXCELLENT! Very close to perfect performance")
        print("   ✅ Strong practical results with good sophistication")
        print("   🔧 Minor optimizations could reach A+")
    elif final_grade == "B":
        print("   👍 GOOD! Solid practical performance")
        print("   🟡 Room for improvement in sophistication")
        print("   📈 Consider enhancing card counting sensitivity")
    else:
        print("   🔴 NEEDS IMPROVEMENT")
        print("   🛠️ Review core strategy implementation")
        print("   📚 Consider returning to simpler approaches")
    
    return {
        'final_grade': final_grade,
        'total_score': total_score,
        'score_breakdown': score_breakdown,
        'final_metrics': final_metrics,
        'approach_assessment': 'Practical Hybrid'
    }


def main():
    """Run Practical Hybrid AI test."""
    
    print("🎯 PRACTICAL HYBRID AI - THE SMART APPROACH")
    print("=" * 70)
    print("Philosophy: Take what works + add proven enhancements only")
    print()
    
    try:
        # Run test
        results = test_practical_hybrid_ai(n_hands=1500)
        
        # Analyze
        analysis = analyze_practical_performance(results)
        
        # Save results
        timestamp = int(time.time())
        results_file = f"runs/practical_hybrid_test_{timestamp}.json"
        
        save_data = {
            'test_config': {
                'approach': 'Practical Hybrid AI',
                'hands_tested': 1500,
                'philosophy': 'Proven performance + selective enhancement'
            },
            'analysis': analysis,
            'hand_data': results['hand_data']
        }
        
        with open(results_file, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: {results_file}")
        
        # Save AI session
        session_file = results['hybrid_ai'].save_session()
        
        # === COMPARISON SUMMARY ===
        print(f"\n{'='*70}")
        print("📊 APPROACH COMPARISON SUMMARY")
        print('='*70)
        
        approaches = [
            ("Simple AI (Fixed)", "B", "+0.51%", "1.0x", "0.000"),
            ("Advanced AI", "D", "-28.00%", "2.6x", "0.004"),
            ("Ultimate AI", "D", "-17.89%", "1.14x", "0.035"),
            ("Practical Hybrid", analysis['final_grade'], 
             f"{analysis['final_metrics']['total_roi']:+.2%}",
             f"{analysis['final_metrics']['bet_spread']:.2f}x",
             f"{analysis['final_metrics']['tc_bet_correlation']:.3f}")
        ]
        
        print(f"{'Approach':<20} {'Grade':<6} {'ROI':<8} {'Spread':<7} {'TC-Corr':<7}")
        print("-" * 60)
        for approach, grade, roi, spread, tc_corr in approaches:
            print(f"{approach:<20} {grade:<6} {roi:<8} {spread:<7} {tc_corr:<7}")
        
        # Final recommendation
        print(f"\n💡 FINAL RECOMMENDATION:")
        
        if analysis['final_grade'] in ['A+', 'A']:
            print("🎉 SUCCESS! Practical Hybrid AI is the optimal approach!")
            print("✅ Achieved target performance with smart design")
            print("🚀 Ready to proceed with Phase 3")
            return True
        else:
            print("🤔 Mixed results - further optimization needed")
            print("💭 Consider fine-tuning practical parameters")
            return False
        
    except Exception as e:
        print(f"❌ Practical Hybrid test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
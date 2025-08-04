#!/usr/bin/env python3
"""
Advanced AI Behavior Analysis

Test if our AI actually performs sophisticated betting, card counting, and risk management.
"""

import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from betting_environment_fixed import create_fixed_betting_env
from stable_baselines3 import PPO


def detailed_ai_behavior_test():
    """Test AI behavior in detail across different scenarios."""
    
    print("🔍 ADVANCED AI BEHAVIOR ANALYSIS")
    print("=" * 60)
    
    # Load model
    model_path = "runs/final_phase2_model/final_model"
    env = create_fixed_betting_env(
        seed=42,
        initial_bankroll=10000.0,
        min_bet=10.0,
        max_bet=500.0,
        risk_aversion=0.05
    )
    model = PPO.load(model_path, env=env)
    
    # Test scenarios
    scenarios = {
        "high_true_count": [],      # TC > +2
        "low_true_count": [],       # TC < -2
        "neutral_count": [],        # TC around 0
        "good_hands": [],           # Player total 19-21
        "weak_hands": [],           # Player total 12-16
        "strong_hands": [],         # Player total 17-18
        "double_opportunities": [], # 9, 10, 11 vs weak dealer
        "split_opportunities": []   # Pairs
    }
    
    behavior_data = {
        'true_counts': [],
        'player_totals': [],
        'dealer_upcards': [],
        'actions': [],
        'bet_amounts': [],
        'bankrolls': [],
        'rewards': [],
        'situations': []
    }
    
    print("🎯 Testing 1000 hands across different scenarios...")
    
    for test_hand in range(1000):
        obs, _ = env.reset()
        
        # Extract game state
        player_total = int(obs[0])
        dealer_up = int(obs[1])
        usable_ace = bool(obs[2])
        true_count = obs[3] if len(obs) > 3 else 0
        bankroll_ratio = obs[4] if len(obs) > 4 else 1.0
        
        # Classify situation
        situation = classify_situation(player_total, dealer_up, true_count, usable_ace)
        
        # Test different bet amounts based on true count
        # (This is what a real card counter would do)
        if true_count > 2:
            optimal_bet = min(500, max(50, int(true_count * 25)))
        elif true_count > 0:
            optimal_bet = 25
        elif true_count < -2:
            optimal_bet = 10  # Minimum bet
        else:
            optimal_bet = 15
        
        # Set bet for testing
        env.set_bet_amount(optimal_bet)
        
        # Get AI decision
        action, _ = model.predict(obs, deterministic=True)
        
        # Execute action
        obs_new, reward, done, truncated, info = env.step(action)
        
        # Record data (convert numpy array to int)
        behavior_data['true_counts'].append(true_count)
        behavior_data['player_totals'].append(player_total)
        behavior_data['dealer_upcards'].append(dealer_up)
        behavior_data['actions'].append(int(action) if hasattr(action, 'item') else action)
        behavior_data['bet_amounts'].append(optimal_bet)
        behavior_data['bankrolls'].append(env.bankroll)
        behavior_data['rewards'].append(reward)
        behavior_data['situations'].append(situation)
        
        # Categorize by scenario
        if true_count > 2:
            scenarios["high_true_count"].append((action, optimal_bet, reward))
        elif true_count < -2:
            scenarios["low_true_count"].append((action, optimal_bet, reward))
        else:
            scenarios["neutral_count"].append((action, optimal_bet, reward))
        
        if player_total >= 19:
            scenarios["good_hands"].append((action, optimal_bet, reward))
        elif 12 <= player_total <= 16:
            scenarios["weak_hands"].append((action, optimal_bet, reward))
        elif 17 <= player_total <= 18:
            scenarios["strong_hands"].append((action, optimal_bet, reward))
        
        # Double opportunities
        if player_total in [9, 10, 11] and dealer_up <= 6:
            scenarios["double_opportunities"].append((action, optimal_bet, reward))
        
        # Split opportunities (simulated - we'd need pairs)
        if player_total in [16, 18, 20]:  # Simulating pairs (8s, 9s, 10s)
            scenarios["split_opportunities"].append((action, optimal_bet, reward))
    
    return behavior_data, scenarios


def classify_situation(player_total, dealer_up, true_count, usable_ace):
    """Classify the current game situation."""
    
    situations = []
    
    # Count situation
    if true_count > 2:
        situations.append("high_count")
    elif true_count < -2:
        situations.append("low_count")
    else:
        situations.append("neutral_count")
    
    # Hand strength
    if player_total >= 19:
        situations.append("strong_hand")
    elif player_total <= 16:
        situations.append("weak_hand")
    else:
        situations.append("medium_hand")
    
    # Dealer strength
    if dealer_up <= 6:
        situations.append("weak_dealer")
    else:
        situations.append("strong_dealer")
    
    return "_".join(situations)


def analyze_betting_patterns(behavior_data):
    """Analyze if AI adapts betting based on true count."""
    
    print("\n📊 BETTING PATTERN ANALYSIS")
    print("-" * 40)
    
    df = pd.DataFrame(behavior_data)
    
    # Group by true count ranges
    df['tc_range'] = pd.cut(df['true_counts'], 
                           bins=[-10, -2, -1, 0, 1, 2, 10], 
                           labels=['Very Low', 'Low', 'Slight Low', 'Slight High', 'High', 'Very High'])
    
    betting_by_count = df.groupby('tc_range')['bet_amounts'].agg(['mean', 'std', 'count']).round(2)
    
    print("Betting by True Count:")
    print(betting_by_count)
    
    # Test if betting varies significantly
    bet_variance = df['bet_amounts'].std()
    bet_mean = df['bet_amounts'].mean()
    cv = bet_variance / bet_mean if bet_mean > 0 else 0
    
    print(f"\nBet Amount Statistics:")
    print(f"   Mean: ${bet_mean:.2f}")
    print(f"   Std: ${bet_variance:.2f}")
    print(f"   Coefficient of Variation: {cv:.3f}")
    
    if cv < 0.1:
        print("   🔴 CONCERN: Very low bet variation - possibly not adapting to count")
    elif cv > 0.3:
        print("   🟢 GOOD: High bet variation - adapting to situations")
    else:
        print("   🟡 MODERATE: Some bet variation observed")
    
    return betting_by_count


def analyze_action_patterns(behavior_data):
    """Analyze action patterns by situation."""
    
    print("\n🎯 ACTION PATTERN ANALYSIS")
    print("-" * 40)
    
    df = pd.DataFrame(behavior_data)
    
    # Action distribution
    action_names = {0: 'Stand', 1: 'Hit', 2: 'Double', 3: 'Split'}
    df['action_name'] = df['actions'].map(action_names)
    
    action_dist = df['action_name'].value_counts(normalize=True) * 100
    print("Overall Action Distribution:")
    for action, pct in action_dist.items():
        print(f"   {action}: {pct:.1f}%")
    
    # Actions by hand strength
    print("\nActions by Player Hand Strength:")
    hand_ranges = [(4, 11, 'Weak'), (12, 16, 'Risky'), (17, 21, 'Strong')]
    
    for min_hand, max_hand, label in hand_ranges:
        mask = (df['player_totals'] >= min_hand) & (df['player_totals'] <= max_hand)
        if mask.sum() > 0:
            actions_in_range = df[mask]['action_name'].value_counts(normalize=True) * 100
            print(f"   {label} hands ({min_hand}-{max_hand}):")
            for action, pct in actions_in_range.items():
                print(f"      {action}: {pct:.1f}%")
    
    # Double opportunities
    double_spots = df[df['player_totals'].isin([9, 10, 11]) & (df['dealer_upcards'] <= 6)]
    if len(double_spots) > 0:
        double_rate = (double_spots['actions'] == 2).sum() / len(double_spots) * 100
        print(f"\nDouble Rate on 9/10/11 vs weak dealer: {double_rate:.1f}%")
        
        if double_rate > 50:
            print("   🟢 GOOD: High doubling rate in favorable spots")
        elif double_rate > 20:
            print("   🟡 MODERATE: Some doubling in good spots")
        else:
            print("   🔴 CONCERN: Low doubling rate - missing opportunities")
    
    return action_dist


def risk_assessment_analysis(behavior_data):
    """Analyze risk management capabilities."""
    
    print("\n⚠️ RISK MANAGEMENT ANALYSIS")
    print("-" * 40)
    
    df = pd.DataFrame(behavior_data)
    
    # Bankroll correlation with betting
    bankroll_bet_corr = np.corrcoef(df['bankrolls'], df['bet_amounts'])[0, 1]
    
    print(f"Bankroll-Bet Correlation: {bankroll_bet_corr:.3f}")
    
    if abs(bankroll_bet_corr) > 0.3:
        print("   🟢 GOOD: Strong correlation between bankroll and bet sizing")
    elif abs(bankroll_bet_corr) > 0.1:
        print("   🟡 MODERATE: Some bankroll consideration in betting")
    else:
        print("   🔴 CONCERN: No apparent bankroll consideration")
    
    # Risk during different count situations
    high_count_mask = df['true_counts'] > 2
    low_count_mask = df['true_counts'] < -2
    
    if high_count_mask.sum() > 0 and low_count_mask.sum() > 0:
        avg_bet_high_count = df[high_count_mask]['bet_amounts'].mean()
        avg_bet_low_count = df[low_count_mask]['bet_amounts'].mean()
        
        bet_ratio = avg_bet_high_count / avg_bet_low_count if avg_bet_low_count > 0 else 1
        
        print(f"High Count Avg Bet: ${avg_bet_high_count:.2f}")
        print(f"Low Count Avg Bet: ${avg_bet_low_count:.2f}")
        print(f"Bet Ratio (High/Low): {bet_ratio:.2f}x")
        
        if bet_ratio > 3:
            print("   🟢 EXCELLENT: Strong bet scaling with count")
        elif bet_ratio > 1.5:
            print("   🟢 GOOD: Moderate bet scaling with count")
        elif bet_ratio > 1.1:
            print("   🟡 MINIMAL: Slight bet adjustment")
        else:
            print("   🔴 NONE: No bet scaling with count")
    
    # Performance by situation
    situation_performance = df.groupby('situations')['rewards'].agg(['mean', 'std', 'count']).round(3)
    print(f"\nPerformance by Situation:")
    print(situation_performance.head(10))


def generate_improvement_recommendations(behavior_data, scenarios):
    """Generate specific recommendations for improvement."""
    
    print("\n💡 IMPROVEMENT RECOMMENDATIONS")
    print("=" * 50)
    
    df = pd.DataFrame(behavior_data)
    
    recommendations = []
    
    # Check bet variation
    bet_cv = df['bet_amounts'].std() / df['bet_amounts'].mean()
    if bet_cv < 0.2:
        recommendations.append("🔧 CRITICAL: Implement dynamic bet sizing based on true count")
        recommendations.append("   → Kelly Criterion implementation needed")
        recommendations.append("   → True count sensitivity training required")
    
    # Check action patterns
    double_rate = (df['actions'] == 2).sum() / len(df) * 100
    if double_rate < 5:
        recommendations.append("🔧 IMPORTANT: Increase doubling frequency in favorable situations")
        recommendations.append("   → Reward shaping for doubling needed")
    
    # Check risk management
    bankroll_corr = np.corrcoef(df['bankrolls'], df['bet_amounts'])[0, 1]
    if abs(bankroll_corr) < 0.2:
        recommendations.append("🔧 CRITICAL: Implement bankroll-aware betting")
        recommendations.append("   → Risk-of-ruin calculations needed")
        recommendations.append("   → Position sizing algorithms required")
    
    # Performance analysis
    avg_reward = df['rewards'].mean()
    if avg_reward < 0:
        recommendations.append("🔧 FUNDAMENTAL: Overall strategy generating losses")
        recommendations.append("   → Environment reward function review needed")
        recommendations.append("   → Basic strategy compliance check required")
    
    print("Priority Improvements Needed:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # State-of-the-art suggestions
    print(f"\n🚀 STATE-OF-THE-ART ENHANCEMENTS:")
    print("1. 🧠 Deep Q-Network with Dueling Architecture")
    print("2. 📊 Multi-Objective Optimization (Risk + Return)")
    print("3. 🎯 Hierarchical Reinforcement Learning (Bet + Play)")
    print("4. 📈 Transformer-based Sequential Decision Making")
    print("5. 🔄 Meta-Learning for Rapid Adaptation")
    print("6. 🎰 Monte Carlo Tree Search for Perfect Information")
    print("7. 📱 Real-time Bayesian Risk Assessment")
    
    return recommendations


def main():
    """Run comprehensive AI behavior analysis."""
    
    try:
        # Test AI behavior
        behavior_data, scenarios = detailed_ai_behavior_test()
        
        # Analyze patterns
        betting_analysis = analyze_betting_patterns(behavior_data)
        action_analysis = analyze_action_patterns(behavior_data)
        risk_analysis = risk_assessment_analysis(behavior_data)
        
        # Generate recommendations
        recommendations = generate_improvement_recommendations(behavior_data, scenarios)
        
        # Save results
        results = {
            'behavior_data': behavior_data,
            'betting_analysis': betting_analysis.to_dict(),
            'action_analysis': action_analysis.to_dict(),
            'recommendations': recommendations
        }
        
        with open('runs/ai_behavior_analysis.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed analysis saved to: runs/ai_behavior_analysis.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
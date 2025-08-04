#!/usr/bin/env python3
"""
B: Enhanced Adaptive AI Test - Comprehensive Comparison
"""

from enhanced_adaptive_ai import create_enhanced_adaptive_ai
from optimized_adaptive_ai import create_optimized_adaptive_ai
from betting_environment_fixed import create_fixed_betting_env
import time
import numpy as np

def run_enhanced_ai_test():
    """Test Enhanced Adaptive AI vs Optimized version"""
    print('🚀 ENHANCED ADAPTIVE AI vs OPTIMIZED COMPARISON TEST')
    print('=' * 60)
    
    # Test parameters
    n_hands = 2000  # Longer test for better analysis
    initial_bankroll = 10000.0
    min_bet = 25.0
    max_bet = 500.0
    
    # Create AIs
    print('\n📊 Creating AI Instances...')
    enhanced_ai = create_enhanced_adaptive_ai(initial_bankroll)
    optimized_ai = create_optimized_adaptive_ai(initial_bankroll)
    
    # Create environments
    enhanced_env = create_fixed_betting_env(seed=42, initial_bankroll=initial_bankroll, 
                                          min_bet=min_bet, max_bet=max_bet, risk_aversion=0.05)
    optimized_env = create_fixed_betting_env(seed=42, initial_bankroll=initial_bankroll,
                                           min_bet=min_bet, max_bet=max_bet, risk_aversion=0.05)
    
    print(f'\n🎯 Testing {n_hands} hands each...')
    
    # Test Enhanced AI
    print('\n🔥 ENHANCED AI TEST:')
    start_time = time.time()
    
    for i in range(n_hands):
        obs, _ = enhanced_env.reset()
        player_total, dealer_up, usable_ace = int(obs[0]), int(obs[1]), bool(obs[2])
        
        # Enhanced AI decision with true count simulation
        true_count = np.random.normal(0, 1.5)  # Simulated TC
        bet = enhanced_ai.decide_bet_size(min_bet, max_bet, true_count)
        enhanced_env.set_bet_amount(bet)
        
        action_str = enhanced_ai.decide_play_action(player_total, dealer_up, usable_ace)
        # Convert action to environment format
        action_map = {"hit": 0, "stand": 1, "double": 2, "split": 3}
        action = action_map.get(action_str, 1)  # Default to stand
        obs, reward, done, truncated, info = enhanced_env.step(action)
        
        if done or truncated:
            enhanced_ai.update_result(bet, reward)
            
            if (i+1) % 500 == 0:
                metrics = enhanced_ai.get_performance_metrics()
                print(f'   Hand {i+1}: ROI {metrics["current_roi"]:+.1%}, Crisis: {metrics["current_crisis_level"]}, Sharpe: {metrics["sharpe_ratio"]:.3f}')
    
    enhanced_time = time.time() - start_time
    
    # Test Optimized AI
    print('\n⚡ OPTIMIZED AI TEST:')
    start_time = time.time()
    
    for i in range(n_hands):
        obs, _ = optimized_env.reset()
        player_total, dealer_up, usable_ace = int(obs[0]), int(obs[1]), bool(obs[2])
        
        bet = optimized_ai.decide_bet_size(min_bet, max_bet)
        optimized_env.set_bet_amount(bet)
        
        action_str = optimized_ai.decide_play_action(player_total, dealer_up, usable_ace)
        # Convert action to environment format
        action_map = {"hit": 0, "stand": 1, "double": 2, "split": 3}
        action = action_map.get(action_str, 1)  # Default to stand
        obs, reward, done, truncated, info = optimized_env.step(action)
        
        if done or truncated:
            optimized_ai.update_result(bet, reward)
            
            if (i+1) % 500 == 0:
                metrics = optimized_ai.get_performance_metrics()
                print(f'   Hand {i+1}: ROI {metrics["total_roi"]:+.1%}, Crisis: {metrics["current_crisis_level"]}, Bankroll: ${metrics["current_bankroll"]:,.0f}')
    
    optimized_time = time.time() - start_time
    
    # Compare results
    print('\n' + '='*60)
    print('📊 FINAL COMPARISON RESULTS')
    print('='*60)
    
    enhanced_metrics = enhanced_ai.get_performance_metrics()
    optimized_metrics = optimized_ai.get_performance_metrics()
    
    print(f'\n🔥 ENHANCED ADAPTIVE AI:')
    print(f'   Final Bankroll: ${enhanced_metrics["current_bankroll"]:,.2f}')
    print(f'   ROI: {enhanced_metrics["current_roi"]:+.2%}')
    print(f'   Win Rate: {enhanced_metrics["win_rate"]:.1%}')
    print(f'   Sharpe Ratio: {enhanced_metrics["sharpe_ratio"]:.3f}')
    print(f'   Max Drawdown: {enhanced_metrics["max_drawdown"]:.1%}')
    print(f'   Crisis Level: {enhanced_metrics["current_crisis_level"]}')
    print(f'   Volatility: {enhanced_metrics["volatility"]:.3f}')
    print(f'   Risk of Ruin: {enhanced_metrics["risk_of_ruin"]:.1%}')
    print(f'   Execution Time: {enhanced_time:.1f}s')
    
    print(f'\n⚡ OPTIMIZED ADAPTIVE AI:')
    print(f'   Final Bankroll: ${optimized_metrics["current_bankroll"]:,.2f}')
    print(f'   ROI: {optimized_metrics["total_roi"]:+.2%}')
    print(f'   Win Rate: {optimized_metrics["win_rate"]:.1%}')
    print(f'   Crisis Level: {optimized_metrics["current_crisis_level"]}')
    print(f'   Execution Time: {optimized_time:.1f}s')
    
    # Performance comparison
    print(f'\n🏆 PERFORMANCE COMPARISON:')
    roi_diff = enhanced_metrics["current_roi"] - optimized_metrics["total_roi"]
    bankroll_diff = enhanced_metrics["current_bankroll"] - optimized_metrics["current_bankroll"]
    
    print(f'   ROI Difference: {roi_diff:+.2%} (Enhanced vs Optimized)')
    print(f'   Bankroll Difference: ${bankroll_diff:+,.2f}')
    
    if enhanced_metrics["sharpe_ratio"] > optimized_metrics.get("sharpe_ratio", 0):
        print(f'   🎯 Enhanced AI has BETTER risk-adjusted returns!')
    
    if enhanced_metrics["max_drawdown"] < optimized_metrics.get("max_drawdown", 1):
        print(f'   🛡️  Enhanced AI has BETTER risk management!')
    
    # Detailed status reports
    print(f'\n🔥 ENHANCED AI STATUS:')
    print(enhanced_ai.get_status_report())
    
    print(f'\n⚡ OPTIMIZED AI STATUS:')
    print(optimized_ai.get_status_report())
    
    return enhanced_metrics, optimized_metrics

if __name__ == "__main__":
    run_enhanced_ai_test() 
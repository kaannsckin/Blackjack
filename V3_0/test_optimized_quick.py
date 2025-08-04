#!/usr/bin/env python3
"""Quick test for optimized adaptive AI"""

from optimized_adaptive_ai import create_optimized_adaptive_ai
from betting_environment_fixed import create_fixed_betting_env
import time

print('🎯 QUICK OPTIMIZED TEST')
ai = create_optimized_adaptive_ai(10000)
env = create_fixed_betting_env(seed=42, initial_bankroll=10000.0, min_bet=25.0, max_bet=500.0, risk_aversion=0.05)

for i in range(1000):
    obs, _ = env.reset()
    player_total, dealer_up, usable_ace = int(obs[0]), int(obs[1]), bool(obs[2])
    
    bet = ai.decide_bet_size(env.min_bet, env.max_bet)
    env.set_bet_amount(bet)
    
    action = ai.decide_play_action(player_total, dealer_up, usable_ace)
    obs, reward, done, truncated, info = env.step(action)
    
    if done or truncated:
        ai.update_result(bet, reward)
        
        if (i+1) % 250 == 0:
            metrics = ai.get_performance_metrics()
            print(f'   Hand {i+1}: ROI {metrics["total_roi"]:+.1%}, Crisis: {metrics["current_crisis_level"]}, Bankroll: ${metrics["current_bankroll"]:,.0f}')

print('\n' + ai.get_status_report()) 
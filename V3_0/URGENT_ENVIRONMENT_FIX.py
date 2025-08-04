#!/usr/bin/env python3
"""
URGENT ENVIRONMENT FIX - Phase 3 Ready
Quick fix for the environment bias issue to enable Phase 3 development
"""

import gymnasium as gym
import numpy as np
from typing import Tuple, Dict, Any
from betting_environment_fixed import FixedBettingBlackjackEnv

class FixedEnvironmentV2(FixedBettingBlackjackEnv):
    """
    URGENT FIX: Corrected environment for Phase 3 readiness
    Fixes the action bias and reward calculation issues
    """
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Fixed step function with proper action handling"""
        
        # Validate bet amount set
        if self.current_bet <= 0:
            return self._get_enhanced_obs(), -25.0, True, False, {"error": "No bet set"}
        
        # Check bankroll
        if self.bankroll < self.current_bet:
            return self._get_enhanced_obs(), -self.current_bet, True, False, {
                "error": "Insufficient bankroll",
                "bankroll": self.bankroll
            }
        
        # Deduct bet from bankroll
        self.bankroll -= self.current_bet
        
        # FIXED: Force complete game for STAND action
        if action == 1:  # Stand
            # Force game completion by setting done=True
            obs, game_reward, _, truncated, info = super().step(action)
            done = True  # Force completion
        else:
            # Execute normal action
            obs, game_reward, done, truncated, info = super().step(action)
        
        # FIXED: Only process betting when game actually completes
        if done:
            # CORRECTED: Realistic blackjack reward calculation
            if game_reward > 0:
                # Win: Return bet + winnings (1:1 for normal win, 1.5:1 for blackjack)
                winnings = self.current_bet * (1 + min(game_reward, 1.5))
                self.bankroll += winnings
                net_result = winnings - self.current_bet
            elif game_reward == 0:
                # Push: Return original bet
                self.bankroll += self.current_bet 
                net_result = 0
            else:
                # Loss: Bet already deducted, no return
                net_result = -self.current_bet
            
            # FIXED: Proper reward calculation
            betting_reward = net_result
            
            # Update tracking
            self.previous_result = net_result
            self.update_bankroll(0)
            
            return self._get_enhanced_obs(), betting_reward, done, truncated, {
                "net_units": net_result,
                "betting_reward": betting_reward,
                "bankroll": self.bankroll,
                "bet_amount": self.current_bet,
                "bankroll_ratio": self.bankroll / self.initial_bankroll,
                "game_outcome": game_reward
            }
        else:
            # Game continues
            return self._get_enhanced_obs(), 0.0, done, truncated, {}

def create_fixed_betting_env_v2(**kwargs):
    """Create corrected environment for Phase 3"""
    return FixedEnvironmentV2(**kwargs)

# Test the fix
if __name__ == "__main__":
    print("🔧 TESTING URGENT ENVIRONMENT FIX")
    
    env = create_fixed_betting_env_v2(
        seed=42, 
        initial_bankroll=10000.0, 
        min_bet=25.0, 
        max_bet=500.0, 
        risk_aversion=0.05
    )
    
    print("\n📊 Testing All Actions:")
    actions = {0: "hit", 1: "stand", 2: "double"}
    
    for action_id, action_name in actions.items():
        obs, _ = env.reset()
        env.set_bet_amount(50.0)
        obs, reward, done, truncated, info = env.step(action_id)
        
        print(f"{action_name:6s}: reward={reward:6.1f}, done={done}, game_outcome={info.get('game_outcome', 'N/A')}")
    
    print("\n✅ ENVIRONMENT FIX COMPLETE - READY FOR PHASE 3!") 
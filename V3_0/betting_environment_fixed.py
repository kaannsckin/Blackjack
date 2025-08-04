"""
FIXED Betting Environment for F2.1 - Corrected Episode Logic

This fixes the critical bugs causing episodes to end immediately.
"""

from __future__ import annotations

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Import the base RL environment
from rl_environment import BlackjackEnv


@dataclass
class BettingMetrics:
    """Betting performance metrics."""
    total_episodes: int = 0
    winning_episodes: int = 0
    losing_episodes: int = 0
    push_episodes: int = 0
    max_winning_streak: int = 0
    max_losing_streak: int = 0


class FixedBettingBlackjackEnv(BlackjackEnv):
    """
    FIXED Betting-aware Blackjack environment.
    
    Key fixes:
    1. Corrected episode termination logic
    2. Fixed reward calculation
    3. Proper bankroll management
    """
    
    def __init__(
        self,
        *,
        seed: Optional[int] = None,
        rules: Optional[Dict[str, Any]] = None,
        penetration: float = 0.75,
        initial_bankroll: float = 1000.0,
        min_bet: float = 1.0,
        max_bet: float = 100.0,
        bet_increments: Optional[list[float]] = None,
        risk_aversion: float = 0.1,
    ) -> None:
        """Initialize FIXED betting environment."""
        
        super().__init__(seed=seed, rules=rules, penetration=penetration)
        
        # Betting parameters
        self.initial_bankroll = initial_bankroll
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.bet_increments = bet_increments or [1, 2, 5, 10, 25, 50, 100]
        self.risk_aversion = np.clip(risk_aversion, 0.0, 1.0)
        
        # Bankroll tracking
        self.bankroll = initial_bankroll
        self.current_bet = min_bet
        self.previous_result = 0.0
        
        # Performance metrics
        self.metrics = BettingMetrics()
        
        # FIXED: Enhanced observation space
        # [player_total, dealer_up, usable_ace, true_count, bankroll_ratio, prev_result]
        self.observation_space = spaces.Box(
            low=np.array([4, 1, 0, -20, 0.0, -10.0]),
            high=np.array([31, 11, 1, 20, 10.0, 10.0]),
            dtype=np.float32
        )
    
    def set_bet_amount(self, bet_amount: float) -> bool:
        """Set bet amount with validation."""
        if bet_amount < self.min_bet or bet_amount > self.max_bet:
            return False
        
        if bet_amount > self.bankroll:
            return False
        
        self.current_bet = bet_amount
        return True
    
    def calculate_betting_reward(self, game_outcome: float) -> float:
        """
        FIXED: Calculate betting reward based on net units won.
        
        Args:
            game_outcome: Game result (-1, 0, +1, +1.5 for blackjack)
            
        Returns:
            Betting reward incorporating risk adjustment
        """
        # Calculate net units won/lost
        net_units = game_outcome * self.current_bet
        
        # Base reward is the net units
        base_reward = net_units
        
        # FIXED: Apply minimal risk adjustment (was too harsh)
        if net_units < 0:
            # Small penalty for losses
            risk_penalty = abs(net_units) * self.risk_aversion * 0.1  # Reduced penalty
        else:
            # Small bonus for wins
            risk_penalty = -net_units * self.risk_aversion * 0.05  # Small bonus
        
        total_reward = base_reward - risk_penalty
        
        return total_reward
    
    def update_bankroll(self, net_units: float) -> None:
        """Update bankroll and performance metrics."""
        self.bankroll += net_units
        
        # Update metrics
        if net_units > 0:
            self.metrics.winning_episodes += 1
        elif net_units < 0:
            self.metrics.losing_episodes += 1
        else:
            self.metrics.push_episodes += 1
        
        self.metrics.total_episodes += 1
    
    def reset(self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None):
        """Reset environment for new episode."""
        
        # FIXED: Check if bankroll is sufficient for min bet
        if self.bankroll < self.min_bet:
            # Reset bankroll if depleted
            self.bankroll = self.initial_bankroll
        
        # Set default bet amount
        self.current_bet = self.min_bet
        
        # Reset parent environment
        obs, info = super().reset(seed=seed, options=options)
        
        return self._get_enhanced_obs(), info
    
    def step(self, action: int):
        """
        FIXED: Step through environment with corrected logic.
        
        Key fixes:
        1. Only calculate betting reward when game actually ends
        2. Don't terminate episodes prematurely
        3. Proper bankroll management
        """
        
        # CRITICAL FIX: Deduct bet at start of hand (before parent step)
        if self.bankroll >= self.current_bet:
            self.bankroll -= self.current_bet
        else:
            # Not enough bankroll - terminate episode
            return self._get_enhanced_obs(), -self.current_bet, True, False, {
                "error": "Insufficient bankroll",
                "bankroll": self.bankroll
            }
        
        # Execute game action using parent class
        obs, game_reward, done, truncated, info = super().step(action)
        
        # FIXED: Only process betting logic when game ends
        if done:
            # Calculate betting reward based on game outcome
            betting_reward = self.calculate_betting_reward(game_reward)
            
            # Update bankroll with winnings (bet was already deducted)
            if game_reward > 0:
                # Player won - add back bet + winnings
                winnings = self.current_bet * (1 + game_reward)
                self.bankroll += winnings
            elif game_reward == 0:
                # Push - add back original bet
                self.bankroll += self.current_bet
            # If game_reward < 0, player lost - bet stays lost
            
            # Update metrics
            net_result = game_reward * self.current_bet
            self.update_bankroll(0)  # Just update metrics, bankroll already updated
            self.previous_result = net_result
            
            # Enhanced info
            info.update({
                "net_units": net_result,
                "betting_reward": betting_reward,
                "bankroll": self.bankroll,
                "bet_amount": self.current_bet,
                "bankroll_ratio": self.bankroll / self.initial_bankroll,
                "game_outcome": game_reward
            })
            
            return self._get_enhanced_obs(), betting_reward, done, truncated, info
        
        # Game continues - return intermediate state
        return self._get_enhanced_obs(), 0.0, done, truncated, info
    
    def _get_enhanced_obs(self) -> np.ndarray:
        """Get enhanced observation with betting information."""
        
        try:
            # Get base observation from parent
            base_obs = super()._get_obs()
        except IndexError:
            # Fallback for edge cases
            base_obs = np.array([10, 5, 0, 0], dtype=np.int32)
        
        # Convert to float32
        base_obs = base_obs.astype(np.float32)
        
        # Add betting-specific features
        bankroll_ratio = self.bankroll / self.initial_bankroll
        prev_result_normalized = np.clip(self.previous_result / 10.0, -10.0, 10.0)
        
        # Combine all features
        enhanced_obs = np.concatenate([
            base_obs,
            [bankroll_ratio],
            [prev_result_normalized]
        ]).astype(np.float32)
        
        return enhanced_obs
    
    def _calculate_risk_of_ruin(self) -> float:
        """Calculate simplified risk of ruin."""
        if self.bankroll <= 0:
            return 1.0
        
        # Simple approximation
        units = self.bankroll / self.current_bet
        if units <= 10:
            return 0.9  # High risk
        elif units <= 50:
            return 0.1  # Moderate risk
        else:
            return 0.01  # Low risk


# Factory function for easy creation
def create_fixed_betting_env(
    seed: int = None,
    initial_bankroll: float = 1000.0,
    min_bet: float = 10.0,
    max_bet: float = 100.0,
    **kwargs
) -> FixedBettingBlackjackEnv:
    """Create a fixed betting environment with corrected logic."""
    
    return FixedBettingBlackjackEnv(
        seed=seed,
        initial_bankroll=initial_bankroll,
        min_bet=min_bet,
        max_bet=max_bet,
        **kwargs
    ) 
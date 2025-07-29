"""
================================================================================
BETTING BLACKJACK RL ENVIRONMENT (Phase 2 - F2.1)
================================================================================

📋 **AMAÇ:**
   Phase 2 için betting strategy öğrenebilen genişletilmiş Blackjack RL environment.
   Net unit kazancı bazlı reward sistemi ve bankroll tracking.

🎯 **F2.1 ÖZELLİKLERİ:**
   • Unit-based reward calculation
   • Bankroll tracking ve management
   • Risk-adjusted reward function
   • Bet sizing integration

🏗️ **TEKNİK ÖZELLİKLER:**
   • Extended Observation: [player_total, dealer_up, usable_ace, true_count, bankroll, prev_result]
   • Betting Action Space: Continuous or discrete bet amounts
   • Enhanced Reward: Net units won/lost per episode
   • Risk Management: Bankroll protection ve risk metrics

================================================================================
"""

from __future__ import annotations

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Any, Dict, Tuple, Optional
from dataclasses import dataclass

from rl_environment import BlackjackEnv, ACTIONS


@dataclass
class BettingMetrics:
    """Betting performance ve risk metrics."""
    total_units_won: float = 0.0
    total_episodes: int = 0
    max_drawdown: float = 0.0
    peak_bankroll: float = 0.0
    current_streak: int = 0
    max_winning_streak: int = 0
    max_losing_streak: int = 0


class BettingBlackjackEnv(BlackjackEnv):
    """Betting-aware Blackjack environment for Phase 2 RL training."""
    
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
        """
        Initialize betting environment.
        
        Args:
            initial_bankroll: Starting bankroll in units
            min_bet: Minimum bet size in units
            max_bet: Maximum bet size in units  
            bet_increments: Discrete bet options (if None, use continuous)
            risk_aversion: Risk adjustment factor for rewards (0.0-1.0)
        """
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
        self.previous_result = 0.0  # Previous episode net result
        
        # Performance metrics
        self.metrics = BettingMetrics()
        
        # Enhanced observation space
        # [player_total, dealer_up, usable_ace, true_count, bankroll_ratio, prev_result]
        self.observation_space = spaces.Box(
            low=np.array([4, 1, 0, -20, 0.0, -10.0]),
            high=np.array([31, 11, 1, 20, 10.0, 10.0]),
            dtype=np.float32
        )
        
        # Betting action space - we'll start with discrete for F2.1
        if bet_increments:
            self.bet_action_space = spaces.Discrete(len(bet_increments))
        else:
            self.bet_action_space = spaces.Box(
                low=min_bet, high=max_bet, shape=(1,), dtype=np.float32
            )
    
    def set_bet_amount(self, bet_amount: float) -> bool:
        """
        Set bet amount for current episode.
        
        Args:
            bet_amount: Bet size in units
            
        Returns:
            True if bet is valid, False otherwise
        """
        if not (self.min_bet <= bet_amount <= self.max_bet):
            return False
        if bet_amount > self.bankroll:
            return False
            
        self.current_bet = bet_amount
        return True
    
    def set_bet_from_action(self, bet_action: int | float) -> bool:
        """
        Set bet amount from action space.
        
        Args:
            bet_action: Action index (discrete) or bet amount (continuous)
            
        Returns:
            True if bet is valid, False otherwise
        """
        if isinstance(bet_action, int) and self.bet_increments:
            # Discrete bet action
            if 0 <= bet_action < len(self.bet_increments):
                bet_amount = self.bet_increments[bet_action]
                return self.set_bet_amount(bet_amount)
        elif isinstance(bet_action, (float, np.floating)):
            # Continuous bet action
            bet_amount = np.clip(bet_action, self.min_bet, self.max_bet)
            return self.set_bet_amount(bet_amount)
        
        return False
    
    def calculate_betting_reward(self, game_outcome: float) -> float:
        """
        Calculate unit-based betting reward with risk adjustment.
        
        Args:
            game_outcome: Raw game outcome (-1, 0, 1 per hand)
            
        Returns:
            Risk-adjusted reward in units
        """
        # Base reward = units won/lost
        net_units = game_outcome * self.current_bet
        
        # Risk adjustment based on bet size relative to bankroll
        bet_ratio = self.current_bet / max(self.bankroll, 1.0)
        risk_penalty = self.risk_aversion * bet_ratio * abs(net_units)
        
        # Bankroll protection bonus/penalty
        bankroll_factor = 1.0
        if net_units < 0 and self.bankroll < self.initial_bankroll * 0.5:
            # Penalty for losing when bankroll is low
            bankroll_factor = 1.2
        elif net_units > 0 and self.bankroll > self.initial_bankroll * 1.5:
            # Bonus for winning when bankroll is high
            bankroll_factor = 0.9
        
        final_reward = net_units * bankroll_factor - risk_penalty
        return final_reward
    
    def update_bankroll(self, net_units: float) -> None:
        """Update bankroll and related metrics."""
        self.bankroll += net_units
        self.metrics.total_units_won += net_units
        
        # Update peak and drawdown
        if self.bankroll > self.metrics.peak_bankroll:
            self.metrics.peak_bankroll = self.bankroll
        
        current_drawdown = (self.metrics.peak_bankroll - self.bankroll) / self.metrics.peak_bankroll
        if current_drawdown > self.metrics.max_drawdown:
            self.metrics.max_drawdown = current_drawdown
        
        # Update streaks
        if net_units > 0:
            self.metrics.current_streak = max(0, self.metrics.current_streak) + 1
            self.metrics.max_winning_streak = max(
                self.metrics.max_winning_streak, self.metrics.current_streak
            )
        elif net_units < 0:
            self.metrics.current_streak = min(0, self.metrics.current_streak) - 1
            self.metrics.max_losing_streak = max(
                self.metrics.max_losing_streak, abs(self.metrics.current_streak)
            )
        else:
            self.metrics.current_streak = 0
    
    def reset(self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None):
        """Reset environment for new episode."""
        obs, info = super().reset(seed=seed, options=options)
        
        # Reset bet to minimum for new episode
        self.current_bet = self.min_bet
        
        # Update episode count
        self.metrics.total_episodes += 1
        
        return self._get_enhanced_obs(), info
    
    def step(self, action: int):
        """
        Step through environment with enhanced betting rewards.
        
        For F2.1, we focus on play actions only. Betting will be set separately.
        """
        # Use parent class for game logic
        obs, game_reward, done, truncated, info = super().step(action)
        
        if done:
            # Calculate betting-aware reward
            betting_reward = self.calculate_betting_reward(game_reward)
            
            # Update bankroll and metrics
            net_units = game_reward * self.current_bet
            self.update_bankroll(net_units)
            
            # Store result for next episode
            self.previous_result = net_units
            
            # Enhanced info with betting metrics
            info.update({
                "net_units": net_units,
                "betting_reward": betting_reward,
                "bankroll": self.bankroll,
                "bet_amount": self.current_bet,
                "bankroll_ratio": self.bankroll / self.initial_bankroll,
                "risk_of_ruin": self._calculate_risk_of_ruin(),
            })
            
            return self._get_enhanced_obs(), betting_reward, done, truncated, info
        
        return self._get_enhanced_obs(), 0.0, done, truncated, info
    
    def _get_enhanced_obs(self) -> np.ndarray:
        """Get enhanced observation with betting information."""
        # Get base observation safely
        try:
            base_obs = super()._get_obs()
        except IndexError:
            # Handle terminal state - use safe default observation
            base_obs = np.array([0, 1, 0, 0], dtype=np.int32)
        
        # Add betting features
        bankroll_ratio = self.bankroll / self.initial_bankroll
        prev_result_normalized = np.clip(self.previous_result / self.max_bet, -10.0, 10.0)
        
        enhanced_obs = np.array([
            float(base_obs[0]),  # player_total
            float(base_obs[1]),  # dealer_up
            float(base_obs[2]),  # usable_ace
            float(base_obs[3]),  # true_count
            bankroll_ratio,      # bankroll ratio
            prev_result_normalized,  # previous result
        ], dtype=np.float32)
        
        return enhanced_obs
    
    def _calculate_risk_of_ruin(self) -> float:
        """Calculate approximate risk of ruin percentage."""
        if self.bankroll <= 0:
            return 100.0
        
        # Simplified RoR calculation based on current bankroll
        # This is a basic approximation - can be enhanced later
        bet_ratio = self.current_bet / self.bankroll
        base_ror = (1 - self.bankroll / self.initial_bankroll) * 100
        betting_ror = bet_ratio * 50  # Simplified betting risk
        
        return np.clip(base_ror + betting_ror, 0.0, 100.0)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        episodes = max(self.metrics.total_episodes, 1)
        
        return {
            "total_episodes": self.metrics.total_episodes,
            "total_units_won": self.metrics.total_units_won,
            "avg_units_per_episode": self.metrics.total_units_won / episodes,
            "current_bankroll": self.bankroll,
            "bankroll_growth": (self.bankroll / self.initial_bankroll - 1) * 100,
            "max_drawdown_pct": self.metrics.max_drawdown * 100,
            "current_risk_of_ruin": self._calculate_risk_of_ruin(),
            "max_winning_streak": self.metrics.max_winning_streak,
            "max_losing_streak": self.metrics.max_losing_streak,
            "current_streak": self.metrics.current_streak,
        }


# Utility functions for F2.1 testing and validation

def test_betting_environment():
    """Test basic betting environment functionality."""
    print("🧪 Testing Betting Environment (F2.1)...")
    
    env = BettingBlackjackEnv(seed=42, initial_bankroll=100.0)
    
    # Test observation space
    obs, info = env.reset()
    print(f"✅ Enhanced observation shape: {obs.shape}")
    print(f"✅ Enhanced observation: {obs}")
    
    # Test betting
    success = env.set_bet_amount(5.0)
    print(f"✅ Set bet amount: {success}")
    
    # Test episode
    done = False
    total_reward = 0
    steps = 0
    
    while not done and steps < 10:
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        total_reward += reward
        steps += 1
    
    print(f"✅ Episode completed: {steps} steps, reward: {total_reward:.3f}")
    
    if done and "net_units" in info:
        print(f"✅ Net units: {info['net_units']:.3f}")
        print(f"✅ Bankroll: {info['bankroll']:.3f}")
        print(f"✅ Risk of Ruin: {info['risk_of_ruin']:.1f}%")
    
    # Performance summary
    summary = env.get_performance_summary()
    print(f"✅ Performance Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    test_betting_environment() 
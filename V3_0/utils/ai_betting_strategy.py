"""
AI Betting Strategy for F2.5 Motor Entegrasyonu

This module provides an AI-powered betting strategy that integrates trained
betting agents with the simulation engine.
"""

from __future__ import annotations

import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
import logging

# Stable Baselines3 imports
try:
    from stable_baselines3 import PPO, TD3, SAC
    from stable_baselines3.common.base_class import BaseAlgorithm
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False
    BaseAlgorithm = None

# Fallback imports
from .basic_strategy import BasicStrategy


@dataclass
class BettingConfig:
    """Configuration for AI betting strategy."""
    model_path: str
    algorithm: str = "ppo"  # ppo, td3, sac
    min_bet: float = 1.0
    max_bet: float = 100.0
    initial_bankroll: float = 10000.0
    risk_threshold: float = 0.01  # 1% risk of ruin limit
    fallback_strategy: str = "basic"  # fallback when AI fails
    use_validation: bool = True
    confidence_threshold: float = 0.7


class AIBettingStrategy:
    """
    AI-powered betting strategy using trained RL agents.
    
    F2.5 Implementation: Integrates trained betting models with simulation engine.
    """
    
    def __init__(self, config: BettingConfig):
        """
        Initialize AI betting strategy.
        
        Args:
            config: Configuration for the betting strategy
        """
        self.config = config
        self.model: Optional[BaseAlgorithm] = None
        self.fallback_strategy = BasicStrategy() if config.fallback_strategy == "basic" else None
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.stats = {
            "total_bets": 0,
            "ai_decisions": 0,
            "fallback_decisions": 0,
            "total_units_bet": 0.0,
            "avg_bet_size": 0.0,
        }
        
        # Current state tracking
        self.current_bankroll = config.initial_bankroll
        self.bet_history = []
        self.results_history = []
        
        # Load the trained model
        self._load_model()
    
    def _load_model(self) -> bool:
        """Load the trained betting model."""
        if not SB3_AVAILABLE:
            self.logger.warning("Stable-Baselines3 not available. Using fallback strategy.")
            return False
        
        model_path = Path(self.config.model_path)
        if not model_path.exists():
            self.logger.error(f"Model not found: {model_path}")
            return False
        
        try:
            # Load model based on algorithm type
            if self.config.algorithm.lower() == "ppo":
                self.model = PPO.load(str(model_path))
            elif self.config.algorithm.lower() == "td3":
                self.model = TD3.load(str(model_path))
            elif self.config.algorithm.lower() == "sac":
                self.model = SAC.load(str(model_path))
            else:
                raise ValueError(f"Unsupported algorithm: {self.config.algorithm}")
            
            self.logger.info(f"Successfully loaded {self.config.algorithm.upper()} model from {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.model = None
            return False
    
    def decide_bet(
        self, 
        player_total: int, 
        dealer_up: int, 
        usable_ace: bool, 
        true_count: float,
        current_bankroll: Optional[float] = None,
        previous_result: Optional[float] = None
    ) -> float:
        """
        Decide bet amount using AI model.
        
        Args:
            player_total: Player's total (for observation)
            dealer_up: Dealer's upcard
            usable_ace: Whether player has usable ace
            true_count: Current true count
            current_bankroll: Current bankroll (optional, uses tracked if None)
            previous_result: Previous hand result (optional)
            
        Returns:
            Bet amount in units
        """
        # Update bankroll if provided
        if current_bankroll is not None:
            self.current_bankroll = current_bankroll
        
        # Use AI model if available
        if self.model is not None:
            try:
                bet_amount = self._ai_bet_decision(
                    player_total, dealer_up, usable_ace, true_count, previous_result
                )
                self.stats["ai_decisions"] += 1
                
                # Validate and constrain bet
                bet_amount = self._validate_bet(bet_amount)
                
            except Exception as e:
                self.logger.warning(f"AI betting decision failed: {e}. Using fallback.")
                bet_amount = self._fallback_bet_decision(true_count)
                self.stats["fallback_decisions"] += 1
        else:
            # Use fallback strategy
            bet_amount = self._fallback_bet_decision(true_count)
            self.stats["fallback_decisions"] += 1
        
        # Update statistics
        self._update_stats(bet_amount)
        
        return bet_amount
    
    def _ai_bet_decision(
        self, 
        player_total: int, 
        dealer_up: int, 
        usable_ace: bool, 
        true_count: float,
        previous_result: Optional[float] = None
    ) -> float:
        """Make betting decision using AI model."""
        # Prepare observation (based on AdvancedBettingEnv observation space)
        # Simplified observation for simulation context
        bankroll_ratio = self.current_bankroll / self.config.initial_bankroll
        prev_result_normalized = 0.0 if previous_result is None else np.clip(previous_result / 10.0, -10.0, 10.0)
        
        # Basic observation features (matching training environment)
        obs = np.array([
            player_total,
            dealer_up,
            float(usable_ace),
            true_count,
            bankroll_ratio,
            prev_result_normalized
        ], dtype=np.float32)
        
        # If using AdvancedBettingEnv (49D), pad with zeros for missing features
        if hasattr(self.model, 'observation_space') and len(self.model.observation_space.shape) > 0:
            expected_obs_size = self.model.observation_space.shape[0]
            if expected_obs_size > len(obs):
                # Pad with zeros for advanced features not available in simulation
                padding = np.zeros(expected_obs_size - len(obs), dtype=np.float32)
                obs = np.concatenate([obs, padding])
        
        # Get model prediction
        action, _states = self.model.predict(obs, deterministic=True)
        
        # Parse action to get bet amount
        bet_amount = self._parse_action_to_bet(action)
        
        return bet_amount
    
    def _parse_action_to_bet(self, action: Union[np.ndarray, int, Dict]) -> float:
        """Parse model action to bet amount."""
        # Handle different action space types from training
        if isinstance(action, np.ndarray):
            if len(action) == 2:  # MultiDiscrete [play_action, bet_index]
                bet_index = int(action[1])
                bet_levels = [1, 2, 5, 10, 25, 50, 100]  # Default bet levels
                if 0 <= bet_index < len(bet_levels):
                    return float(bet_levels[bet_index])
                else:
                    return self.config.min_bet
            elif len(action) == 1:  # Continuous betting
                return float(np.clip(action[0], self.config.min_bet, self.config.max_bet))
        elif isinstance(action, dict):  # Dict action space
            if 'bet_amount' in action:
                return float(np.clip(action['bet_amount'], self.config.min_bet, self.config.max_bet))
        elif isinstance(action, (int, float)):  # Single value
            return float(np.clip(action, self.config.min_bet, self.config.max_bet))
        
        # Fallback to minimum bet
        return self.config.min_bet
    
    def _fallback_bet_decision(self, true_count: float) -> float:
        """Fallback betting decision using simple true count strategy."""
        # Simple Kelly-like betting based on true count
        if true_count <= 1:
            return self.config.min_bet
        elif true_count <= 2:
            return min(2.0, self.config.max_bet)
        elif true_count <= 3:
            return min(5.0, self.config.max_bet)
        elif true_count <= 4:
            return min(10.0, self.config.max_bet)
        else:
            return min(25.0, self.config.max_bet)
    
    def _validate_bet(self, bet_amount: float) -> float:
        """Validate and constrain bet amount."""
        # Basic constraints
        bet_amount = max(self.config.min_bet, min(bet_amount, self.config.max_bet))
        
        # Bankroll constraints (don't bet more than 10% of bankroll)
        max_bankroll_bet = self.current_bankroll * 0.1
        bet_amount = min(bet_amount, max_bankroll_bet)
        
        # Round to reasonable precision
        bet_amount = round(bet_amount, 2)
        
        return bet_amount
    
    def _update_stats(self, bet_amount: float) -> None:
        """Update betting statistics."""
        self.stats["total_bets"] += 1
        self.stats["total_units_bet"] += bet_amount
        self.stats["avg_bet_size"] = self.stats["total_units_bet"] / self.stats["total_bets"]
        
        # Store in history
        self.bet_history.append(bet_amount)
        
        # Keep only last 1000 bets in memory
        if len(self.bet_history) > 1000:
            self.bet_history = self.bet_history[-1000:]
    
    def update_result(self, net_result: float) -> None:
        """Update with hand result."""
        self.current_bankroll += net_result
        self.results_history.append(net_result)
        
        # Keep only last 1000 results in memory
        if len(self.results_history) > 1000:
            self.results_history = self.results_history[-1000:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get betting strategy statistics."""
        ai_ratio = self.stats["ai_decisions"] / max(1, self.stats["total_bets"])
        fallback_ratio = self.stats["fallback_decisions"] / max(1, self.stats["total_bets"])
        
        return {
            **self.stats,
            "ai_decision_ratio": ai_ratio,
            "fallback_decision_ratio": fallback_ratio,
            "current_bankroll": self.current_bankroll,
            "bankroll_change": self.current_bankroll - self.config.initial_bankroll,
            "roi": (self.current_bankroll - self.config.initial_bankroll) / self.config.initial_bankroll,
            "recent_avg_bet": np.mean(self.bet_history[-100:]) if self.bet_history else 0.0,
            "recent_results": np.sum(self.results_history[-100:]) if self.results_history else 0.0,
        }
    
    def reset_bankroll(self, new_bankroll: Optional[float] = None) -> None:
        """Reset bankroll to initial or specified amount."""
        self.current_bankroll = new_bankroll or self.config.initial_bankroll
        self.bet_history.clear()
        self.results_history.clear()


def create_ai_betting_strategy(
    model_path: str,
    algorithm: str = "ppo",
    min_bet: float = 1.0,
    max_bet: float = 100.0,
    **kwargs
) -> AIBettingStrategy:
    """
    Factory function to create AI betting strategy.
    
    Args:
        model_path: Path to trained model
        algorithm: Algorithm type (ppo, td3, sac)
        min_bet: Minimum bet amount
        max_bet: Maximum bet amount
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured AIBettingStrategy instance
    """
    config = BettingConfig(
        model_path=model_path,
        algorithm=algorithm,
        min_bet=min_bet,
        max_bet=max_bet,
        **kwargs
    )
    
    return AIBettingStrategy(config) 
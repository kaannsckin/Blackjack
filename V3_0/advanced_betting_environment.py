"""
Advanced Betting Environment with State-of-the-Art AI Integration

Combines the fixed betting environment with sophisticated AI betting system.
"""

from __future__ import annotations

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, List, Any, Optional, Tuple

# Import our components
from betting_environment_fixed import FixedBettingBlackjackEnv
from advanced_betting_ai import (
    create_advanced_betting_agent,
    AdvancedBettingConfig,
    HierarchicalBettingAgent
)


class AdvancedBettingEnvironment(FixedBettingBlackjackEnv):
    """
    Advanced betting environment with state-of-the-art AI integration.
    
    Features:
    - Kelly Criterion bet sizing
    - Advanced risk management
    - Transformer-based decision making
    - Multi-objective optimization
    - Real-time performance tracking
    """
    
    def __init__(
        self,
        *,
        seed: Optional[int] = None,
        rules: Optional[Dict[str, Any]] = None,
        penetration: float = 0.75,
        initial_bankroll: float = 10000.0,
        min_bet: float = 10.0,
        max_bet: float = 500.0,
        risk_aversion: float = 0.05,
        use_advanced_ai: bool = True,
        advanced_config: Optional[AdvancedBettingConfig] = None
    ) -> None:
        """Initialize advanced betting environment."""
        
        super().__init__(
            seed=seed,
            rules=rules,
            penetration=penetration,
            initial_bankroll=initial_bankroll,
            min_bet=min_bet,
            max_bet=max_bet,
            risk_aversion=risk_aversion
        )
        
        # Advanced AI system
        self.use_advanced_ai = use_advanced_ai
        if use_advanced_ai:
            if advanced_config is None:
                advanced_config = AdvancedBettingConfig()
            self.advanced_agent = create_advanced_betting_agent(advanced_config)
        else:
            self.advanced_agent = None
        
        # Enhanced tracking
        self.hand_count = 0
        self.session_stats = {
            'total_hands': 0,
            'ai_bet_decisions': 0,
            'kelly_bets': 0,
            'risk_adjusted_bets': 0,
            'advantage_positive_hands': 0,
            'advantage_negative_hands': 0
        }
        
        # Performance tracking
        self.performance_buffer = []
        self.bet_history = []
        self.outcome_history = []
        
        # Enhanced observation space for advanced features
        # [player_total, dealer_up, usable_ace, true_count, bankroll_ratio, prev_result,
        #  hand_count_ratio, deck_penetration, advantage_estimate, risk_score]
        self.observation_space = spaces.Box(
            low=np.array([4, 1, 0, -20, 0.0, -10.0, 0.0, 0.0, -0.1, 0.0]),
            high=np.array([31, 11, 1, 20, 10.0, 10.0, 1.0, 1.0, 0.1, 1.0]),
            dtype=np.float32
        )
    
    def reset(self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None):
        """Reset environment with advanced AI integration."""
        
        # Reset parent environment
        obs, info = super().reset(seed=seed, options=options)
        
        # Reset hand count for this shoe
        self.hand_count = 0
        
        # Get enhanced observation
        enhanced_obs = self._get_advanced_obs(obs)
        
        return enhanced_obs, info
    
    def step(self, action: int):
        """
        Step with advanced AI betting integration.
        
        The action parameter is for play decisions (hit/stand/double/split).
        Bet sizing is handled automatically by the advanced AI system.
        """
        
        # Get current state for advanced analysis
        current_obs = self._get_enhanced_obs()
        
        # Advanced AI bet sizing (if enabled)
        if self.use_advanced_ai and self.advanced_agent:
            optimal_bet = self._get_ai_bet_decision(current_obs)
            self.set_bet_amount(optimal_bet)
            self.session_stats['ai_bet_decisions'] += 1
        
        # Execute the parent step logic
        obs, reward, done, truncated, info = super().step(action)
        
        # Update advanced tracking
        self.hand_count += 1
        self.session_stats['total_hands'] += 1
        
        # Track performance for advanced AI
        if self.use_advanced_ai and self.advanced_agent and done:
            self._update_ai_performance(reward, info)
        
        # Get enhanced observation
        enhanced_obs = self._get_advanced_obs(obs)
        
        # Enhanced info
        if self.use_advanced_ai:
            info.update(self._get_advanced_info())
        
        return enhanced_obs, reward, done, truncated, info
    
    def _get_ai_bet_decision(self, observation: np.ndarray) -> float:
        """Get sophisticated bet decision from advanced AI."""
        
        # Get deck composition (simplified)
        deck_composition = self._estimate_deck_composition()
        
        # AI bet decision
        ai_bet = self.advanced_agent.decide_bet_size(
            observation=observation,
            bankroll=self.bankroll,
            bet_range=(self.min_bet, self.max_bet),
            deck_composition=deck_composition
        )
        
        # Track statistics
        if ai_bet > self.min_bet * 1.5:
            self.session_stats['kelly_bets'] += 1
        
        return ai_bet
    
    def _estimate_deck_composition(self) -> Dict[str, int]:
        """Estimate remaining deck composition (simplified)."""
        
        # In a real implementation, this would track dealt cards
        # For now, return a neutral deck composition
        cards_per_suit = 4
        return {
            'A': cards_per_suit, '2': cards_per_suit, '3': cards_per_suit,
            '4': cards_per_suit, '5': cards_per_suit, '6': cards_per_suit,
            '7': cards_per_suit, '8': cards_per_suit, '9': cards_per_suit,
            '10': cards_per_suit, 'J': cards_per_suit, 'Q': cards_per_suit, 'K': cards_per_suit
        }
    
    def _get_advanced_obs(self, base_obs: Optional[np.ndarray] = None) -> np.ndarray:
        """Get enhanced observation with advanced features."""
        
        if base_obs is None:
            base_obs = self._get_enhanced_obs()
        
        # Extract basic features
        player_total = base_obs[0]
        dealer_up = base_obs[1]
        usable_ace = base_obs[2]
        true_count = base_obs[3] if len(base_obs) > 3 else 0.0
        bankroll_ratio = base_obs[4] if len(base_obs) > 4 else 1.0
        prev_result = base_obs[5] if len(base_obs) > 5 else 0.0
        
        # Advanced features
        hand_count_ratio = self.hand_count / 100.0  # Normalize hand count
        deck_penetration = min(1.0, self.hand_count / 50.0)  # Estimate penetration
        
        # Advantage estimate (simplified)
        advantage_estimate = true_count * 0.005  # Basic Hi-Lo advantage
        
        # Risk score (if advanced AI available)
        risk_score = 0.0
        if self.use_advanced_ai and self.advanced_agent:
            try:
                risk_metrics = self.advanced_agent.risk_manager.assess_risk(
                    self.bankroll, self.current_bet, advantage_estimate
                )
                risk_score = risk_metrics.get('risk_score', 0.0)
            except:
                risk_score = 0.0
        
        # Combine all features
        advanced_obs = np.array([
            player_total,
            dealer_up,
            usable_ace,
            true_count,
            bankroll_ratio,
            prev_result,
            hand_count_ratio,
            deck_penetration,
            advantage_estimate,
            risk_score
        ], dtype=np.float32)
        
        return advanced_obs
    
    def _update_ai_performance(self, reward: float, info: Dict[str, Any]):
        """Update advanced AI performance tracking."""
        
        if not self.advanced_agent:
            return
        
        # Game state for AI update
        game_state = {
            'true_count': info.get('true_count', 0.0),
            'bankroll_before': info.get('bankroll', self.bankroll) + reward,
            'bankroll_after': self.bankroll
        }
        
        # Update AI performance
        self.advanced_agent.update_performance(
            bet_size=self.current_bet,
            play_outcome=reward,
            game_state=game_state
        )
        
        # Track in performance buffer
        self.performance_buffer.append({
            'bet_size': self.current_bet,
            'outcome': reward,
            'bankroll': self.bankroll,
            'true_count': game_state['true_count']
        })
        
        # Keep buffer manageable
        if len(self.performance_buffer) > 200:
            self.performance_buffer = self.performance_buffer[-100:]
    
    def _get_advanced_info(self) -> Dict[str, Any]:
        """Get advanced environment information."""
        
        info = {
            'session_stats': self.session_stats.copy(),
            'hand_count': self.hand_count,
            'advanced_ai_enabled': self.use_advanced_ai
        }
        
        # Add AI performance metrics if available
        if self.use_advanced_ai and self.advanced_agent:
            try:
                ai_metrics = self.advanced_agent.get_performance_metrics()
                info['ai_performance'] = ai_metrics
            except:
                pass
        
        return info
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary."""
        
        summary = {
            'session_stats': self.session_stats,
            'total_hands': self.hand_count,
            'final_bankroll': self.bankroll,
            'bankroll_change': self.bankroll - self.initial_bankroll,
            'roi': (self.bankroll - self.initial_bankroll) / self.initial_bankroll,
        }
        
        # Advanced AI summary
        if self.use_advanced_ai and self.advanced_agent:
            summary['ai_summary'] = self.advanced_agent.get_performance_metrics()
        
        # Performance buffer analysis
        if self.performance_buffer:
            outcomes = [entry['outcome'] for entry in self.performance_buffer]
            bet_sizes = [entry['bet_size'] for entry in self.performance_buffer]
            
            summary['recent_performance'] = {
                'avg_outcome': np.mean(outcomes),
                'outcome_std': np.std(outcomes),
                'avg_bet_size': np.mean(bet_sizes),
                'bet_size_std': np.std(bet_sizes),
                'win_rate': np.mean([outcome > 0 for outcome in outcomes])
            }
        
        return summary


# Factory function
def create_advanced_betting_env(
    seed: int = None,
    initial_bankroll: float = 10000.0,
    min_bet: float = 10.0,
    max_bet: float = 500.0,
    use_advanced_ai: bool = True,
    **kwargs
) -> AdvancedBettingEnvironment:
    """Create an advanced betting environment with state-of-the-art AI."""
    
    return AdvancedBettingEnvironment(
        seed=seed,
        initial_bankroll=initial_bankroll,
        min_bet=min_bet,
        max_bet=max_bet,
        use_advanced_ai=use_advanced_ai,
        **kwargs
    ) 
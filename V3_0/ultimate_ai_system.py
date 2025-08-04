"""
ULTIMATE AI SYSTEM - 4-Level Hierarchical Architecture

Combines all successful approaches for AA grade performance:
- Level 1: Performance Core (Proven Simple AI)
- Level 2: Feature Enhancement (Sophisticated algorithms)  
- Level 3: Real-Time Optimizer (Adaptive learning)
- Level 4: Meta-Controller (Strategic orchestration)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
import json
import time
from collections import deque, defaultdict

# Import our proven components
from betting_environment_fixed import create_fixed_betting_env
from advanced_betting_ai import AdvancedBettingConfig, create_advanced_betting_agent
from stable_baselines3 import PPO


class StrategyMode(Enum):
    """Different strategy modes for different situations."""
    CONSERVATIVE = "conservative"  # Safe performance guaranteed
    AGGRESSIVE = "aggressive"      # High sophistication 
    ADAPTIVE = "adaptive"          # Real-time optimization
    HYBRID = "hybrid"             # Balanced approach


@dataclass
class PerformanceMetrics:
    """Real-time performance tracking."""
    roi: float = 0.0
    win_rate: float = 0.0
    tc_correlation: float = 0.0
    bet_spread: float = 1.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    confidence_score: float = 0.5
    hands_played: int = 0
    
    def get_grade(self) -> str:
        """Calculate current performance grade."""
        score = 0
        if self.tc_correlation > 0.7: score += 25
        elif self.tc_correlation > 0.4: score += 15
        elif self.tc_correlation > 0.1: score += 5
        
        if self.bet_spread > 4: score += 25
        elif self.bet_spread > 2: score += 15
        elif self.bet_spread > 1.5: score += 5
        
        if self.roi > 0.05: score += 25
        elif self.roi > 0: score += 15
        elif self.roi > -0.02: score += 5
        
        if self.win_rate > 0.47: score += 25
        elif self.win_rate > 0.43: score += 15
        elif self.win_rate > 0.40: score += 5
        
        percentage = score / 100 * 100
        
        if percentage >= 90: return "A+"
        elif percentage >= 80: return "A"
        elif percentage >= 70: return "B"
        elif percentage >= 60: return "C"
        else: return "D"


class Level1_PerformanceCore:
    """Level 1: Proven performance baseline with simple strategies."""
    
    def __init__(self):
        self.name = "Performance Core"
        self.confidence = 0.95  # High confidence - proven to work
        
    def get_play_action(self, player_total: int, dealer_up: int, 
                       usable_ace: bool, **kwargs) -> int:
        """Proven basic strategy for play decisions."""
        
        # Enhanced basic strategy
        if usable_ace:
            # Soft totals
            if player_total >= 19:
                return 0  # Stand
            elif player_total == 18:
                return 0 if dealer_up <= 8 else 1  # Stand vs hit
            else:
                return 1  # Hit
        else:
            # Hard totals
            if player_total >= 17:
                return 0  # Stand
            elif player_total <= 11:
                return 1  # Hit  
            elif player_total in [9, 10, 11] and dealer_up <= 6:
                return 2 if 2 in [0, 1, 2, 3] else 1  # Double or hit
            elif player_total <= 16 and dealer_up >= 7:
                return 1  # Hit
            else:
                return 0  # Stand
    
    def get_bet_size(self, min_bet: float, max_bet: float, 
                    bankroll: float, **kwargs) -> float:
        """Conservative bet sizing with slight progression."""
        
        # Simple progression based on recent wins
        recent_results = kwargs.get('recent_results', [])
        
        base_bet = min_bet
        
        if len(recent_results) >= 3:
            recent_wins = sum(1 for r in recent_results[-3:] if r > 0)
            if recent_wins >= 2:
                base_bet = min_bet * 1.5  # Slight increase on wins
        
        # Bankroll protection
        max_safe_bet = bankroll * 0.02  # Max 2% of bankroll
        
        return min(base_bet, max_safe_bet, max_bet)


class Level2_FeatureEnhancement:
    """Level 2: Sophisticated algorithms and card counting."""
    
    def __init__(self):
        self.name = "Feature Enhancement"
        self.confidence = 0.7
        
        # Card counting systems
        self.hi_lo_count = 0
        self.true_count = 0
        self.deck_penetration = 0
        
        # Kelly Criterion parameters
        self.kelly_multiplier = 0.25
        self.advantage_estimates = deque(maxlen=50)
        
    def update_count(self, cards_seen: List[str]):
        """Update Hi-Lo count based on cards seen."""
        
        count_values = {
            '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
            '7': 0, '8': 0, '9': 0,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        }
        
        for card in cards_seen:
            self.hi_lo_count += count_values.get(card, 0)
        
        # Estimate true count (simplified)
        estimated_decks_remaining = max(1, 6 - self.deck_penetration * 6)
        self.true_count = self.hi_lo_count / estimated_decks_remaining
    
    def calculate_advantage(self, true_count: float) -> float:
        """Calculate player advantage from true count."""
        
        # Hi-Lo advantage estimation
        base_advantage = true_count * 0.005  # ~0.5% per true count
        
        # Adjust for playing deviations
        deviation_bonus = 0.001 if abs(true_count) > 2 else 0
        
        total_advantage = base_advantage + deviation_bonus
        
        # Track advantage estimates
        self.advantage_estimates.append(total_advantage)
        
        return max(-0.05, min(0.05, total_advantage))
    
    def kelly_bet_size(self, advantage: float, bankroll: float, 
                      bet_range: Tuple[float, float]) -> float:
        """Advanced Kelly Criterion bet sizing."""
        
        if advantage <= 0:
            return bet_range[0]  # Minimum bet on negative expectation
        
        # Kelly calculation
        win_prob = 0.48 + advantage
        kelly_fraction = advantage / 1.0  # Simplified for even money
        
        # Apply safety multiplier
        safe_fraction = kelly_fraction * self.kelly_multiplier
        
        # Calculate bet
        optimal_bet = safe_fraction * bankroll
        
        # Apply constraints
        final_bet = max(bet_range[0], 
                       min(optimal_bet, bet_range[1], bankroll * 0.1))
        
        return final_bet
    
    def get_enhanced_action(self, player_total: int, dealer_up: int,
                          true_count: float, **kwargs) -> int:
        """Enhanced play decisions based on true count."""
        
        # Basic strategy first
        basic_action = Level1_PerformanceCore().get_play_action(
            player_total, dealer_up, kwargs.get('usable_ace', False)
        )
        
        # True count deviations
        if true_count >= 2:
            # More aggressive on high counts
            if player_total == 16 and dealer_up == 10:
                return 0  # Stand instead of hit
            elif player_total == 15 and dealer_up == 10:
                return 0  # Stand instead of hit
            elif player_total == 12 and dealer_up in [2, 3]:
                return 0  # Stand instead of hit
        
        elif true_count <= -2:
            # More conservative on low counts
            if player_total == 12 and dealer_up in [4, 5, 6]:
                return 1  # Hit instead of stand
        
        return basic_action


class Level3_RealTimeOptimizer:
    """Level 3: Adaptive learning and real-time optimization."""
    
    def __init__(self, window_size: int = 100):
        self.name = "Real-Time Optimizer"
        self.confidence = 0.6
        self.window_size = window_size
        
        # Performance tracking
        self.performance_history = deque(maxlen=window_size)
        self.parameter_history = deque(maxlen=window_size)
        
        # Adaptive parameters
        self.aggression_factor = 1.0
        self.risk_tolerance = 0.05
        self.learning_rate = 0.01
        
    def update_performance(self, outcome: float, bet_size: float,
                          parameters: Dict[str, Any]):
        """Update performance tracking and adapt parameters."""
        
        roi = outcome / bet_size if bet_size > 0 else 0
        
        self.performance_history.append({
            'roi': roi,
            'outcome': outcome,
            'bet_size': bet_size,
            'timestamp': time.time()
        })
        
        self.parameter_history.append(parameters.copy())
        
        # Adaptive optimization
        if len(self.performance_history) >= 20:
            self._optimize_parameters()
    
    def _optimize_parameters(self):
        """Optimize parameters based on recent performance."""
        
        recent_performance = list(self.performance_history)[-20:]
        avg_roi = np.mean([p['roi'] for p in recent_performance])
        
        # Adjust aggression based on performance
        if avg_roi > 0.02:
            # Good performance - increase aggression slightly
            self.aggression_factor = min(1.5, self.aggression_factor + 0.05)
        elif avg_roi < -0.02:
            # Poor performance - decrease aggression
            self.aggression_factor = max(0.5, self.aggression_factor - 0.1)
        
        # Adjust risk tolerance
        volatility = np.std([p['roi'] for p in recent_performance])
        if volatility > 0.1:
            self.risk_tolerance = max(0.02, self.risk_tolerance - 0.01)
        else:
            self.risk_tolerance = min(0.1, self.risk_tolerance + 0.005)
    
    def get_optimized_bet(self, base_bet: float, enhanced_bet: float,
                         bankroll: float, confidence: float) -> float:
        """Real-time optimized bet sizing."""
        
        # Weighted combination based on confidence and performance
        recent_avg_roi = 0
        if len(self.performance_history) >= 10:
            recent_avg_roi = np.mean([p['roi'] for p in 
                                    list(self.performance_history)[-10:]])
        
        # Dynamic weighting
        if recent_avg_roi > 0 and confidence > 0.7:
            # Good performance - favor enhanced approach
            weight_enhanced = 0.7 * self.aggression_factor
        else:
            # Poor performance - favor conservative approach
            weight_enhanced = 0.3 * self.aggression_factor
        
        weight_base = 1.0 - weight_enhanced
        
        optimized_bet = (weight_base * base_bet + 
                        weight_enhanced * enhanced_bet)
        
        # Risk adjustment
        max_bet = bankroll * self.risk_tolerance
        
        return min(optimized_bet, max_bet)


class Level4_MetaController:
    """Level 4: Strategic orchestration and situation assessment."""
    
    def __init__(self):
        self.name = "Meta-Controller"
        self.current_mode = StrategyMode.CONSERVATIVE
        
        # Situation assessment
        self.market_conditions = "normal"
        self.risk_environment = "low"
        self.performance_trend = "stable"
        
        # Strategy switching logic
        self.mode_history = deque(maxlen=50)
        self.switch_cooldown = 0
        
    def assess_situation(self, metrics: PerformanceMetrics,
                        recent_performance: List[float]) -> StrategyMode:
        """Assess current situation and select optimal strategy."""
        
        # Reduce cooldown
        if self.switch_cooldown > 0:
            self.switch_cooldown -= 1
        
        # Situation factors
        performance_stable = len(recent_performance) < 10 or np.std(recent_performance) < 0.05
        currently_profitable = metrics.roi > 0
        high_confidence = metrics.confidence_score > 0.8
        sufficient_data = metrics.hands_played > 50
        
        # Strategy selection logic
        if not sufficient_data or self.switch_cooldown > 0:
            # Not enough data or in cooldown - stay conservative
            new_mode = StrategyMode.CONSERVATIVE
            
        elif currently_profitable and high_confidence and performance_stable:
            # Everything going well - can be aggressive
            new_mode = StrategyMode.AGGRESSIVE
            
        elif currently_profitable and performance_stable:
            # Doing okay - balanced approach
            new_mode = StrategyMode.HYBRID
            
        elif metrics.roi > -0.02:
            # Minor losses - adaptive optimization
            new_mode = StrategyMode.ADAPTIVE
            
        else:
            # Significant losses - back to conservative
            new_mode = StrategyMode.CONSERVATIVE
        
        # Implement mode change with cooldown
        if new_mode != self.current_mode:
            self.current_mode = new_mode
            self.switch_cooldown = 20  # 20 hand cooldown
            self.mode_history.append((new_mode, time.time()))
        
        return self.current_mode
    
    def get_strategy_weights(self, mode: StrategyMode) -> Dict[str, float]:
        """Get weighting for different strategy components."""
        
        weights = {
            StrategyMode.CONSERVATIVE: {
                'level1_weight': 0.8,  # Heavy emphasis on proven approach
                'level2_weight': 0.1,  # Minimal sophistication
                'level3_weight': 0.1,  # Minimal adaptation
                'risk_multiplier': 0.5  # Very conservative
            },
            StrategyMode.AGGRESSIVE: {
                'level1_weight': 0.2,  # Minimal basic approach
                'level2_weight': 0.6,  # Heavy sophistication
                'level3_weight': 0.2,  # Moderate adaptation
                'risk_multiplier': 1.5  # More aggressive
            },
            StrategyMode.HYBRID: {
                'level1_weight': 0.4,  # Balanced proven approach
                'level2_weight': 0.4,  # Balanced sophistication
                'level3_weight': 0.2,  # Some adaptation
                'risk_multiplier': 1.0  # Normal risk
            },
            StrategyMode.ADAPTIVE: {
                'level1_weight': 0.3,  # Some proven approach
                'level2_weight': 0.2,  # Less sophistication
                'level3_weight': 0.5,  # Heavy adaptation
                'risk_multiplier': 0.8  # Slightly conservative
            }
        }
        
        return weights[mode]


class UltimateAI:
    """
    The Ultimate 4-Level Hierarchical AI System.
    
    Combines all successful approaches for maximum performance and sophistication.
    """
    
    def __init__(self, initial_bankroll: float = 10000):
        # Initialize all levels
        self.level1 = Level1_PerformanceCore()
        self.level2 = Level2_FeatureEnhancement()
        self.level3 = Level3_RealTimeOptimizer()
        self.level4 = Level4_MetaController()
        
        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.session_data = []
        self.recent_results = deque(maxlen=20)
        
        # Game state
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.hands_played = 0
        
        print(f"🚀 ULTIMATE AI SYSTEM INITIALIZED")
        print(f"   💰 Initial Bankroll: ${initial_bankroll:,.2f}")
        print(f"   🏗️ 4-Level Architecture Active")
        
    def decide_action(self, player_total: int, dealer_up: int,
                     usable_ace: bool = False, 
                     true_count: float = 0,
                     available_actions: List[int] = None) -> int:
        """Make playing decision using hierarchical system."""
        
        if available_actions is None:
            available_actions = [0, 1]  # Stand, Hit
        
        # Get current strategy mode
        current_mode = self.level4.assess_situation(
            self.metrics, list(self.recent_results)
        )
        weights = self.level4.get_strategy_weights(current_mode)
        
        # Level 1: Basic strategy
        basic_action = self.level1.get_play_action(
            player_total, dealer_up, usable_ace
        )
        
        # Level 2: Enhanced strategy
        enhanced_action = self.level2.get_enhanced_action(
            player_total, dealer_up, true_count, usable_ace=usable_ace
        )
        
        # Weighted decision
        if weights['level1_weight'] > weights['level2_weight']:
            final_action = basic_action
        else:
            final_action = enhanced_action
        
        # Ensure action is available
        if final_action not in available_actions:
            final_action = available_actions[0]  # Default to first available
        
        return final_action
    
    def decide_bet_size(self, min_bet: float, max_bet: float,
                       true_count: float = 0,
                       cards_seen: List[str] = None) -> float:
        """Make betting decision using hierarchical system."""
        
        # Update card counting
        if cards_seen:
            self.level2.update_count(cards_seen)
        
        # Get current strategy mode
        current_mode = self.level4.assess_situation(
            self.metrics, list(self.recent_results)
        )
        weights = self.level4.get_strategy_weights(current_mode)
        
        # Level 1: Conservative bet
        base_bet = self.level1.get_bet_size(
            min_bet, max_bet, self.current_bankroll,
            recent_results=list(self.recent_results)
        )
        
        # Level 2: Sophisticated bet
        advantage = self.level2.calculate_advantage(true_count)
        enhanced_bet = self.level2.kelly_bet_size(
            advantage, self.current_bankroll, (min_bet, max_bet)
        )
        
        # Level 3: Optimized bet
        confidence = (weights['level1_weight'] * self.level1.confidence +
                     weights['level2_weight'] * self.level2.confidence)
        
        final_bet = self.level3.get_optimized_bet(
            base_bet, enhanced_bet, self.current_bankroll, confidence
        )
        
        # Apply risk multiplier from meta-controller
        final_bet *= weights['risk_multiplier']
        
        # Final constraints
        final_bet = max(min_bet, min(final_bet, max_bet, 
                                   self.current_bankroll * 0.15))
        
        return final_bet
    
    def update_result(self, bet_size: float, outcome: float):
        """Update system with hand result."""
        
        self.hands_played += 1
        self.current_bankroll += outcome
        self.recent_results.append(outcome)
        
        # Update Level 3 optimization
        self.level3.update_performance(outcome, bet_size, {
            'bet_size': bet_size,
            'outcome': outcome,
            'bankroll': self.current_bankroll
        })
        
        # Update metrics
        self._update_metrics()
        
        # Log session data
        self.session_data.append({
            'hand': self.hands_played,
            'bet_size': bet_size,
            'outcome': outcome,
            'bankroll': self.current_bankroll,
            'mode': self.level4.current_mode.value,
            'grade': self.metrics.get_grade()
        })
    
    def _update_metrics(self):
        """Update performance metrics."""
        
        if self.hands_played == 0:
            return
        
        # Calculate ROI
        self.metrics.roi = (self.current_bankroll - self.initial_bankroll) / self.initial_bankroll
        
        # Calculate win rate
        if len(self.recent_results) > 0:
            self.metrics.win_rate = sum(1 for r in self.recent_results if r > 0) / len(self.recent_results)
        
        # Calculate bet spread (simplified)
        if len(self.session_data) > 1:
            bet_sizes = [s['bet_size'] for s in self.session_data]
            self.metrics.bet_spread = max(bet_sizes) / min(bet_sizes) if min(bet_sizes) > 0 else 1
        
        # Calculate Sharpe ratio (simplified)
        if len(self.recent_results) > 5:
            returns = list(self.recent_results)
            self.metrics.sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        
        # Update confidence
        grade = self.metrics.get_grade()
        grade_scores = {'A+': 0.95, 'A': 0.85, 'B': 0.75, 'C': 0.65, 'D': 0.5}
        self.metrics.confidence_score = grade_scores.get(grade, 0.5)
        
        # Update hands played
        self.metrics.hands_played = self.hands_played
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        
        return {
            'current_grade': self.metrics.get_grade(),
            'performance_metrics': {
                'roi': f"{self.metrics.roi:+.2%}",
                'win_rate': f"{self.metrics.win_rate:.1%}",
                'tc_correlation': f"{self.metrics.tc_correlation:.3f}",
                'bet_spread': f"{self.metrics.bet_spread:.2f}x",
                'sharpe_ratio': f"{self.metrics.sharpe_ratio:.3f}",
                'confidence': f"{self.metrics.confidence_score:.3f}"
            },
            'system_status': {
                'current_mode': self.level4.current_mode.value,
                'hands_played': self.hands_played,
                'current_bankroll': f"${self.current_bankroll:,.2f}",
                'bankroll_change': f"${self.current_bankroll - self.initial_bankroll:+,.2f}"
            },
            'level_status': {
                'level1_confidence': self.level1.confidence,
                'level2_confidence': self.level2.confidence,
                'level3_confidence': self.level3.confidence,
                'level4_mode': self.level4.current_mode.value
            }
        }
    
    def save_session(self, filename: str = None):
        """Save session data to file."""
        
        if filename is None:
            timestamp = int(time.time())
            filename = f"runs/ultimate_ai_session_{timestamp}.json"
        
        session_summary = {
            'session_data': self.session_data,
            'final_metrics': self.get_status_report(),
            'configuration': {
                'initial_bankroll': self.initial_bankroll,
                'total_hands': self.hands_played,
                'final_grade': self.metrics.get_grade()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(session_summary, f, indent=2, default=str)
        
        print(f"💾 Session saved to: {filename}")
        return filename


# Factory function
def create_ultimate_ai(initial_bankroll: float = 10000) -> UltimateAI:
    """Create the Ultimate AI system."""
    return UltimateAI(initial_bankroll) 
"""
================================================================================
FAZ 4.0 - ADVANCED BUDGET OPTIMIZATION SYSTEM (F4.6)
================================================================================

📋 **AMAÇ:**
   FAZ 4.0 F4.6 - Hierarchical player analysis ve table dynamics'e dayalı
   sophisticated budget optimization ve dynamic bet sizing algoritması.

🎯 **F4.6 ÖZELLİKLERİ:**
   • Risk toleransına göre dynamic bet sizing
   • Player type composition bazlı risk adjustment
   • Table heat level'a göre bankroll protection
   • Multi-session budget tracking ve optimization
   • Kelly Criterion enhanced with player intelligence

🏗️ **OPTIMIZATION FEATURES:**
   • Hierarchical player type risk assessment
   • Table composition advantage calculation
   • Dynamic bankroll allocation
   • Heat-aware bet sizing
   • Performance-based adaptation

================================================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from collections import deque
import math

# Import hierarchical classification
from utils.hierarchical_player_classification import (
    HierarchicalPlayerClassifier, MainPlayerType, HierarchicalPlayerProfile
)

class RiskLevel(Enum):
    """Risk level categories for budget optimization"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    EXTREME = "extreme"

class BudgetStrategy(Enum):
    """Budget management strategies"""
    FLAT_BETTING = "flat_betting"              # Fixed bet size
    KELLY_CRITERION = "kelly_criterion"        # Mathematical optimal
    ENHANCED_KELLY = "enhanced_kelly"          # Kelly + player intelligence
    ADAPTIVE_SIZING = "adaptive_sizing"        # Dynamic based on table
    HEAT_AWARE = "heat_aware"                  # Casino heat consideration
    HIERARCHICAL = "hierarchical"              # Player type based

@dataclass
class BudgetMetrics:
    """Budget performance tracking metrics"""
    total_bankroll: float = 10000.0
    session_bankroll: float = 1000.0
    
    # Performance tracking
    total_hands_played: int = 0
    total_wagered: float = 0.0
    net_winnings: float = 0.0
    
    # Risk metrics
    max_drawdown: float = 0.0
    peak_bankroll: float = 10000.0
    current_streak: int = 0
    
    # Session tracking
    sessions_played: int = 0
    winning_sessions: int = 0
    losing_sessions: int = 0
    
    # Advanced metrics
    sharpe_ratio: float = 0.0
    kelly_fraction: float = 0.0
    risk_of_ruin: float = 0.0
    
    # Table-specific metrics
    player_type_performance: Dict[str, float] = field(default_factory=dict)
    table_heat_incidents: int = 0

@dataclass
class OptimizationContext:
    """Context for budget optimization decisions"""
    # Table composition
    player_types: Dict[MainPlayerType, int] = field(default_factory=dict)
    table_risk_level: float = 0.5
    table_heat_level: float = 0.0
    
    # Game state
    true_count: float = 0.0
    deck_penetration: float = 0.75
    position_advantage: float = 0.0
    
    # Session state
    session_hands: int = 0
    session_performance: float = 0.0
    recent_results: List[float] = field(default_factory=list)
    
    # Player intelligence
    classification_confidence: float = 0.0
    adaptation_opportunities: List[str] = field(default_factory=list)

class FAZ4BudgetOptimizer:
    """
    Advanced budget optimization system for FAZ 4.0.
    
    Combines hierarchical player analysis, table dynamics, and sophisticated
    mathematical models for optimal bet sizing and bankroll management.
    """
    
    def __init__(self,
                 initial_bankroll: float = 10000.0,
                 session_allocation: float = 0.1,  # 10% per session
                 base_bet_unit: float = 10.0,
                 risk_tolerance: float = 0.02,    # 2% risk of ruin
                 strategy: BudgetStrategy = BudgetStrategy.HIERARCHICAL):
        """
        Initialize FAZ 4.0 Budget Optimizer.
        
        Args:
            initial_bankroll: Starting bankroll amount
            session_allocation: Fraction of bankroll per session
            base_bet_unit: Base betting unit
            risk_tolerance: Acceptable risk of ruin
            strategy: Budget optimization strategy
        """
        self.initial_bankroll = initial_bankroll
        self.session_allocation = session_allocation
        self.base_bet_unit = base_bet_unit
        self.risk_tolerance = risk_tolerance
        self.strategy = strategy
        
        # Initialize metrics
        self.metrics = BudgetMetrics(
            total_bankroll=initial_bankroll,
            session_bankroll=initial_bankroll * session_allocation,
            peak_bankroll=initial_bankroll
        )
        
        # Optimization parameters
        self.optimization_params = self._initialize_optimization_params()
        
        # Player type risk assessments
        self.player_type_risks = self._initialize_player_type_risks()
        
        # Performance tracking
        self.session_history: List[Dict] = []
        self.bet_history: deque = deque(maxlen=100)
        self.result_history: deque = deque(maxlen=50)
        
        # Advanced features
        self.hierarchical_classifier = None  # Will be set externally
        self.kelly_calculator = KellyCalculator()
        
        # Logging
        self.logger = logging.getLogger("FAZ4BudgetOptimizer")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"FAZ 4.0 Budget Optimizer initialized")
        self.logger.info(f"Strategy: {strategy.value}, Bankroll: ${initial_bankroll:,.2f}")
    
    def _initialize_optimization_params(self) -> Dict[str, Any]:
        """Initialize optimization parameters for different strategies."""
        return {
            "kelly_multiplier": 0.25,          # Conservative Kelly fraction
            "heat_reduction_factor": 0.7,      # Bet reduction when heat detected
            "player_advantage_bonus": 0.3,     # Bonus for favorable player types
            "position_multiplier": 1.2,        # Late position advantage
            "count_correlation": 2.0,          # True count bet correlation
            
            # Risk management
            "max_bet_fraction": 0.05,          # Max 5% of bankroll per bet
            "session_stop_loss": 0.3,          # Stop at 30% session loss
            "session_stop_win": 2.0,           # Stop at 200% session win
            
            # Table dynamics
            "conservative_table_bonus": 0.2,   # Bonus vs conservative players
            "aggressive_table_penalty": 0.15,  # Penalty vs aggressive players
            "counter_table_caution": 0.5,      # Caution vs card counters
            
            # Heat management
            "heat_threshold": 0.3,             # Heat level threshold
            "camouflage_factor": 0.8,          # Bet reduction for camouflage
            "session_exit_heat": 0.7           # Exit session at high heat
        }
    
    def _initialize_player_type_risks(self) -> Dict[MainPlayerType, Dict[str, float]]:
        """Initialize risk assessments for different player types."""
        return {
            MainPlayerType.CONSERVATIVE: {
                "exploitability": 0.7,         # Easy to exploit
                "predictability": 0.8,         # Predictable behavior
                "aggression_risk": 0.1,        # Low aggression risk
                "opportunity_factor": 1.3      # Good opportunity for profit
            },
            MainPlayerType.AGGRESSIVE: {
                "exploitability": 0.4,         # Harder to exploit
                "predictability": 0.3,         # Unpredictable
                "aggression_risk": 0.8,        # High aggression risk
                "opportunity_factor": 0.8      # Lower opportunity
            },
            MainPlayerType.BASIC_STRATEGY: {
                "exploitability": 0.5,         # Moderate exploitation
                "predictability": 0.9,         # Very predictable
                "aggression_risk": 0.2,        # Low risk
                "opportunity_factor": 1.1      # Slight opportunity
            },
            MainPlayerType.CARD_COUNTER: {
                "exploitability": 0.2,         # Very hard to exploit
                "predictability": 0.6,         # Somewhat predictable
                "aggression_risk": 0.3,        # Moderate risk
                "opportunity_factor": 0.9,     # Follow their lead
                "intelligence_bonus": 0.4      # Learn from them
            },
            MainPlayerType.RANDOM: {
                "exploitability": 0.6,         # Moderate exploitation
                "predictability": 0.1,         # Unpredictable
                "aggression_risk": 0.5,        # Variable risk
                "opportunity_factor": 1.0      # Neutral
            },
            MainPlayerType.SUPERSTITIOUS: {
                "exploitability": 0.8,         # High exploitation
                "predictability": 0.4,         # Pattern-based
                "aggression_risk": 0.3,        # Moderate risk
                "opportunity_factor": 1.2      # Good opportunity
            }
        }
    
    def set_hierarchical_classifier(self, classifier: HierarchicalPlayerClassifier):
        """Set the hierarchical player classifier for advanced analysis."""
        self.hierarchical_classifier = classifier
        self.logger.info("Hierarchical classifier integrated with budget optimizer")
    
    def optimize_bet_size(self, 
                         context: OptimizationContext,
                         base_edge: float = 0.005) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate optimal bet size based on context and strategy.
        
        Args:
            context: Current optimization context
            base_edge: Base player edge (before adjustments)
            
        Returns:
            Optimal bet size and analysis details
        """
        # Calculate enhanced edge based on context
        enhanced_edge = self._calculate_enhanced_edge(base_edge, context)
        
        # Apply strategy-specific optimization
        if self.strategy == BudgetStrategy.HIERARCHICAL:
            bet_size, analysis = self._optimize_hierarchical(enhanced_edge, context)
        elif self.strategy == BudgetStrategy.ENHANCED_KELLY:
            bet_size, analysis = self._optimize_enhanced_kelly(enhanced_edge, context)
        elif self.strategy == BudgetStrategy.HEAT_AWARE:
            bet_size, analysis = self._optimize_heat_aware(enhanced_edge, context)
        elif self.strategy == BudgetStrategy.ADAPTIVE_SIZING:
            bet_size, analysis = self._optimize_adaptive(enhanced_edge, context)
        else:
            bet_size, analysis = self._optimize_kelly_basic(enhanced_edge, context)
        
        # Apply global constraints
        bet_size = self._apply_constraints(bet_size, context)
        
        # Record bet for tracking
        self._record_bet(bet_size, enhanced_edge, context, analysis)
        
        return bet_size, analysis
    
    def _calculate_enhanced_edge(self, base_edge: float, context: OptimizationContext) -> float:
        """Calculate enhanced player edge based on table intelligence."""
        enhanced_edge = base_edge
        
        # True count adjustment
        tc_adjustment = context.true_count * 0.005  # 0.5% per true count
        enhanced_edge += tc_adjustment
        
        # Position advantage
        enhanced_edge += context.position_advantage * 0.002
        
        # Player type advantage
        if self.hierarchical_classifier:
            type_advantage = self._calculate_player_type_advantage(context)
            enhanced_edge += type_advantage
        
        # Table heat penalty
        heat_penalty = context.table_heat_level * 0.01
        enhanced_edge -= heat_penalty
        
        return max(enhanced_edge, -0.02)  # Cap at -2% to prevent extreme negative bets
    
    def _calculate_player_type_advantage(self, context: OptimizationContext) -> float:
        """Calculate advantage based on player type composition."""
        if not context.player_types:
            return 0.0
        
        total_advantage = 0.0
        total_players = sum(context.player_types.values())
        
        for player_type, count in context.player_types.items():
            if player_type in self.player_type_risks:
                risk_data = self.player_type_risks[player_type]
                
                # Calculate type-specific advantage
                type_advantage = (
                    risk_data["exploitability"] * 0.01 +  # Up to 1% advantage
                    risk_data["opportunity_factor"] * 0.005 - 0.005  # Centered around 0
                )
                
                # Weight by player count
                weighted_advantage = type_advantage * (count / total_players)
                total_advantage += weighted_advantage
        
        return total_advantage
    
    def _optimize_hierarchical(self, edge: float, context: OptimizationContext) -> Tuple[float, Dict[str, Any]]:
        """Hierarchical player type based optimization."""
        # Base Kelly calculation
        kelly_fraction = self.kelly_calculator.calculate_kelly_fraction(
            edge, variance=0.04  # Typical blackjack variance
        )
        
        # Player type adjustments
        type_multiplier = 1.0
        if context.player_types:
            type_multiplier = self._calculate_type_multiplier(context.player_types)
        
        # Table dynamics adjustment
        dynamics_multiplier = self._calculate_dynamics_multiplier(context)
        
        # Heat awareness
        heat_multiplier = max(0.3, 1.0 - context.table_heat_level)
        
        # Combined multiplier
        total_multiplier = type_multiplier * dynamics_multiplier * heat_multiplier
        total_multiplier = np.clip(total_multiplier, 0.2, 2.0)  # Reasonable bounds
        
        # Calculate optimal bet
        optimal_fraction = kelly_fraction * total_multiplier * self.optimization_params["kelly_multiplier"]
        bet_size = optimal_fraction * self.metrics.session_bankroll
        
        analysis = {
            "strategy": "hierarchical",
            "edge": edge,
            "kelly_fraction": kelly_fraction,
            "type_multiplier": type_multiplier,
            "dynamics_multiplier": dynamics_multiplier,
            "heat_multiplier": heat_multiplier,
            "total_multiplier": total_multiplier,
            "optimal_fraction": optimal_fraction
        }
        
        return bet_size, analysis
    
    def _calculate_type_multiplier(self, player_types: Dict[MainPlayerType, int]) -> float:
        """Calculate bet multiplier based on player type composition."""
        total_players = sum(player_types.values())
        if total_players == 0:
            return 1.0
        
        weighted_opportunity = 0.0
        
        for player_type, count in player_types.items():
            if player_type in self.player_type_risks:
                opportunity = self.player_type_risks[player_type]["opportunity_factor"]
                weight = count / total_players
                weighted_opportunity += opportunity * weight
        
        # Convert opportunity factor to multiplier (0.8-1.3 range)
        return max(0.5, min(1.5, weighted_opportunity))
    
    def _calculate_dynamics_multiplier(self, context: OptimizationContext) -> float:
        """Calculate multiplier based on table dynamics."""
        base_multiplier = 1.0
        
        # Classification confidence bonus
        confidence_bonus = context.classification_confidence * 0.2
        
        # Session performance adjustment
        performance_adj = np.clip(context.session_performance / 100, -0.3, 0.3)
        
        # Adaptation opportunities
        adaptation_bonus = len(context.adaptation_opportunities) * 0.05
        
        return base_multiplier + confidence_bonus + performance_adj + adaptation_bonus
    
    def _optimize_enhanced_kelly(self, edge: float, context: OptimizationContext) -> Tuple[float, Dict[str, Any]]:
        """Enhanced Kelly Criterion with risk adjustments."""
        # Standard Kelly
        kelly_fraction = self.kelly_calculator.calculate_kelly_fraction(edge)
        
        # Risk adjustment based on recent performance
        risk_multiplier = self._calculate_risk_multiplier(context)
        
        # Enhanced fraction
        enhanced_fraction = kelly_fraction * risk_multiplier * self.optimization_params["kelly_multiplier"]
        bet_size = enhanced_fraction * self.metrics.session_bankroll
        
        analysis = {
            "strategy": "enhanced_kelly",
            "edge": edge,
            "kelly_fraction": kelly_fraction,
            "risk_multiplier": risk_multiplier,
            "enhanced_fraction": enhanced_fraction
        }
        
        return bet_size, analysis
    
    def _optimize_heat_aware(self, edge: float, context: OptimizationContext) -> Tuple[float, Dict[str, Any]]:
        """Heat-aware optimization with camouflage considerations."""
        # Base optimal bet
        base_bet = self.kelly_calculator.calculate_kelly_fraction(edge) * self.metrics.session_bankroll
        
        # Heat reduction
        heat_reduction = context.table_heat_level * self.optimization_params["heat_reduction_factor"]
        heat_multiplier = max(0.3, 1.0 - heat_reduction)
        
        # Camouflage adjustment (add some randomness)
        camouflage_factor = np.random.uniform(0.8, 1.2) if context.table_heat_level > 0.3 else 1.0
        
        bet_size = base_bet * heat_multiplier * camouflage_factor
        
        analysis = {
            "strategy": "heat_aware",
            "base_bet": base_bet,
            "heat_multiplier": heat_multiplier,
            "camouflage_factor": camouflage_factor,
            "heat_level": context.table_heat_level
        }
        
        return bet_size, analysis
    
    def _optimize_adaptive(self, edge: float, context: OptimizationContext) -> Tuple[float, Dict[str, Any]]:
        """Adaptive sizing based on recent performance and table state."""
        # Performance-based adjustment
        recent_performance = np.mean(context.recent_results) if context.recent_results else 0.0
        performance_multiplier = 1.0 + np.clip(recent_performance / 50, -0.5, 0.5)
        
        # Streak adjustment
        streak_multiplier = self._calculate_streak_multiplier()
        
        # Base bet calculation
        base_fraction = max(0.01, abs(edge) * 10)  # Simple edge-based sizing
        adaptive_fraction = base_fraction * performance_multiplier * streak_multiplier
        
        bet_size = adaptive_fraction * self.metrics.session_bankroll
        
        analysis = {
            "strategy": "adaptive",
            "recent_performance": recent_performance,
            "performance_multiplier": performance_multiplier,
            "streak_multiplier": streak_multiplier,
            "adaptive_fraction": adaptive_fraction
        }
        
        return bet_size, analysis
    
    def _optimize_kelly_basic(self, edge: float, context: OptimizationContext) -> Tuple[float, Dict[str, Any]]:
        """Basic Kelly Criterion optimization."""
        kelly_fraction = self.kelly_calculator.calculate_kelly_fraction(edge)
        conservative_fraction = kelly_fraction * self.optimization_params["kelly_multiplier"]
        bet_size = conservative_fraction * self.metrics.session_bankroll
        
        analysis = {
            "strategy": "kelly_basic",
            "kelly_fraction": kelly_fraction,
            "conservative_fraction": conservative_fraction
        }
        
        return bet_size, analysis
    
    def _calculate_risk_multiplier(self, context: OptimizationContext) -> float:
        """Calculate risk multiplier based on recent performance."""
        if not context.recent_results:
            return 1.0
        
        # Recent win rate
        recent_wins = len([r for r in context.recent_results if r > 0])
        win_rate = recent_wins / len(context.recent_results)
        
        # Variance of recent results
        result_variance = np.var(context.recent_results)
        
        # Risk multiplier (conservative when high variance or low win rate)
        risk_multiplier = 0.5 + 0.5 * win_rate - 0.2 * min(result_variance / 100, 1.0)
        
        return max(0.3, min(1.5, risk_multiplier))
    
    def _calculate_streak_multiplier(self) -> float:
        """Calculate multiplier based on current streak."""
        if abs(self.metrics.current_streak) < 3:
            return 1.0
        
        # Reduce bets during losing streaks, slightly increase during winning
        if self.metrics.current_streak > 0:
            return min(1.2, 1.0 + self.metrics.current_streak * 0.02)
        else:
            return max(0.6, 1.0 + self.metrics.current_streak * 0.02)
    
    def _apply_constraints(self, bet_size: float, context: OptimizationContext) -> float:
        """Apply global constraints to bet size."""
        # Minimum bet (table minimum)
        min_bet = self.base_bet_unit
        
        # Maximum bet constraints
        max_fraction = self.optimization_params["max_bet_fraction"]
        max_bet_bankroll = self.metrics.session_bankroll * max_fraction
        max_bet_heat = self.base_bet_unit * 20  # Reasonable table maximum
        
        # Heat-based maximum
        if context.table_heat_level > self.optimization_params["heat_threshold"]:
            max_bet_heat *= self.optimization_params["camouflage_factor"]
        
        max_bet = min(max_bet_bankroll, max_bet_heat)
        
        # Apply constraints
        constrained_bet = max(min_bet, min(bet_size, max_bet))
        
        return constrained_bet
    
    def _record_bet(self, bet_size: float, edge: float, context: OptimizationContext, analysis: Dict[str, Any]):
        """Record bet for performance tracking."""
        bet_record = {
            "timestamp": time.time(),
            "bet_size": bet_size,
            "edge": edge,
            "true_count": context.true_count,
            "table_heat": context.table_heat_level,
            "strategy": analysis.get("strategy", "unknown"),
            "session_hands": context.session_hands
        }
        
        self.bet_history.append(bet_record)
    
    def update_result(self, result: float, bet_size: float, context: OptimizationContext):
        """Update budget metrics with hand result."""
        # Update basic metrics
        self.metrics.total_hands_played += 1
        self.metrics.total_wagered += bet_size
        self.metrics.net_winnings += result
        
        # Update bankroll
        self.metrics.session_bankroll += result
        self.metrics.total_bankroll += result
        
        # Update peak and drawdown
        if self.metrics.total_bankroll > self.metrics.peak_bankroll:
            self.metrics.peak_bankroll = self.metrics.total_bankroll
        
        current_drawdown = (self.metrics.peak_bankroll - self.metrics.total_bankroll) / self.metrics.peak_bankroll
        if current_drawdown > self.metrics.max_drawdown:
            self.metrics.max_drawdown = current_drawdown
        
        # Update streak
        if result > 0:
            self.metrics.current_streak = max(1, self.metrics.current_streak + 1)
        elif result < 0:
            self.metrics.current_streak = min(-1, self.metrics.current_streak - 1)
        else:
            self.metrics.current_streak = 0
        
        # Record result
        self.result_history.append(result)
        
        # Update player type performance if available
        if context.player_types and self.hierarchical_classifier:
            self._update_player_type_performance(result, context)
    
    def _update_player_type_performance(self, result: float, context: OptimizationContext):
        """Update performance tracking by player type."""
        dominant_type = max(context.player_types, key=context.player_types.get)
        type_name = dominant_type.value
        
        if type_name not in self.metrics.player_type_performance:
            self.metrics.player_type_performance[type_name] = 0.0
        
        # Exponential moving average
        alpha = 0.1
        self.metrics.player_type_performance[type_name] = (
            alpha * result + (1 - alpha) * self.metrics.player_type_performance[type_name]
        )
    
    def should_exit_session(self, context: OptimizationContext) -> Tuple[bool, str]:
        """Determine if session should be exited."""
        # Stop loss check
        session_loss = (self.initial_bankroll * self.session_allocation - self.metrics.session_bankroll)
        stop_loss_threshold = self.initial_bankroll * self.session_allocation * self.optimization_params["session_stop_loss"]
        
        if session_loss >= stop_loss_threshold:
            return True, "Stop loss reached"
        
        # Stop win check
        session_profit = self.metrics.session_bankroll - (self.initial_bankroll * self.session_allocation)
        stop_win_threshold = self.initial_bankroll * self.session_allocation * self.optimization_params["session_stop_win"]
        
        if session_profit >= stop_win_threshold:
            return True, "Stop win reached"
        
        # Heat level check
        if context.table_heat_level >= self.optimization_params["session_exit_heat"]:
            return True, "Table heat too high"
        
        # Bankroll protection
        if self.metrics.session_bankroll < self.base_bet_unit * 5:
            return True, "Insufficient bankroll"
        
        return False, ""
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get comprehensive budget optimization summary."""
        # Calculate performance metrics
        total_return = (self.metrics.total_bankroll - self.initial_bankroll) / self.initial_bankroll
        
        # Sharpe ratio calculation
        if len(self.result_history) > 1:
            returns = list(self.result_history)
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Win rate
        wins = len([r for r in self.result_history if r > 0])
        win_rate = wins / len(self.result_history) if self.result_history else 0
        
        return {
            "budget_metrics": {
                "total_bankroll": self.metrics.total_bankroll,
                "session_bankroll": self.metrics.session_bankroll,
                "total_return": total_return,
                "net_winnings": self.metrics.net_winnings,
                "total_wagered": self.metrics.total_wagered
            },
            "performance_metrics": {
                "hands_played": self.metrics.total_hands_played,
                "win_rate": win_rate,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": self.metrics.max_drawdown,
                "current_streak": self.metrics.current_streak
            },
            "optimization_stats": {
                "strategy": self.strategy.value,
                "avg_bet_size": np.mean([b["bet_size"] for b in self.bet_history]) if self.bet_history else 0,
                "player_type_performance": self.metrics.player_type_performance,
                "heat_incidents": self.metrics.table_heat_incidents
            },
            "risk_metrics": {
                "risk_tolerance": self.risk_tolerance,
                "risk_of_ruin": self._calculate_risk_of_ruin(),
                "kelly_fraction": self.metrics.kelly_fraction
            }
        }
    
    def _calculate_risk_of_ruin(self) -> float:
        """Calculate current risk of ruin."""
        if not self.result_history:
            return 0.0
        
        # Simplified risk of ruin calculation
        avg_result = np.mean(self.result_history)
        std_result = np.std(self.result_history)
        
        if avg_result <= 0 or std_result == 0:
            return 1.0
        
        # Approximate risk of ruin using normal approximation
        z_score = avg_result / std_result
        risk_of_ruin = max(0.001, min(0.999, 1 - stats.norm.cdf(z_score * 2)))
        
        return risk_of_ruin


class KellyCalculator:
    """Kelly Criterion calculator for optimal bet sizing."""
    
    def calculate_kelly_fraction(self, edge: float, variance: float = 0.04) -> float:
        """
        Calculate Kelly fraction for given edge and variance.
        
        Args:
            edge: Player edge (expected return)
            variance: Variance of returns
            
        Returns:
            Optimal Kelly fraction
        """
        if variance <= 0 or edge <= -1:
            return 0.0
        
        # Kelly fraction = edge / variance
        kelly_fraction = edge / variance
        
        # Cap at reasonable bounds
        return max(0.0, min(0.25, kelly_fraction))


# Factory function
def create_faz4_budget_optimizer(**kwargs) -> FAZ4BudgetOptimizer:
    """Create FAZ 4.0 Budget Optimizer."""
    return FAZ4BudgetOptimizer(**kwargs)


# Test the budget optimizer
if __name__ == "__main__":
    print("🧪 TESTING FAZ 4.0 BUDGET OPTIMIZATION SYSTEM")
    
    # Create optimizer
    optimizer = FAZ4BudgetOptimizer(
        initial_bankroll=10000.0,
        strategy=BudgetStrategy.HIERARCHICAL
    )
    
    print("✅ FAZ 4.0 Budget Optimizer created successfully")
    print(f"💰 Initial Bankroll: ${optimizer.metrics.total_bankroll:,.2f}")
    print(f"🎯 Strategy: {optimizer.strategy.value}")
    
    # Create test context
    test_context = OptimizationContext(
        player_types={MainPlayerType.CONSERVATIVE: 2, MainPlayerType.AGGRESSIVE: 1},
        table_risk_level=0.4,
        table_heat_level=0.2,
        true_count=2.5,
        classification_confidence=0.8,
        session_performance=150.0,
        recent_results=[25, -10, 15, 30, -5]
    )
    
    print(f"\n🎭 TESTING BUDGET OPTIMIZATION...")
    
    # Test different scenarios
    scenarios = [
        {"edge": 0.01, "context": "favorable_count"},
        {"edge": 0.005, "context": "neutral_count"},
        {"edge": -0.002, "context": "negative_count"}
    ]
    
    for scenario in scenarios:
        edge = scenario["edge"]
        
        bet_size, analysis = optimizer.optimize_bet_size(test_context, edge)
        
        print(f"\n📊 {scenario['context'].replace('_', ' ').title()}:")
        print(f"  Edge: {edge:.1%}")
        print(f"  Optimal Bet: ${bet_size:.2f}")
        print(f"  Strategy: {analysis['strategy']}")
        if 'total_multiplier' in analysis:
            print(f"  Total Multiplier: {analysis['total_multiplier']:.2f}")
        
        # Simulate result and update
        simulated_result = np.random.choice([-bet_size, bet_size], p=[0.45, 0.55])
        optimizer.update_result(simulated_result, bet_size, test_context)
    
    # Get final summary
    summary = optimizer.get_optimization_summary()
    print(f"\n📈 OPTIMIZATION SUMMARY:")
    print(f"  Total Return: {summary['budget_metrics']['total_return']:.1%}")
    print(f"  Win Rate: {summary['performance_metrics']['win_rate']:.1%}")
    print(f"  Max Drawdown: {summary['performance_metrics']['max_drawdown']:.1%}")
    print(f"  Sharpe Ratio: {summary['performance_metrics']['sharpe_ratio']:.2f}")
    print(f"  Risk of Ruin: {summary['risk_metrics']['risk_of_ruin']:.1%}")
    
    print(f"\n✅ FAZ 4.0 Budget Optimization System test complete!") 
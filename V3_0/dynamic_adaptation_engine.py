"""
================================================================================
DYNAMIC ADAPTATION ENGINE (PHASE 3 - F3.2)
================================================================================

📋 **AMAÇ:**
   Phase 3 için real-time dynamic adaptation sistemi.
   Opponent behavior analysis, strategy modification, ve performance optimization.

🎯 **F3.2 ÖZELLİKLERİ:**
   • Real-time opponent behavior tracking
   • Dynamic strategy modification algorithms
   • Performance metrics per opponent type
   • Adaptive learning rate adjustments
   • Counter-strategy deployment

🏗️ **TEKNİK ÖZELLİKLER:**
   • Behavior Pattern Recognition: Statistical analysis of opponent actions
   • Strategy Adaptation: Real-time modification based on table dynamics
   • Performance Monitoring: Continuous tracking vs different opponent types
   • Risk Adjustment: Dynamic risk parameters based on table state

================================================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque, defaultdict
import time

# Analytics and ML imports
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class OpponentType(Enum):
    """Opponent classification types."""
    CONSERVATIVE = "conservative"      # Low risk, basic strategy
    AGGRESSIVE = "aggressive"          # High risk, frequent hits/doubles
    CARD_COUNTER = "card_counter"      # TC-correlated betting patterns
    ERRATIC = "erratic"               # Unpredictable, emotional play
    PROFESSIONAL = "professional"     # Optimal play, advanced strategy
    TOURIST = "tourist"               # Suboptimal play, entertainment focus
    MIXED = "mixed"                   # Mixed/ambiguous behavior, not clearly classifiable

class StrategyModification(Enum):
    """Types of strategy modifications."""
    CONSERVATIVE_ADJUSTMENT = "conservative"   # Play tighter vs aggressive
    AGGRESSIVE_ADJUSTMENT = "aggressive"       # Play looser vs tight
    COUNTER_COUNTING = "counter_counting"      # Camouflage vs counters
    EXPLOITATION = "exploitation"              # Exploit weaknesses
    BASELINE = "baseline"                      # Standard strategy

    @staticmethod
    def get_modification(opponent_type):
        # Import burada yapılıyor circular import'u önlemek için
        if opponent_type == OpponentType.CONSERVATIVE:
            return StrategyModification.AGGRESSIVE_ADJUSTMENT
        elif opponent_type == OpponentType.AGGRESSIVE:
            return StrategyModification.CONSERVATIVE_ADJUSTMENT
        elif opponent_type == OpponentType.CARD_COUNTER:
            return StrategyModification.COUNTER_COUNTING
        elif opponent_type == OpponentType.PROFESSIONAL:
            return StrategyModification.EXPLOITATION
        elif opponent_type == OpponentType.TOURIST:
            return StrategyModification.EXPLOITATION
        elif opponent_type == OpponentType.ERRATIC:
            return StrategyModification.BASELINE
        elif opponent_type == OpponentType.MIXED:
            return StrategyModification.BASELINE
        else:
            return StrategyModification.BASELINE

@dataclass
class OpponentBehaviorData:
    """Comprehensive opponent behavior tracking."""
    player_id: int
    hands_observed: int = 0
    
    # Action frequencies
    action_counts: Dict[str, int] = field(default_factory=lambda: {
        "hit": 0, "stand": 0, "double": 0, "split": 0
    })
    
    # Situational behavior
    hit_on_soft_17: int = 0
    stand_on_hard_16_vs_10: int = 0
    double_11_vs_ace: int = 0
    split_pairs: Dict[int, int] = field(default_factory=dict)
    
    # Betting patterns
    bet_history: List[float] = field(default_factory=list)
    tc_bet_correlation: float = 0.0
    bet_variance: float = 0.0
    progressive_betting: bool = False
    
    # Timing and emotional indicators
    decision_times: List[float] = field(default_factory=list)
    tilt_indicators: List[bool] = field(default_factory=list)
    session_performance: List[float] = field(default_factory=list)
    
    # Advanced metrics
    deviation_score: float = 0.0       # Deviation from basic strategy
    risk_tolerance: float = 0.5        # 0 = conservative, 1 = aggressive
    technical_skill: float = 0.5       # Estimated skill level
    
    # Classification
    opponent_type: OpponentType = OpponentType.CONSERVATIVE
    confidence: float = 0.0            # Classification confidence
    last_updated: float = field(default_factory=time.time)

@dataclass
class AdaptationMetrics:
    """Performance tracking for different adaptations."""
    strategy: StrategyModification
    hands_played: int = 0
    total_reward: float = 0.0
    win_rate: float = 0.0
    avg_reward: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    last_updated: float = field(default_factory=time.time)

class DynamicAdaptationEngine:
    """
    Core engine for real-time opponent analysis and strategy adaptation.
    
    Implements machine learning based opponent classification, behavioral
    pattern recognition, and dynamic strategy modification algorithms.
    """
    
    def __init__(self, 
                 ai_player_id: int,
                 adaptation_rate: float = 0.1,
                 min_observations: int = 10,
                 confidence_threshold: float = 0.7,
                 enable_ml_classification: bool = True):
        """
        Initialize Dynamic Adaptation Engine.
        
        Args:
            ai_player_id: ID of the AI player
            adaptation_rate: Rate of strategy modification (0.0-1.0)
            min_observations: Minimum hands before classification
            confidence_threshold: Minimum confidence for adaptations
            enable_ml_classification: Use ML for opponent classification
        """
        self.ai_player_id = ai_player_id
        self.adaptation_rate = np.clip(adaptation_rate, 0.0, 1.0)
        self.min_observations = min_observations
        self.confidence_threshold = confidence_threshold
        self.enable_ml_classification = enable_ml_classification
        
        # Opponent tracking
        self.opponent_data: Dict[int, OpponentBehaviorData] = {}
        self.table_history: List[Dict] = []
        
        # Adaptation tracking
        self.current_strategy = StrategyModification.BASELINE
        self.adaptation_metrics: Dict[StrategyModification, AdaptationMetrics] = {}
        self.performance_buffer = deque(maxlen=100)
        
        # ML Components
        if self.enable_ml_classification:
            self.behavior_scaler = StandardScaler()
            self.behavior_classifier = None
            self._initialize_ml_components()
        
        # Strategy modification parameters
        self.modification_parameters = self._initialize_modification_parameters()
        
        # Logging
        self.logger = logging.getLogger("DynamicAdaptationEngine")
        self.logger.setLevel(logging.INFO)
        
    def _initialize_ml_components(self):
        """Initialize machine learning components for classification."""
        # Pre-trained behavior patterns (simplified for demo)
        self.behavior_patterns = {
            OpponentType.CONSERVATIVE: {
                "hit_frequency": 0.3, "double_frequency": 0.1, 
                "risk_tolerance": 0.2, "deviation_score": 0.1
            },
            OpponentType.AGGRESSIVE: {
                "hit_frequency": 0.7, "double_frequency": 0.4,
                "risk_tolerance": 0.8, "deviation_score": 0.6
            },
            OpponentType.CARD_COUNTER: {
                "tc_correlation": 0.8, "bet_variance": 0.3,
                "technical_skill": 0.9, "deviation_score": 0.2
            },
            OpponentType.PROFESSIONAL: {
                "technical_skill": 0.95, "deviation_score": 0.05,
                "risk_tolerance": 0.4, "decision_consistency": 0.9
            },
            OpponentType.TOURIST: {
                "technical_skill": 0.2, "deviation_score": 0.7,
                "risk_tolerance": 0.6, "decision_consistency": 0.3
            }
        }
    
    def _initialize_modification_parameters(self) -> Dict[StrategyModification, Dict]:
        """Initialize strategy modification parameters."""
        return {
            StrategyModification.CONSERVATIVE_ADJUSTMENT: {
                "hit_threshold_modifier": -0.1,    # Hit less often
                "double_threshold_modifier": -0.2, # Double less often
                "split_threshold_modifier": -0.1,  # Split less often
                "bet_size_modifier": 0.8           # Bet smaller
            },
            StrategyModification.AGGRESSIVE_ADJUSTMENT: {
                "hit_threshold_modifier": 0.1,     # Hit more often
                "double_threshold_modifier": 0.2,  # Double more often
                "split_threshold_modifier": 0.1,   # Split more often  
                "bet_size_modifier": 1.2           # Bet larger
            },
            StrategyModification.COUNTER_COUNTING: {
                "bet_randomization": 0.3,          # Add betting noise
                "play_randomization": 0.1,         # Add play noise
                "camouflage_factor": 0.2           # Occasional suboptimal plays
            },
            StrategyModification.EXPLOITATION: {
                "aggression_vs_weak": 1.5,         # More aggressive vs weak players
                "patience_vs_strong": 1.2,         # More patient vs strong players
                "bluff_factor": 0.1                # Occasional unexpected plays
            }
        }
    
    def observe_opponent_action(self, 
                              player_id: int,
                              action: str,
                              hand_total: int,
                              dealer_upcard: int,
                              usable_ace: bool,
                              bet_amount: Optional[float] = None,
                              true_count: Optional[float] = None,
                              decision_time: Optional[float] = None):
        """
        Record and analyze opponent action for behavior modeling.
        
        Args:
            player_id: ID of the acting player
            action: Action taken (hit, stand, double, split)
            hand_total: Player's hand total
            dealer_upcard: Dealer's upcard
            usable_ace: Whether player has usable ace
            bet_amount: Bet amount (if available)
            true_count: Current true count (if tracking)
            decision_time: Time taken to make decision
        """
        if player_id == self.ai_player_id:
            return  # Don't track own actions
            
        # Initialize opponent data if new
        if player_id not in self.opponent_data:
            self.opponent_data[player_id] = OpponentBehaviorData(player_id=player_id)
            
        opponent = self.opponent_data[player_id]
        opponent.hands_observed += 1
        
        # Record action
        if action in opponent.action_counts:
            opponent.action_counts[action] += 1
            
        # Record situational behavior
        self._record_situational_behavior(opponent, action, hand_total, dealer_upcard, usable_ace)
        
        # Record betting pattern
        if bet_amount is not None:
            opponent.bet_history.append(bet_amount)
            if true_count is not None and len(opponent.bet_history) > 5:
                self._update_tc_correlation(opponent, true_count)
                
        # Record timing data
        if decision_time is not None:
            opponent.decision_times.append(decision_time)
            
        # Update behavioral metrics
        self._update_behavioral_metrics(opponent)
        
        # Classify opponent if enough data
        if opponent.hands_observed >= self.min_observations:
            self._classify_opponent(opponent)
            
        # Update adaptation strategy if needed
        self._evaluate_adaptation_need()
        
        opponent.last_updated = time.time()
    
    def _record_situational_behavior(self, 
                                   opponent: OpponentBehaviorData,
                                   action: str,
                                   hand_total: int,
                                   dealer_upcard: int,
                                   usable_ace: bool):
        """Record specific situational decisions for analysis."""
        # Soft 17 behavior
        if hand_total == 17 and usable_ace and action == "hit":
            opponent.hit_on_soft_17 += 1
            
        # Hard 16 vs 10 behavior  
        if hand_total == 16 and not usable_ace and dealer_upcard == 10 and action == "stand":
            opponent.stand_on_hard_16_vs_10 += 1
            
        # 11 vs Ace doubling
        if hand_total == 11 and dealer_upcard == 1 and action == "double":
            opponent.double_11_vs_ace += 1
            
        # Pair splitting tracking
        # (Simplified - would need actual hand composition)
        if action == "split":
            pair_value = hand_total // 2  # Simplified assumption
            if pair_value not in opponent.split_pairs:
                opponent.split_pairs[pair_value] = 0
            opponent.split_pairs[pair_value] += 1
    
    def _update_tc_correlation(self, opponent: OpponentBehaviorData, true_count: float):
        """Update true count correlation for betting patterns."""
        if len(opponent.bet_history) < 2:
            return
            
        # Get recent bets and TCs (simplified)
        recent_bets = opponent.bet_history[-10:]
        tc_values = [true_count] * len(recent_bets)  # Simplified
        
        if len(recent_bets) > 1 and len(set(recent_bets)) > 1:
            correlation, _ = stats.pearsonr(recent_bets, tc_values)
            opponent.tc_bet_correlation = correlation if not np.isnan(correlation) else 0.0
            
        # Update bet variance
        opponent.bet_variance = np.var(recent_bets) if len(recent_bets) > 1 else 0.0
    
    def _update_behavioral_metrics(self, opponent: OpponentBehaviorData):
        """Update derived behavioral metrics."""
        total_actions = sum(opponent.action_counts.values())
        if total_actions == 0:
            return
            
        # Calculate frequencies
        hit_freq = opponent.action_counts["hit"] / total_actions
        double_freq = opponent.action_counts["double"] / total_actions
        split_freq = opponent.action_counts["split"] / total_actions
        
        # Calculate risk tolerance (higher = more aggressive)
        opponent.risk_tolerance = (hit_freq * 0.5 + double_freq * 1.0 + split_freq * 0.8)
        
        # Calculate deviation from basic strategy (simplified)
        expected_hit_freq = 0.4  # Approximate basic strategy hit frequency
        expected_double_freq = 0.1
        
        deviation = abs(hit_freq - expected_hit_freq) + abs(double_freq - expected_double_freq)
        opponent.deviation_score = min(deviation, 1.0)
        
        # Calculate technical skill (inverse of deviation)
        opponent.technical_skill = max(0.0, 1.0 - opponent.deviation_score)
    
    def _classify_opponent(self, opponent: OpponentBehaviorData):
        """Classify opponent type based on behavioral data."""
        if self.enable_ml_classification:
            opponent.opponent_type, opponent.confidence = self._ml_classify_opponent(opponent)
        else:
            opponent.opponent_type, opponent.confidence = self._rule_based_classify_opponent(opponent)
    
    def _ml_classify_opponent(self, opponent: OpponentBehaviorData) -> Tuple[OpponentType, float]:
        """Machine learning based opponent classification."""
        # Feature extraction
        features = self._extract_behavioral_features(opponent)
        
        # Compare with known patterns
        similarities = {}
        for opp_type, pattern in self.behavior_patterns.items():
            similarity = self._calculate_pattern_similarity(features, pattern)
            similarities[opp_type] = similarity
            
        # Find best match
        best_type = max(similarities, key=similarities.get)
        confidence = similarities[best_type]
        
        return best_type, confidence
    
    def _rule_based_classify_opponent(self, opponent: OpponentBehaviorData) -> Tuple[OpponentType, float]:
        """Rule-based opponent classification."""
        # Conservative indicators
        if (opponent.risk_tolerance < 0.3 and 
            opponent.deviation_score < 0.2 and
            opponent.technical_skill > 0.7):
            return OpponentType.CONSERVATIVE, 0.8
            
        # Aggressive indicators  
        if (opponent.risk_tolerance > 0.7 and
            opponent.action_counts["double"] / max(1, sum(opponent.action_counts.values())) > 0.3):
            return OpponentType.AGGRESSIVE, 0.7
            
        # Card counter indicators
        if (abs(opponent.tc_bet_correlation) > 0.6 and
            opponent.technical_skill > 0.8 and
            opponent.bet_variance > 0.2):
            return OpponentType.CARD_COUNTER, 0.9
            
        # Professional indicators
        if (opponent.technical_skill > 0.9 and
            opponent.deviation_score < 0.1 and
            0.3 < opponent.risk_tolerance < 0.6):
            return OpponentType.PROFESSIONAL, 0.85
            
        # Tourist indicators
        if (opponent.deviation_score > 0.5 and
            opponent.technical_skill < 0.4):
            return OpponentType.TOURIST, 0.7
            
        # Default to erratic if unclear
        return OpponentType.ERRATIC, 0.5
    
    def _extract_behavioral_features(self, opponent: OpponentBehaviorData) -> Dict[str, float]:
        """Extract numerical features for ML classification."""
        total_actions = max(1, sum(opponent.action_counts.values()))
        
        return {
            "hit_frequency": opponent.action_counts["hit"] / total_actions,
            "double_frequency": opponent.action_counts["double"] / total_actions,
            "split_frequency": opponent.action_counts["split"] / total_actions,
            "risk_tolerance": opponent.risk_tolerance,
            "deviation_score": opponent.deviation_score,
            "technical_skill": opponent.technical_skill,
            "tc_correlation": abs(opponent.tc_bet_correlation),
            "bet_variance": opponent.bet_variance,
            "hands_observed": min(opponent.hands_observed / 100, 1.0)  # Normalized
        }
    
    def _calculate_pattern_similarity(self, features: Dict[str, float], pattern: Dict[str, float]) -> float:
        """Calculate similarity between features and known pattern."""
        similarities = []
        
        for key in pattern:
            if key in features:
                # Use inverse of absolute difference as similarity
                diff = abs(features[key] - pattern[key])
                similarity = max(0.0, 1.0 - diff)
                similarities.append(similarity)
                
        return np.mean(similarities) if similarities else 0.0
    
    def _evaluate_adaptation_need(self):
        """Evaluate if strategy adaptation is needed."""
        # Get current table composition
        opponent_types = [data.opponent_type for data in self.opponent_data.values() 
                         if data.confidence > self.confidence_threshold]
        
        if not opponent_types:
            return
            
        # Determine optimal strategy based on opponents
        optimal_strategy = self._determine_optimal_strategy(opponent_types)
        
        # Switch strategy if different and beneficial
        if optimal_strategy != self.current_strategy:
            self._switch_strategy(optimal_strategy)
    
    def _determine_optimal_strategy(self, opponent_types: List[OpponentType]) -> StrategyModification:
        """Determine optimal strategy based on opponent composition."""
        type_counts = {t: opponent_types.count(t) for t in OpponentType}
        dominant_type = max(type_counts, key=type_counts.get) if type_counts else OpponentType.CONSERVATIVE
        
        # Strategy mapping
        strategy_map = {
            OpponentType.CONSERVATIVE: StrategyModification.AGGRESSIVE_ADJUSTMENT,
            OpponentType.AGGRESSIVE: StrategyModification.CONSERVATIVE_ADJUSTMENT,
            OpponentType.CARD_COUNTER: StrategyModification.COUNTER_COUNTING,
            OpponentType.TOURIST: StrategyModification.EXPLOITATION,
            OpponentType.PROFESSIONAL: StrategyModification.BASELINE,
            OpponentType.ERRATIC: StrategyModification.BASELINE
        }
        
        return strategy_map.get(dominant_type, StrategyModification.BASELINE)
    
    def _switch_strategy(self, new_strategy: StrategyModification):
        """Switch to new adaptation strategy."""
        self.logger.info(f"Switching strategy from {self.current_strategy.value} to {new_strategy.value}")
        
        # Record performance of old strategy
        if self.current_strategy in self.adaptation_metrics:
            self._update_strategy_metrics(self.current_strategy)
            
        # Switch to new strategy
        self.current_strategy = new_strategy
        
        # Initialize metrics for new strategy if needed
        if new_strategy not in self.adaptation_metrics:
            self.adaptation_metrics[new_strategy] = AdaptationMetrics(strategy=new_strategy)
    
    def _update_strategy_metrics(self, strategy: StrategyModification):
        """Update performance metrics for a strategy."""
        if strategy not in self.adaptation_metrics:
            return
            
        metrics = self.adaptation_metrics[strategy]
        
        # Update from recent performance buffer
        recent_rewards = list(self.performance_buffer)[-20:]  # Last 20 hands
        if recent_rewards:
            metrics.avg_reward = np.mean(recent_rewards)
            metrics.win_rate = sum(1 for r in recent_rewards if r > 0) / len(recent_rewards)
            
            # Calculate confidence interval
            if len(recent_rewards) > 1:
                std_err = stats.sem(recent_rewards)
                ci = stats.t.interval(0.95, len(recent_rewards)-1, 
                                    loc=metrics.avg_reward, scale=std_err)
                metrics.confidence_interval = ci
                
        metrics.last_updated = time.time()
    
    def get_strategy_modification(self, 
                                base_action: str,
                                hand_total: int,
                                dealer_upcard: int,
                                true_count: float = 0.0) -> str:
        """
        Get modified action based on current adaptation strategy.
        
        Args:
            base_action: Base strategy action
            hand_total: Player's hand total
            dealer_upcard: Dealer's upcard
            true_count: Current true count
            
        Returns:
            Modified action recommendation
        """
        if self.current_strategy == StrategyModification.BASELINE:
            return base_action
            
        modifications = self.modification_parameters.get(self.current_strategy, {})
        
        # Apply modifications based on strategy type
        if self.current_strategy == StrategyModification.CONSERVATIVE_ADJUSTMENT:
            return self._apply_conservative_modification(base_action, hand_total, dealer_upcard, modifications)
        elif self.current_strategy == StrategyModification.AGGRESSIVE_ADJUSTMENT:
            return self._apply_aggressive_modification(base_action, hand_total, dealer_upcard, modifications)
        elif self.current_strategy == StrategyModification.COUNTER_COUNTING:
            return self._apply_camouflage_modification(base_action, modifications)
        elif self.current_strategy == StrategyModification.EXPLOITATION:
            return self._apply_exploitation_modification(base_action, modifications)
            
        return base_action
    
    def _apply_conservative_modification(self, base_action: str, hand_total: int, 
                                       dealer_upcard: int, modifications: Dict) -> str:
        """Apply conservative strategy modifications."""
        # Stand more often in borderline situations
        if base_action == "hit" and hand_total >= 16 and dealer_upcard < 7:
            if np.random.random() < 0.3:  # 30% chance to stand instead
                return "stand"
                
        # Double less frequently
        if base_action == "double" and np.random.random() < 0.4:
            return "hit"
            
        return base_action
    
    def _apply_aggressive_modification(self, base_action: str, hand_total: int,
                                     dealer_upcard: int, modifications: Dict) -> str:
        """Apply aggressive strategy modifications."""
        # Hit more often in borderline situations
        if base_action == "stand" and hand_total <= 16 and dealer_upcard >= 7:
            if np.random.random() < 0.2:  # 20% chance to hit instead
                return "hit"
                
        # Double more frequently when possible
        if base_action == "hit" and hand_total in [9, 10, 11] and len(str(hand_total)) == 2:  # Simplified check
            if np.random.random() < 0.3:
                return "double"
                
        return base_action
    
    def _apply_camouflage_modification(self, base_action: str, modifications: Dict) -> str:
        """Apply camouflage modifications to hide card counting."""
        camouflage_chance = modifications.get("camouflage_factor", 0.1)
        
        # Occasionally make suboptimal plays
        if np.random.random() < camouflage_chance:
            suboptimal_actions = ["hit", "stand"]  # Simplified
            return np.random.choice([a for a in suboptimal_actions if a != base_action] or [base_action])
            
        return base_action
    
    def _apply_exploitation_modification(self, base_action: str, modifications: Dict) -> str:
        """Apply exploitation modifications against weak opponents."""
        # More aggressive against weak opponents
        aggression = modifications.get("aggression_vs_weak", 1.0)
        
        if aggression > 1.2 and base_action == "stand":
            if np.random.random() < 0.15:  # 15% chance for more aggressive play
                return "hit"
                
        return base_action
    
    def record_performance(self, reward: float):
        """Record performance for strategy evaluation."""
        self.performance_buffer.append(reward)
        
        # Update current strategy metrics
        if self.current_strategy in self.adaptation_metrics:
            metrics = self.adaptation_metrics[self.current_strategy]
            metrics.hands_played += 1
            metrics.total_reward += reward
    
    def get_adaptation_summary(self) -> Dict[str, Any]:
        """Get summary of current adaptations and opponent analysis."""
        summary = {
            "current_strategy": self.current_strategy.value,
            "opponents_classified": len([d for d in self.opponent_data.values() 
                                       if d.confidence > self.confidence_threshold]),
            "opponent_types": {
                data.opponent_type.value: data.confidence 
                for data in self.opponent_data.values()
                if data.confidence > self.confidence_threshold
            },
            "strategy_performance": {
                strategy.value: {
                    "hands": metrics.hands_played,
                    "avg_reward": metrics.avg_reward,
                    "win_rate": metrics.win_rate
                }
                for strategy, metrics in self.adaptation_metrics.items()
            },
            "table_dynamics": {
                "total_opponents": len(self.opponent_data),
                "adaptation_rate": self.adaptation_rate,
                "confidence_threshold": self.confidence_threshold
            }
        }
        
        return summary


# Factory function
def create_adaptation_engine(**kwargs) -> DynamicAdaptationEngine:
    """Create Dynamic Adaptation Engine with given parameters."""
    return DynamicAdaptationEngine(**kwargs)


# Test the adaptation engine
if __name__ == "__main__":
    print("🧪 TESTING DYNAMIC ADAPTATION ENGINE")
    
    engine = DynamicAdaptationEngine(ai_player_id=1)
    
    print("✅ Dynamic Adaptation Engine created successfully")
    print(f"🎯 AI Player ID: {engine.ai_player_id}")
    print(f"📊 Adaptation Rate: {engine.adaptation_rate}")
    print(f"🤖 ML Classification: {engine.enable_ml_classification}")
    
    # Simulate opponent behavior
    print("\n🎭 SIMULATING OPPONENT BEHAVIOR...")
    
    # Aggressive player simulation
    for i in range(15):
        engine.observe_opponent_action(
            player_id=0,
            action=np.random.choice(["hit", "double"], p=[0.6, 0.4]),
            hand_total=np.random.randint(12, 18),
            dealer_upcard=np.random.randint(2, 11),
            usable_ace=False,
            bet_amount=np.random.uniform(50, 200)
        )
    
    # Conservative player simulation
    for i in range(15):
        engine.observe_opponent_action(
            player_id=2,
            action=np.random.choice(["stand", "hit"], p=[0.7, 0.3]),
            hand_total=np.random.randint(15, 20),
            dealer_upcard=np.random.randint(2, 11),
            usable_ace=False,
            bet_amount=np.random.uniform(10, 25)
        )
    
    # Get adaptation summary
    summary = engine.get_adaptation_summary()
    print(f"\n📈 ADAPTATION SUMMARY:")
    print(f"Current Strategy: {summary['current_strategy']}")
    print(f"Opponents Classified: {summary['opponents_classified']}")
    print(f"Opponent Types: {summary['opponent_types']}")
    
    # Test strategy modification
    print(f"\n🎯 STRATEGY MODIFICATION TEST:")
    base_action = "hit"
    modified = engine.get_strategy_modification(base_action, 16, 10)
    print(f"Base Action: {base_action} → Modified: {modified}")
    
    print("\n✅ Dynamic Adaptation Engine test complete!") 
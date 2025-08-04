"""
================================================================================
FAZ 4.0 - ADVANCED PLAYER BEHAVIOR ANALYSIS MODULE (F4.1 + F4.2)
================================================================================

📋 **AMAÇ:**
   FAZ 4.0 için gelişmiş oyuncu davranış kategorileri ve real-time analiz sistemi.
   6 farklı oyuncu tipi ile sophisticated behavior pattern recognition.

🎯 **F4.1 ÖZELLİKLERİ:**
   • 6 oyuncu kategorisi: Conservative, Aggressive, Basic Strategy, Card Counter, Random, Superstitious
   • Detaylı davranış kalıpları tanımlaması
   • Risk toleransı ve betting pattern profilleri

🎯 **F4.2 ÖZELLİKLERİ:**
   • Betting patterns analizi
   • Action frequencies çıkarımı  
   • Risk tolerance hesaplama
   • Confidence score'ları

================================================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import time
import logging
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class PlayerType(Enum):
    """FAZ 4.0 Enhanced Player Categories (F4.1)"""
    CONSERVATIVE = "conservative"      # Düşük risk, düzenli betting, basic strategy'ye yakın
    AGGRESSIVE = "aggressive"          # Yüksek risk, büyük betler, risk almayı sever
    BASIC_STRATEGY = "basic"           # Optimal oyun, matematiksel doğruluk
    CARD_COUNTER = "counter"           # Kart sayımı yapan, TC'ye göre betting
    RANDOM = "random"                  # Rastgele oynayan, tutarsız davranış
    SUPERSTITIOUS = "superstitious"    # Batıl inançlı, mantık dışı kararlar

class BehaviorPattern(Enum):
    """Davranış kalıpları kategorileri"""
    CONSISTENT = "consistent"          # Tutarlı davranış
    VARIABLE = "variable"              # Değişken davranış
    ADAPTIVE = "adaptive"              # Duruma göre adapte olan
    ERRATIC = "erratic"               # Düzensiz, öngörülemeyen
    LEARNING = "learning"             # Öğrenme eğiliminde
    DECLINING = "declining"           # Performans düşen

@dataclass
class BehaviorMetrics:
    """Oyuncu davranış metrikleri"""
    # Betting metrics
    avg_bet_size: float = 0.0
    bet_variance: float = 0.0
    bet_progression_pattern: str = "flat"  # flat, progressive, regressive
    tc_correlation: float = 0.0
    
    # Playing metrics  
    hit_frequency: float = 0.0
    stand_frequency: float = 0.0
    double_frequency: float = 0.0
    split_frequency: float = 0.0
    
    # Risk metrics
    risk_tolerance: float = 0.5
    bankroll_management: str = "unknown"  # tight, normal, loose
    
    # Consistency metrics
    decision_consistency: float = 0.0
    pattern_stability: float = 0.0
    
    # Performance metrics
    win_rate: float = 0.0
    session_performance: float = 0.0
    
    # Timing metrics
    avg_decision_time: float = 0.0
    decision_time_variance: float = 0.0

@dataclass
class PlayerBehaviorProfile:
    """Comprehensive player behavior profile"""
    player_id: int
    player_type: PlayerType = PlayerType.CONSERVATIVE
    confidence: float = 0.0
    
    # Historical data
    hands_observed: int = 0
    sessions_tracked: int = 0
    
    # Behavior metrics
    metrics: BehaviorMetrics = field(default_factory=BehaviorMetrics)
    
    # Pattern tracking
    behavior_pattern: BehaviorPattern = BehaviorPattern.CONSISTENT
    pattern_changes: List[Dict] = field(default_factory=list)
    
    # Recent behavior (sliding window)
    recent_actions: deque = field(default_factory=lambda: deque(maxlen=50))
    recent_bets: deque = field(default_factory=lambda: deque(maxlen=30))
    recent_results: deque = field(default_factory=lambda: deque(maxlen=20))
    
    # Advanced features
    superstition_indicators: Dict[str, float] = field(default_factory=dict)
    counting_indicators: Dict[str, float] = field(default_factory=dict)
    interaction_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    first_observed: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

class PlayerBehaviorAnalyzer:
    """
    FAZ 4.0 Advanced Player Behavior Analyzer (F4.2)
    
    Sophisticated real-time analysis of player behavior patterns,
    betting strategies, and risk preferences with confidence scoring.
    """
    
    def __init__(self, 
                 min_observations: int = 10,
                 confidence_threshold: float = 0.7,
                 pattern_window_size: int = 20):
        """
        Initialize advanced behavior analyzer.
        
        Args:
            min_observations: Minimum hands before classification
            confidence_threshold: Minimum confidence for reliable classification
            pattern_window_size: Size of sliding window for pattern analysis
        """
        self.min_observations = min_observations
        self.confidence_threshold = confidence_threshold
        self.pattern_window_size = pattern_window_size
        
        # Player profiles database
        self.player_profiles: Dict[int, PlayerBehaviorProfile] = {}
        
        # Behavior pattern templates
        self.behavior_templates = self._initialize_behavior_templates()
        
        # Analysis history
        self.analysis_history: List[Dict] = []
        
        # Advanced features
        self.interaction_tracker = InteractionTracker()
        self.change_detector = BehaviorChangeDetector()
        
        # Logging
        self.logger = logging.getLogger("PlayerBehaviorAnalyzer")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info("FAZ 4.0 Advanced Player Behavior Analyzer initialized")
    
    def _initialize_behavior_templates(self) -> Dict[PlayerType, Dict[str, Any]]:
        """Initialize behavior pattern templates for each player type."""
        return {
            PlayerType.CONSERVATIVE: {
                "bet_size_range": (0.5, 2.0),      # 0.5-2x min bet
                "bet_variance_max": 0.3,
                "hit_frequency_range": (0.35, 0.45),
                "double_frequency_max": 0.12,
                "risk_tolerance_max": 0.3,
                "decision_consistency_min": 0.8,
                "tc_correlation_max": 0.2,
                "key_indicators": ["low_variance", "consistent_sizing", "basic_strategy_like"]
            },
            PlayerType.AGGRESSIVE: {
                "bet_size_range": (2.0, 10.0),     # 2-10x min bet
                "bet_variance_min": 0.5,
                "hit_frequency_range": (0.5, 0.7),
                "double_frequency_min": 0.2,
                "risk_tolerance_min": 0.7,
                "decision_consistency_max": 0.6,
                "tc_correlation_max": 0.3,
                "key_indicators": ["high_variance", "large_bets", "risk_seeking"]
            },
            PlayerType.BASIC_STRATEGY: {
                "bet_size_range": (1.0, 3.0),      # 1-3x min bet
                "bet_variance_max": 0.4,
                "hit_frequency_range": (0.4, 0.5),
                "double_frequency_range": (0.08, 0.15),
                "risk_tolerance_range": (0.3, 0.6),
                "decision_consistency_min": 0.85,
                "tc_correlation_max": 0.25,
                "key_indicators": ["optimal_play", "consistent_decisions", "mathematical"]
            },
            PlayerType.CARD_COUNTER: {
                "bet_size_range": (1.0, 8.0),      # 1-8x min bet (spread)
                "bet_variance_min": 0.4,
                "tc_correlation_min": 0.6,         # Strong TC correlation
                "hit_frequency_range": (0.38, 0.48),
                "decision_consistency_min": 0.8,
                "risk_tolerance_range": (0.4, 0.7),
                "key_indicators": ["tc_betting", "count_aware", "strategic_deviations"]
            },
            PlayerType.RANDOM: {
                "bet_variance_range": (0.3, 1.0),
                "decision_consistency_max": 0.5,
                "pattern_stability_max": 0.4,
                "hit_frequency_range": (0.3, 0.8),  # Wide range
                "double_frequency_range": (0.05, 0.3),
                "key_indicators": ["inconsistent", "unpredictable", "no_pattern"]
            },
            PlayerType.SUPERSTITIOUS: {
                "bet_size_range": (0.5, 5.0),
                "decision_consistency_range": (0.3, 0.7),
                "pattern_correlation_max": 0.4,    # Low correlation with optimal play
                "superstition_frequency_min": 0.2,
                "key_indicators": ["irrational_decisions", "pattern_beliefs", "emotional_play"]
            }
        }
    
    def observe_player_action(self,
                            player_id: int,
                            action: str,
                            bet_amount: float,
                            hand_total: int,
                            dealer_upcard: int,
                            true_count: float = 0.0,
                            result: Optional[float] = None,
                            decision_time: Optional[float] = None,
                            context: Optional[Dict] = None) -> None:
        """
        Record and analyze player action for behavior profiling.
        
        Args:
            player_id: Player identifier
            action: Action taken (hit, stand, double, split)
            bet_amount: Bet amount placed
            hand_total: Player's hand total
            dealer_upcard: Dealer's upcard
            true_count: Current true count
            result: Hand result (win/loss/push)
            decision_time: Time taken for decision
            context: Additional context (position, chips, etc.)
        """
        # Initialize profile if new player
        if player_id not in self.player_profiles:
            self.player_profiles[player_id] = PlayerBehaviorProfile(player_id=player_id)
        
        profile = self.player_profiles[player_id]
        profile.hands_observed += 1
        profile.last_updated = time.time()
        
        # Record action and bet
        action_data = {
            "action": action,
            "bet": bet_amount,
            "hand_total": hand_total,
            "dealer_up": dealer_upcard,
            "true_count": true_count,
            "timestamp": time.time(),
            "decision_time": decision_time
        }
        
        profile.recent_actions.append(action_data)
        profile.recent_bets.append(bet_amount)
        
        if result is not None:
            profile.recent_results.append(result)
        
        # Update behavior metrics
        self._update_behavior_metrics(profile)
        
        # Classify player if enough observations
        if profile.hands_observed >= self.min_observations:
            self._classify_player(profile)
            
        # Detect behavior changes
        if profile.hands_observed > self.pattern_window_size:
            self._detect_behavior_changes(profile)
        
        # Track interactions with other players
        if context:
            self.interaction_tracker.record_interaction(player_id, context)
    
    def _update_behavior_metrics(self, profile: PlayerBehaviorProfile) -> None:
        """Update comprehensive behavior metrics for a player."""
        if not profile.recent_actions:
            return
        
        metrics = profile.metrics
        
        # Betting metrics
        if profile.recent_bets:
            bets = list(profile.recent_bets)
            metrics.avg_bet_size = np.mean(bets)
            metrics.bet_variance = np.var(bets) if len(bets) > 1 else 0.0
            
            # Calculate TC correlation if we have true count data
            tc_data = [a.get("true_count", 0) for a in profile.recent_actions if "true_count" in a]
            if len(tc_data) > 5 and len(set(tc_data)) > 1:
                # Ensure arrays have same length
                min_length = min(len(bets), len(tc_data))
                if min_length > 1:
                    correlation, _ = stats.pearsonr(bets[-min_length:], tc_data[-min_length:])
                    metrics.tc_correlation = correlation if not np.isnan(correlation) else 0.0
        
        # Action frequency metrics
        actions = [a["action"] for a in profile.recent_actions]
        action_counts = {action: actions.count(action) for action in set(actions)}
        total_actions = len(actions)
        
        if total_actions > 0:
            metrics.hit_frequency = action_counts.get("hit", 0) / total_actions
            metrics.stand_frequency = action_counts.get("stand", 0) / total_actions
            metrics.double_frequency = action_counts.get("double", 0) / total_actions
            metrics.split_frequency = action_counts.get("split", 0) / total_actions
        
        # Risk tolerance (composite score)
        bet_risk = min(metrics.avg_bet_size / 10, 1.0)  # Normalized bet size
        action_risk = metrics.hit_frequency + metrics.double_frequency * 1.5
        metrics.risk_tolerance = (bet_risk + action_risk) / 2
        
        # Decision consistency (how often player makes same decision in similar situations)
        metrics.decision_consistency = self._calculate_decision_consistency(profile)
        
        # Performance metrics
        if profile.recent_results:
            results = list(profile.recent_results)
            metrics.win_rate = len([r for r in results if r > 0]) / len(results)
            metrics.session_performance = np.mean(results)
        
        # Timing metrics
        decision_times = [a.get("decision_time") for a in profile.recent_actions if a.get("decision_time")]
        if decision_times:
            metrics.avg_decision_time = np.mean(decision_times)
            metrics.decision_time_variance = np.var(decision_times)
    
    def _calculate_decision_consistency(self, profile: PlayerBehaviorProfile) -> float:
        """Calculate how consistent player's decisions are in similar situations."""
        if len(profile.recent_actions) < 5:
            return 0.5
        
        # Group similar situations and check action consistency
        situation_actions = defaultdict(list)
        
        for action_data in profile.recent_actions:
            # Create situation key (simplified)
            situation = (
                min(action_data["hand_total"] // 5 * 5, 20),  # Grouped hand totals
                min(action_data["dealer_up"], 10)  # Dealer upcard
            )
            situation_actions[situation].append(action_data["action"])
        
        # Calculate consistency for each situation
        consistencies = []
        for situation, actions in situation_actions.items():
            if len(actions) > 1:
                most_common_action = max(set(actions), key=actions.count)
                consistency = actions.count(most_common_action) / len(actions)
                consistencies.append(consistency)
        
        return np.mean(consistencies) if consistencies else 0.5
    
    def _classify_player(self, profile: PlayerBehaviorProfile) -> None:
        """Classify player based on behavior patterns."""
        metrics = profile.metrics
        
        # Calculate similarity scores for each player type
        type_scores = {}
        
        for player_type, template in self.behavior_templates.items():
            score = self._calculate_type_similarity(metrics, template)
            type_scores[player_type] = score
        
        # Find best match
        best_type = max(type_scores, key=type_scores.get)
        confidence = type_scores[best_type]
        
        # Apply confidence threshold
        if confidence >= self.confidence_threshold:
            profile.player_type = best_type
            profile.confidence = confidence
            
            # Log classification change
            if profile.hands_observed == self.min_observations:
                self.logger.info(f"Player {profile.player_id} classified as {best_type.value} "
                               f"(confidence: {confidence:.2f})")
        else:
            # Low confidence, keep as current type but update confidence
            profile.confidence = confidence
    
    def _calculate_type_similarity(self, metrics: BehaviorMetrics, template: Dict[str, Any]) -> float:
        """Calculate similarity between player metrics and behavior template."""
        similarity_scores = []
        
        # Betting pattern similarity
        if "bet_size_range" in template:
            bet_min, bet_max = template["bet_size_range"]
            if bet_min <= metrics.avg_bet_size <= bet_max:
                similarity_scores.append(1.0)
            else:
                # Distance-based similarity
                distance = min(abs(metrics.avg_bet_size - bet_min), abs(metrics.avg_bet_size - bet_max))
                similarity = max(0, 1 - distance / bet_max)
                similarity_scores.append(similarity)
        
        # Bet variance similarity
        if "bet_variance_max" in template:
            if metrics.bet_variance <= template["bet_variance_max"]:
                similarity_scores.append(1.0)
            else:
                similarity = max(0, 1 - (metrics.bet_variance - template["bet_variance_max"]) / template["bet_variance_max"])
                similarity_scores.append(similarity)
        
        if "bet_variance_min" in template:
            if metrics.bet_variance >= template["bet_variance_min"]:
                similarity_scores.append(1.0)
            else:
                similarity = metrics.bet_variance / template["bet_variance_min"]
                similarity_scores.append(similarity)
        
        # Action frequency similarity
        if "hit_frequency_range" in template:
            hit_min, hit_max = template["hit_frequency_range"]
            if hit_min <= metrics.hit_frequency <= hit_max:
                similarity_scores.append(1.0)
            else:
                distance = min(abs(metrics.hit_frequency - hit_min), abs(metrics.hit_frequency - hit_max))
                similarity = max(0, 1 - distance / 0.5)  # Normalize by max possible difference
                similarity_scores.append(similarity)
        
        # TC correlation (important for card counters)
        if "tc_correlation_min" in template:
            if abs(metrics.tc_correlation) >= template["tc_correlation_min"]:
                similarity_scores.append(1.0)
            else:
                similarity = abs(metrics.tc_correlation) / template["tc_correlation_min"]
                similarity_scores.append(similarity)
        
        # Decision consistency
        if "decision_consistency_min" in template:
            if metrics.decision_consistency >= template["decision_consistency_min"]:
                similarity_scores.append(1.0)
            else:
                similarity = metrics.decision_consistency / template["decision_consistency_min"]
                similarity_scores.append(similarity)
        
        # Risk tolerance
        if "risk_tolerance_min" in template:
            if metrics.risk_tolerance >= template["risk_tolerance_min"]:
                similarity_scores.append(1.0)
            else:
                similarity = metrics.risk_tolerance / template["risk_tolerance_min"]
                similarity_scores.append(similarity)
        
        if "risk_tolerance_max" in template:
            if metrics.risk_tolerance <= template["risk_tolerance_max"]:
                similarity_scores.append(1.0)
            else:
                similarity = max(0, 1 - (metrics.risk_tolerance - template["risk_tolerance_max"]) / template["risk_tolerance_max"])
                similarity_scores.append(similarity)
        
        # Return weighted average similarity
        return np.mean(similarity_scores) if similarity_scores else 0.0
    
    def _detect_behavior_changes(self, profile: PlayerBehaviorProfile) -> None:
        """Detect significant changes in player behavior patterns."""
        if len(profile.recent_actions) < self.pattern_window_size:
            return
        
        # Analyze recent vs historical behavior
        recent_window = list(profile.recent_actions)[-self.pattern_window_size//2:]
        historical_window = list(profile.recent_actions)[-self.pattern_window_size:-self.pattern_window_size//2]
        
        # Calculate behavior change indicators
        changes = self.change_detector.detect_changes(recent_window, historical_window)
        
        if changes["significant_change"]:
            # Record behavior change
            change_record = {
                "timestamp": time.time(),
                "change_type": changes["change_type"],
                "magnitude": changes["magnitude"],
                "previous_behavior": profile.behavior_pattern.value,
                "indicators": changes["indicators"]
            }
            
            profile.pattern_changes.append(change_record)
            
            # Update behavior pattern
            if changes["change_type"] == "increased_variance":
                profile.behavior_pattern = BehaviorPattern.VARIABLE
            elif changes["change_type"] == "strategy_shift":
                profile.behavior_pattern = BehaviorPattern.ADAPTIVE
            elif changes["change_type"] == "erratic_behavior":
                profile.behavior_pattern = BehaviorPattern.ERRATIC
            
            self.logger.info(f"Behavior change detected for Player {profile.player_id}: {changes['change_type']}")
    
    def get_player_profile(self, player_id: int) -> Optional[PlayerBehaviorProfile]:
        """Get comprehensive player behavior profile."""
        return self.player_profiles.get(player_id)
    
    def get_table_analysis(self) -> Dict[str, Any]:
        """Get comprehensive analysis of all players at the table."""
        if not self.player_profiles:
            return {"error": "No players observed"}
        
        # Aggregate statistics
        player_types = [p.player_type for p in self.player_profiles.values() if p.confidence >= self.confidence_threshold]
        type_distribution = {ptype.value: player_types.count(ptype) for ptype in PlayerType}
        
        # Table dynamics
        avg_confidence = np.mean([p.confidence for p in self.player_profiles.values()])
        total_observations = sum(p.hands_observed for p in self.player_profiles.values())
        
        # Risk analysis
        risk_levels = [p.metrics.risk_tolerance for p in self.player_profiles.values()]
        table_risk = np.mean(risk_levels) if risk_levels else 0.5
        
        return {
            "num_players": len(self.player_profiles),
            "player_type_distribution": type_distribution,
            "avg_classification_confidence": avg_confidence,
            "total_hands_observed": total_observations,
            "table_risk_level": table_risk,
            "players_with_behavior_changes": len([p for p in self.player_profiles.values() if p.pattern_changes]),
            "interaction_patterns": self.interaction_tracker.get_summary()
        }


class BehaviorChangeDetector:
    """Detects significant changes in player behavior patterns."""
    
    def detect_changes(self, recent_window: List[Dict], historical_window: List[Dict]) -> Dict[str, Any]:
        """Detect significant behavior changes between time windows."""
        if not recent_window or not historical_window:
            return {"significant_change": False}
        
        # Calculate metrics for both windows
        recent_metrics = self._calculate_window_metrics(recent_window)
        historical_metrics = self._calculate_window_metrics(historical_window)
        
        # Detect specific types of changes
        changes = {
            "significant_change": False,
            "change_type": None,
            "magnitude": 0.0,
            "indicators": []
        }
        
        # Betting variance change
        bet_variance_change = abs(recent_metrics["bet_variance"] - historical_metrics["bet_variance"])
        if bet_variance_change > 0.3:
            changes["significant_change"] = True
            changes["change_type"] = "increased_variance"
            changes["magnitude"] = bet_variance_change
            changes["indicators"].append("betting_variance")
        
        # Action frequency change
        action_change = abs(recent_metrics["hit_frequency"] - historical_metrics["hit_frequency"])
        if action_change > 0.2:
            changes["significant_change"] = True
            changes["change_type"] = "strategy_shift"
            changes["magnitude"] = max(changes.get("magnitude", 0), action_change)
            changes["indicators"].append("action_frequency")
        
        # Consistency change
        consistency_change = abs(recent_metrics["consistency"] - historical_metrics["consistency"])
        if consistency_change > 0.3:
            changes["significant_change"] = True
            changes["change_type"] = "erratic_behavior"
            changes["magnitude"] = max(changes.get("magnitude", 0), consistency_change)
            changes["indicators"].append("decision_consistency")
        
        return changes
    
    def _calculate_window_metrics(self, window: List[Dict]) -> Dict[str, float]:
        """Calculate behavior metrics for a time window."""
        if not window:
            return {"bet_variance": 0, "hit_frequency": 0, "consistency": 0}
        
        bets = [action["bet"] for action in window]
        actions = [action["action"] for action in window]
        
        return {
            "bet_variance": np.var(bets) if len(bets) > 1 else 0,
            "hit_frequency": actions.count("hit") / len(actions),
            "consistency": len(set(actions)) / len(actions)  # Simplified consistency
        }


class InteractionTracker:
    """Tracks interaction patterns between players."""
    
    def __init__(self):
        self.interactions = defaultdict(list)
    
    def record_interaction(self, player_id: int, context: Dict) -> None:
        """Record player interaction context."""
        self.interactions[player_id].append({
            "timestamp": time.time(),
            "context": context
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of interaction patterns."""
        return {
            "players_with_interactions": len(self.interactions),
            "total_interactions": sum(len(interactions) for interactions in self.interactions.values())
        }


# Factory function
def create_behavior_analyzer(**kwargs) -> PlayerBehaviorAnalyzer:
    """Create FAZ 4.0 Advanced Player Behavior Analyzer."""
    return PlayerBehaviorAnalyzer(**kwargs)


# Test the behavior analyzer
if __name__ == "__main__":
    print("🧪 TESTING FAZ 4.0 ADVANCED PLAYER BEHAVIOR ANALYZER")
    
    analyzer = PlayerBehaviorAnalyzer()
    
    print("✅ Advanced Behavior Analyzer created successfully")
    print(f"🎯 Player Types: {[ptype.value for ptype in PlayerType]}")
    print(f"📊 Behavior Templates: {len(analyzer.behavior_templates)} types")
    
    # Simulate different player behaviors
    print(f"\n🎭 SIMULATING PLAYER BEHAVIORS...")
    
    # Conservative player
    for i in range(15):
        analyzer.observe_player_action(
            player_id=1,
            action=np.random.choice(["stand", "hit"], p=[0.6, 0.4]),
            bet_amount=np.random.uniform(10, 20),  # Small bets
            hand_total=np.random.randint(12, 18),
            dealer_upcard=np.random.randint(2, 11),
            true_count=np.random.uniform(-2, 2)
        )
    
    # Aggressive player
    for i in range(15):
        analyzer.observe_player_action(
            player_id=2,
            action=np.random.choice(["hit", "double"], p=[0.6, 0.4]),
            bet_amount=np.random.uniform(50, 100),  # Large bets
            hand_total=np.random.randint(10, 16),
            dealer_upcard=np.random.randint(2, 11),
            true_count=np.random.uniform(-2, 2)
        )
    
    # Card counter
    for i in range(15):
        tc = np.random.uniform(-3, 3)
        bet_size = 10 + max(0, tc * 20)  # TC-correlated betting
        analyzer.observe_player_action(
            player_id=3,
            action=np.random.choice(["stand", "hit"], p=[0.55, 0.45]),
            bet_amount=bet_size,
            hand_total=np.random.randint(12, 18),
            dealer_upcard=np.random.randint(2, 11),
            true_count=tc
        )
    
    # Get analysis results
    table_analysis = analyzer.get_table_analysis()
    print(f"\n📈 TABLE ANALYSIS:")
    print(f"Players: {table_analysis['num_players']}")
    print(f"Type Distribution: {table_analysis['player_type_distribution']}")
    print(f"Avg Confidence: {table_analysis['avg_classification_confidence']:.2f}")
    print(f"Table Risk Level: {table_analysis['table_risk_level']:.2f}")
    
    # Check individual classifications
    for player_id in [1, 2, 3]:
        profile = analyzer.get_player_profile(player_id)
        if profile:
            print(f"\nPlayer {player_id}:")
            print(f"  Type: {profile.player_type.value}")
            print(f"  Confidence: {profile.confidence:.2f}")
            print(f"  Risk Tolerance: {profile.metrics.risk_tolerance:.2f}")
    
    print(f"\n✅ FAZ 4.0 Advanced Player Behavior Analyzer test complete!") 
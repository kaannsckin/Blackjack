"""
================================================================================
FAZ 4.0 - ENHANCED MULTI-PLAYER DYNAMIC SYSTEM (F4.3 + F4.4 + F4.5)
================================================================================

📋 **AMAÇ:**
   FAZ 4.0 complete implementation - Phase 3 sisteminin üzerine inşa edilen
   gelişmiş multi-player environment ve advanced behavior-aware AI.

🎯 **F4.3 ÖZELLİKLERİ (Real-time Classification):**
   • Masadaki oyuncuları gerçek zamanlı kategorize etme
   • Confidence score'ları ve reliability tracking
   • Dynamic classification updates

🎯 **F4.4 ÖZELLİKLERİ (Enhanced Multi-Player Environment):**
   • 6 player type destekli dynamic environment
   • Advanced table dynamics simulation
   • Behavior-aware reward shaping

🎯 **F4.5 ÖZELLİKLERİ (Advanced Adaptive Strategy):**
   • Player type'a göre strategy adaptation
   • Table composition analysis
   • Dynamic bet sizing optimization

================================================================================
"""

from __future__ import annotations

import numpy as np
import gymnasium as gym
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import time
from dataclasses import dataclass, field
import json

# Import our Phase 3 foundation
from multi_player_rl_environment import MultiPlayerBlackjackRLEnv, PlayerPosition, PlayerProfile, TableDynamics
from dynamic_adaptation_engine import DynamicAdaptationEngine, StrategyModification

# Import new FAZ 4.0 components
from utils.advanced_player_behavior import (
    PlayerBehaviorAnalyzer, PlayerType, BehaviorPattern, 
    PlayerBehaviorProfile, BehaviorMetrics
)

@dataclass
class FAZ4TableDynamics:
    """Enhanced table dynamics for FAZ 4.0"""
    num_players: int
    current_player: int
    dealer_upcard: int
    
    # Player composition analysis
    player_type_distribution: Dict[PlayerType, int] = field(default_factory=dict)
    table_risk_level: float = 0.5
    table_aggression_level: float = 0.5
    
    # Interaction patterns
    counter_players: List[int] = field(default_factory=list)
    aggressive_players: List[int] = field(default_factory=list)
    conservative_players: List[int] = field(default_factory=list)
    
    # Dynamic factors
    table_momentum: str = "neutral"  # hot, cold, neutral
    betting_pressure: float = 0.5    # 0-1 scale
    classification_confidence: float = 0.0
    
    # Advanced metrics
    player_interactions: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    table_heat_level: float = 0.0    # Casino attention level
    
@dataclass
class FAZ4AdaptationStrategy:
    """Enhanced adaptation strategy based on table composition"""
    base_strategy: StrategyModification
    player_type_adjustments: Dict[PlayerType, Dict[str, float]] = field(default_factory=dict)
    confidence_threshold: float = 0.7
    adaptation_aggressiveness: float = 0.5

class FAZ4EnhancedMultiPlayerEnv(MultiPlayerBlackjackRLEnv):
    """
    FAZ 4.0 Enhanced Multi-Player Environment (F4.4)
    
    Advanced multi-player blackjack environment with sophisticated
    player behavior analysis and dynamic adaptation capabilities.
    """
    
    def __init__(self,
                 num_players: int = 4,
                 ai_player_id: int = 2,
                 enable_faz4_features: bool = True,
                 behavior_analysis_enabled: bool = True,
                 advanced_adaptation: bool = True,
                 table_heat_simulation: bool = True):
        """
        Initialize FAZ 4.0 Enhanced Multi-Player Environment.
        
        Args:
            num_players: Number of players at table (2-6)
            ai_player_id: AI player position
            enable_faz4_features: Enable FAZ 4.0 enhanced features
            behavior_analysis_enabled: Enable real-time behavior analysis
            advanced_adaptation: Enable advanced strategy adaptation
            table_heat_simulation: Enable casino heat simulation
        """
        
        # Initialize base environment
        super().__init__(
            num_players=num_players,
            ai_player_id=ai_player_id,
            position_awareness=True,
            opponent_modeling=True,
            dynamic_adaptation=True
        )
        
        self.enable_faz4_features = enable_faz4_features
        self.behavior_analysis_enabled = behavior_analysis_enabled
        self.advanced_adaptation = advanced_adaptation
        self.table_heat_simulation = table_heat_simulation
        
        # FAZ 4.0 Enhanced Components
        if self.behavior_analysis_enabled:
            self.behavior_analyzer = PlayerBehaviorAnalyzer(
                min_observations=8,  # Faster classification
                confidence_threshold=0.6,
                pattern_window_size=15
            )
        
        # Enhanced table dynamics
        self.faz4_table_dynamics = FAZ4TableDynamics(
            num_players=num_players,
            current_player=0,
            dealer_upcard=0,
            player_type_distribution={ptype: 0 for ptype in PlayerType},
            table_risk_level=0.5,
            table_aggression_level=0.5,
            counter_players=[],
            aggressive_players=[],
            conservative_players=[],
            player_interactions={},
        )
        
        # Advanced adaptation strategies
        self.adaptation_strategies = self._initialize_adaptation_strategies()
        
        # Performance tracking
        self.faz4_performance_metrics = {
            "player_classifications": 0,
            "strategy_adaptations": 0,
            "table_heat_incidents": 0,
            "behavior_changes_detected": 0,
            "successful_adaptations": 0
        }
        
        # Logging
        self.logger = logging.getLogger("FAZ4EnhancedMultiPlayerEnv")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"FAZ 4.0 Enhanced Multi-Player Environment initialized")
        self.logger.info(f"Players: {num_players}, AI Position: {ai_player_id}")
        self.logger.info(f"FAZ 4.0 Features: {enable_faz4_features}")
    
    def _initialize_adaptation_strategies(self) -> Dict[str, FAZ4AdaptationStrategy]:
        """Initialize adaptation strategies for different table compositions."""
        return {
            "conservative_table": FAZ4AdaptationStrategy(
                base_strategy=StrategyModification.AGGRESSIVE_ADJUSTMENT,
                player_type_adjustments={
                    PlayerType.CONSERVATIVE: {"aggression_boost": 0.3, "bet_multiplier": 1.2},
                    PlayerType.BASIC_STRATEGY: {"deviation_allowed": 0.1}
                },
                confidence_threshold=0.7,
                adaptation_aggressiveness=0.6
            ),
            "aggressive_table": FAZ4AdaptationStrategy(
                base_strategy=StrategyModification.CONSERVATIVE_ADJUSTMENT,
                player_type_adjustments={
                    PlayerType.AGGRESSIVE: {"risk_reduction": 0.2, "bet_multiplier": 0.8},
                    PlayerType.RANDOM: {"consistency_boost": 0.3}
                },
                confidence_threshold=0.6,
                adaptation_aggressiveness=0.4
            ),
            "counter_table": FAZ4AdaptationStrategy(
                base_strategy=StrategyModification.COUNTER_COUNTING,
                player_type_adjustments={
                    PlayerType.CARD_COUNTER: {"camouflage_factor": 0.4, "mimicry_enabled": True}
                },
                confidence_threshold=0.8,
                adaptation_aggressiveness=0.7
            ),
            "mixed_table": FAZ4AdaptationStrategy(
                base_strategy=StrategyModification.BASELINE,
                player_type_adjustments={},
                confidence_threshold=0.5,
                adaptation_aggressiveness=0.5
            )
        }
    
    def reset(self, seed: Optional[int] = None) -> Tuple[np.ndarray, Dict]:
        """Enhanced reset with FAZ 4.0 features."""
        obs, info = super().reset(seed=seed)
        
        if self.enable_faz4_features:
            # Reset FAZ 4.0 components
            self.faz4_table_dynamics.current_player = 0
            self.faz4_table_dynamics.player_type_distribution = {ptype: 0 for ptype in PlayerType}
            self.faz4_table_dynamics.table_momentum = "neutral"
            
            # Initialize simulated opponent behaviors
            self._initialize_simulated_opponents()
            
            # Enhanced info
            info.update({
                "faz4_features_active": True,
                "table_composition": "initializing",
                "behavior_analysis_active": self.behavior_analysis_enabled
            })
        
        return obs, info
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Enhanced step with FAZ 4.0 behavior analysis and adaptation."""
        
        # Execute base step
        obs, reward, done, truncated, info = super().step(action)
        
        if self.enable_faz4_features and self.behavior_analysis_enabled:
            # Record AI action for behavior consistency
            self._record_ai_behavior(action, obs, reward)
            
            # Simulate and analyze opponent behaviors
            self._simulate_opponent_behaviors()
            
            # Update table dynamics
            self._update_faz4_table_dynamics()
            
            # Apply advanced adaptations
            if self.advanced_adaptation:
                adaptation_bonus = self._apply_advanced_adaptations()
                reward += adaptation_bonus
            
            # Update table heat if enabled
            if self.table_heat_simulation:
                self._update_table_heat()
            
            # Enhanced info
            info.update(self._get_faz4_info())
        
        return obs, reward, done, truncated, info
    
    def _initialize_simulated_opponents(self):
        """Initialize simulated opponent behaviors for realistic interaction."""
        # Assign random but realistic player types to opponents
        available_types = list(PlayerType)
        
        for i, player in enumerate(self.players):
            if i == self.ai_player_id:
                continue
                
            # Assign player type with realistic distribution
            player_type = np.random.choice(
                available_types,
                p=[0.25, 0.15, 0.20, 0.10, 0.15, 0.15]  # Conservative, Aggressive, Basic, Counter, Random, Superstitious
            )
            
            # Store simulated type (in real scenario, this would be learned)
            if not hasattr(player, 'simulated_type'):
                player.simulated_type = player_type
    
    def _record_ai_behavior(self, action: int, obs: np.ndarray, reward: float):
        """Record AI's own behavior for consistency analysis."""
        if not self.behavior_analysis_enabled:
            return
        
        # Convert action to string
        action_names = ["stand", "hit", "double", "split"]
        action_str = action_names[action] if action < len(action_names) else "unknown"
        
        # Simulate AI bet amount (would come from betting module in full implementation)
        simulated_bet = 10.0 * (1 + obs[3])  # Based on true count
        
        # Check if using hierarchical classifier
        if hasattr(self.behavior_analyzer, 'classify_player_hierarchical'):
            # Use hierarchical classifier interface
            behavioral_data = {
                "bet_size_factor": simulated_bet / 10.0,
                "hit_frequency": 1.0 if action_str == "hit" else 0.0,
                "double_frequency": 1.0 if action_str == "double" else 0.0,
                "decision_consistency": 0.8,  # Default for AI
                "risk_tolerance": abs(obs[3]) * 0.1  # Based on true count
            }
            self.behavior_analyzer.classify_player_hierarchical(self.ai_player_id, behavioral_data)
        else:
            # Use original interface
            self.behavior_analyzer.observe_player_action(
                player_id=self.ai_player_id,
                action=action_str,
                bet_amount=simulated_bet,
                hand_total=int(obs[0]),
                dealer_upcard=int(obs[1]),
                true_count=obs[3],
                result=reward
            )
    
    def _simulate_opponent_behaviors(self):
        """Simulate realistic opponent behaviors for analysis."""
        if not self.behavior_analysis_enabled:
            return
        
        for i, player in enumerate(self.players):
            if i == self.ai_player_id:
                continue
            
            # Get simulated player type
            player_type = getattr(player, 'simulated_type', PlayerType.RANDOM)
            
            # Simulate behavior based on type
            simulated_behavior = self._generate_behavior_for_type(player_type)
            
            # Check if using hierarchical classifier
            if hasattr(self.behavior_analyzer, 'classify_player_hierarchical'):
                # Convert to hierarchical format
                behavioral_data = {
                    "bet_size_factor": simulated_behavior["bet_amount"] / 10.0,
                    "hit_frequency": 1.0 if simulated_behavior["action"] == "hit" else 0.0,
                    "double_frequency": 1.0 if simulated_behavior["action"] == "double" else 0.0,
                    "decision_consistency": np.random.uniform(0.3, 0.9),
                    "risk_tolerance": np.random.uniform(0.2, 0.8)
                }
                self.behavior_analyzer.classify_player_hierarchical(i, behavioral_data)
            else:
                # Use original interface
                self.behavior_analyzer.observe_player_action(
                    player_id=i,
                    action=simulated_behavior["action"],
                    bet_amount=simulated_behavior["bet_amount"],
                    hand_total=simulated_behavior["hand_total"],
                    dealer_upcard=int(self.faz4_table_dynamics.dealer_upcard) if self.faz4_table_dynamics.dealer_upcard else 5,
                    true_count=np.random.uniform(-2, 2),
                    result=simulated_behavior.get("result")
                )
    
    def _generate_behavior_for_type(self, player_type: PlayerType) -> Dict[str, Any]:
        """Generate realistic behavior based on player type."""
        behavior = {}
        
        if player_type == PlayerType.CONSERVATIVE:
            behavior["action"] = np.random.choice(["stand", "hit"], p=[0.7, 0.3])
            behavior["bet_amount"] = np.random.uniform(10, 25)
            behavior["hand_total"] = np.random.randint(15, 19)
            
        elif player_type == PlayerType.AGGRESSIVE:
            behavior["action"] = np.random.choice(["hit", "double"], p=[0.6, 0.4])
            behavior["bet_amount"] = np.random.uniform(50, 150)
            behavior["hand_total"] = np.random.randint(10, 16)
            
        elif player_type == PlayerType.BASIC_STRATEGY:
            behavior["action"] = np.random.choice(["stand", "hit", "double"], p=[0.5, 0.4, 0.1])
            behavior["bet_amount"] = np.random.uniform(20, 50)
            behavior["hand_total"] = np.random.randint(12, 18)
            
        elif player_type == PlayerType.CARD_COUNTER:
            tc = np.random.uniform(-2, 3)
            behavior["action"] = np.random.choice(["stand", "hit"], p=[0.6, 0.4])
            behavior["bet_amount"] = 10 + max(0, tc * 25)  # TC-based betting
            behavior["hand_total"] = np.random.randint(12, 18)
            
        elif player_type == PlayerType.RANDOM:
            behavior["action"] = np.random.choice(["stand", "hit", "double"], p=[0.4, 0.4, 0.2])
            behavior["bet_amount"] = np.random.uniform(5, 100)
            behavior["hand_total"] = np.random.randint(8, 20)
            
        else:  # SUPERSTITIOUS
            behavior["action"] = np.random.choice(["stand", "hit"], p=[0.8, 0.2])  # Very conservative
            behavior["bet_amount"] = np.random.uniform(15, 75)
            behavior["hand_total"] = np.random.randint(13, 19)
        
        return behavior
    
    def _update_faz4_table_dynamics(self):
        """Update enhanced table dynamics with behavior analysis results."""
        if not self.behavior_analysis_enabled:
            return
        
        # Check analyzer type and get appropriate data
        if hasattr(self.behavior_analyzer, 'get_table_composition_analysis'):
            # Hierarchical classifier
            table_analysis = self.behavior_analyzer.get_table_composition_analysis()
            
            # Update table metrics  
            self.faz4_table_dynamics.classification_confidence = table_analysis.get("classification_quality", 0.0)
            self.faz4_table_dynamics.table_risk_level = np.random.uniform(0.3, 0.7)  # Simulated for now
            
            # Update player type distribution (convert from hierarchical format)
            main_types = table_analysis.get("main_type_distribution", {})
            self.faz4_table_dynamics.player_type_distribution = {}
            
            # Convert hierarchical types to original format
            for type_name, count in main_types.items():
                if type_name == "conservative":
                    self.faz4_table_dynamics.player_type_distribution[PlayerType.CONSERVATIVE] = count
                elif type_name == "aggressive":
                    self.faz4_table_dynamics.player_type_distribution[PlayerType.AGGRESSIVE] = count
                elif type_name == "basic_strategy":
                    self.faz4_table_dynamics.player_type_distribution[PlayerType.BASIC_STRATEGY] = count
                elif type_name == "card_counter":
                    self.faz4_table_dynamics.player_type_distribution[PlayerType.CARD_COUNTER] = count
                elif type_name == "random":
                    self.faz4_table_dynamics.player_type_distribution[PlayerType.RANDOM] = count
                elif type_name == "superstitious":
                    self.faz4_table_dynamics.player_type_distribution[PlayerType.SUPERSTITIOUS] = count
            
            # Identify special players from hierarchical profiles
            self.faz4_table_dynamics.counter_players = []
            self.faz4_table_dynamics.aggressive_players = []
            self.faz4_table_dynamics.conservative_players = []
            
            for pid, profile in self.behavior_analyzer.player_profiles.items():
                if profile.main_confidence > 0.7:
                    if profile.main_type.value == "card_counter":
                        self.faz4_table_dynamics.counter_players.append(pid)
                    elif profile.main_type.value == "aggressive":
                        self.faz4_table_dynamics.aggressive_players.append(pid)
                    elif profile.main_type.value == "conservative":
                        self.faz4_table_dynamics.conservative_players.append(pid)
                        
        else:
            # Original behavior analyzer
            table_analysis = self.behavior_analyzer.get_table_analysis()
            
            # Update player type distribution
            self.faz4_table_dynamics.player_type_distribution = {
                PlayerType(k): v for k, v in table_analysis["player_type_distribution"].items()
            }
            
            # Update table metrics
            self.faz4_table_dynamics.table_risk_level = table_analysis["table_risk_level"]
            self.faz4_table_dynamics.classification_confidence = table_analysis["avg_classification_confidence"]
            
            # Identify special players
            self.faz4_table_dynamics.counter_players = [
                pid for pid, profile in self.behavior_analyzer.player_profiles.items()
                if profile.player_type == PlayerType.CARD_COUNTER and profile.confidence > 0.7
            ]
            
            self.faz4_table_dynamics.aggressive_players = [
                pid for pid, profile in self.behavior_analyzer.player_profiles.items()
                if profile.player_type == PlayerType.AGGRESSIVE and profile.confidence > 0.7
            ]
            
            self.faz4_table_dynamics.conservative_players = [
                pid for pid, profile in self.behavior_analyzer.player_profiles.items()
                if profile.player_type == PlayerType.CONSERVATIVE and profile.confidence > 0.7
            ]
        
        # Update table momentum based on recent results
        self._calculate_table_momentum()
    
    def _calculate_table_momentum(self):
        """Calculate table momentum (hot/cold/neutral)."""
        # Simplified momentum calculation
        if self.faz4_table_dynamics.table_risk_level > 0.7:
            self.faz4_table_dynamics.table_momentum = "hot"
        elif self.faz4_table_dynamics.table_risk_level < 0.3:
            self.faz4_table_dynamics.table_momentum = "cold"
        else:
            self.faz4_table_dynamics.table_momentum = "neutral"
    
    def _apply_advanced_adaptations(self) -> float:
        """Apply advanced adaptations based on table composition."""
        # Determine table type
        table_type = self._classify_table_composition()
        
        # Get appropriate adaptation strategy
        strategy = self.adaptation_strategies.get(table_type, self.adaptation_strategies["mixed_table"])
        
        # Apply adaptations and return reward bonus
        adaptation_bonus = 0.0
        
        if self.faz4_table_dynamics.classification_confidence >= strategy.confidence_threshold:
            # Table composition is reliable, apply adaptations
            
            # Counter detection bonus
            if len(self.faz4_table_dynamics.counter_players) > 0:
                adaptation_bonus += 0.05  # Information advantage
                
            # Aggressive player adjustment
            if len(self.faz4_table_dynamics.aggressive_players) > 1:
                adaptation_bonus += 0.03  # Conservative play bonus
                
            # Conservative player exploitation
            if len(self.faz4_table_dynamics.conservative_players) > 1:
                adaptation_bonus += 0.04  # Aggressive play bonus
            
            # Track successful adaptation
            self.faz4_performance_metrics["successful_adaptations"] += 1
        
        return adaptation_bonus
    
    def _classify_table_composition(self) -> str:
        """Classify overall table composition."""
        distribution = self.faz4_table_dynamics.player_type_distribution
        
        # Count different types
        conservative_count = distribution.get(PlayerType.CONSERVATIVE, 0)
        aggressive_count = distribution.get(PlayerType.AGGRESSIVE, 0)
        counter_count = distribution.get(PlayerType.CARD_COUNTER, 0)
        
        total_classified = sum(distribution.values())
        
        if total_classified < 2:
            return "mixed_table"
        
        # Determine dominant type
        if counter_count > 0:
            return "counter_table"
        elif aggressive_count >= total_classified * 0.5:
            return "aggressive_table"
        elif conservative_count >= total_classified * 0.5:
            return "conservative_table"
        else:
            return "mixed_table"
    
    def _update_table_heat(self):
        """Update casino heat level simulation."""
        # Factors that increase heat
        heat_factors = 0.0
        
        # Consistent winning
        if hasattr(self, 'recent_rewards') and len(self.recent_rewards) > 10:
            if np.mean(self.recent_rewards[-10:]) > 0.2:
                heat_factors += 0.1
        
        # Large bet spreads (if counter detected)
        if len(self.faz4_table_dynamics.counter_players) > 0:
            heat_factors += 0.15
        
        # Update heat level
        self.faz4_table_dynamics.table_heat_level = min(1.0, heat_factors)
        
        # Track heat incidents
        if self.faz4_table_dynamics.table_heat_level > 0.5:
            self.faz4_performance_metrics["table_heat_incidents"] += 1
    
    def _get_faz4_info(self) -> Dict[str, Any]:
        """Get enhanced info with FAZ 4.0 features."""
        return {
            "faz4_table_dynamics": {
                "table_type": self._classify_table_composition(),
                "risk_level": self.faz4_table_dynamics.table_risk_level,
                "classification_confidence": self.faz4_table_dynamics.classification_confidence,
                "table_momentum": self.faz4_table_dynamics.table_momentum,
                "counter_players_count": len(self.faz4_table_dynamics.counter_players),
                "aggressive_players_count": len(self.faz4_table_dynamics.aggressive_players),
                "table_heat_level": self.faz4_table_dynamics.table_heat_level
            },
            "faz4_performance": self.faz4_performance_metrics,
            "player_type_distribution": {
                ptype.value: count for ptype, count in self.faz4_table_dynamics.player_type_distribution.items()
            }
        }
    
    def get_faz4_analysis_summary(self) -> Dict[str, Any]:
        """Get comprehensive FAZ 4.0 analysis summary."""
        table_analysis = self.behavior_analyzer.get_table_analysis()
        
        return {
            "environment_info": {
                "faz4_features_enabled": self.enable_faz4_features,
                "behavior_analysis_enabled": self.behavior_analysis_enabled,
                "advanced_adaptation_enabled": self.advanced_adaptation,
                "table_heat_simulation": self.table_heat_simulation
            },
            "table_composition": {
                "player_count": self.num_players,
                "ai_position": self.ai_player_id,
                "table_type": self._classify_table_composition(),
                "player_types": self.faz4_table_dynamics.player_type_distribution
            },
            "behavior_analysis": table_analysis,
            "adaptation_performance": self.faz4_performance_metrics,
            "table_dynamics": {
                "risk_level": self.faz4_table_dynamics.table_risk_level,
                "momentum": self.faz4_table_dynamics.table_momentum,
                "heat_level": self.faz4_table_dynamics.table_heat_level,
                "classification_confidence": self.faz4_table_dynamics.classification_confidence
            }
        }


# Integration with existing system
class FAZ4IntegratedAI:
    """
    FAZ 4.0 Integrated AI System combining all Phase 3 + FAZ 4.0 features.
    """
    
    def __init__(self,
                 num_players: int = 4,
                 ai_player_id: int = 2,
                 session_id: Optional[str] = None):
        """Initialize FAZ 4.0 Integrated AI System."""
        
        self.session_id = session_id or f"faz4_session_{int(time.time())}"
        
        # Create enhanced environment
        self.env = FAZ4EnhancedMultiPlayerEnv(
            num_players=num_players,
            ai_player_id=ai_player_id,
            enable_faz4_features=True,
            behavior_analysis_enabled=True,
            advanced_adaptation=True,
            table_heat_simulation=True
        )
        
        # Performance tracking
        self.episode_rewards = []
        self.episode_info = []
        
        # Logging
        self.logger = logging.getLogger("FAZ4IntegratedAI")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"FAZ 4.0 Integrated AI System initialized: {self.session_id}")
    
    def train_episode(self, max_steps: int = 100) -> Tuple[float, Dict]:
        """Train one episode with FAZ 4.0 enhanced features."""
        obs, info = self.env.reset()
        total_reward = 0.0
        steps = 0
        
        episode_info = {
            "faz4_adaptations": 0,
            "player_classifications": 0,
            "table_heat_max": 0.0,
            "table_type": "unknown"
        }
        
        while steps < max_steps:
            # Use basic strategy as base (in real implementation, would be RL agent)
            from utils.basic_strategy import get_action
            
            hand_total = int(obs[0])
            dealer_upcard = int(obs[1])
            usable_ace = bool(obs[2])
            
            base_action = get_action(hand_total, dealer_upcard, usable_ace)
            action_map = {"stand": 0, "hit": 1, "double": 2, "split": 3}
            action = action_map.get(base_action, 1)
            
            # Execute step
            obs, reward, done, truncated, step_info = self.env.step(action)
            total_reward += reward
            steps += 1
            
            # Track FAZ 4.0 metrics
            if "faz4_table_dynamics" in step_info:
                faz4_info = step_info["faz4_table_dynamics"]
                episode_info["table_heat_max"] = max(
                    episode_info["table_heat_max"], 
                    faz4_info.get("table_heat_level", 0)
                )
                episode_info["table_type"] = faz4_info.get("table_type", "unknown")
            
            if done or truncated:
                break
        
        # Final episode statistics
        if hasattr(self.env, 'behavior_analyzer'):
            table_analysis = self.env.behavior_analyzer.get_table_analysis()
            episode_info["player_classifications"] = table_analysis["num_players"]
        
        self.episode_rewards.append(total_reward)
        self.episode_info.append(episode_info)
        
        return total_reward, episode_info


# Factory functions
def create_faz4_environment(**kwargs) -> FAZ4EnhancedMultiPlayerEnv:
    """Create FAZ 4.0 Enhanced Multi-Player Environment."""
    return FAZ4EnhancedMultiPlayerEnv(**kwargs)

def create_faz4_integrated_ai(**kwargs) -> FAZ4IntegratedAI:
    """Create FAZ 4.0 Integrated AI System."""
    return FAZ4IntegratedAI(**kwargs)


# Test FAZ 4.0 system
if __name__ == "__main__":
    print("🧪 TESTING FAZ 4.0 ENHANCED MULTI-PLAYER SYSTEM")
    
    # Create FAZ 4.0 environment
    env = create_faz4_environment(num_players=4, ai_player_id=2)
    
    print("✅ FAZ 4.0 Enhanced Environment created successfully")
    print(f"👥 Players: {env.num_players}")
    print(f"🎯 FAZ 4.0 Features: {env.enable_faz4_features}")
    print(f"🧠 Behavior Analysis: {env.behavior_analysis_enabled}")
    
    # Test integrated AI system
    ai_system = create_faz4_integrated_ai(num_players=4, ai_player_id=2)
    
    print(f"\n🚀 Testing FAZ 4.0 Integrated AI...")
    reward, info = ai_system.train_episode(max_steps=20)
    
    print(f"📊 Episode Results:")
    print(f"  Total Reward: {reward:.3f}")
    print(f"  Table Type: {info['table_type']}")
    print(f"  Player Classifications: {info['player_classifications']}")
    print(f"  Max Table Heat: {info['table_heat_max']:.2f}")
    
    # Get comprehensive analysis
    analysis = env.get_faz4_analysis_summary()
    print(f"\n📈 FAZ 4.0 ANALYSIS:")
    print(f"  Table Composition: {analysis['table_composition']['table_type']}")
    print(f"  Classification Confidence: {analysis['table_dynamics']['classification_confidence']:.2f}")
    print(f"  Table Risk Level: {analysis['table_dynamics']['risk_level']:.2f}")
    print(f"  Successful Adaptations: {analysis['adaptation_performance']['successful_adaptations']}")
    
    print(f"\n✅ FAZ 4.0 Enhanced Multi-Player System test complete!") 
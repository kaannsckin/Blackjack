"""
================================================================================
FAZ 4.0 ENHANCED - HIERARCHICAL PLAYER CLASSIFICATION SYSTEM
================================================================================

📋 **AMAÇ:**
   Enhanced hierarchical player segmentation - Ana kategoriler altında 
   specialized sub-segments ile daha precise player profiling.

🎯 **HİERARŞİK YAPISI:**
   • Main Categories: 6 ana tip
   • Sub-Categories: Her ana tip altında 2-4 sub-segment
   • Micro-Behaviors: Detailed behavioral indicators
   • Dynamic Classification: Real-time switching between sub-types

🏗️ **ENHANCED SEGMENTATION:**
   Conservative → Conservative-Tight, Conservative-Loose, Conservative-Scared
   Aggressive → Aggressive-Calculated, Aggressive-Reckless, Aggressive-Tilted
   Basic Strategy → Basic-Perfect, Basic-Decent, Basic-Learning
   Card Counter → Counter-Basic, Counter-Advanced, Counter-Professional
   Random → Random-Chaotic, Random-Beginner, Random-Emotional
   Superstitious → Superstitious-Mild, Superstitious-Extreme, Superstitious-Pattern

================================================================================
"""

from __future__ import annotations

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque
import time

class MainPlayerType(Enum):
    """Ana oyuncu kategorileri"""
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BASIC_STRATEGY = "basic_strategy"
    CARD_COUNTER = "card_counter"
    RANDOM = "random"
    SUPERSTITIOUS = "superstitious"

class ConservativeSubType(Enum):
    """Conservative alt kategorileri"""
    TIGHT = "conservative_tight"           # Çok temkinli, minimal risk
    LOOSE = "conservative_loose"           # Orta düzey conservative
    SCARED = "conservative_scared"         # Kaybetme korkusu olan

class AggressiveSubType(Enum):
    """Aggressive alt kategorileri"""
    CALCULATED = "aggressive_calculated"   # Hesaplı agresif
    RECKLESS = "aggressive_reckless"       # Düşüncesiz agresif
    TILTED = "aggressive_tilted"           # Emotional/tilt durumunda
    SHOW_OFF = "aggressive_show_off"       # Gösteriş amaçlı

class BasicStrategySubType(Enum):
    """Basic Strategy alt kategorileri"""
    PERFECT = "basic_perfect"              # Mükemmel basic strategy
    DECENT = "basic_decent"                # İyi basic strategy
    LEARNING = "basic_learning"            # Öğrenmeye çalışan

class CardCounterSubType(Enum):
    """Card Counter alt kategorileri"""
    BASIC = "counter_basic"                # Temel Hi-Lo counter
    ADVANCED = "counter_advanced"          # İleri düzey systems
    PROFESSIONAL = "counter_professional"  # Pro level counter
    CAMOUFLAGED = "counter_camouflaged"    # Gizlice sayım yapan

class RandomSubType(Enum):
    """Random alt kategorileri"""
    CHAOTIC = "random_chaotic"             # Tamamen rastgele
    BEGINNER = "random_beginner"           # Yeni başlayan, bilgisiz
    EMOTIONAL = "random_emotional"         # Duygusal kararlar
    DRUNK = "random_drunk"                 # Alkol etkisinde

class SuperstitiousSubType(Enum):
    """Superstitious alt kategorileri"""
    MILD = "superstitious_mild"            # Hafif batıl inanç
    EXTREME = "superstitious_extreme"      # Aşırı batıl inanç
    PATTERN = "superstitious_pattern"      # Pattern arayışında olan
    LUCKY_CHARM = "superstitious_charm"    # Şanslı eşya kullanan

@dataclass
class HierarchicalPlayerProfile:
    """Hierarchical player classification profile"""
    player_id: int
    
    # Main classification
    main_type: MainPlayerType = MainPlayerType.CONSERVATIVE
    main_confidence: float = 0.0
    
    # Sub-classification
    sub_type: Optional[Union[ConservativeSubType, AggressiveSubType, BasicStrategySubType, 
                           CardCounterSubType, RandomSubType, SuperstitiousSubType]] = None
    sub_confidence: float = 0.0
    
    # Behavioral metrics for classification
    behavioral_scores: Dict[str, float] = field(default_factory=dict)
    
    # Classification history
    classification_history: List[Dict] = field(default_factory=list)
    
    # Micro-behaviors
    micro_behaviors: Dict[str, Any] = field(default_factory=dict)
    
    # Performance tracking
    hands_observed: int = 0
    classification_stability: float = 0.0
    last_reclassification: float = 0.0

class HierarchicalPlayerClassifier:
    """
    Advanced hierarchical player classification system.
    
    Two-level classification: Main Type → Sub Type with confidence scoring
    and dynamic switching capabilities.
    """
    
    def __init__(self, 
                 main_confidence_threshold: float = 0.7,
                 sub_confidence_threshold: float = 0.6,
                 reclassification_threshold: float = 0.4):
        """
        Initialize hierarchical classifier.
        
        Args:
            main_confidence_threshold: Threshold for main type classification
            sub_confidence_threshold: Threshold for sub-type classification
            reclassification_threshold: Threshold for triggering reclassification
        """
        self.main_confidence_threshold = main_confidence_threshold
        self.sub_confidence_threshold = sub_confidence_threshold
        self.reclassification_threshold = reclassification_threshold
        
        # Player profiles
        self.player_profiles: Dict[int, HierarchicalPlayerProfile] = {}
        
        # Classification templates
        self.main_type_templates = self._initialize_main_type_templates()
        self.sub_type_templates = self._initialize_sub_type_templates()
        
        # Micro-behavior indicators
        self.micro_behavior_indicators = self._initialize_micro_behaviors()
        
        # Logging
        self.logger = logging.getLogger("HierarchicalPlayerClassifier")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info("Hierarchical Player Classification System initialized")
    
    def _initialize_main_type_templates(self) -> Dict[MainPlayerType, Dict[str, Any]]:
        """Initialize main type classification templates."""
        return {
            MainPlayerType.CONSERVATIVE: {
                "bet_size_factor": (0.5, 2.0),        # 0.5-2x base bet
                "bet_variance_max": 0.3,
                "hit_frequency": (0.30, 0.45),
                "double_frequency_max": 0.12,
                "risk_tolerance_max": 0.35,
                "decision_consistency_min": 0.75
            },
            MainPlayerType.AGGRESSIVE: {
                "bet_size_factor": (2.0, 8.0),        # 2-8x base bet
                "bet_variance_min": 0.4,
                "hit_frequency": (0.45, 0.75),
                "double_frequency_min": 0.15,
                "risk_tolerance_min": 0.65,
                "decision_consistency_max": 0.65
            },
            MainPlayerType.BASIC_STRATEGY: {
                "bet_size_factor": (0.8, 3.0),        # Reasonable betting
                "decision_consistency_min": 0.80,
                "basic_strategy_adherence_min": 0.85,
                "hit_frequency": (0.38, 0.48),
                "double_frequency": (0.08, 0.15)
            },
            MainPlayerType.CARD_COUNTER: {
                "tc_bet_correlation_min": 0.6,        # Strong TC correlation
                "bet_spread_factor": (1.0, 10.0),     # Variable betting spread
                "decision_consistency_min": 0.75,
                "camouflage_attempts": 0.0            # May make deceptive plays
            },
            MainPlayerType.RANDOM: {
                "decision_consistency_max": 0.5,
                "pattern_predictability_max": 0.4,
                "bet_variance": (0.3, 1.0),
                "action_randomness_min": 0.6
            },
            MainPlayerType.SUPERSTITIOUS: {
                "irrational_decision_frequency_min": 0.2,
                "pattern_seeking_behavior": 0.3,
                "superstition_indicators_min": 2,     # Number of superstitious behaviors
                "decision_consistency": (0.3, 0.7)    # Inconsistent but with patterns
            }
        }
    
    def _initialize_sub_type_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize sub-type classification templates."""
        return {
            # Conservative Sub-types
            "conservative_tight": {
                "bet_size_factor": (0.5, 1.2),
                "risk_tolerance_max": 0.2,
                "hit_frequency_max": 0.35,
                "session_loss_tolerance": 0.1
            },
            "conservative_loose": {
                "bet_size_factor": (1.0, 2.5),
                "risk_tolerance": (0.2, 0.35),
                "hit_frequency": (0.35, 0.45),
                "occasional_risk_taking": 0.1
            },
            "conservative_scared": {
                "bet_decrease_on_loss": 0.3,
                "early_session_exit": 0.2,
                "hit_frequency_max": 0.3,
                "loss_aversion_high": True
            },
            
            # Aggressive Sub-types
            "aggressive_calculated": {
                "bet_increase_on_win": 0.4,
                "risk_tolerance": (0.6, 0.8),
                "decision_consistency": (0.6, 0.8),
                "strategic_aggression": True
            },
            "aggressive_reckless": {
                "bet_size_factor": (3.0, 10.0),
                "risk_tolerance_min": 0.8,
                "decision_consistency_max": 0.5,
                "impulse_betting": 0.3
            },
            "aggressive_tilted": {
                "bet_variance_high": 0.8,
                "consecutive_loss_escalation": 0.5,
                "emotional_betting": 0.4,
                "decision_quality_decline": 0.3
            },
            "aggressive_show_off": {
                "large_bet_frequency": 0.3,
                "attention_seeking_plays": 0.2,
                "social_betting_pressure": 0.25
            },
            
            # Basic Strategy Sub-types
            "basic_perfect": {
                "basic_strategy_adherence": (0.95, 1.0),
                "decision_consistency_min": 0.9,
                "optimal_play_frequency": 0.95
            },
            "basic_decent": {
                "basic_strategy_adherence": (0.80, 0.94),
                "decision_consistency": (0.75, 0.9),
                "learning_improvement": 0.1
            },
            "basic_learning": {
                "basic_strategy_adherence": (0.65, 0.85),
                "improvement_over_time": 0.15,
                "mistake_correction": 0.2
            },
            
            # Card Counter Sub-types
            "counter_basic": {
                "tc_bet_correlation": (0.6, 0.8),
                "bet_spread_factor": (1.0, 6.0),
                "basic_hi_lo_indicators": True
            },
            "counter_advanced": {
                "tc_bet_correlation": (0.8, 0.95),
                "bet_spread_factor": (1.0, 12.0),
                "advanced_count_indicators": True,
                "index_play_usage": 0.3
            },
            "counter_professional": {
                "tc_bet_correlation_min": 0.9,
                "perfect_camouflage": 0.4,
                "team_play_indicators": 0.2,
                "advanced_techniques": True
            },
            "counter_camouflaged": {
                "tc_bet_correlation": (0.7, 0.85),
                "camouflage_plays": 0.3,
                "cover_betting": 0.25,
                "stealth_indicators": True
            },
            
            # Random Sub-types
            "random_chaotic": {
                "decision_consistency_max": 0.3,
                "pattern_predictability_max": 0.2,
                "pure_randomness": 0.8
            },
            "random_beginner": {
                "basic_strategy_knowledge": 0.3,
                "learning_attempts": 0.2,
                "confusion_indicators": 0.4
            },
            "random_emotional": {
                "emotion_driven_decisions": 0.5,
                "mood_swings": 0.3,
                "result_dependent_strategy": 0.4
            },
            "random_drunk": {
                "decision_time_variance": 0.6,
                "increasingly_poor_decisions": 0.4,
                "coordination_issues": 0.3
            },
            
            # Superstitious Sub-types
            "superstitious_mild": {
                "superstition_frequency": (0.1, 0.3),
                "pattern_belief": 0.2,
                "lucky_number_usage": 0.15
            },
            "superstitious_extreme": {
                "superstition_frequency_min": 0.4,
                "irrational_decision_min": 0.3,
                "ritual_behavior": 0.4
            },
            "superstitious_pattern": {
                "pattern_seeking": 0.5,
                "sequence_betting": 0.3,
                "hot_cold_belief": 0.4
            },
            "superstitious_charm": {
                "lucky_charm_dependency": 0.6,
                "ritual_adherence": 0.5,
                "charm_based_decisions": 0.3
            }
        }
    
    def _initialize_micro_behaviors(self) -> Dict[str, Dict[str, Any]]:
        """Initialize micro-behavior indicators for detailed profiling."""
        return {
            "betting_patterns": {
                "martingale_usage": "doubles bet after loss",
                "paroli_usage": "doubles bet after win",
                "flat_betting": "consistent bet size",
                "progressive_betting": "systematic bet increases",
                "regression_betting": "systematic bet decreases"
            },
            "timing_patterns": {
                "quick_decisions": "fast decision making",
                "deliberate_thinking": "takes time to decide",
                "hesitation_patterns": "frequently changes mind",
                "confidence_timing": "decision speed correlates with confidence"
            },
            "social_behaviors": {
                "table_chat": "communicates with other players",
                "dealer_interaction": "engages with dealer",
                "observation_focus": "watches other players closely",
                "isolation_preference": "avoids social interaction"
            },
            "physical_tells": {
                "chip_handling": "nervous chip stacking/unstacking",
                "body_language": "posture changes with hand strength",
                "facial_expressions": "emotional reactions to cards",
                "breathing_patterns": "stress indicators"
            }
        }
    
    def classify_player_hierarchical(self, 
                                   player_id: int,
                                   behavioral_data: Dict[str, Any]) -> HierarchicalPlayerProfile:
        """
        Perform hierarchical classification of a player.
        
        Args:
            player_id: Player identifier
            behavioral_data: Comprehensive behavioral metrics
            
        Returns:
            Hierarchical player profile with main and sub classifications
        """
        # Get or create player profile
        if player_id not in self.player_profiles:
            self.player_profiles[player_id] = HierarchicalPlayerProfile(player_id=player_id)
        
        profile = self.player_profiles[player_id]
        profile.hands_observed += 1
        
        # Step 1: Main type classification
        main_type, main_confidence = self._classify_main_type(behavioral_data)
        
        # Step 2: Sub-type classification (if main type is confident enough)
        sub_type, sub_confidence = None, 0.0
        if main_confidence >= self.main_confidence_threshold:
            sub_type, sub_confidence = self._classify_sub_type(main_type, behavioral_data)
        
        # Step 3: Update profile if classification is confident enough
        if main_confidence >= self.main_confidence_threshold:
            # Check if this is a significant change
            if profile.main_type != main_type:
                self._record_classification_change(profile, main_type, sub_type, main_confidence, sub_confidence)
            
            profile.main_type = main_type
            profile.main_confidence = main_confidence
            
            if sub_confidence >= self.sub_confidence_threshold:
                profile.sub_type = sub_type
                profile.sub_confidence = sub_confidence
        
        # Step 4: Update behavioral scores and micro-behaviors
        profile.behavioral_scores.update(behavioral_data)
        self._analyze_micro_behaviors(profile, behavioral_data)
        
        # Step 5: Calculate classification stability
        profile.classification_stability = self._calculate_stability(profile)
        
        return profile
    
    def _classify_main_type(self, behavioral_data: Dict[str, Any]) -> Tuple[MainPlayerType, float]:
        """Classify main player type with confidence score."""
        type_scores = {}
        
        for main_type, template in self.main_type_templates.items():
            score = self._calculate_template_similarity(behavioral_data, template)
            type_scores[main_type] = score
        
        # Find best match
        best_type = max(type_scores, key=type_scores.get)
        confidence = type_scores[best_type]
        
        return best_type, confidence
    
    def _classify_sub_type(self, main_type: MainPlayerType, behavioral_data: Dict[str, Any]) -> Tuple[Optional[Any], float]:
        """Classify sub-type within the main type category."""
        # Get relevant sub-types for the main type
        sub_type_candidates = self._get_sub_types_for_main_type(main_type)
        
        if not sub_type_candidates:
            return None, 0.0
        
        sub_type_scores = {}
        
        for sub_type_name in sub_type_candidates:
            if sub_type_name in self.sub_type_templates:
                template = self.sub_type_templates[sub_type_name]
                score = self._calculate_template_similarity(behavioral_data, template)
                sub_type_scores[sub_type_name] = score
        
        if not sub_type_scores:
            return None, 0.0
        
        # Find best sub-type
        best_sub_type_name = max(sub_type_scores, key=sub_type_scores.get)
        confidence = sub_type_scores[best_sub_type_name]
        
        # Convert string back to enum
        best_sub_type = self._string_to_sub_type_enum(main_type, best_sub_type_name)
        
        return best_sub_type, confidence
    
    def _get_sub_types_for_main_type(self, main_type: MainPlayerType) -> List[str]:
        """Get list of sub-type names for a given main type."""
        sub_type_mapping = {
            MainPlayerType.CONSERVATIVE: ["conservative_tight", "conservative_loose", "conservative_scared"],
            MainPlayerType.AGGRESSIVE: ["aggressive_calculated", "aggressive_reckless", "aggressive_tilted", "aggressive_show_off"],
            MainPlayerType.BASIC_STRATEGY: ["basic_perfect", "basic_decent", "basic_learning"],
            MainPlayerType.CARD_COUNTER: ["counter_basic", "counter_advanced", "counter_professional", "counter_camouflaged"],
            MainPlayerType.RANDOM: ["random_chaotic", "random_beginner", "random_emotional", "random_drunk"],
            MainPlayerType.SUPERSTITIOUS: ["superstitious_mild", "superstitious_extreme", "superstitious_pattern", "superstitious_charm"]
        }
        
        return sub_type_mapping.get(main_type, [])
    
    def _string_to_sub_type_enum(self, main_type: MainPlayerType, sub_type_name: str) -> Optional[Any]:
        """Convert sub-type string to appropriate enum."""
        enum_mapping = {
            MainPlayerType.CONSERVATIVE: ConservativeSubType,
            MainPlayerType.AGGRESSIVE: AggressiveSubType,
            MainPlayerType.BASIC_STRATEGY: BasicStrategySubType,
            MainPlayerType.CARD_COUNTER: CardCounterSubType,
            MainPlayerType.RANDOM: RandomSubType,
            MainPlayerType.SUPERSTITIOUS: SuperstitiousSubType
        }
        
        sub_enum_class = enum_mapping.get(main_type)
        if sub_enum_class:
            try:
                return sub_enum_class(sub_type_name)
            except ValueError:
                return None
        
        return None
    
    def _calculate_template_similarity(self, behavioral_data: Dict[str, Any], template: Dict[str, Any]) -> float:
        """Calculate similarity between behavioral data and template."""
        similarities = []
        
        for key, expected_value in template.items():
            if key not in behavioral_data:
                continue
            
            actual_value = behavioral_data[key]
            
            if isinstance(expected_value, tuple):
                # Range check
                min_val, max_val = expected_value
                if min_val <= actual_value <= max_val:
                    similarities.append(1.0)
                else:
                    # Distance-based similarity
                    distance = min(abs(actual_value - min_val), abs(actual_value - max_val))
                    max_distance = max_val - min_val
                    similarity = max(0.0, 1.0 - distance / max_distance)
                    similarities.append(similarity)
            
            elif isinstance(expected_value, (int, float)):
                # Direct comparison with tolerance
                if key.endswith("_min"):
                    similarity = min(1.0, actual_value / expected_value) if expected_value > 0 else 1.0
                elif key.endswith("_max"):
                    similarity = min(1.0, expected_value / actual_value) if actual_value > 0 else 1.0
                else:
                    # Exact match with tolerance
                    tolerance = abs(expected_value) * 0.2  # 20% tolerance
                    distance = abs(actual_value - expected_value)
                    similarity = max(0.0, 1.0 - distance / (tolerance + 1e-6))
                
                similarities.append(similarity)
            
            elif isinstance(expected_value, bool):
                # Boolean match
                similarities.append(1.0 if bool(actual_value) == expected_value else 0.0)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _analyze_micro_behaviors(self, profile: HierarchicalPlayerProfile, behavioral_data: Dict[str, Any]):
        """Analyze and record micro-behaviors for detailed profiling."""
        micro_behaviors = {}
        
        # Betting pattern analysis
        if "bet_progression" in behavioral_data:
            if behavioral_data["bet_progression"] == "martingale":
                micro_behaviors["martingale_usage"] = True
            elif behavioral_data["bet_progression"] == "paroli":
                micro_behaviors["paroli_usage"] = True
        
        # Decision timing analysis
        if "avg_decision_time" in behavioral_data:
            if behavioral_data["avg_decision_time"] < 3.0:
                micro_behaviors["quick_decisions"] = True
            elif behavioral_data["avg_decision_time"] > 10.0:
                micro_behaviors["deliberate_thinking"] = True
        
        # Social behavior indicators
        if "social_interaction" in behavioral_data:
            micro_behaviors["social_level"] = behavioral_data["social_interaction"]
        
        profile.micro_behaviors.update(micro_behaviors)
    
    def _record_classification_change(self, profile: HierarchicalPlayerProfile, new_main_type: MainPlayerType, 
                                    new_sub_type: Optional[Any], main_confidence: float, sub_confidence: float):
        """Record significant classification changes."""
        change_record = {
            "timestamp": time.time(),
            "previous_main": profile.main_type.value if profile.main_type else None,
            "previous_sub": profile.sub_type.value if profile.sub_type else None,
            "new_main": new_main_type.value,
            "new_sub": new_sub_type.value if new_sub_type else None,
            "main_confidence": main_confidence,
            "sub_confidence": sub_confidence,
            "hands_observed": profile.hands_observed
        }
        
        profile.classification_history.append(change_record)
        profile.last_reclassification = time.time()
        
        self.logger.info(f"Player {profile.player_id} reclassified: {profile.main_type.value if profile.main_type else 'None'} → {new_main_type.value}")
    
    def _calculate_stability(self, profile: HierarchicalPlayerProfile) -> float:
        """Calculate classification stability score."""
        if len(profile.classification_history) < 2:
            return 1.0
        
        # Stability based on frequency of classification changes
        recent_changes = len([c for c in profile.classification_history[-5:]])  # Last 5 changes
        max_changes = min(5, profile.hands_observed // 10)  # Expect some changes early on
        
        stability = max(0.0, 1.0 - recent_changes / max(1, max_changes))
        return stability
    
    def get_detailed_profile(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get comprehensive detailed profile for a player."""
        if player_id not in self.player_profiles:
            return None
        
        profile = self.player_profiles[player_id]
        
        return {
            "player_id": profile.player_id,
            "main_classification": {
                "type": profile.main_type.value if profile.main_type else "unknown",
                "confidence": profile.main_confidence
            },
            "sub_classification": {
                "type": profile.sub_type.value if profile.sub_type else "unknown",
                "confidence": profile.sub_confidence
            },
            "stability_metrics": {
                "classification_stability": profile.classification_stability,
                "hands_observed": profile.hands_observed,
                "classification_changes": len(profile.classification_history)
            },
            "behavioral_scores": profile.behavioral_scores,
            "micro_behaviors": profile.micro_behaviors,
            "classification_history": profile.classification_history[-3:]  # Last 3 changes
        }
    
    def get_table_composition_analysis(self) -> Dict[str, Any]:
        """Get detailed table composition analysis with hierarchical data."""
        if not self.player_profiles:
            return {"error": "No players classified"}
        
        # Main type distribution
        main_type_counts = defaultdict(int)
        sub_type_counts = defaultdict(int)
        
        high_confidence_players = 0
        stable_classifications = 0
        
        for profile in self.player_profiles.values():
            if profile.main_confidence >= self.main_confidence_threshold:
                main_type_counts[profile.main_type.value] += 1
                high_confidence_players += 1
                
                if profile.sub_confidence >= self.sub_confidence_threshold and profile.sub_type:
                    sub_type_counts[profile.sub_type.value] += 1
                
                if profile.classification_stability > 0.7:
                    stable_classifications += 1
        
        # Table dynamics
        total_players = len(self.player_profiles)
        classification_quality = high_confidence_players / total_players if total_players > 0 else 0
        
        return {
            "total_players": total_players,
            "high_confidence_players": high_confidence_players,
            "classification_quality": classification_quality,
            "stable_classifications": stable_classifications,
            "main_type_distribution": dict(main_type_counts),
            "sub_type_distribution": dict(sub_type_counts),
            "table_dynamics": {
                "dominant_main_type": max(main_type_counts, key=main_type_counts.get) if main_type_counts else "unknown",
                "type_diversity": len(main_type_counts),
                "sub_type_diversity": len(sub_type_counts)
            }
        }


# Factory function
def create_hierarchical_classifier(**kwargs) -> HierarchicalPlayerClassifier:
    """Create hierarchical player classifier."""
    return HierarchicalPlayerClassifier(**kwargs)


# Test the hierarchical classifier
if __name__ == "__main__":
    print("🧪 TESTING HIERARCHICAL PLAYER CLASSIFICATION SYSTEM")
    
    classifier = HierarchicalPlayerClassifier()
    
    print("✅ Hierarchical Classifier created successfully")
    print(f"🎯 Main Types: {[t.value for t in MainPlayerType]}")
    print(f"📊 Sub-types per main type:")
    
    for main_type in MainPlayerType:
        sub_types = classifier._get_sub_types_for_main_type(main_type)
        print(f"  {main_type.value}: {len(sub_types)} sub-types")
    
    # Test classification with sample data
    print(f"\n🎭 TESTING HIERARCHICAL CLASSIFICATION...")
    
    # Conservative-Tight player
    conservative_data = {
        "bet_size_factor": 0.8,
        "bet_variance": 0.2,
        "hit_frequency": 0.32,
        "double_frequency": 0.08,
        "risk_tolerance": 0.15,
        "decision_consistency": 0.85,
        "session_loss_tolerance": 0.05
    }
    
    profile1 = classifier.classify_player_hierarchical(1, conservative_data)
    
    # Aggressive-Reckless player  
    aggressive_data = {
        "bet_size_factor": 5.0,
        "bet_variance": 0.8,
        "hit_frequency": 0.65,
        "double_frequency": 0.25,
        "risk_tolerance": 0.9,
        "decision_consistency": 0.45,
        "impulse_betting": 0.4
    }
    
    profile2 = classifier.classify_player_hierarchical(2, aggressive_data)
    
    # Counter-Advanced player
    counter_data = {
        "tc_bet_correlation": 0.85,
        "bet_spread_factor": 8.0,
        "decision_consistency": 0.82,
        "advanced_count_indicators": True,
        "index_play_usage": 0.35
    }
    
    profile3 = classifier.classify_player_hierarchical(3, counter_data)
    
    # Print results
    for player_id in [1, 2, 3]:
        detailed = classifier.get_detailed_profile(player_id)
        if detailed:
            print(f"\nPlayer {player_id}:")
            print(f"  Main: {detailed['main_classification']['type']} (conf: {detailed['main_classification']['confidence']:.2f})")
            print(f"  Sub: {detailed['sub_classification']['type']} (conf: {detailed['sub_classification']['confidence']:.2f})")
            print(f"  Stability: {detailed['stability_metrics']['classification_stability']:.2f}")
    
    # Table analysis
    table_analysis = classifier.get_table_composition_analysis()
    print(f"\n📈 TABLE COMPOSITION ANALYSIS:")
    print(f"  Classification Quality: {table_analysis['classification_quality']:.1%}")
    print(f"  Main Type Distribution: {table_analysis['main_type_distribution']}")
    print(f"  Sub-type Distribution: {table_analysis['sub_type_distribution']}")
    print(f"  Dominant Type: {table_analysis['table_dynamics']['dominant_main_type']}")
    
    print(f"\n✅ Hierarchical Player Classification System test complete!") 
"""
================================================================================
F3.2: DYNAMIC RULE RANDOMIZATION SYSTEM
================================================================================

🎯 **AMAÇ:** Her episode için rastgele kural seti oluşturma
📋 **KAPSAM:** num_decks, H17/S17, penetration, DAS, surrender randomization
🔧 **ENTEGRASYON:** Multi-player environment ile seamless integration

================================================================================
"""

import random
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

class DealerRule(Enum):
    H17 = "H17"  # Hit on soft 17
    S17 = "S17"  # Stand on soft 17

@dataclass
class RuleSet:
    """Complete blackjack rule configuration."""
    num_decks: int
    penetration: float
    dealer_rule: DealerRule
    das: bool  # Double After Split
    surrender: bool
    blackjack_payout: float
    insurance: bool = True
    peek_on_ace: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for environment configuration."""
        return {
            "num_decks": self.num_decks,
            "penetration": self.penetration,
            "dealer_rule": self.dealer_rule.value,
            "das": self.das,
            "surrender": self.surrender,
            "blackjack_payout": self.blackjack_payout,
            "insurance": self.insurance,
            "peek_on_ace": self.peek_on_ace
        }
    
    def __str__(self) -> str:
        return f"RuleSet({self.num_decks}D, {self.dealer_rule.value}, DAS:{self.das}, Surr:{self.surrender}, Pen:{self.penetration:.2f})"

class DynamicRuleRandomizer:
    """
    F3.2: Dynamic rule randomization system.
    
    Generates random rule sets for each episode to improve model robustness
    and prevent overfitting to specific rule configurations.
    """
    
    def __init__(self, 
                 seed: Optional[int] = None,
                 rule_variation_level: str = "medium"):
        """
        Initialize dynamic rule randomizer.
        
        Args:
            seed: Random seed for reproducibility
            rule_variation_level: "low", "medium", "high" - controls variation range
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        self.rule_variation_level = rule_variation_level
        self.rule_history: List[RuleSet] = []
        self.episode_count = 0
        
        # Configure variation ranges based on level
        self._configure_variation_ranges()
        
        # Logging
        self.logger = logging.getLogger("DynamicRuleRandomizer")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"Initialized DynamicRuleRandomizer with {rule_variation_level} variation level")
    
    def _configure_variation_ranges(self):
        """Configure rule variation ranges based on variation level."""
        if self.rule_variation_level == "low":
            self.deck_range = (6, 8)  # 6-8 decks
            self.penetration_range = (0.70, 0.80)  # 70-80%
            self.das_probability = 0.9  # 90% DAS
            self.surrender_probability = 0.1  # 10% surrender
            self.bj_payout_range = (1.4, 1.6)  # 7:5 to 3:2
            
        elif self.rule_variation_level == "medium":
            self.deck_range = (4, 8)  # 4-8 decks
            self.penetration_range = (0.65, 0.85)  # 65-85%
            self.das_probability = 0.8  # 80% DAS
            self.surrender_probability = 0.3  # 30% surrender
            self.bj_payout_range = (1.2, 1.6)  # 6:5 to 3:2
            
        else:  # high variation
            self.deck_range = (1, 8)  # 1-8 decks
            self.penetration_range = (0.60, 0.90)  # 60-90%
            self.das_probability = 0.7  # 70% DAS
            self.surrender_probability = 0.5  # 50% surrender
            self.bj_payout_range = (1.0, 1.6)  # 1:1 to 3:2
    
    def generate_random_rules(self) -> RuleSet:
        """
        Generate a random rule set for the current episode.
        
        Returns:
            RuleSet: Randomly generated rule configuration
        """
        self.episode_count += 1
        
        # Generate random values within configured ranges
        num_decks = random.randint(*self.deck_range)
        penetration = random.uniform(*self.penetration_range)
        dealer_rule = random.choice([DealerRule.H17, DealerRule.S17])
        das = random.random() < self.das_probability
        surrender = random.random() < self.surrender_probability
        blackjack_payout = random.uniform(*self.bj_payout_range)
        
        # Create rule set
        rule_set = RuleSet(
            num_decks=num_decks,
            penetration=penetration,
            dealer_rule=dealer_rule,
            das=das,
            surrender=surrender,
            blackjack_payout=blackjack_payout
        )
        
        # Store in history
        self.rule_history.append(rule_set)
        
        # Log rule generation
        self.logger.info(f"Episode {self.episode_count}: Generated {rule_set}")
        
        return rule_set
    
    def get_rule_statistics(self) -> Dict:
        """Get statistics about generated rule sets."""
        if not self.rule_history:
            return {}
        
        stats = {
            "total_episodes": len(self.rule_history),
            "deck_distribution": {},
            "dealer_rule_distribution": {},
            "das_frequency": sum(1 for r in self.rule_history if r.das) / len(self.rule_history),
            "surrender_frequency": sum(1 for r in self.rule_history if r.surrender) / len(self.rule_history),
            "avg_penetration": np.mean([r.penetration for r in self.rule_history]),
            "avg_bj_payout": np.mean([r.blackjack_payout for r in self.rule_history])
        }
        
        # Deck distribution
        for rule in self.rule_history:
            stats["deck_distribution"][rule.num_decks] = stats["deck_distribution"].get(rule.num_decks, 0) + 1
        
        # Dealer rule distribution
        for rule in self.rule_history:
            rule_name = rule.dealer_rule.value
            stats["dealer_rule_distribution"][rule_name] = stats["dealer_rule_distribution"].get(rule_name, 0) + 1
        
        return stats
    
    def reset_history(self):
        """Reset rule history (useful for new training sessions)."""
        self.rule_history.clear()
        self.episode_count = 0
        self.logger.info("Rule history reset")

# Integration helper functions
def create_dynamic_randomizer(variation_level: str = "medium", seed: Optional[int] = None) -> DynamicRuleRandomizer:
    """Factory function to create dynamic rule randomizer."""
    return DynamicRuleRandomizer(seed=seed, rule_variation_level=variation_level)

def integrate_with_environment(env, randomizer: DynamicRuleRandomizer):
    """
    Integrate dynamic rule randomizer with existing environment.
    
    This function modifies the environment's reset method to use random rules.
    """
    original_reset = env.reset
    
    def dynamic_reset(seed=None):
        # Generate random rules for this episode
        rule_set = randomizer.generate_random_rules()
        
        # Update environment with new rules
        env.num_decks = rule_set.num_decks
        env.penetration = rule_set.penetration
        env.rules = rule_set.to_dict()
        
        # Call original reset
        return original_reset(seed)
    
    # Replace reset method
    env.reset = dynamic_reset
    
    return env

# Example usage and testing
if __name__ == "__main__":
    # Test dynamic rule randomizer
    randomizer = create_dynamic_randomizer("medium", seed=42)
    
    print("🔬 F3.2: Dynamic Rule Randomization Test")
    print("=" * 50)
    
    # Generate 10 random rule sets
    for i in range(10):
        rules = randomizer.generate_random_rules()
        print(f"Episode {i+1}: {rules}")
    
    # Show statistics
    stats = randomizer.get_rule_statistics()
    print(f"\n📊 Rule Statistics:")
    print(f"   Total episodes: {stats['total_episodes']}")
    print(f"   DAS frequency: {stats['das_frequency']:.2f}")
    print(f"   Surrender frequency: {stats['surrender_frequency']:.2f}")
    print(f"   Avg penetration: {stats['avg_penetration']:.3f}")
    print(f"   Avg BJ payout: {stats['avg_bj_payout']:.3f}")
    print(f"   Deck distribution: {stats['deck_distribution']}")
    print(f"   Dealer rule distribution: {stats['dealer_rule_distribution']}")
    
    print("\n✅ F3.2 Dynamic Rule Randomization: READY FOR INTEGRATION") 
#!/usr/bin/env python3
"""
Engine Integration Example (F1.5)

This script demonstrates how to integrate the AI Play Strategy with the blackjack engine.
Shows different integration patterns and configuration options.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any

import numpy as np

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Local imports
from utils.ai_play_strategy import create_ai_play_strategy
from utils.basic_strategy import BasicStrategy


class BlackjackEngine:
    """
    Simplified blackjack engine for demonstration.
    
    This shows how to integrate AI strategies with a game engine.
    """
    
    def __init__(self, player_config: Dict[str, Any]):
        """
        Initialize engine with player configuration.
        
        Args:
            player_config: Configuration for player strategy
        """
        self.player_config = player_config
        self.player_strategy = self._create_player_strategy()
        
    def _create_player_strategy(self):
        """Create player strategy based on configuration."""
        strategy_type = self.player_config.get("strategy", "basic")
        
        if strategy_type == "basic":
            return BasicStrategy()
        elif strategy_type == "ai_play":
            # Create action space for AI strategy
            from gymnasium import spaces
            action_space = spaces.Discrete(4)  # 0=stand, 1=hit, 2=double, 3=split
            
            model_path = self.player_config.get("model_path")
            use_validation = self.player_config.get("use_validation", True)
            
            return create_ai_play_strategy(
                action_space=action_space,
                model_path=model_path,
                use_validation=use_validation
            )
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
    
    def play_hand(self, player_total: int, dealer_up: int, usable_ace: bool = False, true_count: float = 0.0):
        """
        Play a single hand.
        
        Args:
            player_total: Player's hand total
            dealer_up: Dealer's up card
            usable_ace: Whether player has usable ace
            true_count: Current true count
            
        Returns:
            Action taken by the strategy
        """
        if hasattr(self.player_strategy, 'act'):
            # AI Play Strategy interface
            obs = (player_total, dealer_up, usable_ace, true_count)
            action_idx = self.player_strategy.act(obs)
            action_map = {0: "stand", 1: "hit", 2: "double", 3: "split"}
            return action_map[action_idx]
        else:
            # Basic Strategy interface
            return self.player_strategy.get_action(player_total, dealer_up, usable_ace)


def demonstrate_integration():
    """Demonstrate different integration patterns."""
    
    print("🎰 Blackjack Engine Integration Demo")
    print("=" * 50)
    
    # Configuration examples
    configs = {
        "basic": {
            "strategy": "basic"
        },
        "ai_random": {
            "strategy": "ai_play",
            "model_path": None,  # Will use random fallback
            "use_validation": True
        },
        "ai_with_model": {
            "strategy": "ai_play",
            "model_path": "runs/phase1/models/best_model.zip",
            "use_validation": True
        }
    }
    
    # Test scenarios
    scenarios = [
        (12, 6, False, 0.0),   # Basic scenario
        (16, 10, False, -2.0), # Tough scenario
        (11, 5, False, 1.0),   # Good double opportunity
        (20, 6, False, 0.0),   # Stand scenario
    ]
    
    for config_name, config in configs.items():
        print(f"\n📋 Testing {config_name} strategy:")
        print(f"   Config: {config}")
        
        try:
            engine = BlackjackEngine(config)
            
            for i, (player_total, dealer_up, usable_ace, true_count) in enumerate(scenarios):
                action = engine.play_hand(player_total, dealer_up, usable_ace, true_count)
                print(f"   Scenario {i+1}: Player {player_total} vs Dealer {dealer_up} → {action}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Integration demo completed!")


def test_performance_comparison():
    """Compare performance of different strategies."""
    
    print("\n📊 Performance Comparison")
    print("=" * 50)
    
    # Create strategies
    from gymnasium import spaces
    action_space = spaces.Discrete(4)
    
    strategies = {
        "basic": BasicStrategy(),
        "ai_random": create_ai_play_strategy(action_space, model_path=None),
        "ai_with_validation": create_ai_play_strategy(action_space, model_path=None, use_validation=True)
    }
    
    # Test scenarios
    num_scenarios = 1000
    rng = np.random.default_rng(42)
    
    results = {}
    
    for strategy_name, strategy in strategies.items():
        print(f"\nTesting {strategy_name}...")
        
        actions = []
        for _ in range(num_scenarios):
            # Generate random scenario
            player_total = rng.integers(4, 22)
            dealer_up = rng.integers(2, 12)
            usable_ace = rng.choice([True, False])
            true_count = rng.uniform(-5, 5)
            
            if hasattr(strategy, 'act'):
                # AI strategy
                obs = (player_total, dealer_up, usable_ace, true_count)
                action_idx = strategy.act(obs)
                action_map = {0: "stand", 1: "hit", 2: "double", 3: "split"}
                action = action_map[action_idx]
            else:
                # Basic strategy
                action = strategy.get_action(player_total, dealer_up, usable_ace)
            
            actions.append(action)
        
        # Calculate action distribution
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        results[strategy_name] = {
            "total_actions": len(actions),
            "action_distribution": action_counts
        }
        
        print(f"   Action distribution: {action_counts}")
    
    print("\n📈 Results Summary:")
    for strategy_name, result in results.items():
        print(f"   {strategy_name}: {result['action_distribution']}")


if __name__ == "__main__":
    demonstrate_integration()
    test_performance_comparison() 
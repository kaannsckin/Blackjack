"""
================================================================================
BETTING ACTION SPACE ENVIRONMENT (Phase 2 - F2.2)
================================================================================

📋 **AMAÇ:**
   F2.2 için combined action space: {play_action, bet_size} veya continuous betting.
   Tek RL agent'ın hem play hem betting kararlarını öğrenmesi.

🎯 **F2.2 ÖZELLİKLERİ:**
   • Combined Action Space: [play_action, bet_action] 
   • Discrete/Continuous betting options
   • Simultaneous play + betting decisions
   • Action masking for invalid combinations

🏗️ **ACTION SPACE OPTIONS:**
   • Option 1: MultiDiscrete([4, 7]) - Discrete play + Discrete bet
   • Option 2: Dict({play: Discrete(4), bet: Box()}) - Mixed action space
   • Option 3: Box() - Continuous combined actions

================================================================================
"""

from __future__ import annotations

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Any, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum

from betting_environment import BettingBlackjackEnv, BettingMetrics


class ActionSpaceType(Enum):
    """Different action space configurations for F2.2."""
    MULTI_DISCRETE = "multi_discrete"     # [play_idx, bet_idx]
    DICT_SPACE = "dict_space"             # {play: int, bet: float}
    CONTINUOUS = "continuous"             # [play_logits, bet_amount]


@dataclass
class ActionConfig:
    """Configuration for betting action space."""
    action_type: ActionSpaceType = ActionSpaceType.MULTI_DISCRETE
    bet_levels: list[float] = None
    min_bet: float = 1.0
    max_bet: float = 100.0
    continuous_play: bool = False  # If True, play actions are continuous too


class BettingActionEnv(BettingBlackjackEnv):
    """
    Enhanced environment with combined play+betting action space.
    
    F2.2 Implementation: Single agent learns both play strategy and bet sizing.
    """
    
    def __init__(
        self,
        *,
        seed: Optional[int] = None,
        rules: Optional[Dict[str, Any]] = None,
        penetration: float = 0.75,
        initial_bankroll: float = 1000.0,
        action_config: Optional[ActionConfig] = None,
        risk_aversion: float = 0.1,
    ) -> None:
        """
        Initialize combined action space environment.
        
        Args:
            action_config: Configuration for action space type and parameters
        """
        # Initialize with default betting config first
        super().__init__(
            seed=seed,
            rules=rules,
            penetration=penetration,
            initial_bankroll=initial_bankroll,
            min_bet=action_config.min_bet if action_config else 1.0,
            max_bet=action_config.max_bet if action_config else 100.0,
            risk_aversion=risk_aversion,
        )
        
        # Configure action space
        self.action_config = action_config or ActionConfig()
        if self.action_config.bet_levels is None:
            self.action_config.bet_levels = [1, 2, 5, 10, 25, 50, 100]
        
        # Store original action space for parent environment calls
        self._parent_action_space = spaces.Discrete(4)  # Original blackjack action space
        
        # Set up combined action space
        self._setup_action_space()
        
        # Track action statistics
        self.action_stats = {
            "play_actions": [0, 0, 0, 0],  # stand, hit, double, split
            "bet_amounts": [],
            "invalid_actions": 0,
            "total_actions": 0,
        }
    
    def _setup_action_space(self) -> None:
        """Setup the combined action space based on configuration."""
        if self.action_config.action_type == ActionSpaceType.MULTI_DISCRETE:
            # MultiDiscrete: [play_action, bet_level_index]
            self.action_space = spaces.MultiDiscrete([
                4,  # play actions: stand, hit, double, split
                len(self.action_config.bet_levels)  # bet level indices
            ])
            
        elif self.action_config.action_type == ActionSpaceType.DICT_SPACE:
            # Dict: {play: Discrete, bet: Box}
            self.action_space = spaces.Dict({
                "play": spaces.Discrete(4),
                "bet": spaces.Box(
                    low=self.min_bet,
                    high=self.max_bet,
                    shape=(1,),
                    dtype=np.float32
                )
            })
            
        elif self.action_config.action_type == ActionSpaceType.CONTINUOUS:
            # Continuous: [play_action_probs(4), bet_amount(1)]
            self.action_space = spaces.Box(
                low=np.array([0., 0., 0., 0., self.min_bet]),
                high=np.array([1., 1., 1., 1., self.max_bet]),
                dtype=np.float32
            )
        
        else:
            raise ValueError(f"Unknown action type: {self.action_config.action_type}")
    
    def parse_combined_action(self, action: Union[np.ndarray, Dict]) -> Tuple[int, float]:
        """
        Parse combined action into play_action and bet_amount.
        
        Args:
            action: Combined action from agent
            
        Returns:
            (play_action_idx, bet_amount)
        """
        if self.action_config.action_type == ActionSpaceType.MULTI_DISCRETE:
            play_action = int(action[0])
            bet_idx = int(action[1])
            bet_amount = self.action_config.bet_levels[bet_idx]
            
        elif self.action_config.action_type == ActionSpaceType.DICT_SPACE:
            play_action = int(action["play"])
            bet_amount = float(action["bet"][0])
            
        elif self.action_config.action_type == ActionSpaceType.CONTINUOUS:
            # Convert continuous play action to discrete
            play_probs = action[:4]
            play_action = int(np.argmax(play_probs))
            bet_amount = float(action[4])
            
        else:
            raise ValueError(f"Unknown action type: {self.action_config.action_type}")
        
        # Clamp bet amount to valid range
        bet_amount = np.clip(bet_amount, self.min_bet, self.max_bet)
        
        return play_action, bet_amount
    
    def is_valid_action(self, play_action: int, bet_amount: float) -> Tuple[bool, str]:
        """
        Check if the combined action is valid.
        
        Args:
            play_action: Play action index (0-3)
            bet_amount: Bet amount in units
            
        Returns:
            (is_valid, reason)
        """
        # Check play action validity
        if not (0 <= play_action <= 3):
            return False, f"Invalid play action: {play_action}"
        
        # Check bet amount validity
        if not (self.min_bet <= bet_amount <= self.max_bet):
            return False, f"Invalid bet amount: {bet_amount}"
        
        if bet_amount > self.bankroll:
            return False, f"Insufficient bankroll: {bet_amount} > {self.bankroll}"
        
        # Check split action validity (only if we have a pair)
        if play_action == 3:  # split
            current_hand = self.player_hands[self._current_hand_idx]
            if (len(current_hand) != 2 or 
                current_hand[0] != current_hand[1] or 
                self._split_count >= 3):
                return False, "Split not allowed for current hand"
        
        return True, "Valid action"
    
    def step(self, action: Union[np.ndarray, Dict]):
        """
        Execute combined play+betting action.
        
        Args:
            action: Combined action (format depends on action_space type)
            
        Returns:
            Standard gym step return: (obs, reward, done, truncated, info)
        """
        # Parse the combined action
        try:
            play_action, bet_amount = self.parse_combined_action(action)
        except Exception as e:
            # Invalid action format
            self.action_stats["invalid_actions"] += 1
            return self._get_enhanced_obs(), -10.0, True, False, {"error": f"Invalid action format: {e}"}
        
        # Validate action
        is_valid, reason = self.is_valid_action(play_action, bet_amount)
        if not is_valid:
            self.action_stats["invalid_actions"] += 1
            penalty = -min(bet_amount, 10.0)  # Penalty proportional to attempted bet
            return self._get_enhanced_obs(), penalty, True, False, {"error": reason}
        
        # Set bet amount for this episode
        success = self.set_bet_amount(bet_amount)
        if not success:
            # This shouldn't happen if validation passed, but safety check
            return self._get_enhanced_obs(), -5.0, True, False, {"error": "Failed to set bet amount"}
        
        # Update action statistics
        self.action_stats["play_actions"][play_action] += 1
        self.action_stats["bet_amounts"].append(bet_amount)
        self.action_stats["total_actions"] += 1
        
        # Execute the play action using parent environment
        # Temporarily restore original action space for parent step call
        original_action_space = self.action_space
        self.action_space = self._parent_action_space
        
        try:
            play_action_int = int(play_action)
            obs, reward, done, truncated, info = super().step(play_action_int)
        finally:
            # Restore our combined action space
            self.action_space = original_action_space
        
        # Add action info to episode info
        if done:
            info.update({
                "play_action": play_action,
                "bet_amount": bet_amount,
                "action_valid": True,
                "action_stats": self.get_action_statistics(),
            })
        
        return obs, reward, done, truncated, info
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """Get statistics about action usage."""
        total_actions = max(self.action_stats["total_actions"], 1)
        
        stats = {
            "total_actions": total_actions,
            "invalid_action_rate": self.action_stats["invalid_actions"] / total_actions,
            "play_action_distribution": [
                count / total_actions for count in self.action_stats["play_actions"]
            ],
            "play_action_names": ["stand", "hit", "double", "split"],
        }
        
        if self.action_stats["bet_amounts"]:
            bet_amounts = np.array(self.action_stats["bet_amounts"])
            stats.update({
                "avg_bet_amount": float(np.mean(bet_amounts)),
                "min_bet_amount": float(np.min(bet_amounts)),
                "max_bet_amount": float(np.max(bet_amounts)),
                "bet_std": float(np.std(bet_amounts)),
            })
        
        return stats
    
    def reset_action_stats(self) -> None:
        """Reset action statistics."""
        self.action_stats = {
            "play_actions": [0, 0, 0, 0],
            "bet_amounts": [],
            "invalid_actions": 0,
            "total_actions": 0,
        }


# Utility functions for F2.2 testing

def test_multi_discrete_action_space():
    """Test MultiDiscrete action space configuration."""
    print("🧪 Testing MultiDiscrete Action Space...")
    
    config = ActionConfig(
        action_type=ActionSpaceType.MULTI_DISCRETE,
        bet_levels=[1, 5, 10, 25]
    )
    env = BettingActionEnv(seed=42, action_config=config, initial_bankroll=100)
    
    # Test action space
    assert isinstance(env.action_space, spaces.MultiDiscrete)
    assert env.action_space.nvec.tolist() == [4, 4]  # 4 play actions, 4 bet levels
    
    # Test sample action
    action = env.action_space.sample()
    print(f"   ✅ Sample action: {action}")
    
    # Test action parsing
    play_action, bet_amount = env.parse_combined_action(action)
    print(f"   ✅ Parsed: play={play_action}, bet={bet_amount}")
    
    # Test episode
    obs, _ = env.reset()
    obs, reward, done, truncated, info = env.step([1, 2])  # hit, bet 10
    print(f"   ✅ Step result: reward={reward:.3f}, done={done}")
    
    print("✅ MultiDiscrete action space: PASSED")


def test_dict_action_space():
    """Test Dict action space configuration."""
    print("\n🧪 Testing Dict Action Space...")
    
    config = ActionConfig(
        action_type=ActionSpaceType.DICT_SPACE,
        min_bet=1.0,
        max_bet=50.0
    )
    env = BettingActionEnv(seed=42, action_config=config, initial_bankroll=100)
    
    # Test action space
    assert isinstance(env.action_space, spaces.Dict)
    assert "play" in env.action_space.spaces
    assert "bet" in env.action_space.spaces
    
    # Test sample action
    action = env.action_space.sample()
    print(f"   ✅ Sample action: {action}")
    
    # Test action parsing
    play_action, bet_amount = env.parse_combined_action(action)
    print(f"   ✅ Parsed: play={play_action}, bet={bet_amount:.2f}")
    
    # Test manual action
    manual_action = {"play": 0, "bet": np.array([5.0])}  # stand, bet 5
    obs, _ = env.reset()
    obs, reward, done, truncated, info = env.step(manual_action)
    print(f"   ✅ Manual action result: reward={reward:.3f}, done={done}")
    
    print("✅ Dict action space: PASSED")


def test_continuous_action_space():
    """Test Continuous action space configuration."""
    print("\n🧪 Testing Continuous Action Space...")
    
    config = ActionConfig(
        action_type=ActionSpaceType.CONTINUOUS,
        min_bet=1.0,
        max_bet=20.0
    )
    env = BettingActionEnv(seed=42, action_config=config, initial_bankroll=100)
    
    # Test action space
    assert isinstance(env.action_space, spaces.Box)
    assert env.action_space.shape == (5,)  # 4 play probs + 1 bet amount
    
    # Test sample action
    action = env.action_space.sample()
    print(f"   ✅ Sample action: {action}")
    
    # Test action parsing
    play_action, bet_amount = env.parse_combined_action(action)
    print(f"   ✅ Parsed: play={play_action}, bet={bet_amount:.2f}")
    
    # Test manual action
    manual_action = np.array([0.1, 0.8, 0.05, 0.05, 10.0])  # prefer hit, bet 10
    obs, _ = env.reset()
    obs, reward, done, truncated, info = env.step(manual_action)
    print(f"   ✅ Manual action result: reward={reward:.3f}, done={done}")
    
    print("✅ Continuous action space: PASSED")


def test_action_validation():
    """Test action validation logic."""
    print("\n🧪 Testing Action Validation...")
    
    env = BettingActionEnv(seed=42, initial_bankroll=50)
    obs, _ = env.reset()
    
    # Test valid action
    is_valid, reason = env.is_valid_action(1, 5.0)  # hit, bet 5
    assert is_valid, f"Valid action rejected: {reason}"
    print(f"   ✅ Valid action accepted: hit, bet 5")
    
    # Test invalid bet (too high)
    is_valid, reason = env.is_valid_action(1, 100.0)  # hit, bet 100 (> bankroll)
    assert not is_valid, "Invalid high bet was accepted"
    print(f"   ✅ Invalid high bet rejected: {reason}")
    
    # Test invalid play action
    is_valid, reason = env.is_valid_action(5, 5.0)  # invalid play action
    assert not is_valid, "Invalid play action was accepted"
    print(f"   ✅ Invalid play action rejected: {reason}")
    
    print("✅ Action validation: PASSED")


def run_f2_2_validation():
    """Run all F2.2 validation tests."""
    print("🚀 F2.2 BETTING ACTION SPACE - VALIDATION TESTS")
    print("=" * 60)
    
    try:
        test_multi_discrete_action_space()
        test_dict_action_space()
        test_continuous_action_space()
        test_action_validation()
        
        print("\n" + "=" * 60)
        print("🎉 F2.2 VALIDATION: ALL TESTS PASSED!")
        print("✅ MultiDiscrete action space working")
        print("✅ Dict action space implemented")
        print("✅ Continuous action space functional")
        print("✅ Action validation operational")
        print("\n🚀 F2.2 BETTING ACTION SPACE: READY FOR TRAINING!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_f2_2_validation()
    exit(0 if success else 1) 
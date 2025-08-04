#!/usr/bin/env python3
"""
Environment Debugging Script

Debug why AI betting environment episodes end immediately.
"""

import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from advanced_betting_environment import AdvancedBettingEnv, AdvancedConfig, ActionSpaceType
from betting_action_environment import ActionConfig
import gymnasium as gym


def test_basic_environment():
    """Test basic environment functionality."""
    
    print("🔍 BASIC ENVIRONMENT TEST")
    print("=" * 40)
    
    try:
        # Create simplest possible environment
        from betting_environment import BettingBlackjackEnv
        
        env = BettingBlackjackEnv(
            seed=42,
            initial_bankroll=1000.0,
            min_bet=10.0,
            max_bet=100.0
        )
        
        print("✅ Basic environment created")
        
        # Test reset
        obs, info = env.reset()
        print(f"✅ Reset successful")
        print(f"   Observation shape: {obs.shape}")
        print(f"   Observation: {obs}")
        print(f"   Info: {info}")
        
        # Test simple actions
        for i in range(5):
            action = env.action_space.sample()
            obs, reward, done, truncated, info = env.step(action)
            
            print(f"\nStep {i+1}:")
            print(f"   Action: {action}")
            print(f"   Reward: {reward:.3f}")
            print(f"   Done: {done}")
            print(f"   Truncated: {truncated}")
            print(f"   Bankroll: {info.get('bankroll', 'N/A')}")
            
            if done or truncated:
                print(f"   Episode ended after {i+1} steps")
                obs, info = env.reset()
        
        return True
        
    except Exception as e:
        print(f"❌ Basic environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_betting_action_environment():
    """Test betting action environment."""
    
    print("\n🔍 BETTING ACTION ENVIRONMENT TEST")
    print("=" * 40)
    
    try:
        from betting_action_environment import BettingActionEnv
        
        action_config = ActionConfig(
            action_type=ActionSpaceType.MULTI_DISCRETE,
            bet_levels=[10, 20, 50],
            min_bet=10.0,
            max_bet=50.0
        )
        
        env = BettingActionEnv(
            seed=42,
            initial_bankroll=1000.0,
            action_config=action_config
        )
        
        print("✅ Betting action environment created")
        print(f"   Action space: {env.action_space}")
        
        # Test reset
        obs, info = env.reset()
        print(f"✅ Reset successful")
        print(f"   Observation shape: {obs.shape}")
        
        # Test manual actions
        print("\n🎯 Testing manual actions:")
        
        test_actions = [
            [1, 0],  # hit, min bet
            [0, 1],  # stand, mid bet  
            [1, 2],  # hit, max bet
        ]
        
        for i, action in enumerate(test_actions):
            obs, reward, done, truncated, info = env.step(np.array(action))
            
            print(f"\nAction {i+1}: {action}")
            print(f"   Reward: {reward:.3f}")
            print(f"   Done: {done}")
            print(f"   Bankroll: {info.get('bankroll', 'N/A')}")
            print(f"   Bet amount: {info.get('bet_amount', 'N/A')}")
            
            if done or truncated:
                print(f"   Episode ended - resetting")
                obs, info = env.reset()
        
        return True
        
    except Exception as e:
        print(f"❌ Betting action environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_advanced_environment():
    """Test advanced environment with minimal features."""
    
    print("\n🔍 ADVANCED ENVIRONMENT TEST")
    print("=" * 40)
    
    try:
        # Test with minimal advanced features
        advanced_config = AdvancedConfig(
            enable_card_counting=True,
            enable_hand_history=False,  # Disable for now
            enable_deck_composition=False,  # Disable for now
            enable_table_dynamics=False,  # Disable for now
            hand_history_length=0
        )
        
        action_config = ActionConfig(
            action_type=ActionSpaceType.MULTI_DISCRETE,
            bet_levels=[10, 20, 50],
            min_bet=10.0,
            max_bet=50.0
        )
        
        env = AdvancedBettingEnv(
            seed=42,
            initial_bankroll=1000.0,
            action_config=action_config,
            advanced_config=advanced_config
        )
        
        print("✅ Advanced environment created")
        print(f"   Action space: {env.action_space}")
        
        # Test reset
        obs, info = env.reset()
        print(f"✅ Reset successful")
        print(f"   Observation shape: {obs.shape}")
        print(f"   Observation space: {env.observation_space}")
        
        # Check observation breakdown
        print(f"\n📊 Observation breakdown:")
        print(f"   Basic features [0-5]: {obs[:6]}")
        if len(obs) > 6:
            print(f"   Card counting [6-9]: {obs[6:10] if len(obs) > 9 else obs[6:]}")
        
        # Test a few steps
        for i in range(3):
            action = env.action_space.sample()
            obs, reward, done, truncated, info = env.step(action)
            
            print(f"\nStep {i+1}:")
            print(f"   Action: {action}")
            print(f"   Reward: {reward:.3f}")
            print(f"   Done: {done}")
            print(f"   Info keys: {list(info.keys())}")
            
            if done or truncated:
                print(f"   Episode ended - resetting")
                obs, info = env.reset()
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reward_calculation():
    """Test reward calculation logic."""
    
    print("\n🔍 REWARD CALCULATION TEST")
    print("=" * 40)
    
    try:
        from betting_environment import BettingBlackjackEnv
        
        env = BettingBlackjackEnv(
            seed=42,
            initial_bankroll=1000.0,
            min_bet=10.0,
            max_bet=100.0,
            risk_aversion=0.1
        )
        
        # Test different game outcomes
        test_scenarios = [
            (1.0, "Player wins"),
            (-1.0, "Player loses"), 
            (0.0, "Push"),
            (1.5, "Blackjack"),
            (-1.0, "Player busts")
        ]
        
        print("🧪 Testing reward calculation for different outcomes:")
        
        for game_reward, description in test_scenarios:
            env.current_bet = 20.0  # Set a test bet
            betting_reward = env.calculate_betting_reward(game_reward)
            
            print(f"   {description:<15}: Game reward: {game_reward:+.1f} → Betting reward: {betting_reward:+.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Reward calculation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_episode_termination():
    """Test why episodes terminate immediately."""
    
    print("\n🔍 EPISODE TERMINATION TEST")
    print("=" * 40)
    
    try:
        from betting_action_environment import BettingActionEnv
        
        action_config = ActionConfig(
            action_type=ActionSpaceType.MULTI_DISCRETE,
            bet_levels=[10, 20, 50],
            min_bet=10.0,
            max_bet=50.0
        )
        
        env = BettingActionEnv(
            seed=42,
            initial_bankroll=100.0,  # Small bankroll to test termination
            action_config=action_config
        )
        
        obs, info = env.reset()
        print(f"Initial bankroll: {env.bankroll}")
        print(f"Initial observation: {obs}")
        
        step_count = 0
        max_steps = 20
        
        while step_count < max_steps:
            # Try a simple action
            action = [1, 0]  # hit, min bet
            
            print(f"\nStep {step_count + 1}:")
            print(f"   Before action - Bankroll: {env.bankroll}")
            
            obs, reward, done, truncated, info = env.step(np.array(action))
            
            print(f"   Action: {action}")
            print(f"   Reward: {reward:.3f}")
            print(f"   Done: {done}")
            print(f"   Truncated: {truncated}")
            print(f"   After action - Bankroll: {env.bankroll}")
            print(f"   Info: {info}")
            
            step_count += 1
            
            if done or truncated:
                print(f"   *** Episode terminated after {step_count} steps ***")
                break
        
        if step_count >= max_steps:
            print(f"   Episode ran for {max_steps} steps without terminating")
        
        return True
        
    except Exception as e:
        print(f"❌ Episode termination test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all debugging tests."""
    
    print("🚨 ENVIRONMENT DEBUGGING SESSION")
    print("=" * 50)
    
    tests = [
        ("Basic Environment", test_basic_environment),
        ("Betting Action Environment", test_betting_action_environment),
        ("Advanced Environment", test_advanced_environment),
        ("Reward Calculation", test_reward_calculation),
        ("Episode Termination", test_episode_termination),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        success = test_func()
        results.append((test_name, success))
        
        if not success:
            print(f"\n🔴 {test_name} FAILED - stopping debug session")
            break
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 DEBUG SESSION SUMMARY")
    print('='*60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    if all(result[1] for result in results):
        print("\n🎉 All tests passed - environment seems functional")
        print("💡 Issue might be in training loop or hyperparameters")
    else:
        print(f"\n⚠️ {sum(1 for _, success in results if not success)} test(s) failed")
        print("🔧 Fix environment issues before retraining")


if __name__ == "__main__":
    main() 
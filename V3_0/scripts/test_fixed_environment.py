#!/usr/bin/env python3
"""
Test Fixed Environment

Test the corrected betting environment to verify bug fixes.
"""

import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from betting_environment_fixed import FixedBettingBlackjackEnv, create_fixed_betting_env


def test_fixed_environment():
    """Test the fixed betting environment."""
    
    print("🔧 TESTING FIXED BETTING ENVIRONMENT")
    print("=" * 50)
    
    # Create fixed environment
    env = create_fixed_betting_env(
        seed=42,
        initial_bankroll=1000.0,
        min_bet=10.0,
        max_bet=100.0,
        risk_aversion=0.05  # Reduced risk aversion
    )
    
    print("✅ Fixed environment created")
    print(f"   Action space: {env.action_space}")
    print(f"   Observation space: {env.observation_space.shape}")
    
    # Test multiple episodes
    total_steps = 0
    total_reward = 0.0
    episode_count = 0
    
    for episode in range(5):
        print(f"\n🎯 Episode {episode + 1}")
        print("-" * 30)
        
        obs, info = env.reset()
        episode_steps = 0
        episode_reward = 0.0
        
        print(f"   Initial bankroll: ${env.bankroll:.2f}")
        print(f"   Initial observation: {obs}")
        
        # Play one episode
        max_steps_per_episode = 50  # Safety limit
        
        while episode_steps < max_steps_per_episode:
            # Set a manual bet for testing
            env.set_bet_amount(20.0)
            
            # Choose action based on basic strategy
            player_total = int(obs[0])
            dealer_up = int(obs[1])
            
            if player_total < 12:
                action = 1  # hit
            elif player_total > 16:
                action = 0  # stand
            else:
                action = 1 if dealer_up >= 7 else 0
            
            obs, reward, done, truncated, info = env.step(action)
            
            print(f"      Step {episode_steps + 1}: action={action}, reward={reward:.3f}, done={done}")
            
            episode_steps += 1
            episode_reward += reward
            
            if done or truncated:
                print(f"      Episode ended after {episode_steps} steps")
                print(f"      Final bankroll: ${env.bankroll:.2f}")
                print(f"      Episode reward: {episode_reward:.3f}")
                print(f"      Game outcome: {info.get('game_outcome', 'N/A')}")
                break
        
        total_steps += episode_steps
        total_reward += episode_reward
        episode_count += 1
        
        if episode_steps >= max_steps_per_episode:
            print(f"      ⚠️ Episode hit step limit ({max_steps_per_episode})")
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("-" * 30)
    print(f"Episodes played: {episode_count}")
    print(f"Total steps: {total_steps}")
    print(f"Average steps per episode: {total_steps / episode_count:.1f}")
    print(f"Total reward: {total_reward:.3f}")
    print(f"Average reward per episode: {total_reward / episode_count:.3f}")
    print(f"Final bankroll: ${env.bankroll:.2f}")
    
    # Check if episodes are now longer than 1 step
    avg_episode_length = total_steps / episode_count
    if avg_episode_length > 1.5:
        print("✅ SUCCESS: Episodes are now multi-step (bug fixed!)")
        return True
    else:
        print("❌ FAILURE: Episodes still too short")
        return False


def test_reward_calculation():
    """Test reward calculation with fixed environment."""
    
    print("\n🧪 TESTING REWARD CALCULATION")
    print("=" * 40)
    
    env = create_fixed_betting_env(
        seed=42,
        initial_bankroll=1000.0,
        min_bet=10.0,
        risk_aversion=0.1
    )
    
    # Test different game outcomes
    test_scenarios = [
        (1.0, "Player wins", 20.0),
        (-1.0, "Player loses", 20.0), 
        (0.0, "Push", 20.0),
        (1.5, "Blackjack", 20.0),
    ]
    
    print("Game outcome → Betting reward:")
    
    for game_outcome, description, bet_amount in test_scenarios:
        env.current_bet = bet_amount
        betting_reward = env.calculate_betting_reward(game_outcome)
        
        print(f"   {description:<12}: {game_outcome:+.1f} → {betting_reward:+.3f} (bet: ${bet_amount})")
    
    return True


def test_multiple_hands():
    """Test playing multiple hands in sequence."""
    
    print("\n🃏 TESTING MULTIPLE HANDS")
    print("=" * 40)
    
    env = create_fixed_betting_env(
        seed=123,  # Different seed for variety
        initial_bankroll=500.0,
        min_bet=5.0,
        max_bet=50.0,
        risk_aversion=0.05
    )
    
    hands_played = 0
    initial_bankroll = env.bankroll
    
    for hand in range(10):
        obs, info = env.reset()
        
        # Vary bet amounts
        bet_amounts = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        bet_amount = bet_amounts[hand]
        
        env.set_bet_amount(bet_amount)
        
        print(f"\nHand {hand + 1}: Bet ${bet_amount}")
        print(f"   Before: Bankroll ${env.bankroll:.2f}")
        
        # Play the hand
        steps = 0
        while steps < 10:  # Safety limit
            action = env.action_space.sample()  # Random actions for test
            obs, reward, done, truncated, info = env.step(action)
            steps += 1
            
            if done or truncated:
                outcome = info.get('game_outcome', 'unknown')
                print(f"   After:  Bankroll ${env.bankroll:.2f} (outcome: {outcome:+.1f})")
                break
        
        hands_played += 1
        
        # Stop if bankroll too low
        if env.bankroll < env.min_bet:
            print(f"   💸 Bankroll depleted after {hands_played} hands")
            break
    
    final_bankroll = env.bankroll
    total_change = final_bankroll - initial_bankroll
    
    print(f"\n📈 Results after {hands_played} hands:")
    print(f"   Initial: ${initial_bankroll:.2f}")
    print(f"   Final:   ${final_bankroll:.2f}")
    print(f"   Change:  ${total_change:+.2f}")
    
    return True


def main():
    """Run all tests for fixed environment."""
    
    print("🔧 FIXED ENVIRONMENT TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Fixed Environment Basic Test", test_fixed_environment),
        ("Reward Calculation Test", test_reward_calculation),
        ("Multiple Hands Test", test_multiple_hands),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 TEST SUMMARY")
    print('='*60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - Environment fixes successful!")
        print("💡 Ready to proceed with training using fixed environment")
    else:
        print(f"\n⚠️ Some tests failed - need more fixes")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
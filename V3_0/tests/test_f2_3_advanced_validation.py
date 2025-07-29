#!/usr/bin/env python3
"""
F2.3 Advanced Validation Tests: Ultra-Sophisticated Environment
=============================================================

Comprehensive testing of all F2.3 advanced features:
- Multiple card counting systems
- Hand history tracking
- Table dynamics
- Deck composition analysis
- Advanced risk metrics
- Kelly Criterion & Sharpe Ratio
"""

import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from advanced_betting_environment import (
    AdvancedBettingEnv, AdvancedConfig, ActionConfig, ActionSpaceType,
    CardCountingSystem
)


def test_multiple_card_counting():
    """Test multiple card counting systems accuracy."""
    print("🧪 Testing Multiple Card Counting Systems...")
    
    config = AdvancedConfig(
        counting_systems=[CardCountingSystem.HI_LO, CardCountingSystem.KO, CardCountingSystem.RED_SEVEN],
        hand_history_size=5,
    )
    env = AdvancedBettingEnv(seed=42, initial_bankroll=1000, advanced_config=config)
    
    # Test initial counts
    for system_name, system_data in env.counting_systems.items():
        assert system_data["running_count"] == 0, f"{system_name} should start at 0"
        assert system_data["true_count"] == 0.0, f"{system_name} TC should start at 0"
    
    print(f"   ✅ Initialized {len(env.counting_systems)} counting systems")
    
    # Test card counting updates
    test_cards = [2, 5, 10, 1, 7, 9]  # Mix of low, high, neutral
    expected_hi_lo = [1, 2, 1, 0, 0, 0]  # Running count progression
    
    for i, card in enumerate(test_cards):
        env._update_card_counting(card)
        
        hi_lo_count = env.counting_systems["hi_lo"]["running_count"]
        assert hi_lo_count == expected_hi_lo[i], f"Hi-Lo count error at card {i}: expected {expected_hi_lo[i]}, got {hi_lo_count}"
    
    print(f"   ✅ Hi-Lo counting accuracy verified")
    
    # Test system differences
    hi_lo_final = env.counting_systems["hi_lo"]["running_count"]
    ko_final = env.counting_systems["ko"]["running_count"]
    
    # KO counts 7 as +1, Hi-Lo doesn't
    assert ko_final > hi_lo_final, "KO should be higher than Hi-Lo (includes 7)"
    
    print(f"   ✅ System differences verified: Hi-Lo={hi_lo_final}, KO={ko_final}")
    print("✅ Multiple card counting: PASSED")


def test_hand_history_tracking():
    """Test detailed hand history tracking."""
    print("\n🧪 Testing Hand History Tracking...")
    
    config = AdvancedConfig(
        hand_history_size=3,
        detailed_history=True,
    )
    env = AdvancedBettingEnv(seed=42, initial_bankroll=100, advanced_config=config)
    
    # Play several hands
    hand_results = []
    for episode in range(5):
        obs, _ = env.reset()
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        
        if done:
            hand_results.append({
                "hand_number": info.get("hand_number"),
                "net_result": info.get("net_units", 0),
                "bet_amount": info.get("bet_amount", 0),
            })
    
    # Test history size limit
    assert len(env.hand_history) <= config.hand_history_size, f"History too large: {len(env.hand_history)}"
    
    # Test hand record completeness
    if env.hand_history:
        latest_hand = env.hand_history[-1]
        assert hasattr(latest_hand, "hand_number"), "Missing hand_number"
        assert hasattr(latest_hand, "bet_amount"), "Missing bet_amount"
        assert hasattr(latest_hand, "net_result"), "Missing net_result"
        assert hasattr(latest_hand, "true_counts"), "Missing true_counts"
        assert hasattr(latest_hand, "bankroll_before"), "Missing bankroll_before"
        assert hasattr(latest_hand, "bankroll_after"), "Missing bankroll_after"
    
    print(f"   ✅ History size: {len(env.hand_history)}/{config.hand_history_size}")
    print(f"   ✅ Hand records contain all required fields")
    
    # Test history features calculation
    history_features = env._calculate_hand_history_features()
    assert len(history_features) == 10, f"Expected 10 history features, got {len(history_features)}"
    assert all(np.isfinite(f) for f in history_features), "History features contain NaN/inf"
    
    print(f"   ✅ History features: {history_features[:5]}")
    print("✅ Hand history tracking: PASSED")


def test_deck_composition_tracking():
    """Test deck composition analysis."""
    print("\n🧪 Testing Deck Composition Tracking...")
    
    config = AdvancedConfig(track_deck_composition=True)
    env = AdvancedBettingEnv(seed=42, initial_bankroll=1000, advanced_config=config, rules={"num_decks": 2})
    
    # Check initial composition
    initial_total = sum(env.deck_composition.values())
    expected_total = 2 * 52  # 2 decks
    assert initial_total == expected_total, f"Wrong initial deck size: {initial_total}"
    
    # Check each rank has correct count
    for rank in range(1, 14):
        expected_count = 2 * 4  # 2 decks * 4 suits
        assert env.deck_composition[rank] == expected_count, f"Rank {rank}: expected {expected_count}, got {env.deck_composition[rank]}"
    
    print(f"   ✅ Initial deck composition: {expected_total} cards")
    
    # Test card removal
    test_cards = [1, 1, 10, 10, 5, 7]  # Remove some cards
    original_aces = env.deck_composition[1]
    original_tens = env.deck_composition[10]
    
    for card in test_cards:
        env._update_deck_composition(card)
    
    # Verify updates
    assert env.deck_composition[1] == original_aces - 2, "Aces not properly updated"
    assert env.deck_composition[10] == original_tens - 2, "Tens not properly updated"
    assert env.total_cards_seen == len(test_cards), f"Cards seen: {env.total_cards_seen}"
    
    print(f"   ✅ Deck updates: Aces {original_aces}→{env.deck_composition[1]}, Tens {original_tens}→{env.deck_composition[10]}")
    
    # Test composition features
    comp_features = env._calculate_deck_composition_features()
    assert len(comp_features) == 13, f"Expected 13 composition features, got {len(comp_features)}"
    assert all(0 <= f <= 1 for f in comp_features), "Composition ratios should be 0-1"
    
    print(f"   ✅ Composition features: {comp_features[:5]}")
    print("✅ Deck composition tracking: PASSED")


def test_table_dynamics():
    """Test table dynamics tracking."""
    print("\n🧪 Testing Table Dynamics...")
    
    config = AdvancedConfig(
        track_table_dynamics=True,
        betting_pattern_window=10,
    )
    env = AdvancedBettingEnv(seed=42, initial_bankroll=1000, advanced_config=config)
    
    # Play several hands to generate dynamics
    results = []
    bets = []
    
    for episode in range(15):
        obs, _ = env.reset()
        
        # Vary bet amounts
        if hasattr(env.action_space, 'nvec'):  # MultiDiscrete
            bet_action = episode % len(env.action_config.bet_levels)
            action = [1, bet_action]  # Hit with varying bet
        else:
            action = env.action_space.sample()
        
        obs, reward, done, truncated, info = env.step(action)
        
        if done:
            results.append(info.get("net_units", 0))
            bets.append(info.get("bet_amount", 0))
    
    # Test table dynamics updates
    td = env.table_dynamics
    assert td.total_hands > 0, "No hands recorded"
    assert 0 <= td.win_rate <= 1, f"Invalid win rate: {td.win_rate}"
    assert td.average_bet > 0, f"Invalid average bet: {td.average_bet}"
    
    print(f"   ✅ Total hands: {td.total_hands}")
    print(f"   ✅ Win rate: {td.win_rate:.3f}")
    print(f"   ✅ Average bet: {td.average_bet:.2f}")
    print(f"   ✅ Win/Loss streaks: {td.max_win_streak}/{td.max_loss_streak}")
    
    # Test dynamics features
    dynamics_features = env._calculate_table_dynamics_features()
    assert len(dynamics_features) == 8, f"Expected 8 dynamics features, got {len(dynamics_features)}"
    assert all(np.isfinite(f) for f in dynamics_features), "Dynamics features contain NaN/inf"
    
    print(f"   ✅ Dynamics features: {dynamics_features[:4]}")
    print("✅ Table dynamics: PASSED")


def test_advanced_risk_metrics():
    """Test advanced risk calculation methods."""
    print("\n🧪 Testing Advanced Risk Metrics...")
    
    config = AdvancedConfig(
        calculate_kelly=True,
        real_time_sharpe=True,
        advanced_ror=True,
    )
    env = AdvancedBettingEnv(seed=42, initial_bankroll=100, advanced_config=config)
    
    # Simulate some episodes to build return history
    for episode in range(25):  # Enough for meaningful risk calculations
        obs, _ = env.reset()
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
    
    # Test risk metrics calculation
    risk_metrics = env._calculate_risk_metrics()
    
    # Risk of Ruin
    ror = risk_metrics[0]
    assert 0 <= ror <= 100, f"Invalid RoR: {ror}"
    
    # Kelly Criterion
    kelly = risk_metrics[1]
    assert 0.1 <= kelly <= 5.0, f"Kelly out of bounds: {kelly}"
    
    # Sharpe Ratio
    sharpe = risk_metrics[2]
    assert -5 <= sharpe <= 5, f"Sharpe out of bounds: {sharpe}"
    
    # Drawdown
    drawdown = risk_metrics[3]
    assert 0 <= drawdown <= 1, f"Invalid drawdown: {drawdown}"
    
    # Growth rate
    growth = risk_metrics[4]
    assert growth != 0, "Growth rate should not be exactly 0"
    
    print(f"   ✅ Risk of Ruin: {ror:.2f}%")
    print(f"   ✅ Kelly Criterion: {kelly:.2f}")
    print(f"   ✅ Sharpe Ratio: {sharpe:.2f}")
    print(f"   ✅ Max Drawdown: {drawdown:.3f}")
    print(f"   ✅ Growth Rate: {growth:.3f}")
    print("✅ Advanced risk metrics: PASSED")


def test_observation_space_integrity():
    """Test comprehensive observation space."""
    print("\n🧪 Testing Observation Space Integrity...")
    
    # Full configuration
    config = AdvancedConfig(
        counting_systems=[CardCountingSystem.HI_LO, CardCountingSystem.KO, CardCountingSystem.RED_SEVEN],
        hand_history_size=20,
        detailed_history=True,
        track_deck_composition=True,
        track_table_dynamics=True,
        calculate_kelly=True,
        real_time_sharpe=True,
        advanced_ror=True,
    )
    
    env = AdvancedBettingEnv(seed=42, initial_bankroll=1000, advanced_config=config)
    
    # Test observation space dimensions
    obs_dim = env.observation_space.shape[0]
    print(f"   ✅ Observation dimension: {obs_dim}")
    
    # Expected breakdown:
    # Base: 7, Counting: 6 (3 systems × 2), History: 10, Deck: 13, Dynamics: 8, Risk: 5
    # Total: 7 + 6 + 10 + 13 + 8 + 5 = 49
    expected_dim = 49
    assert obs_dim == expected_dim, f"Expected {expected_dim} dimensions, got {obs_dim}"
    
    # Test observation generation
    obs, _ = env.reset()
    assert obs.shape == (obs_dim,), f"Observation shape mismatch: {obs.shape}"
    assert all(np.isfinite(obs)), "Observation contains NaN/inf values"
    
    # Test observation bounds
    assert env.observation_space.contains(obs), "Observation outside space bounds"
    
    print(f"   ✅ Observation sample: {obs[:10]}")
    print(f"   ✅ All values finite: {all(np.isfinite(obs))}")
    print(f"   ✅ Within bounds: {env.observation_space.contains(obs)}")
    
    # Test multiple episodes
    for episode in range(3):
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        
        if done:
            assert obs.shape == (obs_dim,), f"Episode {episode}: wrong obs shape"
            assert all(np.isfinite(obs)), f"Episode {episode}: non-finite values"
            obs, _ = env.reset()
    
    print("✅ Observation space integrity: PASSED")


def test_performance_comprehensive():
    """Test comprehensive environment performance."""
    print("\n🧪 Testing Comprehensive Performance...")
    
    config = AdvancedConfig()  # Default full config
    env = AdvancedBettingEnv(seed=42, initial_bankroll=1000, advanced_config=config)
    
    # Performance test
    import time
    start_time = time.time()
    
    total_episodes = 100
    total_steps = 0
    
    for episode in range(total_episodes):
        obs, _ = env.reset()
        done = False
        episode_steps = 0
        
        while not done and episode_steps < 20:  # Cap steps per episode
            action = env.action_space.sample()
            obs, reward, done, truncated, info = env.step(action)
            episode_steps += 1
            total_steps += 1
    
    elapsed_time = time.time() - start_time
    steps_per_second = total_steps / elapsed_time
    
    print(f"   ✅ Total episodes: {total_episodes}")
    print(f"   ✅ Total steps: {total_steps}")
    print(f"   ✅ Time elapsed: {elapsed_time:.2f}s")
    print(f"   ✅ Steps per second: {steps_per_second:.1f}")
    
    # Performance should be reasonable (>10 steps/second even with all features)
    assert steps_per_second > 10, f"Performance too slow: {steps_per_second:.1f} steps/s"
    
    # Test final metrics
    if hasattr(env, 'table_dynamics'):
        print(f"   ✅ Final win rate: {env.table_dynamics.win_rate:.3f}")
        print(f"   ✅ Hands tracked: {env.table_dynamics.total_hands}")
    
    print("✅ Comprehensive performance: PASSED")


def run_f2_3_validation():
    """Run all F2.3 advanced validation tests."""
    print("🚀 F2.3 ADVANCED BETTING ENVIRONMENT - COMPREHENSIVE VALIDATION")
    print("=" * 70)
    
    try:
        test_multiple_card_counting()
        test_hand_history_tracking()
        test_deck_composition_tracking()
        test_table_dynamics()
        test_advanced_risk_metrics()
        test_observation_space_integrity()
        test_performance_comprehensive()
        
        print("\n" + "=" * 70)
        print("🎉 F2.3 COMPREHENSIVE VALIDATION: ALL TESTS PASSED!")
        print("✅ Multiple card counting systems operational")
        print("✅ Hand history tracking comprehensive")
        print("✅ Deck composition analysis accurate")
        print("✅ Table dynamics monitoring functional")
        print("✅ Advanced risk metrics calculated")
        print("✅ 49-dimensional observation space validated")
        print("✅ Performance benchmarks met")
        print("\n🚀 F2.3 ADVANCED ENVIRONMENT: PRODUCTION READY!")
        print("🎯 Ready for professional-level RL training!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_f2_3_validation()
    exit(0 if success else 1) 
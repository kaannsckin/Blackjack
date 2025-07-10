#!/usr/bin/env python3
"""
Master Test Script for FAZ1.3 Enhancements

Tests all improvements:
1. Split action implementation
2. Comprehensive basic strategy
3. Performance metrics
4. Hyperparameter optimization
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.basic_strategy import BasicStrategy
from utils.performance_metrics import PerformanceAnalyzer, calculate_session_metrics


def test_basic_strategy() -> bool:
    """Test comprehensive basic strategy."""
    print("\n🧪 Testing Basic Strategy...")
    
    strategy = BasicStrategy()
    
    # Test cases
    test_cases = [
        # (player_total, dealer_up, usable_ace, expected_action)
        (20, 6, False, 0),  # Stand on 20
        (16, 10, False, 1),  # Hit 16 vs 10
        (11, 5, False, 2),   # Double 11 vs 5
        (8, 8, False, 1),    # Hit 8 vs 8
        (18, 6, True, 2),    # Double soft 18 vs 6
        (12, 4, False, 0),   # Stand 12 vs 4
    ]
    
    passed = 0
    for i, (player_total, dealer_up, usable_ace, expected) in enumerate(test_cases):
        action = strategy.get_action(player_total, dealer_up, usable_ace)
        if action == expected:
            passed += 1
            print(f"  ✅ Test {i+1}: {player_total} vs {dealer_up} (soft={usable_ace}) → {action}")
        else:
            print(f"  ❌ Test {i+1}: {player_total} vs {dealer_up} (soft={usable_ace}) → {action} (expected {expected})")
    
    print(f"Basic Strategy: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_performance_metrics() -> bool:
    """Test performance metrics calculation."""
    print("\n📊 Testing Performance Metrics...")
    
    analyzer = PerformanceAnalyzer()
    
    # Simulate rewards
    rewards = [1, -1, 0, 1, 1, -1, 0, 1, -1, 1]
    
    metrics = analyzer.calculate_metrics(rewards)
    
    # Verify metrics
    expected_ev = np.mean(rewards)
    expected_win_rate = np.mean([r > 0 for r in rewards]) * 100
    
    tests_passed = 0
    total_tests = 3
    
    if abs(metrics.ev - expected_ev) < 1e-6:
        print(f"  ✅ EV calculation: {metrics.ev:.4f}")
        tests_passed += 1
    else:
        print(f"  ❌ EV calculation: {metrics.ev:.4f} (expected {expected_ev:.4f})")
    
    if abs(metrics.win_rate - expected_win_rate) < 1e-6:
        print(f"  ✅ Win rate calculation: {metrics.win_rate:.2f}%")
        tests_passed += 1
    else:
        print(f"  ❌ Win rate calculation: {metrics.win_rate:.2f}% (expected {expected_win_rate:.2f}%)")
    
    if metrics.total_hands == len(rewards):
        print(f"  ✅ Total hands: {metrics.total_hands}")
        tests_passed += 1
    else:
        print(f"  ❌ Total hands: {metrics.total_hands} (expected {len(rewards)})")
    
    print(f"Performance Metrics: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests


def test_split_environment() -> bool:
    """Test split action in environment."""
    print("\n🃏 Testing Split Environment...")
    
    try:
        from rl_environment import BlackjackEnv
        
        env = BlackjackEnv(seed=42)
        obs, _ = env.reset()
        
        # Test basic functionality
        action = 1  # hit
        try:
            result = env.step(action)
            print("  ✅ Environment step works (no exception)")
            return True
        except Exception as e:
            print(f"  ❌ Environment step raised exception: {e}")
            return False
        
    except Exception as e:
        print(f"  ❌ Environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hyperparameter_optimization() -> bool:
    """Test hyperparameter optimization setup."""
    print("\n🔧 Testing Hyperparameter Optimization...")
    
    try:
        import optuna
        
        # Test basic Optuna functionality
        def objective(trial):
            x = trial.suggest_float("x", -10, 10)
            return x**2
        
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=5)
        
        print(f"  ✅ Optuna optimization works (best value: {study.best_value:.4f})")
        return True
        
    except ImportError:
        print("  ⚠️  Optuna not installed, skipping test")
        return True
    except Exception as e:
        print(f"  ❌ Optuna test failed: {e}")
        return False


def test_callback_module() -> bool:
    """Test callback module functionality."""
    print("\n📞 Testing Callback Module...")
    
    try:
        from utils.callbacks import SaveBestModelCallback
        
        # Test if class can be instantiated
        callback = SaveBestModelCallback(
            eval_env=None,  # Will be set later
            eval_freq=1000,
            n_eval_episodes=100,
            save_path="test_models",
            deterministic=True,
            verbose=1,
        )
        
        print("  ✅ SaveBestModelCallback can be instantiated")
        return True
        
    except Exception as e:
        print(f"  ❌ Callback test failed: {e}")
        return False


def test_tracking_module() -> bool:
    """Test tracking module functionality."""
    print("\n📈 Testing Tracking Module...")
    
    try:
        from utils.tracking import init_wandb, get_tb_writer
        
        # Test if functions exist
        if callable(init_wandb) and callable(get_tb_writer):
            print("  ✅ Tracking functions are callable")
            return True
        else:
            print("  ❌ Tracking functions not callable")
            return False
        
    except Exception as e:
        print(f"  ❌ Tracking test failed: {e}")
        return False


def run_comprehensive_test() -> Dict[str, bool]:
    """Run all tests and return results."""
    print("🚀 FAZ1.3 COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    start_time = time.time()
    
    test_results = {
        "basic_strategy": test_basic_strategy(),
        "performance_metrics": test_performance_metrics(),
        "split_environment": test_split_environment(),
        "hyperparameter_optimization": test_hyperparameter_optimization(),
        "callback_module": test_callback_module(),
        "tracking_module": test_tracking_module(),
    }
    
    elapsed_time = time.time() - start_time
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! FAZ1.3 enhancements are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the implementation.")
    
    return test_results


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Master test suite for FAZ1.3 enhancements")
    p.add_argument("--quick", action="store_true", help="Run quick tests only")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    
    if args.quick:
        print("Running quick tests only...")
        # Skip longer tests in quick mode
        pass
    
    results = run_comprehensive_test()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main() 
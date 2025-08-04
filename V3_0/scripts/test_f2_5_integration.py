#!/usr/bin/env python3
"""
F2.5 Motor Entegrasyonu Test Script

Tests AI betting strategy integration with simulation engine.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from blackjack_simulator import run_ai_betting_demo, save_results
from simulation_engine import PlayerConfig, GameConfig
from utils.ai_betting_strategy import create_ai_betting_strategy, BettingConfig
import time


def test_ai_betting_strategy_basic():
    """Test basic AI betting strategy functionality."""
    print("🧪 Testing AI Betting Strategy Basic Functionality...")
    
    # Check if we have a trained model
    model_path = "runs/f2_4_test/final_model.zip"
    if not Path(model_path).exists():
        print(f"❌ Model not found: {model_path}")
        print("   Please ensure F2.4 training is completed first.")
        return False
    
    try:
        # Create AI betting strategy
        config = BettingConfig(
            model_path=model_path,
            algorithm="ppo",
            min_bet=1.0,
            max_bet=100.0,
            initial_bankroll=1000.0
        )
        
        strategy = create_ai_betting_strategy(
            model_path=model_path,
            algorithm="ppo",
            min_bet=1.0,
            max_bet=100.0
        )
        
        # Test basic betting decision
        bet_amount = strategy.decide_bet(
            player_total=20,
            dealer_up=5,
            usable_ace=False,
            true_count=2.0
        )
        
        print(f"   ✅ AI bet decision: ${bet_amount:.2f} (TC=+2)")
        
        # Test with different scenarios
        scenarios = [
            (15, 10, False, -1.0),  # Negative count
            (21, 6, False, 3.0),    # High count
            (11, 5, False, 1.5),    # Neutral
        ]
        
        for player_total, dealer_up, usable_ace, true_count in scenarios:
            bet = strategy.decide_bet(player_total, dealer_up, usable_ace, true_count)
            print(f"   TC={true_count:+.1f}: ${bet:.2f}")
        
        print("   ✅ AI betting strategy basic test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ AI betting strategy test failed: {e}")
        return False


def test_simulation_integration():
    """Test full simulation integration."""
    print("\n🧪 Testing Simulation Integration...")
    
    model_path = "runs/f2_4_test/final_model.zip"
    if not Path(model_path).exists():
        print(f"❌ Model not found: {model_path}")
        return False
    
    try:
        # Run short simulation
        results = run_ai_betting_demo(
            bet_model_path=model_path,
            num_hands=100,  # Short test
            verbose=False
        )
        
        print(f"   ✅ Simulation completed: {results.total_hands} hands")
        print(f"   ✅ Speed: {results.hands_per_second:.0f} hands/sec")
        
        # Check that AI betting player exists
        ai_player_found = False
        for i, stats in enumerate(results.players_stats):
            if 'ai_betting_stats' in stats:
                ai_player_found = True
                ai_stats = stats['ai_betting_stats']
                print(f"   ✅ AI decisions: {ai_stats['ai_decisions']}")
                print(f"   ✅ AI decision ratio: {ai_stats['ai_decision_ratio']:.1%}")
                break
        
        if not ai_player_found:
            print("   ❌ AI betting player not found in results")
            return False
        
        print("   ✅ Simulation integration test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Simulation integration test failed: {e}")
        return False


def test_player_config_integration():
    """Test PlayerConfig with AI betting."""
    print("\n🧪 Testing PlayerConfig Integration...")
    
    model_path = "runs/f2_4_test/final_model.zip"
    if not Path(model_path).exists():
        print(f"❌ Model not found: {model_path}")
        return False
    
    try:
        # Create player config with AI betting
        config = PlayerConfig(
            name="TestAI",
            play_strategy="basic",
            bet_strategy="ai_bet",
            bet_model_path=model_path,
            bet_algorithm="ppo",
            bankroll=5000.0,
            min_bet=5.0,
            max_bet=250.0
        )
        
        print(f"   ✅ PlayerConfig created: {config.name}")
        print(f"   ✅ Bet strategy: {config.bet_strategy}")
        print(f"   ✅ Model path: {config.bet_model_path}")
        
        # Test with different bet strategies for comparison
        configs = [
            PlayerConfig(name="Flat", bet_strategy="flat", flat_bet_amount=25.0, bankroll=5000.0),
            PlayerConfig(name="TC", bet_strategy="tc_based", tc_bet_multiplier=3.0, bankroll=5000.0),
            config  # AI betting
        ]
        
        print(f"   ✅ Created {len(configs)} player configurations")
        print("   ✅ PlayerConfig integration test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ PlayerConfig integration test failed: {e}")
        return False


def run_comparison_demo():
    """Run a small demo comparing different betting strategies."""
    print("\n🎯 Running Betting Strategy Comparison Demo...")
    
    model_path = "runs/f2_4_test/final_model.zip"
    if not Path(model_path).exists():
        print(f"❌ Model not found: {model_path}")
        return False
    
    try:
        # Run comparison simulation
        results = run_ai_betting_demo(
            bet_model_path=model_path,
            num_hands=1000,
            verbose=True
        )
        
        # Save results
        timestamp = int(time.time())
        output_path = f"runs/f2_5_integration_test_{timestamp}.json"
        save_results(results, output_path)
        
        print("\n📊 STRATEGY COMPARISON SUMMARY:")
        print("="*50)
        
        for i, stats in enumerate(results.players_stats):
            config_name = ["AI_Betting_Basic", "Flat_Basic", "TC_Basic"][i] if i < 3 else "Unknown"
            
            print(f"\n{config_name}:")
            print(f"  ROI: {stats['roi']:+.2%}")
            print(f"  Win Rate: {stats['win_rate']:.1%}")
            print(f"  Avg Bet: ${stats['avg_bet']:.2f}")
            
            if 'ai_betting_stats' in stats:
                ai_stats = stats['ai_betting_stats']
                print(f"  AI Decisions: {ai_stats['ai_decision_ratio']:.1%}")
        
        print("\n✅ Comparison demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Comparison demo failed: {e}")
        return False


def main():
    """Run all F2.5 integration tests."""
    print("🚀 F2.5 MOTOR ENTEGRASYONU TEST SUITE")
    print("="*50)
    
    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    
    # Run tests
    tests = [
        ("AI Betting Strategy Basic", test_ai_betting_strategy_basic),
        ("Player Config Integration", test_player_config_integration),
        ("Simulation Integration", test_simulation_integration),
        ("Comparison Demo", run_comparison_demo),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if not result:
                print(f"\n❌ {test_name} FAILED - stopping tests")
                break
        except Exception as e:
            print(f"\n❌ {test_name} ERROR: {e}")
            results.append((test_name, False))
            break
    
    # Summary
    print("\n" + "="*50)
    print("🏁 TEST SUMMARY:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - F2.5 Integration Ready!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Please fix issues before proceeding")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Production Model Test for F2.5

Tests the production trained model performance against other betting strategies.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from blackjack_simulator import run_ai_betting_demo, save_results, BlackjackSimulator
from simulation_engine import PlayerConfig, GameConfig


def test_production_model_performance():
    """Test production model with comprehensive strategy comparison."""
    
    # Production model path
    production_model = "runs/f2_4_production/best_model/best_model.zip"
    
    if not Path(production_model).exists():
        print(f"❌ Production model not found: {production_model}")
        return False
    
    print("🚀 PRODUCTION MODEL PERFORMANCE TEST")
    print("="*50)
    print(f"Model: {production_model}")
    print(f"Hands: 10,000")
    print()
    
    # Game configuration
    game_config = GameConfig(
        num_hands=10000,
        num_decks=6,
        penetration=0.75,
        dealer_rule="S17",
        seed=42
    )
    
    # Player configurations for comprehensive comparison
    players_config = [
        # AI betting with production model
        PlayerConfig(
            name="AI_Production",
            play_strategy="basic",
            bet_strategy="ai_bet",
            bet_model_path=production_model,
            bet_algorithm="ppo",
            bankroll=50000.0,
            min_bet=10.0,
            max_bet=500.0
        ),
        
        # Flat betting baseline
        PlayerConfig(
            name="Flat_25",
            play_strategy="basic",
            bet_strategy="flat",
            flat_bet_amount=25.0,
            bankroll=50000.0,
            min_bet=10.0,
            max_bet=500.0
        ),
        
        # Conservative True Count betting
        PlayerConfig(
            name="TC_Conservative", 
            play_strategy="basic",
            bet_strategy="tc_based",
            tc_bet_multiplier=1.5,
            bankroll=50000.0,
            min_bet=10.0,
            max_bet=200.0
        ),
        
        # Aggressive True Count betting
        PlayerConfig(
            name="TC_Aggressive",
            play_strategy="basic", 
            bet_strategy="tc_based",
            tc_bet_multiplier=3.0,
            bankroll=50000.0,
            min_bet=10.0,
            max_bet=500.0
        ),
        
        # Small flat bet (risk-averse baseline)
        PlayerConfig(
            name="Flat_10",
            play_strategy="basic",
            bet_strategy="flat",
            flat_bet_amount=10.0,
            bankroll=50000.0,
            min_bet=10.0,
            max_bet=500.0
        ),
    ]
    
    try:
        # Run simulation
        simulator = BlackjackSimulator(game_config, players_config)
        results = simulator.run_simulation(verbose=True)
        
        # Save detailed results
        timestamp = int(time.time())
        output_path = f"runs/production_model_test_{timestamp}.json"
        save_results(results, output_path)
        
        # Detailed analysis
        print("\n" + "="*60)
        print("📊 PRODUCTION MODEL DETAILED ANALYSIS")
        print("="*60)
        
        # Find AI player
        ai_stats = None
        for i, stats in enumerate(results.players_stats):
            if 'ai_betting_stats' in stats:
                ai_stats = stats
                ai_config = players_config[i]
                break
        
        if ai_stats:
            print(f"\n🤖 AI BETTING ANALYSIS ({ai_config.name}):")
            print(f"   Final Bankroll: ${ai_stats['current_bankroll']:,.0f}")
            print(f"   ROI: {ai_stats['roi']:+.2%}")
            print(f"   Win Rate: {ai_stats['win_rate']:.1%}")
            print(f"   Total Hands: {ai_stats['hands_played']:,}")
            print(f"   Average Bet: ${ai_stats['avg_bet']:.2f}")
            print(f"   Total Bet Volume: ${ai_stats['total_bet']:,.0f}")
            
            # AI-specific metrics
            ai_betting = ai_stats['ai_betting_stats']
            print(f"\n   🎯 AI BETTING METRICS:")
            print(f"   AI Decisions: {ai_betting['ai_decisions']:,} ({ai_betting['ai_decision_ratio']:.1%})")
            print(f"   Fallback Decisions: {ai_betting['fallback_decisions']:,}")
            print(f"   Recent Avg Bet: ${ai_betting['recent_avg_bet']:.2f}")
            print(f"   Recent P&L: ${ai_betting['recent_results']:+.0f}")
            
            # Risk metrics
            max_dd = (ai_stats['initial_bankroll'] - ai_stats['min_bankroll']) / ai_stats['initial_bankroll']
            max_up = (ai_stats['max_bankroll'] - ai_stats['initial_bankroll']) / ai_stats['initial_bankroll']
            
            print(f"\n   📉 RISK METRICS:")
            print(f"   Max Drawdown: {max_dd:.1%}")
            print(f"   Max Runup: {max_up:.1%}")
            print(f"   Bankroll Range: ${ai_stats['min_bankroll']:,.0f} - ${ai_stats['max_bankroll']:,.0f}")
        
        # Strategy comparison
        print(f"\n📈 STRATEGY COMPARISON RANKINGS:")
        print("-" * 50)
        
        # Sort by ROI
        strategy_results = []
        for i, stats in enumerate(results.players_stats):
            config = players_config[i]
            strategy_results.append({
                'name': config.name,
                'roi': stats['roi'],
                'win_rate': stats['win_rate'],
                'avg_bet': stats['avg_bet'],
                'sharpe': stats['roi'] / (stats['avg_bet'] / stats['initial_bankroll']) if stats['avg_bet'] > 0 else 0,
                'total_bet': stats['total_bet'],
                'final_bankroll': stats['current_bankroll']
            })
        
        # Sort by ROI descending
        strategy_results.sort(key=lambda x: x['roi'], reverse=True)
        
        for i, result in enumerate(strategy_results, 1):
            print(f"{i}. {result['name']:<15} ROI: {result['roi']:+7.2%} | "
                  f"Win Rate: {result['win_rate']:5.1%} | "
                  f"Avg Bet: ${result['avg_bet']:6.2f} | "
                  f"Final: ${result['final_bankroll']:8.0f}")
        
        # Performance insights
        ai_result = next((r for r in strategy_results if 'AI' in r['name']), None)
        if ai_result:
            ai_rank = strategy_results.index(ai_result) + 1
            print(f"\n🎯 AI PERFORMANCE INSIGHTS:")
            print(f"   Ranking: #{ai_rank} out of {len(strategy_results)} strategies")
            
            best_strategy = strategy_results[0]
            if ai_result['name'] == best_strategy['name']:
                print("   🏆 AI BETTING IS THE BEST STRATEGY!")
            else:
                gap = best_strategy['roi'] - ai_result['roi']
                print(f"   Gap to #1: {gap:.2%} behind {best_strategy['name']}")
            
            # Compare to flat betting
            flat_results = [r for r in strategy_results if 'Flat' in r['name']]
            if flat_results:
                best_flat = max(flat_results, key=lambda x: x['roi'])
                ai_vs_flat = ai_result['roi'] - best_flat['roi']
                print(f"   vs Best Flat: {ai_vs_flat:+.2%} (vs {best_flat['name']})")
        
        print(f"\n📄 Detailed results saved to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Production model test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_production_model_performance()
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1) 
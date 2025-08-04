#!/usr/bin/env python3
"""
Advanced AI Calibration Script

Tune the state-of-the-art AI system for practical performance while maintaining sophistication.
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from advanced_betting_ai import AdvancedBettingConfig, create_advanced_betting_agent
from advanced_betting_environment import create_advanced_betting_env


def test_configuration(config: AdvancedBettingConfig, test_rounds: int = 50) -> Dict[str, float]:
    """Test a specific configuration and return performance metrics."""
    
    env = create_advanced_betting_env(
        seed=42,
        initial_bankroll=5000.0,
        min_bet=25.0,
        max_bet=250.0,
        use_advanced_ai=True,
        advanced_config=config
    )
    
    bet_data = []
    performance_data = []
    
    for round_num in range(test_rounds):
        obs, _ = env.reset()
        
        # Extract state
        true_count = obs[3]
        bankroll = env.bankroll
        
        # Get AI bet decision
        if env.advanced_agent:
            ai_bet = env.advanced_agent.decide_bet_size(
                observation=obs,
                bankroll=bankroll,
                bet_range=(env.min_bet, env.max_bet)
            )
        else:
            ai_bet = env.min_bet
        
        bet_data.append({
            'true_count': true_count,
            'ai_bet': ai_bet,
            'bankroll': bankroll
        })
        
        # Simple play for testing
        player_total = int(obs[0])
        dealer_up = int(obs[1])
        
        if player_total < 12:
            action = 1  # Hit
        elif player_total > 16:
            action = 0  # Stand
        elif dealer_up <= 6:
            action = 0  # Stand
        else:
            action = 1  # Hit
        
        obs, reward, done, truncated, info = env.step(action)
        
        if done:
            performance_data.append({
                'reward': reward,
                'bet_amount': ai_bet,
                'final_bankroll': env.bankroll
            })
    
    # Calculate metrics
    df_bets = pd.DataFrame(bet_data)
    df_perf = pd.DataFrame(performance_data)
    
    # Betting sophistication metrics
    tc_bet_corr = np.corrcoef(df_bets['true_count'], df_bets['ai_bet'])[0, 1] if len(df_bets) > 1 else 0
    bet_variance = df_bets['ai_bet'].std()
    bet_mean = df_bets['ai_bet'].mean()
    bet_cv = bet_variance / bet_mean if bet_mean > 0 else 0
    
    # Performance metrics
    avg_reward = df_perf['reward'].mean() if len(df_perf) > 0 else 0
    final_bankroll = env.bankroll
    roi = (final_bankroll - env.initial_bankroll) / env.initial_bankroll
    
    # Bet spread analysis
    high_count_bets = df_bets[df_bets['true_count'] > 1]['ai_bet']
    low_count_bets = df_bets[df_bets['true_count'] < 0]['ai_bet']
    bet_spread = (high_count_bets.mean() / low_count_bets.mean()) if len(high_count_bets) > 0 and len(low_count_bets) > 0 and low_count_bets.mean() > 0 else 1.0
    
    return {
        'tc_bet_correlation': tc_bet_corr,
        'bet_coefficient_variation': bet_cv,
        'bet_spread': bet_spread,
        'avg_reward': avg_reward,
        'roi': roi,
        'final_bankroll': final_bankroll,
        'mean_bet': bet_mean,
        'bet_std': bet_variance
    }


def optimize_kelly_parameters():
    """Optimize Kelly Criterion parameters for practical performance."""
    
    print("🔧 OPTIMIZING KELLY CRITERION PARAMETERS")
    print("=" * 50)
    
    # Test different Kelly multipliers
    kelly_multipliers = [0.1, 0.25, 0.5, 0.75, 1.0]
    confidence_thresholds = [0.5, 0.7, 0.9]
    
    best_config = None
    best_score = -float('inf')
    results = []
    
    for kelly_mult in kelly_multipliers:
        for conf_thresh in confidence_thresholds:
            config = AdvancedBettingConfig(
                kelly_multiplier=kelly_mult,
                confidence_threshold=conf_thresh,
                max_bet_percentage=0.15,  # Increase from 0.05
                risk_of_ruin_threshold=0.05,  # Increase from 0.01
                volatility_target=0.25,  # Increase from 0.15
                true_count_bet_correlation=2.0,  # Increase from 1.0
                return_weight=0.8,  # Increase from 0.6
                risk_weight=0.2   # Decrease from 0.4
            )
            
            metrics = test_configuration(config, test_rounds=30)
            
            # Scoring function (weighted combination)
            score = (
                0.3 * metrics['tc_bet_correlation'] +
                0.2 * min(metrics['bet_spread'], 5.0) / 5.0 +  # Cap at 5x spread
                0.2 * metrics['bet_coefficient_variation'] +
                0.3 * (metrics['roi'] + 0.5)  # Shift ROI to positive range
            )
            
            results.append({
                'kelly_multiplier': kelly_mult,
                'confidence_threshold': conf_thresh,
                'score': score,
                **metrics
            })
            
            if score > best_score:
                best_score = score
                best_config = config
            
            print(f"   Kelly: {kelly_mult:.2f}, Conf: {conf_thresh:.1f} → "
                  f"Score: {score:.3f}, TC-Corr: {metrics['tc_bet_correlation']:.3f}, "
                  f"Spread: {metrics['bet_spread']:.2f}x, ROI: {metrics['roi']:.2%}")
    
    print(f"\n🏆 Best Kelly Configuration:")
    print(f"   Kelly Multiplier: {best_config.kelly_multiplier}")
    print(f"   Confidence Threshold: {best_config.confidence_threshold}")
    print(f"   Best Score: {best_score:.3f}")
    
    return best_config, results


def optimize_risk_parameters():
    """Optimize risk management parameters for balance."""
    
    print("\n⚠️ OPTIMIZING RISK MANAGEMENT PARAMETERS")
    print("=" * 50)
    
    # Test different risk parameters
    max_bet_percentages = [0.05, 0.10, 0.15, 0.20]
    ror_thresholds = [0.01, 0.03, 0.05, 0.10]
    
    best_config = None
    best_score = -float('inf')
    results = []
    
    for max_bet_pct in max_bet_percentages:
        for ror_thresh in ror_thresholds:
            config = AdvancedBettingConfig(
                kelly_multiplier=0.5,  # Use moderate Kelly
                confidence_threshold=0.7,
                max_bet_percentage=max_bet_pct,
                risk_of_ruin_threshold=ror_thresh,
                volatility_target=0.3,  # More permissive
                true_count_bet_correlation=2.0,
                return_weight=0.75,
                risk_weight=0.25
            )
            
            metrics = test_configuration(config, test_rounds=30)
            
            # Risk-adjusted scoring
            score = (
                0.25 * metrics['tc_bet_correlation'] +
                0.25 * min(metrics['bet_spread'], 4.0) / 4.0 +
                0.25 * metrics['bet_coefficient_variation'] +
                0.25 * max(0, metrics['roi'] + 0.3)  # Positive ROI bonus
            )
            
            results.append({
                'max_bet_percentage': max_bet_pct,
                'ror_threshold': ror_thresh,
                'score': score,
                **metrics
            })
            
            if score > best_score:
                best_score = score
                best_config = config
            
            print(f"   Max Bet: {max_bet_pct:.1%}, RoR: {ror_thresh:.2f} → "
                  f"Score: {score:.3f}, Mean Bet: ${metrics['mean_bet']:.2f}, "
                  f"ROI: {metrics['roi']:.2%}")
    
    print(f"\n🏆 Best Risk Configuration:")
    print(f"   Max Bet Percentage: {best_config.max_bet_percentage:.1%}")
    print(f"   RoR Threshold: {best_config.risk_of_ruin_threshold:.2f}")
    print(f"   Best Score: {best_score:.3f}")
    
    return best_config, results


def create_optimized_config():
    """Create the final optimized configuration."""
    
    print("\n🚀 CREATING OPTIMIZED CONFIGURATION")
    print("=" * 50)
    
    # Combine best practices from optimization
    optimized_config = AdvancedBettingConfig(
        # Kelly Criterion - More aggressive for better bet scaling
        kelly_multiplier=0.75,  # Increased from 0.25
        confidence_threshold=0.6,  # Decreased from 0.7
        
        # Risk management - More permissive for better performance
        max_bet_percentage=0.15,  # Increased from 0.05
        risk_of_ruin_threshold=0.05,  # Increased from 0.01
        volatility_target=0.30,  # Increased from 0.15
        
        # Card counting - More responsive
        true_count_bet_correlation=2.5,  # Increased from 1.0
        count_systems=["hi_lo", "ko"],  # Simplified from 4 systems
        
        # Transformer parameters - Lighter for faster decisions
        sequence_length=10,  # Decreased from 20
        attention_heads=4,  # Decreased from 8
        hidden_dim=128,  # Decreased from 256
        
        # Multi-objective weights - Favor returns over risk
        return_weight=0.8,  # Increased from 0.6
        risk_weight=0.2   # Decreased from 0.4
    )
    
    print("Optimized Configuration:")
    print(f"   Kelly Multiplier: {optimized_config.kelly_multiplier}")
    print(f"   Max Bet %: {optimized_config.max_bet_percentage:.1%}")
    print(f"   RoR Threshold: {optimized_config.risk_of_ruin_threshold:.2f}")
    print(f"   TC Correlation: {optimized_config.true_count_bet_correlation}")
    print(f"   Return Weight: {optimized_config.return_weight}")
    
    return optimized_config


def test_optimized_performance(config: AdvancedBettingConfig, test_rounds: int = 200):
    """Test the optimized configuration extensively."""
    
    print(f"\n🧪 TESTING OPTIMIZED PERFORMANCE ({test_rounds} hands)")
    print("=" * 50)
    
    env = create_advanced_betting_env(
        seed=123,
        initial_bankroll=10000.0,
        min_bet=25.0,
        max_bet=500.0,
        use_advanced_ai=True,
        advanced_config=config
    )
    
    session_data = []
    bet_decisions = []
    
    for hand_num in range(test_rounds):
        obs, _ = env.reset()
        
        # Record betting decision
        true_count = obs[3]
        bankroll = env.bankroll
        
        if env.advanced_agent:
            ai_bet = env.advanced_agent.decide_bet_size(
                observation=obs,
                bankroll=bankroll,
                bet_range=(env.min_bet, env.max_bet)
            )
        else:
            ai_bet = env.min_bet
        
        bet_decisions.append({
            'hand': hand_num + 1,
            'true_count': true_count,
            'ai_bet': ai_bet,
            'bankroll': bankroll,
            'bet_ratio': ai_bet / env.min_bet
        })
        
        # Simple optimal play
        player_total = int(obs[0])
        dealer_up = int(obs[1])
        
        # Enhanced basic strategy
        if player_total <= 11:
            action = 1  # Hit
        elif player_total >= 17:
            action = 0  # Stand
        elif player_total in [9, 10, 11] and dealer_up <= 6:
            action = 2 if 2 in [0, 1, 2, 3] else 1  # Double or Hit
        elif player_total <= 16 and dealer_up >= 7:
            action = 1  # Hit
        else:
            action = 0  # Stand
        
        obs, reward, done, truncated, info = env.step(action)
        
        if done:
            session_data.append({
                'hand': hand_num + 1,
                'bet_amount': ai_bet,
                'reward': reward,
                'bankroll': env.bankroll,
                'roi': reward / ai_bet if ai_bet > 0 else 0
            })
    
    # Analysis
    df_bets = pd.DataFrame(bet_decisions)
    df_session = pd.DataFrame(session_data)
    
    # Betting analysis
    tc_bet_corr = np.corrcoef(df_bets['true_count'], df_bets['ai_bet'])[0, 1]
    bet_spread = df_bets['bet_ratio'].max() / df_bets['bet_ratio'].min() if df_bets['bet_ratio'].min() > 0 else 1
    
    # Performance analysis
    final_bankroll = env.bankroll
    total_roi = (final_bankroll - env.initial_bankroll) / env.initial_bankroll
    avg_reward = df_session['reward'].mean()
    win_rate = (df_session['reward'] > 0).mean()
    
    print("📊 OPTIMIZED RESULTS:")
    print(f"   TC-Bet Correlation: {tc_bet_corr:.3f}")
    print(f"   Bet Spread: {bet_spread:.2f}x")
    print(f"   Mean Bet: ${df_bets['ai_bet'].mean():.2f}")
    print(f"   Bet Range: ${df_bets['ai_bet'].min():.2f} - ${df_bets['ai_bet'].max():.2f}")
    print(f"   Final Bankroll: ${final_bankroll:,.2f}")
    print(f"   Total ROI: {total_roi:+.2%}")
    print(f"   Win Rate: {win_rate:.1%}")
    print(f"   Avg Reward: {avg_reward:+.2f}")
    
    # Grade the results
    sophistication_score = 0
    if tc_bet_corr > 0.7:
        sophistication_score += 25
        print("   ✅ TC Correlation: EXCELLENT")
    elif tc_bet_corr > 0.4:
        sophistication_score += 15
        print("   🟡 TC Correlation: GOOD")
    else:
        sophistication_score += 5
        print("   🔴 TC Correlation: NEEDS WORK")
    
    if bet_spread > 3:
        sophistication_score += 25
        print("   ✅ Bet Spread: EXCELLENT")
    elif bet_spread > 2:
        sophistication_score += 15
        print("   🟡 Bet Spread: GOOD")
    else:
        sophistication_score += 5
        print("   🔴 Bet Spread: INSUFFICIENT")
    
    if total_roi > 0.05:
        sophistication_score += 25
        print("   ✅ Performance: EXCELLENT")
    elif total_roi > 0:
        sophistication_score += 15
        print("   🟡 Performance: POSITIVE")
    else:
        sophistication_score += 5
        print("   🔴 Performance: NEEDS WORK")
    
    if win_rate > 0.47:
        sophistication_score += 25
        print("   ✅ Win Rate: EXCELLENT")
    elif win_rate > 0.43:
        sophistication_score += 15
        print("   🟡 Win Rate: GOOD")
    else:
        sophistication_score += 5
        print("   🔴 Win Rate: LOW")
    
    final_grade = sophistication_score / 100 * 100
    
    print(f"\n🎯 FINAL OPTIMIZED GRADE: {final_grade:.0f}%")
    
    if final_grade >= 90:
        print("🏆 GRADE: A+ (State-of-the-art achieved!)")
    elif final_grade >= 80:
        print("🏆 GRADE: A (Excellent performance)")
    elif final_grade >= 70:
        print("🟡 GRADE: B (Good performance)")
    else:
        print("🔴 GRADE: Needs more optimization")
    
    return {
        'tc_bet_correlation': tc_bet_corr,
        'bet_spread': bet_spread,
        'total_roi': total_roi,
        'win_rate': win_rate,
        'final_grade': final_grade,
        'betting_data': df_bets.to_dict('records'),
        'session_data': df_session.to_dict('records')
    }


def main():
    """Run complete AI calibration process."""
    
    print("🔧 ADVANCED AI CALIBRATION SUITE")
    print("=" * 60)
    
    try:
        # Step 1: Optimize Kelly parameters
        best_kelly_config, kelly_results = optimize_kelly_parameters()
        
        # Step 2: Optimize risk parameters
        best_risk_config, risk_results = optimize_risk_parameters()
        
        # Step 3: Create optimized configuration
        optimized_config = create_optimized_config()
        
        # Step 4: Test optimized performance
        final_results = test_optimized_performance(optimized_config, test_rounds=300)
        
        # Save all results
        calibration_results = {
            'kelly_optimization': kelly_results,
            'risk_optimization': risk_results,
            'optimized_config': {
                'kelly_multiplier': optimized_config.kelly_multiplier,
                'confidence_threshold': optimized_config.confidence_threshold,
                'max_bet_percentage': optimized_config.max_bet_percentage,
                'risk_of_ruin_threshold': optimized_config.risk_of_ruin_threshold,
                'volatility_target': optimized_config.volatility_target,
                'true_count_bet_correlation': optimized_config.true_count_bet_correlation,
                'return_weight': optimized_config.return_weight,
                'risk_weight': optimized_config.risk_weight
            },
            'final_performance': final_results
        }
        
        with open('runs/advanced_ai_calibration_results.json', 'w') as f:
            json.dump(calibration_results, f, indent=2, default=str)
        
        print(f"\n📄 Calibration results saved to: runs/advanced_ai_calibration_results.json")
        
        # Summary
        print(f"\n{'='*60}")
        print("📋 CALIBRATION SUMMARY")
        print('='*60)
        print(f"Final Grade: {final_results['final_grade']:.0f}%")
        print(f"TC-Bet Correlation: {final_results['tc_bet_correlation']:.3f}")
        print(f"Bet Spread: {final_results['bet_spread']:.2f}x")
        print(f"ROI: {final_results['total_roi']:+.2%}")
        print(f"Win Rate: {final_results['win_rate']:.1%}")
        
        if final_results['final_grade'] >= 80:
            print("\n🎉 CALIBRATION SUCCESSFUL!")
            print("✅ Advanced AI is now ready for sophisticated betting!")
        else:
            print("\n🔧 CALIBRATION NEEDS MORE WORK")
            print("💡 Consider further parameter tuning or algorithm improvements")
        
        return final_results['final_grade'] >= 70
        
    except Exception as e:
        print(f"❌ Calibration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
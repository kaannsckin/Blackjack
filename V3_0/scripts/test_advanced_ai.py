#!/usr/bin/env python3
"""
Test Advanced AI Betting System

Comprehensive validation of state-of-the-art betting behavior.
"""

import sys
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from advanced_betting_environment import create_advanced_betting_env
from advanced_betting_ai import AdvancedBettingConfig


def test_advanced_bet_sizing():
    """Test if advanced AI shows sophisticated bet sizing."""
    
    print("🧠 TESTING ADVANCED AI BET SIZING")
    print("=" * 50)
    
    # Create advanced environment
    env = create_advanced_betting_env(
        seed=42,
        initial_bankroll=10000.0,
        min_bet=10.0,
        max_bet=500.0,
        use_advanced_ai=True
    )
    
    bet_data = []
    
    # Test across different scenarios
    for test_round in range(200):
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
            'bankroll': bankroll,
            'ai_bet': ai_bet,
            'bet_ratio': ai_bet / env.min_bet
        })
    
    # Analyze betting patterns
    df = pd.DataFrame(bet_data)
    
    print(f"Bet Analysis (200 hands):")
    print(f"   Mean Bet: ${df['ai_bet'].mean():.2f}")
    print(f"   Bet Range: ${df['ai_bet'].min():.2f} - ${df['ai_bet'].max():.2f}")
    print(f"   Bet Std: ${df['ai_bet'].std():.2f}")
    print(f"   Max Ratio: {df['bet_ratio'].max():.2f}x")
    
    # True count correlation
    if len(df) > 10:
        correlation = np.corrcoef(df['true_count'], df['ai_bet'])[0, 1]
        print(f"   TC-Bet Correlation: {correlation:.3f}")
        
        if correlation > 0.7:
            print("   🟢 EXCELLENT: Strong TC-bet correlation")
        elif correlation > 0.4:
            print("   🟡 GOOD: Moderate TC-bet correlation")
        else:
            print("   🔴 POOR: Weak TC-bet correlation")
    
    # Bet spread analysis
    high_count_bets = df[df['true_count'] > 2]['ai_bet']
    low_count_bets = df[df['true_count'] < 0]['ai_bet']
    
    if len(high_count_bets) > 0 and len(low_count_bets) > 0:
        bet_spread = high_count_bets.mean() / low_count_bets.mean()
        print(f"   Bet Spread: {bet_spread:.2f}x")
        
        if bet_spread > 4:
            print("   🟢 EXCELLENT: Professional bet spread")
        elif bet_spread > 2:
            print("   🟡 GOOD: Reasonable bet spread")
        else:
            print("   🔴 POOR: Insufficient bet spread")
    
    return df


def test_risk_management():
    """Test advanced risk management capabilities."""
    
    print("\n⚠️ TESTING RISK MANAGEMENT")
    print("=" * 50)
    
    env = create_advanced_betting_env(
        seed=123,
        initial_bankroll=1000.0,  # Smaller bankroll to test risk management
        min_bet=10.0,
        max_bet=500.0,
        use_advanced_ai=True
    )
    
    risk_data = []
    
    # Simulate bankroll changes and test risk response
    bankroll_scenarios = [1000, 800, 600, 400, 200, 100]  # Decreasing bankroll
    
    for bankroll in bankroll_scenarios:
        env.bankroll = bankroll
        obs, _ = env.reset()
        
        if env.advanced_agent:
            # Test different true counts
            for tc in [-2, 0, 2, 4]:
                obs[3] = tc  # Set true count
                
                ai_bet = env.advanced_agent.decide_bet_size(
                    observation=obs,
                    bankroll=bankroll,
                    bet_range=(env.min_bet, env.max_bet)
                )
                
                # Get risk metrics
                risk_metrics = env.advanced_agent.risk_manager.assess_risk(
                    bankroll, ai_bet, tc * 0.005
                )
                
                risk_data.append({
                    'bankroll': bankroll,
                    'true_count': tc,
                    'ai_bet': ai_bet,
                    'bet_percentage': ai_bet / bankroll * 100,
                    'risk_of_ruin': risk_metrics['risk_of_ruin'],
                    'risk_score': risk_metrics['risk_score']
                })
    
    # Analyze risk management
    df = pd.DataFrame(risk_data)
    
    print("Risk Management Analysis:")
    print(f"   Max Bet %: {df['bet_percentage'].max():.2f}%")
    print(f"   Avg Risk Score: {df['risk_score'].mean():.3f}")
    print(f"   Max Risk of Ruin: {df['risk_of_ruin'].max():.3f}")
    
    # Check if bet size decreases with bankroll
    bankroll_bet_corr = np.corrcoef(df['bankroll'], df['ai_bet'])[0, 1]
    print(f"   Bankroll-Bet Correlation: {bankroll_bet_corr:.3f}")
    
    if bankroll_bet_corr > 0.7:
        print("   🟢 EXCELLENT: Strong bankroll awareness")
    elif bankroll_bet_corr > 0.3:
        print("   🟡 GOOD: Some bankroll consideration")
    else:
        print("   🔴 POOR: No bankroll awareness")
    
    # Check if high risk situations reduce betting
    high_risk = df[df['risk_score'] > 0.5]
    low_risk = df[df['risk_score'] < 0.3]
    
    if len(high_risk) > 0 and len(low_risk) > 0:
        risk_bet_reduction = high_risk['bet_percentage'].mean() / low_risk['bet_percentage'].mean()
        print(f"   Risk-Based Bet Reduction: {risk_bet_reduction:.2f}x")
        
        if risk_bet_reduction < 0.7:
            print("   🟢 EXCELLENT: Strong risk-based bet reduction")
        elif risk_bet_reduction < 0.9:
            print("   🟡 GOOD: Some risk-based adjustment")
        else:
            print("   🔴 POOR: No risk-based adjustment")
    
    return df


def test_kelly_criterion():
    """Test Kelly Criterion implementation."""
    
    print("\n📊 TESTING KELLY CRITERION")
    print("=" * 50)
    
    env = create_advanced_betting_env(
        seed=456,
        initial_bankroll=5000.0,
        min_bet=25.0,
        max_bet=250.0,
        use_advanced_ai=True
    )
    
    if not env.advanced_agent:
        print("   ❌ Advanced AI not available")
        return None
    
    kelly_data = []
    
    # Test Kelly calculation across advantage scenarios
    test_advantages = [-0.02, -0.01, 0.0, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05]
    
    for advantage in test_advantages:
        # Simulate advantage by setting true count
        true_count = advantage / 0.005  # Convert advantage to true count
        
        obs = np.array([15, 6, 0, true_count, 1.0, 0.0, 0.1, 0.2, advantage, 0.2])
        
        kelly_bet = env.advanced_agent.kelly_calculator.calculate_kelly_bet(
            advantage=advantage,
            bankroll=env.bankroll,
            current_bet_range=(env.min_bet, env.max_bet)
        )
        
        kelly_data.append({
            'advantage': advantage,
            'true_count': true_count,
            'kelly_bet': kelly_bet,
            'kelly_fraction': kelly_bet / env.bankroll,
            'bet_units': kelly_bet / env.min_bet
        })
    
    # Analyze Kelly implementation
    df = pd.DataFrame(kelly_data)
    
    print("Kelly Criterion Analysis:")
    print(f"   Negative EV betting: ${df[df['advantage'] < 0]['kelly_bet'].mean():.2f}")
    print(f"   Positive EV betting: ${df[df['advantage'] > 0]['kelly_bet'].mean():.2f}")
    
    # Check if betting increases with advantage
    advantage_bet_corr = np.corrcoef(df['advantage'], df['kelly_bet'])[0, 1]
    print(f"   Advantage-Bet Correlation: {advantage_bet_corr:.3f}")
    
    if advantage_bet_corr > 0.8:
        print("   🟢 EXCELLENT: Strong Kelly implementation")
    elif advantage_bet_corr > 0.5:
        print("   🟡 GOOD: Moderate Kelly implementation")
    else:
        print("   🔴 POOR: Weak Kelly implementation")
    
    # Check minimum betting on negative EV
    neg_ev_bets = df[df['advantage'] < 0]['kelly_bet']
    if len(neg_ev_bets) > 0 and all(bet <= env.min_bet * 1.1 for bet in neg_ev_bets):
        print("   🟢 EXCELLENT: Minimum betting on negative EV")
    else:
        print("   🔴 CONCERN: Over-betting on negative EV")
    
    return df


def test_session_performance():
    """Test full session performance with advanced AI."""
    
    print("\n🎯 TESTING SESSION PERFORMANCE")
    print("=" * 50)
    
    env = create_advanced_betting_env(
        seed=789,
        initial_bankroll=5000.0,
        min_bet=25.0,
        max_bet=250.0,
        use_advanced_ai=True
    )
    
    session_data = []
    hands_played = 0
    max_hands = 100
    
    print(f"Playing {max_hands} hands with advanced AI...")
    
    start_time = time.time()
    
    while hands_played < max_hands and env.bankroll >= env.min_bet:
        obs, _ = env.reset()
        
        # Simple playing strategy for testing
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
            session_data.append({
                'hand': hands_played + 1,
                'bankroll': env.bankroll,
                'bet_amount': env.current_bet,
                'reward': reward,
                'true_count': obs[3] if len(obs) > 3 else 0,
                'advantage': obs[8] if len(obs) > 8 else 0,
                'risk_score': obs[9] if len(obs) > 9 else 0
            })
            
            hands_played += 1
    
    elapsed_time = time.time() - start_time
    
    # Session analysis
    df = pd.DataFrame(session_data)
    
    final_bankroll = env.bankroll
    total_change = final_bankroll - env.initial_bankroll
    roi = total_change / env.initial_bankroll
    
    print(f"Session Results:")
    print(f"   Hands Played: {hands_played}")
    print(f"   Initial Bankroll: ${env.initial_bankroll:,.2f}")
    print(f"   Final Bankroll: ${final_bankroll:,.2f}")
    print(f"   Total Change: ${total_change:+,.2f}")
    print(f"   ROI: {roi:+.2%}")
    print(f"   Avg Bet: ${df['bet_amount'].mean():.2f}")
    print(f"   Max Bet: ${df['bet_amount'].max():.2f}")
    print(f"   Bet Std: ${df['bet_amount'].std():.2f}")
    print(f"   Session Time: {elapsed_time:.1f}s")
    
    # Advanced metrics
    if len(df) > 0:
        win_rate = (df['reward'] > 0).mean()
        sharpe = df['reward'].mean() / df['reward'].std() if df['reward'].std() > 0 else 0
        
        print(f"   Win Rate: {win_rate:.1%}")
        print(f"   Sharpe Ratio: {sharpe:.3f}")
        
        # Session assessment
        if roi > 0.05 and win_rate > 0.45:
            print("   🟢 EXCELLENT: Strong session performance")
        elif roi > 0 and win_rate > 0.40:
            print("   🟡 GOOD: Positive session performance")
        elif roi > -0.05:
            print("   🟡 ACCEPTABLE: Minor losses")
        else:
            print("   🔴 POOR: Significant losses")
    
    # Get session summary from environment
    session_summary = env.get_session_summary()
    
    return df, session_summary


def main():
    """Run comprehensive advanced AI testing."""
    
    print("🚀 ADVANCED AI BETTING SYSTEM TEST SUITE")
    print("=" * 60)
    
    try:
        # Test suite
        bet_sizing_results = test_advanced_bet_sizing()
        risk_mgmt_results = test_risk_management()
        kelly_results = test_kelly_criterion()
        session_results, session_summary = test_session_performance()
        
        # Overall assessment
        print(f"\n{'='*60}")
        print("🏆 OVERALL ADVANCED AI ASSESSMENT")
        print('='*60)
        
        assessment_points = 0
        max_points = 20
        
        # Bet sizing assessment
        if bet_sizing_results is not None:
            tc_corr = np.corrcoef(bet_sizing_results['true_count'], bet_sizing_results['ai_bet'])[0, 1]
            if tc_corr > 0.7:
                assessment_points += 5
                print("✅ Bet Sizing: EXCELLENT")
            elif tc_corr > 0.4:
                assessment_points += 3
                print("🟡 Bet Sizing: GOOD")
            else:
                assessment_points += 1
                print("🔴 Bet Sizing: NEEDS WORK")
        
        # Risk management assessment
        if risk_mgmt_results is not None:
            max_bet_pct = risk_mgmt_results['bet_percentage'].max()
            if max_bet_pct < 10:
                assessment_points += 5
                print("✅ Risk Management: EXCELLENT")
            elif max_bet_pct < 20:
                assessment_points += 3
                print("🟡 Risk Management: GOOD")
            else:
                assessment_points += 1
                print("🔴 Risk Management: RISKY")
        
        # Kelly implementation assessment
        if kelly_results is not None:
            adv_corr = np.corrcoef(kelly_results['advantage'], kelly_results['kelly_bet'])[0, 1]
            if adv_corr > 0.8:
                assessment_points += 5
                print("✅ Kelly Criterion: EXCELLENT")
            elif adv_corr > 0.5:
                assessment_points += 3
                print("🟡 Kelly Criterion: GOOD")
            else:
                assessment_points += 1
                print("🔴 Kelly Criterion: NEEDS WORK")
        
        # Session performance assessment
        if session_results is not None and len(session_results) > 0:
            session_roi = (session_results['bankroll'].iloc[-1] - session_results['bankroll'].iloc[0]) / session_results['bankroll'].iloc[0]
            if session_roi > 0.05:
                assessment_points += 5
                print("✅ Session Performance: EXCELLENT")
            elif session_roi > 0:
                assessment_points += 3
                print("🟡 Session Performance: GOOD")
            else:
                assessment_points += 1
                print("🔴 Session Performance: NEEDS WORK")
        
        # Final grade
        percentage = (assessment_points / max_points) * 100
        
        print(f"\n🎯 FINAL GRADE: {assessment_points}/{max_points} ({percentage:.0f}%)")
        
        if percentage >= 90:
            print("🏆 GRADE: A+ (State-of-the-art performance)")
        elif percentage >= 80:
            print("🏆 GRADE: A (Excellent performance)")
        elif percentage >= 70:
            print("🟡 GRADE: B (Good performance)")
        elif percentage >= 60:
            print("🟡 GRADE: C (Acceptable performance)")
        else:
            print("🔴 GRADE: D (Needs significant improvement)")
        
        # Save results
        results = {
            'bet_sizing': bet_sizing_results.to_dict() if bet_sizing_results is not None else None,
            'risk_management': risk_mgmt_results.to_dict() if risk_mgmt_results is not None else None,
            'kelly_criterion': kelly_results.to_dict() if kelly_results is not None else None,
            'session_performance': session_results.to_dict() if session_results is not None else None,
            'session_summary': session_summary,
            'final_grade': {
                'points': assessment_points,
                'max_points': max_points,
                'percentage': percentage
            }
        }
        
        with open('runs/advanced_ai_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: runs/advanced_ai_test_results.json")
        
        return percentage >= 70  # Success if grade >= B
        
    except Exception as e:
        print(f"❌ Advanced AI testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
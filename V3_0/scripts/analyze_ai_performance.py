#!/usr/bin/env python3
"""
AI Performance Analysis for F2.7

Detailed analysis of AI betting strategy performance issues.
"""

import sys
import json
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


def load_test_results(results_file: str) -> dict:
    """Load and parse test results."""
    with open(results_file, 'r') as f:
        return json.load(f)


def identify_ai_player(results: dict) -> tuple:
    """Identify the AI player in results."""
    
    players = results['players']
    
    for i, player in enumerate(players):
        # Look for AI betting statistics
        if 'ai_betting_stats' in player:
            return i, player
    
    return None, None


def analyze_ai_performance_issues(ai_player: dict) -> dict:
    """Analyze specific AI performance issues."""
    
    analysis = {
        "performance_issues": [],
        "risk_issues": [],
        "behavioral_issues": [],
        "recommendations": []
    }
    
    # Performance analysis
    roi = ai_player.get('roi', 0)
    win_rate = ai_player.get('win_rate', 0)
    avg_bet = ai_player.get('avg_bet', 0)
    
    if roi < -0.5:
        analysis["performance_issues"].append({
            "issue": "Severe negative ROI",
            "value": f"{roi:.2%}",
            "severity": "CRITICAL"
        })
    
    if win_rate < 0.35:
        analysis["performance_issues"].append({
            "issue": "Very low win rate",
            "value": f"{win_rate:.1%}",
            "severity": "HIGH"
        })
    
    if avg_bet < 15:  # Assuming min bet is 10
        analysis["behavioral_issues"].append({
            "issue": "Overly conservative betting",
            "value": f"${avg_bet:.2f}",
            "severity": "HIGH"
        })
    
    # AI-specific analysis
    if 'ai_betting_stats' in ai_player:
        ai_stats = ai_player['ai_betting_stats']
        
        fallback_ratio = ai_stats.get('fallback_decision_ratio', 0)
        if fallback_ratio > 0.1:
            analysis["behavioral_issues"].append({
                "issue": "High fallback usage",
                "value": f"{fallback_ratio:.1%}",
                "severity": "MEDIUM"
            })
        
        recent_avg_bet = ai_stats.get('recent_avg_bet', 0)
        if abs(recent_avg_bet - avg_bet) > avg_bet * 0.5:
            analysis["behavioral_issues"].append({
                "issue": "Inconsistent bet sizing",
                "value": f"Recent: ${recent_avg_bet:.2f} vs Avg: ${avg_bet:.2f}",
                "severity": "MEDIUM"
            })
    
    # Risk analysis
    max_drawdown = (ai_player.get('initial_bankroll', 0) - ai_player.get('min_bankroll', 0)) / ai_player.get('initial_bankroll', 1)
    if max_drawdown > 0.5:
        analysis["risk_issues"].append({
            "issue": "Excessive drawdown",
            "value": f"{max_drawdown:.1%}",
            "severity": "CRITICAL"
        })
    
    return analysis


def generate_training_recommendations(analysis: dict, ai_player: dict) -> list:
    """Generate specific training recommendations."""
    
    recommendations = []
    
    # Performance-based recommendations
    performance_issues = analysis["performance_issues"]
    if any(issue["severity"] == "CRITICAL" for issue in performance_issues):
        recommendations.extend([
            "🔄 Complete model retraining required",
            "🎯 Increase training steps to 5M+",
            "⚡ Try different algorithm (TD3/SAC)",
            "🎲 Increase exploration rate"
        ])
    
    # Behavioral recommendations
    behavioral_issues = analysis["behavioral_issues"]
    if any("conservative" in issue["issue"].lower() for issue in behavioral_issues):
        recommendations.extend([
            "📈 Adjust reward function to encourage larger bets",
            "🎯 Reduce risk aversion parameter",
            "💰 Implement bet sizing reward bonuses"
        ])
    
    # Environment recommendations
    recommendations.extend([
        "🔍 Debug observation space compatibility",
        "🎮 Validate training environment matches simulation",
        "📊 Add true count sensitivity analysis",
        "🧪 Test with simplified observation space"
    ])
    
    return recommendations


def calculate_expected_performance() -> dict:
    """Calculate what we should expect from a good AI strategy."""
    
    return {
        "min_roi": 0.05,  # 5% minimum ROI
        "target_roi": 0.15,  # 15% target ROI
        "min_win_rate": 0.42,  # 42% minimum win rate
        "target_win_rate": 0.48,  # 48% target win rate
        "max_drawdown": 0.15,  # 15% max acceptable drawdown
        "min_avg_bet": 15,  # Minimum average bet (above min bet)
        "max_avg_bet": 50,  # Maximum reasonable average bet
    }


def main():
    """Run AI performance analysis."""
    
    print("🤖 AI PERFORMANCE ANALYSIS - F2.7")
    print("="*50)
    
    # Load results
    results_file = "runs/production_model_test_1753895177.json"
    
    try:
        results = load_test_results(results_file)
        print(f"📄 Loaded: {results_file}")
        
        # Identify AI player
        ai_idx, ai_player = identify_ai_player(results)
        
        if ai_player is None:
            print("❌ No AI player found in results")
            return False
        
        print(f"🎯 Found AI player at index {ai_idx}")
        
        # Analyze performance
        analysis = analyze_ai_performance_issues(ai_player)
        
        # Print detailed analysis
        print_detailed_analysis(ai_player, analysis)
        
        # Generate recommendations
        training_recs = generate_training_recommendations(analysis, ai_player)
        print_training_recommendations(training_recs)
        
        # Compare to expectations
        compare_to_expectations(ai_player)
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False


def print_detailed_analysis(ai_player: dict, analysis: dict):
    """Print detailed AI analysis."""
    
    print(f"\n📊 AI PLAYER PERFORMANCE")
    print("-" * 40)
    
    # Basic metrics
    print(f"Initial Bankroll: ${ai_player.get('initial_bankroll', 0):,.0f}")
    print(f"Final Bankroll: ${ai_player.get('current_bankroll', 0):,.0f}")
    print(f"ROI: {ai_player.get('roi', 0):+.2%}")
    print(f"Win Rate: {ai_player.get('win_rate', 0):.1%}")
    print(f"Hands Played: {ai_player.get('hands_played', 0):,}")
    print(f"Average Bet: ${ai_player.get('avg_bet', 0):.2f}")
    
    # AI-specific metrics
    if 'ai_betting_stats' in ai_player:
        ai_stats = ai_player['ai_betting_stats']
        print(f"\n🤖 AI BETTING BEHAVIOR:")
        print(f"AI Decisions: {ai_stats.get('ai_decisions', 0):,}")
        print(f"AI Decision Ratio: {ai_stats.get('ai_decision_ratio', 0):.1%}")
        print(f"Fallback Decisions: {ai_stats.get('fallback_decisions', 0):,}")
        print(f"Recent Avg Bet: ${ai_stats.get('recent_avg_bet', 0):.2f}")
    
    # Issues analysis
    print(f"\n🚨 IDENTIFIED ISSUES:")
    
    all_issues = analysis["performance_issues"] + analysis["risk_issues"] + analysis["behavioral_issues"]
    if not all_issues:
        print("✅ No major issues detected")
    else:
        for issue in all_issues:
            severity_icon = {"CRITICAL": "🔴", "HIGH": "🟡", "MEDIUM": "🟠"}.get(issue["severity"], "⚪")
            print(f"{severity_icon} {issue['issue']}: {issue['value']} ({issue['severity']})")


def print_training_recommendations(recommendations: list):
    """Print training recommendations."""
    
    print(f"\n💡 TRAINING RECOMMENDATIONS")
    print("-" * 40)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")


def compare_to_expectations(ai_player: dict):
    """Compare AI performance to expected benchmarks."""
    
    print(f"\n📈 PERFORMANCE vs EXPECTATIONS")
    print("-" * 40)
    
    expected = calculate_expected_performance()
    actual = {
        "roi": ai_player.get('roi', 0),
        "win_rate": ai_player.get('win_rate', 0),
        "avg_bet": ai_player.get('avg_bet', 0),
    }
    
    # Calculate drawdown
    initial = ai_player.get('initial_bankroll', 1)
    min_bankroll = ai_player.get('min_bankroll', initial)
    actual["drawdown"] = (initial - min_bankroll) / initial
    
    # Compare metrics
    comparisons = [
        ("ROI", actual["roi"], expected["min_roi"], expected["target_roi"]),
        ("Win Rate", actual["win_rate"], expected["min_win_rate"], expected["target_win_rate"]),
        ("Avg Bet", actual["avg_bet"], expected["min_avg_bet"], expected["max_avg_bet"]),
        ("Drawdown", actual["drawdown"], 0, expected["max_drawdown"])
    ]
    
    for metric, actual_val, min_val, target_val in comparisons:
        if metric == "Drawdown":
            status = "✅" if actual_val <= target_val else "❌"
            print(f"{status} {metric}: {actual_val:.2%} (max: {target_val:.2%})")
        elif metric == "Avg Bet":
            status = "✅" if min_val <= actual_val <= target_val else "❌"
            print(f"{status} {metric}: ${actual_val:.2f} (range: ${min_val:.2f}-${target_val:.2f})")
        else:
            if actual_val >= target_val:
                status = "🟢 EXCELLENT"
            elif actual_val >= min_val:
                status = "🟡 ACCEPTABLE"
            else:
                status = "🔴 POOR"
            
            format_val = f"{actual_val:.2%}" if metric in ["ROI", "Win Rate"] else f"${actual_val:.2f}"
            format_min = f"{min_val:.2%}" if metric in ["ROI", "Win Rate"] else f"${min_val:.2f}"
            format_target = f"{target_val:.2%}" if metric in ["ROI", "Win Rate"] else f"${target_val:.2f}"
            
            print(f"{status} {metric}: {format_val} (min: {format_min}, target: {format_target})")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
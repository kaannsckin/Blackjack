#!/usr/bin/env python3
"""
Risk Analysis Script for F2.7

Runs comprehensive risk analysis on simulation results.
"""

import sys
import json
import glob
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from risk_analysis import analyze_simulation_results, RiskAnalyzer, RiskLimits


def find_latest_results_file() -> str:
    """Find the latest production model test results."""
    
    # Look for production model test files
    pattern = "runs/production_model_test_*.json"
    files = glob.glob(pattern)
    
    if files:
        # Get the most recent file
        latest_file = max(files, key=lambda x: Path(x).stat().st_mtime)
        return latest_file
    
    # Fallback to any recent test files
    pattern = "runs/*test*.json"
    files = glob.glob(pattern)
    
    if files:
        latest_file = max(files, key=lambda x: Path(x).stat().st_mtime)
        return latest_file
    
    raise FileNotFoundError("No simulation results files found")


def main():
    """Run comprehensive risk analysis."""
    
    print("🔍 F2.7 RISK & GÜVENLİK ANALİZİ")
    print("="*50)
    
    try:
        # Find latest results
        results_file = find_latest_results_file()
        print(f"📄 Analyzing: {results_file}")
        
        # Run analysis
        print("\n🔄 Running comprehensive risk analysis...")
        report = analyze_simulation_results(results_file)
        
        # Print summary
        print_risk_summary(report)
        
        # Check AI strategy specifically
        analyze_ai_strategy(report)
        
        # Generate recommendations
        print_final_recommendations(report)
        
        return True
        
    except Exception as e:
        print(f"❌ Risk analysis failed: {e}")
        return False


def print_risk_summary(report: dict):
    """Print risk analysis summary."""
    
    summary = report['summary']
    
    print(f"\n📊 RISK ANALYSIS SUMMARY")
    print("-" * 40)
    print(f"Strategies Analyzed: {summary['strategies_analyzed']}")
    print(f"Total Violations: {summary['total_violations']}")
    print(f"Overall Risk Level: {summary['overall_risk_level']}")
    print(f"Best Strategy: {summary['best_strategy']}")
    print(f"Worst Strategy: {summary['worst_strategy']}")
    
    # Strategy rankings
    print(f"\n🏆 STRATEGY RISK RANKINGS:")
    print("-" * 40)
    
    strategies = report['strategies']
    rankings = [(name, data['risk_score'], data['metrics']['roi']) 
                for name, data in strategies.items()]
    rankings.sort(key=lambda x: x[1])  # Sort by risk score
    
    for i, (name, risk_score, roi) in enumerate(rankings, 1):
        risk_level = "🟢 LOW" if risk_score < 25 else "🟡 MED" if risk_score < 50 else "🔴 HIGH"
        print(f"{i}. {name:<15} Risk: {risk_score:5.1f} | ROI: {roi:+7.2%} | {risk_level}")


def analyze_ai_strategy(report: dict):
    """Analyze AI strategy specifically."""
    
    print(f"\n🤖 AI STRATEGY DETAILED ANALYSIS")
    print("=" * 45)
    
    # Find AI strategy
    ai_strategy = None
    for name, data in report['strategies'].items():
        if 'ai' in name.lower() or 'AI' in name:
            ai_strategy = (name, data)
            break
    
    if not ai_strategy:
        print("❌ No AI strategy found in results")
        return
    
    name, data = ai_strategy
    metrics = data['metrics']
    violations = data['violations']
    
    print(f"Strategy: {name}")
    print(f"Recommendation: {data['recommendation']}")
    print(f"Risk Score: {data['risk_score']:.1f}/100")
    
    print(f"\n📈 PERFORMANCE METRICS:")
    print(f"   ROI: {metrics['roi']:+.2%}")
    print(f"   Win Rate: {metrics['win_rate']:.1%}")
    print(f"   Average Bet: ${metrics['avg_bet']:.2f}")
    print(f"   Total Return: ${metrics['total_return']:,.0f}")
    
    print(f"\n⚠️ RISK METRICS:")
    print(f"   Risk of Ruin: {metrics['risk_of_ruin']:.2%}")
    print(f"   Max Drawdown: {metrics['max_drawdown']:.2%}")
    print(f"   Volatility: {metrics['volatility']:.2%}")
    print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
    
    print(f"\n🔍 KELLY ANALYSIS:")
    print(f"   Kelly %: {metrics['kelly_percentage']:.2%}")
    print(f"   Kelly Violation: {'Yes' if metrics['kelly_violation'] else 'No'}")
    
    if violations:
        print(f"\n🚨 RISK VIOLATIONS ({len(violations)}):")
        for violation in violations:
            print(f"   • {violation}")
    else:
        print(f"\n✅ No risk violations detected")
    
    # AI-specific analysis
    print(f"\n🎯 AI-SPECIFIC INSIGHTS:")
    
    # Identify key issues
    issues = []
    if metrics['roi'] < -0.5:
        issues.append("Severe negative returns (-50%+)")
    if metrics['win_rate'] < 0.35:
        issues.append("Very low win rate (<35%)")
    if metrics['risk_of_ruin'] > 0.5:
        issues.append("Extremely high risk of ruin")
    if metrics['avg_bet'] < 15:  # Assuming min bet is 10
        issues.append("Overly conservative betting")
    
    if issues:
        print("   Issues Identified:")
        for issue in issues:
            print(f"   🔴 {issue}")
    
    # Possible causes
    print(f"\n🔬 POSSIBLE CAUSES:")
    print("   • Model not converged properly during training")
    print("   • Observation space mismatch between training/simulation")
    print("   • Overly conservative reward shaping")
    print("   • Insufficient exploration during training")
    print("   • Training environment vs simulation discrepancy")


def print_final_recommendations(report: dict):
    """Print final recommendations."""
    
    print(f"\n💡 FINAL RECOMMENDATIONS")
    print("=" * 50)
    
    summary = report['summary']
    recommendations = summary.get('recommendations', [])
    
    print("📋 IMMEDIATE ACTIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # Additional AI-specific recommendations
    print(f"\n🤖 AI MODEL SPECIFIC ACTIONS:")
    print("1. 🔄 Retrain model with adjusted hyperparameters")
    print("2. 🎯 Review reward function - may be too conservative")
    print("3. 🔍 Debug observation space compatibility")
    print("4. 📊 Increase training steps (try 5M+ steps)")
    print("5. ⚡ Try different algorithms (TD3/SAC instead of PPO)")
    print("6. 🎲 Increase exploration (higher epsilon)")
    
    print(f"\n🛡️ SAFETY MEASURES:")
    print("1. Implement real-time risk monitoring")
    print("2. Set maximum bet limits (10% of bankroll)")
    print("3. Auto-stop at 15% drawdown")
    print("4. Monitor consecutive losses (stop at 10)")
    print("5. Weekly risk assessment reviews")
    
    # Overall assessment
    risk_level = summary['overall_risk_level']
    if risk_level == "EXTREME":
        print(f"\n🚨 CRITICAL: System NOT ready for deployment")
    elif risk_level == "HIGH":
        print(f"\n⚠️ WARNING: Significant improvements needed")
    elif risk_level == "MODERATE":
        print(f"\n🟡 CAUTION: Address issues before proceeding")
    else:
        print(f"\n✅ GOOD: Risk levels acceptable")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
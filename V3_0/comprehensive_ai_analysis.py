#!/usr/bin/env python3
"""
C: Comprehensive AI Analysis - Complete Phase 2 Evaluation
Analyzes all AI approaches, identifies issues, and provides Phase 3 recommendations
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import json
from datetime import datetime
import os

class ComprehensiveAIAnalysis:
    """
    C: Complete analysis of all AI approaches developed in Phase 2
    """
    
    def __init__(self):
        self.results = {}
        self.analysis_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.output_dir = "runs/comprehensive_analysis"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def run_simple_ai_test(self) -> Dict:
        """Test Simple AI (our baseline)"""
        print("🔵 Testing Simple AI (Fixed Strategy)...")
        
        # Use basic strategy directly
        from betting_environment_fixed import create_fixed_betting_env
        
        env = create_fixed_betting_env(seed=42, initial_bankroll=10000.0, min_bet=25.0, max_bet=500.0)
        
        hands = 1000
        results = []
        
        for i in range(hands):
            obs, _ = env.reset()
            player_total, dealer_up, usable_ace = int(obs[0]), int(obs[1]), bool(obs[2])
            
            # Simple AI uses fixed betting
            bet = 50.0  # Fixed $50 bets
            env.set_bet_amount(bet)
            
            # Simple strategy (basic strategy logic)
            action_str = self._simple_strategy(player_total, dealer_up, usable_ace)
            action_map = {"hit": 0, "stand": 1, "double": 2, "split": 3}
            action = action_map.get(action_str, 1)
            
            obs, reward, done, truncated, info = env.step(action)
            
            if done or truncated:
                results.append({
                    "hand": i+1,
                    "bet": bet,
                    "reward": reward,
                    "roi": reward / bet
                })
        
        # Calculate metrics
        total_bet = sum(r["bet"] for r in results)
        total_reward = sum(r["reward"] for r in results)
        roi = (total_reward - total_bet) / total_bet if total_bet > 0 else 0
        win_rate = sum(1 for r in results if r["reward"] > 0) / len(results)
        
        return {
            "name": "Simple AI (Fixed)",
            "hands": hands,
            "total_bet": total_bet,
            "total_reward": total_reward,
            "roi": roi,
            "win_rate": win_rate,
            "final_bankroll": 10000 + total_reward,
            "avg_bet": total_bet / hands,
            "volatility": np.std([r["roi"] for r in results]),
            "max_consecutive_losses": self._calculate_max_consecutive_losses(results)
        }
    
    def run_adaptive_ai_test(self) -> Dict:
        """Test Adaptive AI (crisis management)"""
        print("🟡 Testing Adaptive AI (Crisis Management)...")
        
        from adaptive_simple_ai import create_adaptive_simple_ai
        from betting_environment_fixed import create_fixed_betting_env
        
        ai = create_adaptive_simple_ai(10000)
        env = create_fixed_betting_env(seed=42, initial_bankroll=10000.0, min_bet=25.0, max_bet=500.0)
        
        hands = 500  # Shorter test due to observed issues
        results = []
        
        for i in range(hands):
            obs, _ = env.reset()
            player_total, dealer_up, usable_ace = int(obs[0]), int(obs[1]), bool(obs[2])
            
            bet = ai.decide_bet_size(25.0, 500.0)
            env.set_bet_amount(bet)
            
            action_str = ai.decide_play_action(player_total, dealer_up, usable_ace)
            action_map = {"hit": 0, "stand": 1, "double": 2, "split": 3}
            action = action_map.get(action_str, 1)
            
            obs, reward, done, truncated, info = env.step(action)
            
            if done or truncated:
                ai.update_result(bet, reward)
                results.append({
                    "hand": i+1,
                    "bet": bet,
                    "reward": reward,
                    "roi": reward / bet if bet > 0 else 0
                })
                
                # Early termination if bankroll depleted
                metrics = ai.get_performance_metrics()
                if metrics.get("current_bankroll", 10000) <= 0:
                    print(f"   ⚠️  Bankroll depleted at hand {i+1}")
                    break
        
        metrics = ai.get_performance_metrics()
        
        return {
            "name": "Adaptive AI (Crisis)",
            "hands": len(results),
            "total_bet": sum(r["bet"] for r in results),
            "total_reward": sum(r["reward"] for r in results),
            "roi": metrics.get("total_roi", 0),
            "win_rate": metrics.get("win_rate", 0),
            "final_bankroll": metrics.get("current_bankroll", 0),
            "avg_bet": np.mean([r["bet"] for r in results]) if results else 0,
            "volatility": np.std([r["roi"] for r in results]) if results else 0,
            "max_consecutive_losses": self._calculate_max_consecutive_losses(results),
            "crisis_level": metrics.get("current_crisis_level", "unknown"),
            "max_drawdown": metrics.get("max_drawdown", 0)
        }
    
    def _calculate_max_consecutive_losses(self, results: List[Dict]) -> int:
        """Calculate maximum consecutive losses"""
        max_consecutive = 0
        current_consecutive = 0
        
        for result in results:
            if result["reward"] <= 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
                
        return max_consecutive
    
    def _simple_strategy(self, player_total: int, dealer_up: int, usable_ace: bool) -> str:
        """Simple basic strategy implementation"""
        if player_total == 21:
            return "stand"
        if player_total > 21:
            return "stand"
        
        # Soft hands
        if usable_ace:
            if player_total >= 19:
                return "stand"
            elif player_total == 18:
                return "stand" if dealer_up in [2, 7, 8] else "hit"
            else:
                return "hit"
        
        # Hard hands
        if player_total >= 17:
            return "stand"
        elif player_total <= 11:
            return "hit"
        elif player_total in [12, 13, 14, 15, 16]:
            return "stand" if dealer_up <= 6 else "hit"
        else:
            return "hit"
    
    def analyze_environment_issues(self) -> Dict:
        """Analyze potential environment issues"""
        print("🔍 Analyzing Environment Issues...")
        
        # Test basic environment behavior
        from betting_environment_fixed import create_fixed_betting_env
        
        env = create_fixed_betting_env(seed=42, initial_bankroll=10000.0, min_bet=25.0, max_bet=500.0)
        
        # Test 100 basic hands
        rewards = []
        bet_amounts = []
        
        for i in range(100):
            obs, _ = env.reset()
            
            # Fixed $50 bet, always stand
            env.set_bet_amount(50.0)
            obs, reward, done, truncated, info = env.step(1)  # Stand
            
            if done or truncated:
                rewards.append(reward)
                bet_amounts.append(50.0)
        
        # Calculate basic environment stats
        total_reward = sum(rewards)
        total_bet = sum(bet_amounts)
        env_roi = (total_reward - total_bet) / total_bet if total_bet > 0 else 0
        
        return {
            "environment_type": "Fixed Betting Environment",
            "test_hands": len(rewards),
            "env_roi": env_roi,
            "avg_reward": np.mean(rewards),
            "reward_std": np.std(rewards),
            "positive_rewards": sum(1 for r in rewards if r > 0),
            "negative_rewards": sum(1 for r in rewards if r < 0),
            "zero_rewards": sum(1 for r in rewards if r == 0),
            "reward_range": (min(rewards), max(rewards)),
            "suspected_issues": self._identify_environment_issues(rewards, env_roi)
        }
    
    def _identify_environment_issues(self, rewards: List[float], roi: float) -> List[str]:
        """Identify potential environment issues"""
        issues = []
        
        if roi < -0.3:  # More than 30% loss
            issues.append("Extremely negative ROI suggests environment bias")
        
        if np.std(rewards) > 100:  # High variance
            issues.append("Very high reward variance")
        
        negative_rate = sum(1 for r in rewards if r < 0) / len(rewards)
        if negative_rate > 0.8:  # More than 80% losses
            issues.append("Unusually high loss rate")
        
        if min(rewards) < -1000:  # Very large negative rewards
            issues.append("Extremely large negative rewards detected")
            
        return issues
    
    def run_comprehensive_analysis(self) -> Dict:
        """Run complete analysis of all AI approaches"""
        print("🚀 COMPREHENSIVE AI ANALYSIS - PHASE 2 EVALUATION")
        print("=" * 70)
        
        # Test all AI approaches
        simple_results = self.run_simple_ai_test()
        adaptive_results = self.run_adaptive_ai_test()
        
        # Analyze environment
        env_analysis = self.analyze_environment_issues()
        
        # Compile results
        analysis = {
            "analysis_date": self.analysis_date,
            "ai_comparisons": [simple_results, adaptive_results],
            "environment_analysis": env_analysis,
            "conclusions": self._generate_conclusions(simple_results, adaptive_results, env_analysis),
            "phase_3_recommendations": self._generate_phase_3_recommendations(simple_results, adaptive_results, env_analysis)
        }
        
        # Save analysis
        self._save_analysis(analysis)
        self._create_visualizations(analysis)
        
        return analysis
    
    def _generate_conclusions(self, simple: Dict, adaptive: Dict, env: Dict) -> Dict:
        """Generate analysis conclusions"""
        conclusions = {
            "best_performer": None,
            "key_findings": [],
            "major_issues": [],
            "successful_features": []
        }
        
        # Determine best performer
        if simple["roi"] > adaptive["roi"]:
            conclusions["best_performer"] = simple["name"]
        else:
            conclusions["best_performer"] = adaptive["name"]
        
        # Key findings
        conclusions["key_findings"] = [
            f"Simple AI achieved {simple['roi']:.1%} ROI vs Adaptive AI {adaptive['roi']:.1%} ROI",
            f"Environment shows {env['env_roi']:.1%} baseline ROI with stand-only strategy",
            f"Maximum consecutive losses: Simple {simple['max_consecutive_losses']}, Adaptive {adaptive['max_consecutive_losses']}",
            f"Win rates: Simple {simple['win_rate']:.1%}, Adaptive {adaptive['win_rate']:.1%}"
        ]
        
        # Major issues
        if env["env_roi"] < -0.1:
            conclusions["major_issues"].append("Environment appears to have significant negative bias")
        
        if adaptive["roi"] < -0.5:
            conclusions["major_issues"].append("Adaptive AI shows severe performance degradation")
        
        if env["suspected_issues"]:
            conclusions["major_issues"].extend(env["suspected_issues"])
        
        # Successful features
        if simple["roi"] > -0.1:
            conclusions["successful_features"].append("Simple fixed betting strategy shows stability")
        
        if adaptive["crisis_level"] != "unknown":
            conclusions["successful_features"].append("Crisis management system functioning")
        
        return conclusions
    
    def _generate_phase_3_recommendations(self, simple: Dict, adaptive: Dict, env: Dict) -> Dict:
        """Generate Phase 3 recommendations"""
        recommendations = {
            "priority_actions": [],
            "environment_fixes": [],
            "ai_improvements": [],
            "phase_3_approach": ""
        }
        
        # Priority actions
        if env["env_roi"] < -0.2:
            recommendations["priority_actions"].append("CRITICAL: Fix environment bias before Phase 3")
        
        recommendations["priority_actions"].append("Validate F2.5 motor integration with controlled tests")
        recommendations["priority_actions"].append("Complete F2.8 policy visualization analysis")
        
        # Environment fixes
        if env["suspected_issues"]:
            recommendations["environment_fixes"] = [
                "Review betting environment reward calculation",
                "Validate blackjack game logic and payouts",
                "Test with multiple random seeds",
                "Compare against theoretical blackjack house edge (~0.5%)"
            ]
        
        # AI improvements
        if adaptive["roi"] < simple["roi"]:
            recommendations["ai_improvements"] = [
                "Simplify adaptive betting strategy",
                "Reduce initial bet sizes",
                "Implement more conservative crisis thresholds",
                "Add betting validation and limits"
            ]
        
        # Phase 3 approach
        if simple["roi"] > adaptive["roi"]:
            recommendations["phase_3_approach"] = (
                "Proceed with Simple AI as baseline for Phase 3 multi-player development. "
                "Focus on environment validation and multi-player dynamics rather than "
                "complex betting strategies until core issues are resolved."
            )
        else:
            recommendations["phase_3_approach"] = (
                "Use best-performing adaptive elements for Phase 3 while addressing "
                "identified environment and performance issues."
            )
        
        return recommendations
    
    def _save_analysis(self, analysis: Dict) -> str:
        """Save analysis to JSON and markdown"""
        # JSON export
        json_path = os.path.join(self.output_dir, f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(json_path, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Markdown report
        md_path = os.path.join(self.output_dir, f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(md_path, 'w') as f:
            f.write("# Phase 2 Comprehensive AI Analysis Report\n\n")
            f.write(f"**Generated:** {analysis['analysis_date']}\n\n")
            
            f.write("## AI Performance Comparison\n\n")
            f.write("| AI Type | ROI | Win Rate | Hands | Final Bankroll | Avg Bet |\n")
            f.write("|---------|-----|----------|-------|----------------|----------|\n")
            
            for ai in analysis["ai_comparisons"]:
                f.write(f"| {ai['name']} | {ai['roi']:.1%} | {ai['win_rate']:.1%} | {ai['hands']} | ${ai['final_bankroll']:,.0f} | ${ai['avg_bet']:.0f} |\n")
            
            f.write("\n## Environment Analysis\n\n")
            env = analysis["environment_analysis"]
            f.write(f"- **Environment ROI:** {env['env_roi']:.1%}\n")
            f.write(f"- **Test Hands:** {env['test_hands']}\n")
            f.write(f"- **Positive/Negative/Zero Rewards:** {env['positive_rewards']}/{env['negative_rewards']}/{env['zero_rewards']}\n")
            
            if env["suspected_issues"]:
                f.write("\n### Suspected Issues:\n")
                for issue in env["suspected_issues"]:
                    f.write(f"- {issue}\n")
            
            f.write("\n## Key Conclusions\n\n")
            conclusions = analysis["conclusions"]
            f.write(f"**Best Performer:** {conclusions['best_performer']}\n\n")
            
            f.write("### Key Findings:\n")
            for finding in conclusions["key_findings"]:
                f.write(f"- {finding}\n")
            
            if conclusions["major_issues"]:
                f.write("\n### Major Issues:\n")
                for issue in conclusions["major_issues"]:
                    f.write(f"- {issue}\n")
            
            f.write("\n## Phase 3 Recommendations\n\n")
            rec = analysis["phase_3_recommendations"]
            
            f.write("### Priority Actions:\n")
            for action in rec["priority_actions"]:
                f.write(f"- {action}\n")
            
            f.write(f"\n### Recommended Approach:\n{rec['phase_3_approach']}\n")
        
        print(f"📄 Analysis saved to: {md_path}")
        return md_path
    
    def _create_visualizations(self, analysis: Dict) -> None:
        """Create analysis visualizations"""
        print("📊 Creating analysis visualizations...")
        
        # AI Comparison Chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Phase 2 AI Comprehensive Analysis', fontsize=16, fontweight='bold')
        
        # ROI Comparison
        ai_data = analysis["ai_comparisons"]
        names = [ai["name"] for ai in ai_data]
        rois = [ai["roi"] * 100 for ai in ai_data]  # Convert to percentage
        
        bars1 = ax1.bar(names, rois, color=['blue', 'orange'])
        ax1.set_title('ROI Comparison (%)')
        ax1.set_ylabel('ROI (%)')
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        
        # Add value labels on bars
        for bar, roi in zip(bars1, rois):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{roi:.1f}%', ha='center', va='bottom' if height >= 0 else 'top')
        
        # Win Rate Comparison
        win_rates = [ai["win_rate"] * 100 for ai in ai_data]
        bars2 = ax2.bar(names, win_rates, color=['green', 'red'])
        ax2.set_title('Win Rate Comparison (%)')
        ax2.set_ylabel('Win Rate (%)')
        
        for bar, wr in zip(bars2, win_rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{wr:.1f}%', ha='center', va='bottom')
        
        # Bankroll Comparison
        bankrolls = [ai["final_bankroll"] for ai in ai_data]
        bars3 = ax3.bar(names, bankrolls, color=['purple', 'brown'])
        ax3.set_title('Final Bankroll ($)')
        ax3.set_ylabel('Bankroll ($)')
        ax3.axhline(y=10000, color='green', linestyle='--', alpha=0.5, label='Initial')
        ax3.legend()
        
        # Risk Metrics
        volatilities = [ai["volatility"] for ai in ai_data]
        max_losses = [ai["max_consecutive_losses"] for ai in ai_data]
        
        x = np.arange(len(names))
        width = 0.35
        
        ax4.bar(x - width/2, volatilities, width, label='Volatility', alpha=0.8)
        ax4.bar(x + width/2, max_losses, width, label='Max Consecutive Losses', alpha=0.8)
        ax4.set_title('Risk Metrics')
        ax4.set_xticks(x)
        ax4.set_xticklabels(names)
        ax4.legend()
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.output_dir, f"ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Visualization saved to: {plot_path}")


def run_comprehensive_analysis():
    """Main function to run comprehensive analysis"""
    analyzer = ComprehensiveAIAnalysis()
    results = analyzer.run_comprehensive_analysis()
    
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE ANALYSIS COMPLETE")
    print("="*70)
    
    # Print summary
    print(f"\n🏆 Best Performer: {results['conclusions']['best_performer']}")
    
    print(f"\n📈 Key Findings:")
    for finding in results['conclusions']['key_findings']:
        print(f"   • {finding}")
    
    if results['conclusions']['major_issues']:
        print(f"\n⚠️  Major Issues:")
        for issue in results['conclusions']['major_issues']:
            print(f"   • {issue}")
    
    print(f"\n🚀 Phase 3 Approach:")
    print(f"   {results['phase_3_recommendations']['phase_3_approach']}")
    
    return results


if __name__ == "__main__":
    run_comprehensive_analysis() 
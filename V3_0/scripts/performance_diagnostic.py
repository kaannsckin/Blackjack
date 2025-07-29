#!/usr/bin/env python3
"""
Performance Diagnostic Script for Phase 1 AI Agent
================================================

Comprehensive analysis of AI performance vs Basic Strategy to identify
specific weaknesses and improvement opportunities.
"""

from __future__ import annotations

import argparse
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from stable_baselines3 import DQN
from rl_environment import BlackjackEnv
from utils.basic_strategy import BasicStrategy
from utils.performance_metrics import PerformanceAnalyzer

@dataclass
class PerformanceResults:
    """Container for performance analysis results."""
    ai_returns: List[float]
    basic_returns: List[float]
    ai_actions: List[List[int]]
    basic_actions: List[List[int]]
    situations: List[Tuple[int, int, bool, float]]  # player_total, dealer_up, usable_ace, true_count
    ai_ev: float
    basic_ev: float
    agreement_rate: float
    win_rates: Dict[str, float]
    action_distributions: Dict[str, Dict[int, int]]

class PerformanceDiagnostic:
    """Comprehensive performance diagnostic for AI agent."""
    
    def __init__(self, model_path: str, num_episodes: int = 10000):
        """Initialize diagnostic with model and test parameters."""
        self.model_path = Path(model_path)
        self.num_episodes = num_episodes
        
        # Load components
        self.env = BlackjackEnv(seed=42)
        self.basic_strategy = BasicStrategy()
        self.analyzer = PerformanceAnalyzer()
        
        # Load AI model
        try:
            self.ai_model = DQN.load(self.model_path)
            print(f"✅ Loaded AI model from {self.model_path}")
        except Exception as e:
            raise RuntimeError(f"❌ Failed to load model: {e}")
    
    def run_comprehensive_evaluation(self) -> PerformanceResults:
        """Run comprehensive evaluation comparing AI vs Basic Strategy."""
        print(f"🚀 Starting comprehensive evaluation with {self.num_episodes} episodes...")
        
        ai_returns = []
        basic_returns = []
        ai_actions = []
        basic_actions = []
        situations = []
        
        np_rng = np.random.default_rng(42)
        
        for episode in range(self.num_episodes):
            if episode % 1000 == 0:
                print(f"Progress: {episode}/{self.num_episodes} episodes")
            
            # Run single episode comparison
            ai_ret, basic_ret, ai_acts, basic_acts, situation = self._run_episode_comparison(np_rng)
            
            ai_returns.append(ai_ret)
            basic_returns.append(basic_ret)
            ai_actions.append(ai_acts)
            basic_actions.append(basic_acts)
            situations.append(situation)
        
        # Calculate metrics
        ai_ev = np.mean(ai_returns)
        basic_ev = np.mean(basic_returns)
        
        # Calculate agreement rate
        agreements = []
        for ai_acts, basic_acts in zip(ai_actions, basic_actions):
            if len(ai_acts) > 0 and len(basic_acts) > 0:
                # Compare first action of each episode
                agreements.append(ai_acts[0] == basic_acts[0])
        agreement_rate = np.mean(agreements) * 100
        
        # Calculate win rates
        ai_wins = sum(1 for r in ai_returns if r > 0)
        ai_pushes = sum(1 for r in ai_returns if r == 0)
        ai_losses = sum(1 for r in ai_returns if r < 0)
        
        basic_wins = sum(1 for r in basic_returns if r > 0)
        basic_pushes = sum(1 for r in basic_returns if r == 0)
        basic_losses = sum(1 for r in basic_returns if r < 0)
        
        win_rates = {
            "ai_win_rate": ai_wins / self.num_episodes * 100,
            "ai_push_rate": ai_pushes / self.num_episodes * 100,
            "ai_loss_rate": ai_losses / self.num_episodes * 100,
            "basic_win_rate": basic_wins / self.num_episodes * 100,
            "basic_push_rate": basic_pushes / self.num_episodes * 100,
            "basic_loss_rate": basic_losses / self.num_episodes * 100,
        }
        
        # Calculate action distributions
        action_distributions = self._calculate_action_distributions(ai_actions, basic_actions)
        
        return PerformanceResults(
            ai_returns=ai_returns,
            basic_returns=basic_returns,
            ai_actions=ai_actions,
            basic_actions=basic_actions,
            situations=situations,
            ai_ev=ai_ev,
            basic_ev=basic_ev,
            agreement_rate=agreement_rate,
            win_rates=win_rates,
            action_distributions=action_distributions
        )
    
    def _run_episode_comparison(self, rng: np.random.Generator) -> Tuple[float, float, List[int], List[int], Tuple]:
        """Run single episode with both AI and Basic Strategy."""
        episode_seed = int(rng.integers(1_000_000))
        
        # AI episode
        obs, _ = self.env.reset(seed=episode_seed)
        initial_situation = tuple(obs)
        done = truncated = False
        ai_reward = 0.0
        ai_actions = []
        
        while not (done or truncated):
            action, _ = self.ai_model.predict(obs, deterministic=True)
            ai_actions.append(int(action))
            obs, reward, done, truncated, _ = self.env.step(action)
            ai_reward += reward
        
        # Basic Strategy episode (same seed)
        obs, _ = self.env.reset(seed=episode_seed)
        done = truncated = False
        basic_reward = 0.0
        basic_actions = []
        
        while not (done or truncated):
            player_total, dealer_up, usable_ace, true_count = obs
            action = self.basic_strategy.get_action(int(player_total), int(dealer_up), bool(usable_ace))
            basic_actions.append(action)
            obs, reward, done, truncated, _ = self.env.step(action)
            basic_reward += reward
        
        return ai_reward, basic_reward, ai_actions, basic_actions, initial_situation
    
    def _calculate_action_distributions(self, ai_actions: List[List[int]], basic_actions: List[List[int]]) -> Dict[str, Dict[int, int]]:
        """Calculate action distribution statistics."""
        ai_first_actions = [actions[0] for actions in ai_actions if len(actions) > 0]
        basic_first_actions = [actions[0] for actions in basic_actions if len(actions) > 0]
        
        ai_dist = {}
        basic_dist = {}
        
        for action in range(4):  # 0: stand, 1: hit, 2: double, 3: split
            ai_dist[action] = ai_first_actions.count(action)
            basic_dist[action] = basic_first_actions.count(action)
        
        return {"ai": ai_dist, "basic": basic_dist}
    
    def analyze_weaknesses(self, results: PerformanceResults) -> Dict[str, Any]:
        """Analyze specific weaknesses in AI performance."""
        print("\n🔍 Analyzing AI weaknesses...")
        
        weaknesses = {}
        
        # 1. Low-level action analysis
        action_names = {0: "Stand", 1: "Hit", 2: "Double", 3: "Split"}
        
        # 2. Situation-specific analysis
        situations_df = pd.DataFrame(results.situations, columns=['player_total', 'dealer_up', 'usable_ace', 'true_count'])
        
        # 3. Performance by dealer upcard
        dealer_performance = {}
        for dealer_up in range(1, 12):  # A, 2-10, face cards
            mask = [sit[1] == dealer_up for sit in results.situations]
            if any(mask):
                ai_avg = np.mean([ret for ret, m in zip(results.ai_returns, mask) if m])
                basic_avg = np.mean([ret for ret, m in zip(results.basic_returns, mask) if m])
                dealer_performance[dealer_up] = {
                    'ai_ev': ai_avg,
                    'basic_ev': basic_avg,
                    'difference': ai_avg - basic_avg
                }
        
        # 4. Performance by player total
        player_performance = {}
        for player_total in range(4, 22):
            mask = [sit[0] == player_total for sit in results.situations]
            if any(mask):
                ai_avg = np.mean([ret for ret, m in zip(results.ai_returns, mask) if m])
                basic_avg = np.mean([ret for ret, m in zip(results.basic_returns, mask) if m])
                player_performance[player_total] = {
                    'ai_ev': ai_avg,
                    'basic_ev': basic_avg,
                    'difference': ai_avg - basic_avg
                }
        
        weaknesses.update({
            'action_distributions': results.action_distributions,
            'dealer_performance': dealer_performance,
            'player_performance': player_performance,
            'overall_performance': {
                'ai_ev': results.ai_ev,
                'basic_ev': results.basic_ev,
                'ev_gap': results.basic_ev - results.ai_ev,
                'agreement_rate': results.agreement_rate
            }
        })
        
        return weaknesses
    
    def generate_improvement_recommendations(self, weaknesses: Dict[str, Any]) -> List[str]:
        """Generate specific improvement recommendations."""
        recommendations = []
        
        ev_gap = weaknesses['overall_performance']['ev_gap']
        agreement_rate = weaknesses['overall_performance']['agreement_rate']
        
        # Critical issues
        if ev_gap > 0.05:
            recommendations.append("🚨 CRITICAL: Large EV gap (>5%) - reward function needs redesign")
        
        if agreement_rate < 50:
            recommendations.append("🚨 CRITICAL: Very low agreement rate (<50%) - model is not learning basic strategy")
        
        # Specific action issues
        ai_dist = weaknesses['action_distributions']['ai']
        basic_dist = weaknesses['action_distributions']['basic']
        
        for action in range(4):
            ai_pct = ai_dist[action] / sum(ai_dist.values()) * 100
            basic_pct = basic_dist[action] / sum(basic_dist.values()) * 100
            diff = abs(ai_pct - basic_pct)
            
            if diff > 20:
                action_names = {0: "Stand", 1: "Hit", 2: "Double", 3: "Split"}
                recommendations.append(f"⚠️ ACTION: {action_names[action]} usage differs by {diff:.1f}% from basic strategy")
        
        # Dealer-specific issues
        worst_dealer_performance = min(
            weaknesses['dealer_performance'].values(),
            key=lambda x: x['difference']
        )
        if worst_dealer_performance['difference'] < -0.1:
            recommendations.append("⚠️ DEALER: Poor performance against certain dealer upcards")
        
        # Training recommendations
        if ev_gap > 0.03:
            recommendations.append("💡 TRAINING: Increase training episodes and improve reward shaping")
        
        if agreement_rate < 70:
            recommendations.append("💡 TRAINING: Add basic strategy guidance to reward function")
        
        recommendations.append("💡 ARCHITECTURE: Consider deeper network or better feature engineering")
        recommendations.append("💡 EXPLORATION: Tune exploration parameters for better coverage")
        
        return recommendations
    
    def save_results(self, results: PerformanceResults, weaknesses: Dict[str, Any], 
                    recommendations: List[str], output_dir: Path):
        """Save analysis results to files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        results_data = {
            'ai_ev': results.ai_ev,
            'basic_ev': results.basic_ev,
            'agreement_rate': results.agreement_rate,
            'win_rates': results.win_rates,
            'action_distributions': results.action_distributions,
            'num_episodes': self.num_episodes
        }
        
        with open(output_dir / "performance_results.json", "w") as f:
            json.dump(results_data, f, indent=2)
        
        # Save weaknesses analysis
        with open(output_dir / "weakness_analysis.json", "w") as f:
            json.dump(weaknesses, f, indent=2)
        
        # Save recommendations
        with open(output_dir / "improvement_recommendations.txt", "w") as f:
            f.write("AI PERFORMANCE IMPROVEMENT RECOMMENDATIONS\n")
            f.write("=" * 50 + "\n\n")
            for rec in recommendations:
                f.write(f"{rec}\n")
        
        print(f"📊 Results saved to {output_dir}")
    
    def print_summary(self, results: PerformanceResults, recommendations: List[str]):
        """Print comprehensive summary."""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   AI Expected Value:     {results.ai_ev:+.4f}")
        print(f"   Basic Strategy EV:     {results.basic_ev:+.4f}")
        print(f"   Performance Gap:       {results.basic_ev - results.ai_ev:+.4f}")
        print(f"   Agreement Rate:        {results.agreement_rate:.1f}%")
        
        print(f"\n🏆 WIN RATES:")
        print(f"   AI Win Rate:          {results.win_rates['ai_win_rate']:.1f}%")
        print(f"   Basic Strategy:       {results.win_rates['basic_win_rate']:.1f}%")
        
        print(f"\n🎲 ACTION DISTRIBUTIONS:")
        action_names = {0: "Stand", 1: "Hit", 2: "Double", 3: "Split"}
        for action in range(4):
            ai_pct = results.action_distributions['ai'][action] / sum(results.action_distributions['ai'].values()) * 100
            basic_pct = results.action_distributions['basic'][action] / sum(results.action_distributions['basic'].values()) * 100
            print(f"   {action_names[action]:8s}: AI={ai_pct:5.1f}% | Basic={basic_pct:5.1f}% | Diff={ai_pct-basic_pct:+5.1f}%")
        
        print(f"\n💡 KEY RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"   {i}. {rec}")
        
        print("=" * 60)

def main():
    """Main diagnostic function."""
    parser = argparse.ArgumentParser(description="AI Performance Diagnostic")
    parser.add_argument("--model-path", type=str, required=True, help="Path to trained model")
    parser.add_argument("--episodes", type=int, default=10000, help="Number of test episodes")
    parser.add_argument("--output-dir", type=str, default="diagnostic_output", help="Output directory")
    
    args = parser.parse_args()
    
    # Run diagnostic
    diagnostic = PerformanceDiagnostic(args.model_path, args.episodes)
    results = diagnostic.run_comprehensive_evaluation()
    weaknesses = diagnostic.analyze_weaknesses(results)
    recommendations = diagnostic.generate_improvement_recommendations(weaknesses)
    
    # Save and display results
    diagnostic.save_results(results, weaknesses, recommendations, Path(args.output_dir))
    diagnostic.print_summary(results, recommendations)

if __name__ == "__main__":
    main() 
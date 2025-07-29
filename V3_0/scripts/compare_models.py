#!/usr/bin/env python3
"""
Model Performance Comparison Script
==================================

Compare baseline vs enhanced model performance to validate improvements.
"""

from __future__ import annotations

import argparse
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from stable_baselines3 import DQN
from rl_environment import BlackjackEnv
from utils.basic_strategy import BasicStrategy


class ModelComparator:
    """Compare performance between different models."""
    
    def __init__(self, num_episodes: int = 5000):
        self.num_episodes = num_episodes
        self.env = BlackjackEnv(seed=42)
        self.basic_strategy = BasicStrategy()
    
    def evaluate_model(self, model_path: str, model_name: str) -> Dict:
        """Evaluate a single model."""
        print(f"🔍 Evaluating {model_name}...")
        
        try:
            model = DQN.load(model_path)
        except Exception as e:
            print(f"❌ Failed to load {model_name}: {e}")
            return None
        
        returns = []
        actions_taken = {"stand": 0, "hit": 0, "double": 0, "split": 0}
        agreement_count = 0
        
        np_rng = np.random.default_rng(42)
        
        for episode in range(self.num_episodes):
            if episode % 1000 == 0:
                print(f"  Progress: {episode}/{self.num_episodes}")
            
            episode_seed = int(np_rng.integers(1_000_000))
            obs, _ = self.env.reset(seed=episode_seed)
            
            episode_return = 0.0
            first_action_taken = False
            
            done = truncated = False
            while not (done or truncated):
                # AI action
                action, _ = model.predict(obs, deterministic=True)
                action = int(action)
                
                # Check agreement with basic strategy on first action
                if not first_action_taken:
                    player_total, dealer_up, usable_ace, _ = obs
                    optimal_action = self.basic_strategy.get_action(
                        int(player_total), int(dealer_up), bool(usable_ace)
                    )
                    
                    if action == optimal_action:
                        agreement_count += 1
                    
                    # Count action distribution
                    action_names = ["stand", "hit", "double", "split"]
                    actions_taken[action_names[action]] += 1
                    first_action_taken = True
                
                obs, reward, done, truncated, _ = self.env.step(action)
                episode_return += reward
            
            returns.append(episode_return)
        
        # Calculate metrics
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        win_rate = sum(1 for r in returns if r > 0) / len(returns) * 100
        push_rate = sum(1 for r in returns if r == 0) / len(returns) * 100
        loss_rate = sum(1 for r in returns if r < 0) / len(returns) * 100
        agreement_rate = agreement_count / self.num_episodes * 100
        
        return {
            "model_name": model_name,
            "mean_return": mean_return,
            "std_return": std_return,
            "win_rate": win_rate,
            "push_rate": push_rate,
            "loss_rate": loss_rate,
            "agreement_rate": agreement_rate,
            "actions_taken": actions_taken,
            "total_episodes": self.num_episodes
        }
    
    def compare_models(self, model_configs: List[Tuple[str, str]]) -> Dict:
        """Compare multiple models."""
        results = {}
        
        for model_path, model_name in model_configs:
            if Path(model_path).exists():
                result = self.evaluate_model(model_path, model_name)
                if result:
                    results[model_name] = result
            else:
                print(f"⚠️ Model not found: {model_path}")
        
        return results
    
    def print_comparison(self, results: Dict):
        """Print detailed comparison results."""
        print("\n" + "=" * 80)
        print("📊 MODEL PERFORMANCE COMPARISON")
        print("=" * 80)
        
        if not results:
            print("❌ No valid results to compare")
            return
        
        # Create comparison table
        metrics = ["mean_return", "win_rate", "agreement_rate"]
        
        print(f"\n🎯 PERFORMANCE METRICS:")
        print(f"{'Model':<20} {'Expected Value':<15} {'Win Rate %':<12} {'Agreement %':<12}")
        print("-" * 60)
        
        for model_name, data in results.items():
            print(f"{model_name:<20} {data['mean_return']:>+.4f}        "
                  f"{data['win_rate']:>7.1f}      {data['agreement_rate']:>8.1f}")
        
        print(f"\n🎲 ACTION DISTRIBUTIONS:")
        actions = ["stand", "hit", "double", "split"]
        
        # Header
        header = f"{'Model':<20}"
        for action in actions:
            header += f"{action.capitalize():<10}"
        print(header)
        print("-" * 60)
        
        # Data rows
        for model_name, data in results.items():
            row = f"{model_name:<20}"
            total_actions = sum(data['actions_taken'].values())
            for action in actions:
                pct = data['actions_taken'][action] / total_actions * 100
                row += f"{pct:>7.1f}%  "
            print(row)
        
        # Find best model
        if len(results) > 1:
            best_model = max(results.keys(), key=lambda k: results[k]['mean_return'])
            best_ev = results[best_model]['mean_return']
            
            print(f"\n🏆 BEST PERFORMING MODEL:")
            print(f"   {best_model} with EV of {best_ev:+.4f}")
            
            # Show improvements
            baseline_candidates = [name for name in results.keys() if 'baseline' in name.lower() or 'best' in name.lower()]
            enhanced_candidates = [name for name in results.keys() if 'enhanced' in name.lower()]
            
            if baseline_candidates and enhanced_candidates:
                baseline = baseline_candidates[0]
                enhanced = enhanced_candidates[0]
                
                improvement = results[enhanced]['mean_return'] - results[baseline]['mean_return']
                agreement_improvement = results[enhanced]['agreement_rate'] - results[baseline]['agreement_rate']
                
                print(f"\n🚀 IMPROVEMENTS:")
                print(f"   Expected Value: {improvement:+.4f}")
                print(f"   Agreement Rate: {agreement_improvement:+.1f}%")
        
        print("=" * 80)
    
    def save_results(self, results: Dict, output_file: str):
        """Save comparison results to file."""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📊 Results saved to {output_file}")


def main():
    """Main comparison function."""
    parser = argparse.ArgumentParser(description="Compare model performance")
    parser.add_argument("--baseline-model", type=str, help="Path to baseline model")
    parser.add_argument("--enhanced-model", type=str, help="Path to enhanced model")
    parser.add_argument("--episodes", type=int, default=5000, help="Number of test episodes")
    parser.add_argument("--output", type=str, default="model_comparison.json", help="Output file")
    
    args = parser.parse_args()
    
    # Default model paths if not provided
    if not args.baseline_model:
        args.baseline_model = "runs/phase1_full_corrected/models/best_model.zip"
    
    if not args.enhanced_model:
        args.enhanced_model = "runs/enhanced_test/models/best_model.zip"
    
    # Setup comparator
    comparator = ModelComparator(args.episodes)
    
    # Define models to compare
    model_configs = [
        (args.baseline_model, "Baseline Model"),
    ]
    
    # Add enhanced model if it exists
    if Path(args.enhanced_model).exists():
        model_configs.append((args.enhanced_model, "Enhanced Model"))
    else:
        print(f"⚠️ Enhanced model not found: {args.enhanced_model}")
        print("   Will only evaluate baseline model")
    
    # Run comparison
    results = comparator.compare_models(model_configs)
    
    # Display and save results
    comparator.print_comparison(results)
    comparator.save_results(results, args.output)


if __name__ == "__main__":
    main() 
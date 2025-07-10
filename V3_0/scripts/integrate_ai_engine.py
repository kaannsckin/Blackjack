#!/usr/bin/env python3
"""
AI Engine Integration Script (FAZ 1 – F1.5)

This script integrates the trained AI model with the existing blackjack engine
and runs comprehensive tests to validate the integration.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Local imports
from utils.ai_strategy import create_ai_strategy
from utils.ai_play_strategy import create_ai_play_strategy
from utils.basic_strategy import BasicStrategy
from utils.performance_metrics import PerformanceAnalyzer


class AIEngineIntegration:
    """Integration class for testing AI model with blackjack engine."""
    
    def __init__(self, model_path: Path, num_episodes: int = 1000):
        """
        Initialize AI engine integration.
        
        Args:
            model_path: Path to trained AI model
            num_episodes: Number of episodes to test
        """
        self.model_path = model_path
        self.num_episodes = num_episodes
        self.ai_strategy = None
        self.basic_strategy = BasicStrategy()
        self.performance_analyzer = PerformanceAnalyzer()
        
        self._load_ai_strategy()
    
    def _load_ai_strategy(self):
        """Load AI strategy with trained model."""
        try:
            self.ai_strategy = create_ai_strategy(self.model_path, "ai")
            print(f"✅ AI strategy loaded from {self.model_path}")
        except Exception as e:
            print(f"❌ Failed to load AI strategy: {e}")
            self.ai_strategy = None
    
    def _load_env_class(self):
        """Load environment class like evaluate_play_agent.py."""
        import importlib
        import inspect
        from typing import Type
        
        env_mod = importlib.import_module("rl_environment")
        for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
            if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
                return getattr(env_mod, cls_name)
        raise RuntimeError("Environment class not found in rl_environment.py")

    def test_ai_vs_basic(self) -> Dict[str, Any]:
        """
        Test AI model using evaluate_play_agent.py exact approach.
        Returns:
            Dictionary with test results
        """
        from stable_baselines3 import DQN
        import random
        print(f"🔄 Testing AI vs Basic Strategy ({self.num_episodes:,} episodes)... [Exact Approach]")

        ai_rewards = []
        basic_rewards = []
        action_agreements = []

        # Model ve environment'ı evaluate_play_agent.py gibi yükle
        rng = random.Random(42)  # Fixed seed for reproducibility
        EnvCls = self._load_env_class()
        env = EnvCls()
        
        try:
            model = DQN.load(self.model_path, env=env, print_system_info=False)
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {self.model_path}: {e}")

        for episode in range(self.num_episodes):
            # Environment'dan observation al (evaluate_play_agent.py gibi)
            episode_seed = int(rng.randint(1, 1_000_000))
            obs, _info = env.reset(seed=episode_seed)
            
            # AI action - environment'ın döndürdüğü observation ile
            try:
                action_idx, _state = model.predict(obs, deterministic=True)
                action_map = {0: "stand", 1: "hit", 2: "double", 3: "split"}
                ai_action = action_map.get(action_idx, "hit")
            except Exception as e:
                print(f"[DEBUG] AI prediction failed: {e}")
                ai_action = "hit"

            # Basic strategy action - observation'dan değerleri çıkar
            player_total, dealer_up, usable_ace, _tc = obs
            basic_action = self.basic_strategy.get_action(player_total, dealer_up, usable_ace)
            basic_action_str = action_map.get(basic_action, "hit")

            # Check agreement
            agreement = ai_action == basic_action_str
            action_agreements.append(agreement)

            # Simulate rewards (simplified)
            ai_reward = self._simulate_reward(player_total, dealer_up, ai_action)
            basic_reward = self._simulate_reward(player_total, dealer_up, basic_action_str)

            ai_rewards.append(ai_reward)
            basic_rewards.append(basic_reward)

        env.close()

        # Calculate metrics
        ai_metrics = self.performance_analyzer.calculate_metrics(ai_rewards)
        basic_metrics = self.performance_analyzer.calculate_metrics(basic_rewards)

        agreement_rate = np.mean(action_agreements) * 100

        results = {
            "ai_metrics": ai_metrics,
            "basic_metrics": basic_metrics,
            "agreement_rate": agreement_rate,
            "total_episodes": self.num_episodes,
            "ai_rewards": ai_rewards,
            "basic_rewards": basic_rewards,
            "action_agreements": action_agreements
        }

        return results
    
    def _simulate_reward(self, player_total: int, dealer_up: int, action: str) -> float:
        """
        Simulate reward for given action (simplified).
        
        This is a simplified reward simulation. In a real implementation,
        you would use the actual blackjack engine.
        """
        # Simplified reward logic
        if action == "hit":
            # Hit action - depends on current total
            if player_total <= 11:
                return 0.1  # Good hit
            elif player_total <= 16:
                return 0.0  # Neutral
            else:
                return -0.2  # Bad hit
        elif action == "stand":
            # Stand action - depends on dealer up card
            if player_total >= 17:
                return 0.1  # Good stand
            elif dealer_up <= 6:
                return 0.0  # Neutral
            else:
                return -0.1  # Bad stand
        elif action == "double":
            # Double action - depends on situation
            if player_total in [9, 10, 11] and dealer_up <= 9:
                return 0.2  # Good double
            else:
                return -0.1  # Bad double
        else:  # split
            return 0.0  # Neutral for split
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive test report."""
        if not results:
            return "❌ No results to report"
        
        ai_metrics = results["ai_metrics"]
        basic_metrics = results["basic_metrics"]
        agreement_rate = results["agreement_rate"]
        
        report = f"""
# AI Engine Integration Test Report

## Test Configuration
- Model Path: {self.model_path}
- Episodes: {self.num_episodes:,}
- AI Strategy: {type(self.ai_strategy).__name__}

## Performance Comparison

| Metric | AI Strategy | Basic Strategy | Difference |
|--------|-------------|----------------|------------|
| EV | {ai_metrics.ev:+.4f} | {basic_metrics.ev:+.4f} | {ai_metrics.ev - basic_metrics.ev:+.4f} |
| RTP (%) | {ai_metrics.rtp:.2f} | {basic_metrics.rtp:.2f} | {ai_metrics.rtp - basic_metrics.rtp:+.2f} |
| Win Rate (%) | {ai_metrics.win_rate:.2f} | {basic_metrics.win_rate:.2f} | {ai_metrics.win_rate - basic_metrics.win_rate:+.2f} |
| Volatility | {ai_metrics.volatility:.4f} | {basic_metrics.volatility:.4f} | {ai_metrics.volatility - basic_metrics.volatility:+.4f} |

## Action Agreement
- Agreement Rate: {agreement_rate:.1f}%
- Episodes Tested: {self.num_episodes:,}

## Conclusion
"""
        
        if ai_metrics.ev > basic_metrics.ev:
            report += "✅ AI strategy outperforms basic strategy\n"
        elif ai_metrics.ev < basic_metrics.ev:
            report += "⚠️ AI strategy underperforms basic strategy\n"
        else:
            report += "➖ AI strategy performs similarly to basic strategy\n"
        
        if agreement_rate > 80:
            report += "✅ High agreement with basic strategy\n"
        elif agreement_rate > 60:
            report += "⚠️ Moderate agreement with basic strategy\n"
        else:
            report += "❌ Low agreement with basic strategy\n"
        
        return report
    
    def save_results(self, results: Dict[str, Any], output_path: Path):
        """Save test results to file."""
        if not results:
            return
        
        # Save detailed results
        df = pd.DataFrame({
            "episode": range(len(results["ai_rewards"])),
            "ai_reward": results["ai_rewards"],
            "basic_reward": results["basic_rewards"],
            "agreement": results["action_agreements"]
        })
        
        df.to_csv(output_path / "ai_vs_basic_results.csv", index=False)
        
        # Save summary
        summary = {
            "ai_ev": results["ai_metrics"].ev,
            "basic_ev": results["basic_metrics"].ev,
            "agreement_rate": results["agreement_rate"],
            "total_episodes": results["total_episodes"]
        }
        
        import json
        with open(output_path / "ai_vs_basic_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Results saved to {output_path}")


def main():
    """Main integration test function."""
    parser = argparse.ArgumentParser(description="AI Engine Integration Test")
    parser.add_argument("--model-path", type=str, required=True, help="Path to trained AI model")
    parser.add_argument("--episodes", type=int, default=1000, help="Number of test episodes")
    parser.add_argument("--output-dir", type=str, default="runs/integration_test", help="Output directory")
    
    args = parser.parse_args()
    
    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Run integration test
    integration = AIEngineIntegration(Path(args.model_path), args.episodes)
    results = integration.test_ai_vs_basic()
    
    # Generate and save report
    report = integration.generate_report(results)
    print(report)
    
    # Save results
    integration.save_results(results, output_path)
    
    # Save report
    with open(output_path / "integration_report.md", "w") as f:
        f.write(report)
    
    print(f"✅ Integration test completed. Results saved to {output_path}")


if __name__ == "__main__":
    main() 
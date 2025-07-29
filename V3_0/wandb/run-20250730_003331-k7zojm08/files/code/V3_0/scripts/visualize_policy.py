#!/usr/bin/env python3
"""
Policy Visualization Script (FAZ 1 – F1.7)

This script creates comprehensive visualizations of the trained AI model's policy:
- Q-value heatmaps for different game states
- Policy comparison with basic strategy
- Action distribution analysis
- Decision boundary plots
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from stable_baselines3 import DQN

import wandb
import torch as th  # Added missing PyTorch import

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Local imports
from utils.basic_strategy import BasicStrategy
from utils.tracking import init_wandb


class PolicyVisualizer:
    """Comprehensive policy visualization for blackjack AI."""
    
    def __init__(self, model_path: Path, output_dir: Path):
        """
        Initialize policy visualizer.
        
        Args:
            model_path: Path to trained AI model
            output_dir: Directory to save visualizations
        """
        self.model_path = model_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.basic_strategy = BasicStrategy()
        
        self._load_model()
    
    def _load_model(self):
        """Load trained AI model."""
        try:
            # Load environment class
            import importlib
            import inspect
            from typing import Type
            
            env_mod = importlib.import_module("rl_environment")
            for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
                if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
                    EnvCls = getattr(env_mod, cls_name)
                    break
            else:
                raise RuntimeError("Environment class not found")
            
            # Load model
            env = EnvCls()
            self.model = DQN.load(self.model_path, env=env, print_system_info=False)
            print(f"✅ Model loaded from {self.model_path}")
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def generate_q_value_heatmap(self, usable_ace: bool = False) -> None:
        """
        Generate Q-value heatmap for all player totals vs dealer up cards.
        
        Args:
            usable_ace: Whether to visualize for usable ace or not
        """
        print(f"🔄 Generating Q-value heatmap (usable_ace={usable_ace})...")
        
        # Create state space
        player_totals = list(range(4, 22))  # 4-21
        dealer_ups = list(range(1, 12))     # A-10
        
        # Initialize Q-value matrix
        q_values = np.zeros((len(player_totals), len(dealer_ups), 4))  # 4 actions
        
        # Calculate Q-values for each state
        for i, player_total in enumerate(player_totals):
            for j, dealer_up in enumerate(dealer_ups):
                # Create observation
                obs = np.array([player_total, dealer_up, float(usable_ace), 0.0])  # TC=0
                
                try:
                    # Get Q-values from model - FIXED: Use proper method
                    # Convert observation to proper format
                    obs_tensor = obs.reshape(1, -1)
                    
                    # Get Q-values using the model's q_net properly
                    with th.no_grad():
                        q_values_tensor = self.model.q_net(th.FloatTensor(obs_tensor))
                        q_values[i, j, :] = q_values_tensor.cpu().numpy().flatten()
                        
                except Exception as e:
                    print(f"Warning: Could not get Q-values for state {player_total}, {dealer_up}: {e}")
                    q_values[i, j, :] = 0.0
        
        # Create heatmaps for each action
        actions = ["Stand", "Hit", "Double", "Split"]
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f"Q-Value Heatmaps ({'Usable Ace' if usable_ace else 'No Usable Ace'})", fontsize=16)
        
        for idx, action in enumerate(actions):
            ax = axes[idx // 2, idx % 2]
            
            # Create heatmap
            sns.heatmap(
                q_values[:, :, idx],
                xticklabels=dealer_ups,
                yticklabels=player_totals,
                annot=True,
                fmt=".2f",
                cmap="RdYlBu_r",
                center=0,
                ax=ax,
                cbar_kws={"label": f"Q-Value ({action})"}
            )
            
            ax.set_title(f"{action} Q-Values")
            ax.set_xlabel("Dealer Up Card")
            ax.set_ylabel("Player Total")
        
        plt.tight_layout()
        filename = f"q_value_heatmap_{'ace' if usable_ace else 'no_ace'}.png"
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches="tight")
        plt.close()
        
        print(f"✅ Q-value heatmap saved: {filename}")
    
    def generate_policy_comparison(self) -> None:
        """Generate policy comparison between AI and basic strategy."""
        print("🔄 Generating policy comparison...")
        
        # Create state space
        player_totals = list(range(4, 22))
        dealer_ups = list(range(1, 12))
        
        # Initialize policy matrices
        ai_policy = np.zeros((len(player_totals), len(dealer_ups)), dtype=int)
        basic_policy = np.zeros((len(player_totals), len(dealer_ups)), dtype=int)
        
        # Action mapping
        action_map = {0: "stand", 1: "hit", 2: "double", 3: "split"}
        
        # Calculate policies
        for i, player_total in enumerate(player_totals):
            for j, dealer_up in enumerate(dealer_ups):
                # AI policy
                obs = np.array([player_total, dealer_up, 0.0, 0.0])  # No usable ace, TC=0
                try:
                    action_idx, _ = self.model.predict(obs, deterministic=True)
                    ai_policy[i, j] = action_idx
                except Exception as e:
                    print(f"Warning: AI prediction failed for {player_total}, {dealer_up}: {e}")
                    ai_policy[i, j] = 1  # Default to hit
                
                # Basic strategy policy
                basic_action = self.basic_strategy.get_action(player_total, dealer_up, False)
                basic_policy[i, j] = basic_action
        
        # Create comparison plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Policy Comparison: AI vs Basic Strategy", fontsize=16)
        
        # AI Policy
        ax1 = axes[0, 0]
        sns.heatmap(
            ai_policy,
            xticklabels=dealer_ups,
            yticklabels=player_totals,
            annot=True,
            fmt="d",
            cmap="Set3",
            ax=ax1,
            cbar_kws={"label": "Action (0=Stand, 1=Hit, 2=Double, 3=Split)"}
        )
        ax1.set_title("AI Policy")
        ax1.set_xlabel("Dealer Up Card")
        ax1.set_ylabel("Player Total")
        
        # Basic Strategy Policy
        ax2 = axes[0, 1]
        sns.heatmap(
            basic_policy,
            xticklabels=dealer_ups,
            yticklabels=player_totals,
            annot=True,
            fmt="d",
            cmap="Set3",
            ax=ax2,
            cbar_kws={"label": "Action (0=Stand, 1=Hit, 2=Double, 3=Split)"}
        )
        ax2.set_title("Basic Strategy Policy")
        ax2.set_xlabel("Dealer Up Card")
        ax2.set_ylabel("Player Total")
        
        # Agreement matrix
        agreement = (ai_policy == basic_policy).astype(int)
        ax3 = axes[1, 0]
        sns.heatmap(
            agreement,
            xticklabels=dealer_ups,
            yticklabels=player_totals,
            annot=True,
            fmt="d",
            cmap="RdYlGn",
            ax=ax3,
            cbar_kws={"label": "Agreement (1=Agree, 0=Disagree)"}
        )
        ax3.set_title("Policy Agreement")
        ax3.set_xlabel("Dealer Up Card")
        ax3.set_ylabel("Player Total")
        
        # Agreement rate by player total
        agreement_rate_by_total = np.mean(agreement, axis=1)
        ax4 = axes[1, 1]
        ax4.bar(player_totals, agreement_rate_by_total, color='skyblue', alpha=0.7)
        ax4.set_xlabel("Player Total")
        ax4.set_ylabel("Agreement Rate")
        ax4.set_title("Agreement Rate by Player Total")
        ax4.set_ylim(0, 1)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "policy_comparison.png", dpi=300, bbox_inches="tight")
        plt.close()
        
        # Calculate overall agreement
        overall_agreement = np.mean(agreement) * 100
        print(f"✅ Policy comparison saved. Overall agreement: {overall_agreement:.1f}%")
    
    def generate_action_distribution(self) -> None:
        """Generate action distribution analysis."""
        print("🔄 Generating action distribution analysis...")
        
        # Sample states and collect actions
        states = []
        ai_actions = []
        basic_actions = []
        
        # Generate random states
        np.random.seed(42)
        for _ in range(1000):
            player_total = np.random.randint(4, 22)
            dealer_up = np.random.randint(1, 12)
            usable_ace = np.random.choice([True, False])
            
            obs = np.array([player_total, dealer_up, float(usable_ace), 0.0])
            
            # AI action
            try:
                action_idx, _ = self.model.predict(obs, deterministic=True)
                ai_actions.append(action_idx)
            except:
                ai_actions.append(1)  # Default to hit
            
            # Basic strategy action
            basic_action = self.basic_strategy.get_action(player_total, dealer_up, usable_ace)
            basic_actions.append(basic_action)
            
            states.append({
                'player_total': player_total,
                'dealer_up': dealer_up,
                'usable_ace': usable_ace
            })
        
        # Create action distribution plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Action Distribution Analysis", fontsize=16)
        
        # AI Action Distribution
        ax1 = axes[0, 0]
        ai_counts = pd.Series(ai_actions).value_counts().sort_index()
        ax1.bar(ai_counts.index, ai_counts.values, color='lightcoral', alpha=0.7)
        ax1.set_title("AI Action Distribution")
        ax1.set_xlabel("Action (0=Stand, 1=Hit, 2=Double, 3=Split)")
        ax1.set_ylabel("Count")
        ax1.set_xticks(range(4))
        
        # Basic Strategy Action Distribution
        ax2 = axes[0, 1]
        basic_counts = pd.Series(basic_actions).value_counts().sort_index()
        ax2.bar(basic_counts.index, basic_counts.values, color='lightblue', alpha=0.7)
        ax2.set_title("Basic Strategy Action Distribution")
        ax2.set_xlabel("Action (0=Stand, 1=Hit, 2=Double, 3=Split)")
        ax2.set_ylabel("Count")
        ax2.set_xticks(range(4))
        
        # Action comparison
        ax3 = axes[1, 0]
        action_names = ['Stand', 'Hit', 'Double', 'Split']
        x = np.arange(len(action_names))
        width = 0.35
        
        ai_percentages = [ai_counts.get(i, 0) / len(ai_actions) * 100 for i in range(4)]
        basic_percentages = [basic_counts.get(i, 0) / len(basic_actions) * 100 for i in range(4)]
        
        ax3.bar(x - width/2, ai_percentages, width, label='AI', alpha=0.7)
        ax3.bar(x + width/2, basic_percentages, width, label='Basic Strategy', alpha=0.7)
        ax3.set_xlabel("Action")
        ax3.set_ylabel("Percentage (%)")
        ax3.set_title("Action Distribution Comparison")
        ax3.set_xticks(x)
        ax3.set_xticklabels(action_names)
        ax3.legend()
        
        # Agreement by action type
        ax4 = axes[1, 1]
        agreement_by_action = []
        for action in range(4):
            mask = np.array(basic_actions) == action
            if np.any(mask):
                agreement = np.mean(np.array(ai_actions)[mask] == action)
                agreement_by_action.append(agreement * 100)
            else:
                agreement_by_action.append(0)
        
        ax4.bar(action_names, agreement_by_action, color='lightgreen', alpha=0.7)
        ax4.set_xlabel("Action")
        ax4.set_ylabel("Agreement Rate (%)")
        ax4.set_title("Agreement Rate by Action Type")
        ax4.set_ylim(0, 100)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "action_distribution.png", dpi=300, bbox_inches="tight")
        plt.close()
        
        print("✅ Action distribution analysis saved")
    
    def generate_decision_boundaries(self) -> None:
        """Generate decision boundary plots for key game situations."""
        print("🔄 Generating decision boundaries...")
        
        # Focus on key decision points
        key_situations = [
            (12, 2, "12 vs 2"),
            (12, 3, "12 vs 3"),
            (12, 4, "12 vs 4"),
            (12, 5, "12 vs 5"),
            (12, 6, "12 vs 6"),
            (13, 2, "13 vs 2"),
            (13, 3, "13 vs 3"),
            (13, 4, "13 vs 4"),
            (13, 5, "13 vs 5"),
            (13, 6, "13 vs 6"),
            (16, 7, "16 vs 7"),
            (16, 8, "16 vs 8"),
            (16, 9, "16 vs 9"),
            (16, 10, "16 vs 10"),
            (16, 11, "16 vs A"),
        ]
        
        fig, axes = plt.subplots(3, 5, figsize=(20, 12))
        fig.suptitle("Decision Boundaries: AI vs Basic Strategy", fontsize=16)
        
        for idx, (player_total, dealer_up, title) in enumerate(key_situations):
            row = idx // 5
            col = idx % 5
            ax = axes[row, col]
            
            # Get AI decision
            obs = np.array([player_total, dealer_up, 0.0, 0.0])
            try:
                ai_action, _ = self.model.predict(obs, deterministic=True)
            except:
                ai_action = 1  # Default to hit
            
            # Get basic strategy decision
            basic_action = self.basic_strategy.get_action(player_total, dealer_up, False)
            
            # Create visualization
            actions = ['Stand', 'Hit', 'Double', 'Split']
            ai_decision = actions[ai_action]
            basic_decision = actions[basic_action]
            
            # Color coding
            ai_color = 'green' if ai_action == basic_action else 'red'
            basic_color = 'blue'
            
            ax.text(0.5, 0.7, f"AI: {ai_decision}", 
                   ha='center', va='center', fontsize=12, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=ai_color, alpha=0.7))
            ax.text(0.5, 0.3, f"Basic: {basic_decision}", 
                   ha='center', va='center', fontsize=12,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=basic_color, alpha=0.7))
            
            ax.set_title(title)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "decision_boundaries.png", dpi=300, bbox_inches="tight")
        plt.close()
        
        print("✅ Decision boundaries saved")
    
    def generate_all_visualizations(self) -> None:
        """Generate all policy visualizations."""
        print("🎨 Generating comprehensive policy visualizations...")
        
        # Initialize W&B if available
        try:
            wandb_run = init_wandb(
                project="blackjack_phase1",
                name="policy_visualization",
                config={"model_path": str(self.model_path)}
            )
        except:
            wandb_run = None
        
        # Generate all visualizations
        self.generate_q_value_heatmap(usable_ace=False)
        self.generate_q_value_heatmap(usable_ace=True)
        self.generate_policy_comparison()
        self.generate_action_distribution()
        self.generate_decision_boundaries()
        
        # Log to W&B if available
        if wandb_run:
            for img_file in self.output_dir.glob("*.png"):
                wandb_run.log({img_file.stem: wandb.Image(str(img_file))})
            wandb_run.finish()
        
        print(f"✅ All visualizations saved to {self.output_dir}")


def main():
    """Main visualization function."""
    import os
    
    parser = argparse.ArgumentParser(description="Policy Visualization for Blackjack AI")
    parser.add_argument("--model-path", type=str, required=False, help="Path to trained AI model")
    parser.add_argument("--output-dir", type=str, default="runs/policy_visualization", help="Output directory")
    
    args = parser.parse_args()
    
    # Varsayılan model yolu ve output klasörü (editörden çalıştırma için)
    DEFAULT_MODEL_PATH = "runs/phase1/models/final_model.zip"
    DEFAULT_OUTPUT_DIR = "runs/policy_visualization"
    
    model_path = args.model_path or os.environ.get("MODEL_PATH") or DEFAULT_MODEL_PATH
    output_dir = args.output_dir or os.environ.get("OUTPUT_DIR") or DEFAULT_OUTPUT_DIR
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        print(f"💡 Please provide a valid model path with --model-path")
        return
    
    # Create visualizer and generate all plots
    visualizer = PolicyVisualizer(Path(model_path), Path(output_dir))
    visualizer.generate_all_visualizations()
    
    print("🎉 Policy visualization completed successfully!")


if __name__ == "__main__":
    main() 
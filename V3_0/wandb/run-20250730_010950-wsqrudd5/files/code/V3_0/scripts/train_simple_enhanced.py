#!/usr/bin/env python3
"""
Simple Enhanced DQN Training Script - Working Version
====================================================

A simplified version that focuses on core improvements without complex wrappers.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch as th
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor
from stable_baselines3.common.utils import set_random_seed

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rl_environment import BlackjackEnv
from utils.callbacks import SaveBestModelCallback
from utils.tracking import init_wandb


def enhanced_schedule(initial: float, final: float):
    """Enhanced learning rate schedule."""
    def _schedule(progress: float) -> float:
        return final + (initial - final) * progress
    return _schedule


def create_env(seed: int = None):
    """Create simple monitored environment."""
    return Monitor(BlackjackEnv(seed=seed))


def main():
    """Main training function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=2_000_000, help="Training steps")
    parser.add_argument("--envs", type=int, default=4, help="Parallel environments")
    parser.add_argument("--output", type=str, default="runs/simple_enhanced", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    set_random_seed(args.seed)
    
    # Setup directories
    output_dir = Path(args.output)
    models_dir = output_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Starting enhanced training - {args.steps:,} steps")
    
    # Initialize W&B
    wandb_run = init_wandb(
        project="blackjack_simple_enhanced",
        name="simple-enhanced-dqn",
        config={"steps": args.steps, "seed": args.seed}
    )
    
    # Create environments
    vec_env = make_vec_env(
        lambda: create_env(seed=args.seed),
        n_envs=args.envs,
        seed=args.seed
    )
    vec_env = VecMonitor(vec_env)
    
    eval_env = VecMonitor(
        make_vec_env(lambda: create_env(seed=args.seed + 1000), n_envs=1)
    )
    
    # Enhanced DQN with better hyperparameters
    model = DQN(
        "MlpPolicy",
        vec_env,
        learning_rate=enhanced_schedule(1e-3, 1e-4),
        exploration_fraction=0.4,       # Longer exploration
        exploration_final_eps=0.02,     # Lower final epsilon
        exploration_initial_eps=1.0,
        buffer_size=200_000,           # Larger buffer
        batch_size=256,                # Reasonable batch size
        target_update_interval=8_000,   # More frequent target updates
        gamma=0.995,                   # Higher discount factor
        train_freq=4,                  # Regular training frequency
        gradient_steps=1,
        policy_kwargs=dict(
            net_arch=[512, 256, 128],   # Deeper network
            activation_fn=th.nn.ReLU,
        ),
        tensorboard_log=None,          # No tensorboard to avoid issues
        seed=args.seed,
        verbose=1,
        device="auto",
    )
    
    # Callback
    best_callback = SaveBestModelCallback(
        eval_env=eval_env,
        eval_freq=50_000,
        n_eval_episodes=1000,
        save_path=models_dir,
        deterministic=True,
        verbose=1,
    )
    
    print("🎓 Starting training...")
    
    # Train
    model.learn(
        total_timesteps=args.steps,
        callback=best_callback,
        progress_bar=True,
    )
    
    # Save final model
    final_path = models_dir / "final_enhanced_model"
    model.save(final_path)
    print(f"💾 Model saved to {final_path}.zip")
    
    # Cleanup
    vec_env.close()
    eval_env.close()
    if wandb_run:
        wandb_run.finish()
    
    print("✅ Enhanced training completed!")


if __name__ == "__main__":
    main() 
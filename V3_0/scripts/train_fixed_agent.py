#!/usr/bin/env python3
"""
Improved Training Script with Fixed Environment

Uses the corrected betting environment with optimized hyperparameters.
"""

import argparse
import time
import os
from pathlib import Path
import numpy as np
from typing import Dict, Any

# Stable Baselines3 imports
from stable_baselines3 import PPO, TD3, SAC
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.logger import configure
from stable_baselines3.common.vec_env import VecNormalize

# Add parent directory to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

# Import our fixed environment
from betting_environment_fixed import create_fixed_betting_env


class ImprovedBettingCallback(BaseCallback):
    """Enhanced callback for monitoring betting agent training."""
    
    def __init__(self, eval_freq: int = 10000, verbose: int = 0):
        super().__init__(verbose)
        self.eval_freq = eval_freq
        self.episode_rewards = []
        self.episode_lengths = []
        self.bankroll_history = []
        
    def _on_step(self) -> bool:
        # Collect episode statistics
        for env_idx, done in enumerate(self.locals.get("dones", [])):
            if done:
                env = self.training_env.get_attr("env")[env_idx]
                
                # Get episode info
                info = self.locals.get("infos", [{}])[env_idx]
                episode_reward = info.get("episode", {}).get("r", 0)
                episode_length = info.get("episode", {}).get("l", 0)
                
                self.episode_rewards.append(episode_reward)
                self.episode_lengths.append(episode_length)
                
                # Get bankroll if available
                if hasattr(env, 'bankroll'):
                    self.bankroll_history.append(env.bankroll)
        
        # Log statistics every eval_freq steps
        if self.num_timesteps % self.eval_freq == 0 and self.episode_rewards:
            recent_rewards = self.episode_rewards[-100:]
            recent_lengths = self.episode_lengths[-100:]
            recent_bankrolls = self.bankroll_history[-100:] if self.bankroll_history else [1000]
            
            self.logger.record("train/mean_episode_reward", np.mean(recent_rewards))
            self.logger.record("train/mean_episode_length", np.mean(recent_lengths))
            self.logger.record("train/mean_bankroll", np.mean(recent_bankrolls))
            self.logger.record("train/episode_count", len(self.episode_rewards))
            
            if self.verbose > 0:
                print(f"\n📊 Training Stats @ Step {self.num_timesteps:,}:")
                print(f"   Episodes: {len(self.episode_rewards):,}")
                print(f"   Avg Reward: {np.mean(recent_rewards):.3f}")
                print(f"   Avg Length: {np.mean(recent_lengths):.1f}")
                print(f"   Avg Bankroll: ${np.mean(recent_bankrolls):.0f}")
        
        return True


def create_env(seed: int = None, **env_kwargs):
    """Create a single environment instance."""
    def _make_env():
        return create_fixed_betting_env(
            seed=seed,
            initial_bankroll=1000.0,
            min_bet=10.0,
            max_bet=100.0,
            risk_aversion=0.05,  # Lower risk aversion
            **env_kwargs
        )
    return _make_env


def create_model(
    algorithm: str,
    env,
    learning_rate: float = 3e-4,
    verbose: int = 1,
    **model_kwargs
):
    """Create RL model with algorithm-specific optimizations."""
    
    if algorithm.lower() == "ppo":
        # Optimized PPO for discrete action spaces
        model = PPO(
            "MlpPolicy",
            env,
            learning_rate=learning_rate,
            n_steps=2048,          # More steps per update
            batch_size=128,        # Smaller batches for stability
            n_epochs=10,           # More training epochs
            gamma=0.99,            # Standard discount factor
            gae_lambda=0.95,       # GAE parameter
            clip_range=0.2,        # Standard clipping
            ent_coef=0.01,         # Increased exploration
            vf_coef=0.5,           # Value function coefficient
            max_grad_norm=0.5,     # Gradient clipping
            verbose=verbose,
            **model_kwargs
        )
    
    elif algorithm.lower() == "td3":
        # TD3 for continuous-like problems
        model = TD3(
            "MlpPolicy",
            env,
            learning_rate=learning_rate,
            buffer_size=200_000,   # Large replay buffer
            batch_size=256,        # Larger batches for off-policy
            gamma=0.99,
            tau=0.005,             # Soft update rate
            policy_delay=2,        # Delayed policy updates
            target_policy_noise=0.2,
            target_noise_clip=0.5,
            verbose=verbose,
            **model_kwargs
        )
    
    elif algorithm.lower() == "sac":
        # SAC for maximum entropy exploration
        model = SAC(
            "MlpPolicy",
            env,
            learning_rate=learning_rate,
            buffer_size=200_000,
            batch_size=256,
            gamma=0.99,
            tau=0.005,
            ent_coef="auto",       # Automatic entropy tuning
            verbose=verbose,
            **model_kwargs
        )
    
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    return model


def evaluate_model(model, env, n_episodes: int = 100) -> Dict[str, float]:
    """Evaluate trained model."""
    episode_rewards = []
    episode_lengths = []
    bankroll_changes = []
    
    for episode in range(n_episodes):
        obs, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        initial_bankroll = env.bankroll
        
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            episode_length += 1
            
            if done or truncated:
                break
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        bankroll_changes.append(env.bankroll - initial_bankroll)
    
    return {
        "mean_reward": np.mean(episode_rewards),
        "std_reward": np.std(episode_rewards),
        "mean_length": np.mean(episode_lengths),
        "mean_bankroll_change": np.mean(bankroll_changes),
        "win_rate": np.mean([r > 0 for r in episode_rewards]),
        "episodes": n_episodes
    }


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train Fixed Betting Agent")
    parser.add_argument("--algorithm", type=str, default="ppo", 
                       choices=["ppo", "td3", "sac"], help="RL algorithm")
    parser.add_argument("--total-steps", type=int, default=500_000, 
                       help="Total training steps")
    parser.add_argument("--n-envs", type=int, default=4, 
                       help="Number of parallel environments")
    parser.add_argument("--learning-rate", type=float, default=3e-4, 
                       help="Learning rate")
    parser.add_argument("--eval-freq", type=int, default=25_000, 
                       help="Evaluation frequency")
    parser.add_argument("--save-freq", type=int, default=50_000, 
                       help="Model save frequency")
    parser.add_argument("--log-dir", type=str, default="runs/fixed_training", 
                       help="Logging directory")
    parser.add_argument("--seed", type=int, default=42, 
                       help="Random seed")
    
    args = parser.parse_args()
    
    print("🔧 IMPROVED BETTING AGENT TRAINING")
    print("=" * 50)
    print(f"Algorithm: {args.algorithm.upper()}")
    print(f"Total Steps: {args.total_steps:,}")
    print(f"Environments: {args.n_envs}")
    print(f"Learning Rate: {args.learning_rate}")
    print(f"Log Directory: {args.log_dir}")
    print("=" * 50)
    
    # Create directories
    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(f"{args.log_dir}/models", exist_ok=True)
    
    # Create vectorized environments
    print("🌍 Creating environments...")
    
    # Training environments
    train_env = make_vec_env(
        lambda: create_fixed_betting_env(
            seed=args.seed,
            initial_bankroll=1000.0,
            min_bet=10.0,
            max_bet=100.0,
            risk_aversion=0.05
        ),
        n_envs=args.n_envs,
        seed=args.seed
    )
    
    # Evaluation environment (single)
    eval_env = create_fixed_betting_env(
        seed=args.seed + 1000,
        initial_bankroll=1000.0,
        min_bet=10.0,
        max_bet=100.0,
        risk_aversion=0.05
    )
    
    print(f"✅ Created {args.n_envs} training environments")
    
    # Create model
    print(f"🤖 Creating {args.algorithm.upper()} model...")
    
    model = create_model(
        algorithm=args.algorithm,
        env=train_env,
        learning_rate=args.learning_rate,
        verbose=1
    )
    
    print("✅ Model created successfully")
    
    # Configure logging (no tensorboard to avoid dependency issues)
    logger = configure(args.log_dir, ["stdout"])
    model.set_logger(logger)
    
    # Create callbacks
    training_callback = ImprovedBettingCallback(
        eval_freq=args.eval_freq,
        verbose=1
    )
    
    # Training loop
    print(f"\n🚀 Starting training for {args.total_steps:,} steps...")
    start_time = time.time()
    
    try:
        model.learn(
            total_timesteps=args.total_steps,
            callback=training_callback,
            progress_bar=True
        )
        
        training_time = time.time() - start_time
        print(f"\n✅ Training completed in {training_time:.1f} seconds")
        
        # Save final model
        final_model_path = f"{args.log_dir}/final_model"
        model.save(final_model_path)
        print(f"💾 Final model saved to: {final_model_path}")
        
        # Final evaluation
        print(f"\n🎯 FINAL EVALUATION:")
        print("🧪 Evaluating model over 500 episodes...")
        
        eval_results = evaluate_model(model, eval_env, n_episodes=500)
        
        print(f"   ✅ Mean reward: {eval_results['mean_reward']:.3f}")
        print(f"   ✅ Mean length: {eval_results['mean_length']:.1f}")
        print(f"   ✅ Win rate: {eval_results['win_rate']:.1%}")
        print(f"   ✅ Bankroll change: {eval_results['mean_bankroll_change']:+.1f}")
        
        # Save training summary
        summary = {
            "algorithm": args.algorithm,
            "total_steps": args.total_steps,
            "training_time": training_time,
            "final_evaluation": eval_results,
            "hyperparameters": {
                "learning_rate": args.learning_rate,
                "n_envs": args.n_envs,
                "seed": args.seed
            }
        }
        
        import json
        with open(f"{args.log_dir}/training_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n🎉 IMPROVED TRAINING COMPLETED SUCCESSFULLY!")
        print(f"📈 Final Performance: {eval_results['mean_reward']:.3f} avg reward")
        print(f"📏 Avg Episode Length: {eval_results['mean_length']:.1f}")
        print(f"🎯 Win Rate: {eval_results['win_rate']:.1%}")
        
        # Check if performance improved
        if eval_results['mean_reward'] > -5 and eval_results['mean_length'] > 1.5:
            print("🎊 SUCCESS: Performance significantly improved!")
        elif eval_results['mean_reward'] > -10:
            print("🟡 PROGRESS: Some improvement, but more work needed")
        else:
            print("🔴 NEEDS WORK: Still underperforming, try different approach")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
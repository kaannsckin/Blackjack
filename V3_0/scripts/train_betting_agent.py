#!/usr/bin/env python3
"""
F2.4 BETTING AGENT TRAINING SCRIPT
=================================

Professional-level betting strategy RL training with:
- PPO/TD3 algorithms for combined play+betting decisions
- Advanced 49D observation space environment
- 10M+ episode training capacity
- Learning rate scheduling
- WandB monitoring & logging
- Model checkpointing & evaluation
- Risk-aware training with Kelly Criterion integration

Usage:
    python scripts/train_betting_agent.py --algorithm ppo --total-steps 10000000 --log-wandb
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np
import time
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# RL imports
import torch as th
from stable_baselines3 import PPO, TD3, SAC
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize, VecMonitor
from stable_baselines3.common.callbacks import (
    BaseCallback, EvalCallback, CheckpointCallback, CallbackList
)
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.monitor import Monitor

# Environment imports
from advanced_betting_environment import (
    AdvancedBettingEnv, AdvancedConfig, ActionConfig, ActionSpaceType,
    CardCountingSystem
)
from utils.callbacks import SaveBestModelCallback

# WandB for logging
try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    print("⚠️ WandB not available, using local logging only")
    WANDB_AVAILABLE = False


class BettingTrainingCallback(BaseCallback):
    """Custom callback for betting agent training monitoring."""
    
    def __init__(self, log_wandb: bool = False, eval_freq: int = 10000, verbose: int = 1):
        super().__init__(verbose)
        self.log_wandb = log_wandb and WANDB_AVAILABLE
        self.eval_freq = eval_freq
        self.episode_count = 0
        self.last_eval_step = 0
        
        # Training metrics
        self.episode_rewards = []
        self.episode_lengths = []
        self.bankroll_history = []
        self.risk_metrics_history = []
        
    def _on_step(self) -> bool:
        # Log episode completion
        if len(self.locals.get('infos', [])) > 0:
            for info in self.locals['infos']:
                if 'episode' in info:
                    # Episode completed
                    episode_reward = info['episode']['r']
                    episode_length = info['episode']['l']
                    
                    self.episode_rewards.append(episode_reward)
                    self.episode_lengths.append(episode_length)
                    self.episode_count += 1
                    
                    # Log betting-specific metrics
                    if 'advanced_metrics' in info:
                        metrics = info['advanced_metrics']
                        self.risk_metrics_history.append(metrics.get('risk_metrics', {}))
                        
                        if 'bankroll' in info:
                            self.bankroll_history.append(info['bankroll'])
                    
                    # WandB logging
                    if self.log_wandb and self.episode_count % 100 == 0:  # Log every 100 episodes
                        wandb.log({
                            "episode_reward": episode_reward,
                            "episode_length": episode_length,
                            "episode_count": self.episode_count,
                            "training_step": self.num_timesteps,
                        })
                        
                        # Log recent performance
                        if len(self.episode_rewards) >= 100:
                            recent_rewards = self.episode_rewards[-100:]
                            wandb.log({
                                "avg_reward_100": np.mean(recent_rewards),
                                "std_reward_100": np.std(recent_rewards),
                                "min_reward_100": np.min(recent_rewards),
                                "max_reward_100": np.max(recent_rewards),
                            })
        
        # Periodic evaluation and logging
        if self.num_timesteps - self.last_eval_step >= self.eval_freq:
            self._log_training_stats()
            self.last_eval_step = self.num_timesteps
        
        return True
    
    def _log_training_stats(self):
        """Log comprehensive training statistics."""
        if len(self.episode_rewards) == 0:
            return
        
        # Calculate statistics
        stats = {
            "total_episodes": len(self.episode_rewards),
            "avg_episode_reward": np.mean(self.episode_rewards[-1000:]) if len(self.episode_rewards) >= 1000 else np.mean(self.episode_rewards),
            "avg_episode_length": np.mean(self.episode_lengths[-1000:]) if len(self.episode_lengths) >= 1000 else np.mean(self.episode_lengths),
            "training_steps": self.num_timesteps,
        }
        
        # Risk metrics (if available)
        if self.risk_metrics_history:
            latest_risk = self.risk_metrics_history[-1]
            stats.update({
                "risk_of_ruin": latest_risk.get("risk_of_ruin_pct", 0),
                "kelly_criterion": latest_risk.get("kelly_criterion", 1),
                "sharpe_ratio": latest_risk.get("sharpe_ratio", 0),
                "bankroll_growth": latest_risk.get("bankroll_growth_pct", 0),
            })
        
        # Bankroll tracking
        if self.bankroll_history:
            current_bankroll = self.bankroll_history[-1]
            stats["current_bankroll"] = current_bankroll
            
            if len(self.bankroll_history) >= 100:
                bankroll_change = current_bankroll - self.bankroll_history[-100]
                stats["bankroll_change_100ep"] = bankroll_change
        
        # Log to WandB
        if self.log_wandb:
            wandb.log(stats)
        
        # Console logging
        if self.verbose > 0:
            print(f"\n📊 Training Stats @ Step {self.num_timesteps:,}:")
            print(f"   Episodes: {stats['total_episodes']:,}")
            print(f"   Avg Reward: {stats['avg_episode_reward']:.3f}")
            print(f"   Avg Length: {stats['avg_episode_length']:.1f}")
            if 'current_bankroll' in stats:
                print(f"   Bankroll: {stats['current_bankroll']:.1f}")
            if 'sharpe_ratio' in stats:
                print(f"   Sharpe: {stats['sharpe_ratio']:.2f}")


def create_advanced_betting_env(
    seed: int = None,
    action_type: ActionSpaceType = ActionSpaceType.MULTI_DISCRETE,
    initial_bankroll: float = 10000.0,
    **kwargs
) -> AdvancedBettingEnv:
    """Create advanced betting environment for training."""
    
    # Advanced configuration with all features
    advanced_config = AdvancedConfig(
        counting_systems=[
            CardCountingSystem.HI_LO,
            CardCountingSystem.KO, 
            CardCountingSystem.RED_SEVEN
        ],
        hand_history_size=20,
        detailed_history=True,
        track_deck_composition=True,
        track_table_dynamics=True,
        calculate_kelly=True,
        real_time_sharpe=True,
        advanced_ror=True,
        tc_smoothing=True,
        multiple_tc_norms=True,
    )
    
    # Action configuration
    action_config = ActionConfig(
        action_type=action_type,
        bet_levels=[1, 2, 5, 10, 25, 50, 100, 200] if action_type == ActionSpaceType.MULTI_DISCRETE else None,
        min_bet=1.0,
        max_bet=200.0,
    )
    
    # Create environment
    env = AdvancedBettingEnv(
        seed=seed,
        initial_bankroll=initial_bankroll,
        advanced_config=advanced_config,
        action_config=action_config,
        rules=kwargs.get("rules", {"num_decks": 6, "dealer_rule": "S17"}),
        penetration=kwargs.get("penetration", 0.75),
        risk_aversion=kwargs.get("risk_aversion", 0.1),
    )
    
    return env


def create_model(
    algorithm: str,
    env,
    learning_rate: float = 3e-4,
    architecture: list = None,
    **kwargs
):
    """Create RL model with specified algorithm."""
    
    if architecture is None:
        architecture = [512, 256, 128]  # Default architecture for 49D observation space
    
    # Policy kwargs for network architecture
    policy_kwargs = {
        "net_arch": architecture,
        "activation_fn": th.nn.ReLU,
    }
    
    # Algorithm-specific configurations
    if algorithm.lower() == "ppo":
        model = PPO(
            "MlpPolicy",
            env,
            learning_rate=learning_rate,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            clip_range_vf=None,
            ent_coef=0.01,  # Encourage exploration
            vf_coef=0.5,
            max_grad_norm=0.5,
            policy_kwargs=policy_kwargs,
            verbose=1,
            seed=kwargs.get("seed", 42),
            device="auto",
        )
    
    elif algorithm.lower() == "td3":
        # TD3 requires continuous action space
        if hasattr(env.action_space, 'nvec'):
            raise ValueError("TD3 requires continuous action space, use PPO for discrete actions")
        
        model = TD3(
            "MlpPolicy",
            env,
            learning_rate=learning_rate,
            buffer_size=1000000,
            learning_starts=25000,
            batch_size=256,
            tau=0.005,
            gamma=0.99,
            train_freq=1,
            gradient_steps=1,
            policy_delay=2,
            target_policy_noise=0.2,
            target_noise_clip=0.5,
            policy_kwargs=policy_kwargs,
            verbose=1,
            seed=kwargs.get("seed", 42),
            device="auto",
        )
    
    elif algorithm.lower() == "sac":
        # SAC also requires continuous action space
        if hasattr(env.action_space, 'nvec'):
            raise ValueError("SAC requires continuous action space, use PPO for discrete actions")
        
        model = SAC(
            "MlpPolicy",
            env,
            learning_rate=learning_rate,
            buffer_size=1000000,
            learning_starts=10000,
            batch_size=256,
            tau=0.005,
            gamma=0.99,
            train_freq=1,
            gradient_steps=1,
            ent_coef="auto",
            policy_kwargs=policy_kwargs,
            verbose=1,
            seed=kwargs.get("seed", 42),
            device="auto",
        )
    
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    return model


def setup_wandb(args, config: dict):
    """Setup WandB logging."""
    if not (args.log_wandb and WANDB_AVAILABLE):
        return False
    
    try:
        wandb.init(
            project="blackjack_betting_agent",
            name=f"F2.4_{args.algorithm}_{args.action_type}_{int(time.time())}",
            config=config,
            tags=["F2.4", "betting_agent", args.algorithm, args.action_type],
            notes=f"Professional betting agent training with {args.algorithm.upper()}",
        )
        return True
    except Exception as e:
        print(f"⚠️ WandB setup failed: {e}")
        return False


def evaluate_model(model, env, n_episodes: int = 100) -> Dict[str, float]:
    """Evaluate trained model performance."""
    print(f"🧪 Evaluating model over {n_episodes} episodes...")
    
    episode_rewards = []
    episode_lengths = []
    bankroll_changes = []
    risk_metrics = []
    
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
            
            if done and 'advanced_metrics' in info:
                risk_metrics.append(info['advanced_metrics'].get('risk_metrics', {}))
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        bankroll_changes.append(env.bankroll - initial_bankroll)
    
    # Calculate evaluation metrics (convert numpy types to native Python types for JSON serialization)
    eval_metrics = {
        "eval_mean_reward": float(np.mean(episode_rewards)),
        "eval_std_reward": float(np.std(episode_rewards)),
        "eval_mean_length": float(np.mean(episode_lengths)),
        "eval_mean_bankroll_change": float(np.mean(bankroll_changes)),
        "eval_total_bankroll_change": float(sum(bankroll_changes)),
        "eval_win_rate": float(np.mean([r > 0 for r in episode_rewards])),
        "eval_episodes": int(n_episodes),
    }
    
    # Risk metrics (if available)
    if risk_metrics:
        latest_risk = risk_metrics[-1]
        eval_metrics.update({
            "eval_risk_of_ruin": float(latest_risk.get("risk_of_ruin_pct", 0)),
            "eval_kelly_criterion": float(latest_risk.get("kelly_criterion", 1)),
            "eval_sharpe_ratio": float(latest_risk.get("sharpe_ratio", 0)),
        })
    
    print(f"   ✅ Mean reward: {eval_metrics['eval_mean_reward']:.3f}")
    print(f"   ✅ Win rate: {eval_metrics['eval_win_rate']:.1%}")
    print(f"   ✅ Bankroll change: {eval_metrics['eval_total_bankroll_change']:.1f}")
    
    return eval_metrics


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="F2.4 Betting Agent Training")
    
    # Training parameters
    parser.add_argument("--algorithm", type=str, default="ppo", choices=["ppo", "td3", "sac"],
                        help="RL algorithm to use")
    parser.add_argument("--total-steps", type=int, default=10_000_000,
                        help="Total training steps (default: 10M)")
    parser.add_argument("--n-envs", type=int, default=8,
                        help="Number of parallel environments")
    parser.add_argument("--learning-rate", type=float, default=3e-4,
                        help="Learning rate")
    parser.add_argument("--architecture", type=str, default="512,256,128",
                        help="Network architecture (comma-separated)")
    
    # Environment parameters
    parser.add_argument("--action-type", type=str, default="multi_discrete", 
                        choices=["multi_discrete", "dict_space", "continuous"],
                        help="Action space type")
    parser.add_argument("--initial-bankroll", type=float, default=10000.0,
                        help="Initial bankroll")
    parser.add_argument("--penetration", type=float, default=0.75,
                        help="Deck penetration")
    
    # Logging and saving
    parser.add_argument("--log-dir", type=str, default="runs/betting_agent_training",
                        help="Logging directory")
    parser.add_argument("--log-wandb", action="store_true",
                        help="Log to WandB")
    parser.add_argument("--save-freq", type=int, default=100_000,
                        help="Model save frequency")
    parser.add_argument("--eval-freq", type=int, default=50_000,
                        help="Evaluation frequency")
    
    # Other parameters
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    parser.add_argument("--device", type=str, default="auto",
                        help="Device (auto/cpu/cuda)")
    
    args = parser.parse_args()
    
    # Setup
    set_random_seed(args.seed)
    
    # Parse architecture
    architecture = [int(x) for x in args.architecture.split(",")]
    
    # Create directories
    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuration for logging
    config = {
        "algorithm": args.algorithm,
        "total_steps": args.total_steps,
        "n_envs": args.n_envs,
        "learning_rate": args.learning_rate,
        "architecture": architecture,
        "action_type": args.action_type,
        "initial_bankroll": args.initial_bankroll,
        "penetration": args.penetration,
        "seed": args.seed,
    }
    
    # Setup WandB
    wandb_enabled = setup_wandb(args, config)
    
    print("🚀 F2.4 BETTING AGENT TRAINING STARTED")
    print("=" * 50)
    print(f"Algorithm: {args.algorithm.upper()}")
    print(f"Total Steps: {args.total_steps:,}")
    print(f"Environments: {args.n_envs}")
    print(f"Architecture: {architecture}")
    print(f"Action Type: {args.action_type}")
    print(f"Initial Bankroll: ${args.initial_bankroll:,.0f}")
    print(f"WandB Logging: {'✅' if wandb_enabled else '❌'}")
    print("=" * 50)
    
    # Convert action type string to enum
    action_type_map = {
        "multi_discrete": ActionSpaceType.MULTI_DISCRETE,
        "dict_space": ActionSpaceType.DICT_SPACE,
        "continuous": ActionSpaceType.CONTINUOUS,
    }
    action_type = action_type_map[args.action_type]
    
    # Create vectorized environment
    def make_env():
        return Monitor(create_advanced_betting_env(
            seed=args.seed,
            action_type=action_type,
            initial_bankroll=args.initial_bankroll,
            penetration=args.penetration,
        ))
    
    if args.n_envs > 1:
        env = make_vec_env(make_env, n_envs=args.n_envs)
        env = VecMonitor(env)
    else:
        env = make_env()
    
    # Create evaluation environment
    eval_env = create_advanced_betting_env(
        seed=args.seed + 1000,
        action_type=action_type,
        initial_bankroll=args.initial_bankroll,
        penetration=args.penetration,
    )
    
    # Create model
    print(f"🤖 Creating {args.algorithm.upper()} model...")
    model = create_model(
        args.algorithm,
        env,
        learning_rate=args.learning_rate,
        architecture=architecture,
        seed=args.seed,
    )
    
    # Setup callbacks
    callbacks = []
    
    # Custom training callback
    training_callback = BettingTrainingCallback(
        log_wandb=wandb_enabled,
        eval_freq=args.eval_freq,
        verbose=1
    )
    callbacks.append(training_callback)
    
    # Checkpoint callback
    checkpoint_callback = CheckpointCallback(
        save_freq=args.save_freq,
        save_path=str(log_dir / "checkpoints"),
        name_prefix="betting_agent",
        save_replay_buffer=True,
        save_vecnormalize=True,
    )
    callbacks.append(checkpoint_callback)
    
    # Evaluation callback
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(log_dir / "best_model"),
        log_path=str(log_dir / "eval"),
        eval_freq=args.eval_freq,
        deterministic=True,
        render=False,
        n_eval_episodes=100,
        verbose=1,
    )
    callbacks.append(eval_callback)
    
    callback_list = CallbackList(callbacks)
    
    # Training
    print(f"🎓 Starting training for {args.total_steps:,} steps...")
    start_time = time.time()
    
    try:
        model.learn(
            total_timesteps=args.total_steps,
            callback=callback_list,
            progress_bar=True,
        )
        
        training_time = time.time() - start_time
        print(f"✅ Training completed in {training_time:.1f} seconds")
        
        # Save final model
        final_model_path = log_dir / "final_model"
        model.save(str(final_model_path))
        print(f"💾 Final model saved to: {final_model_path}")
        
        # Final evaluation
        print("\n🎯 FINAL EVALUATION:")
        final_metrics = evaluate_model(model, eval_env, n_episodes=500)
        
        # Save training summary
        summary = {
            "training_config": config,
            "training_time_seconds": training_time,
            "final_evaluation": final_metrics,
            "model_path": str(final_model_path),
        }
        
        with open(log_dir / "training_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        # WandB final log
        if wandb_enabled:
            wandb.log(final_metrics)
            wandb.log({"training_time_seconds": training_time})
            wandb.finish()
        
        print("\n🎉 F2.4 BETTING AGENT TRAINING COMPLETED SUCCESSFULLY!")
        print(f"📈 Final Performance: {final_metrics['eval_mean_reward']:.3f} avg reward")
        print(f"💰 Bankroll Change: {final_metrics['eval_total_bankroll_change']:.1f}")
        print(f"🎯 Win Rate: {final_metrics['eval_win_rate']:.1%}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
        model.save(str(log_dir / "interrupted_model"))
        if wandb_enabled:
            wandb.finish()
    
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        if wandb_enabled:
            wandb.finish()
        raise


if __name__ == "__main__":
    main() 
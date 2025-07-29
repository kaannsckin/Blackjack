#!/usr/bin/env python3
"""
Enhanced DQN Training Script for Blackjack Agent - Phase 1 Performance Boost
============================================================================

Building upon our successful baseline model, this enhanced trainer incorporates:
- Sophisticated reward shaping
- Improved network architecture
- Advanced training techniques
- Better exploration strategies
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Callable

import torch as th
import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import BaseCallback
from torch import nn

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rl_environment import BlackjackEnv
from utils.basic_strategy import BasicStrategy
from utils.callbacks import SaveBestModelCallback
from utils.tracking import init_wandb


class RewardShapingWrapper(gym.Wrapper):
    """Enhanced reward wrapper with sophisticated reward shaping."""
    
    def __init__(self, env, basic_strategy: BasicStrategy = None, shaping_weight: float = 0.1):
        super().__init__(env)
        self.basic_strategy = basic_strategy or BasicStrategy()
        self.shaping_weight = shaping_weight
        self.episode_actions = []
        self.episode_states = []
    
    def step(self, action):
        # Store state and action for reward shaping
        current_obs = self._get_current_obs()
        self.episode_states.append(current_obs)
        self.episode_actions.append(action)
        
        obs, reward, done, truncated, info = super().step(action)
        
        # Apply reward shaping
        if not done and not truncated:
            # Intermediate reward shaping
            shaped_reward = self._shape_intermediate_reward(current_obs, action)
            reward += shaped_reward
        else:
            # Terminal reward shaping
            terminal_shaping = self._shape_terminal_reward()
            reward += terminal_shaping
            # Reset episode tracking
            self.episode_actions = []
            self.episode_states = []
        
        return obs, reward, done, truncated, info
    
    def _get_current_obs(self):
        """Get current observation from environment."""
        # This is a simplified version - in real implementation,
        # you'd get this from the actual environment state
        if hasattr(self.env, '_get_obs'):
            return self.env._get_obs()
        return None
    
    def _shape_intermediate_reward(self, state, action):
        """Provide intermediate reward shaping during episode."""
        if state is None:
            return 0.0
        
        player_total, dealer_up, usable_ace, true_count = state
        
        # Basic strategy agreement bonus
        optimal_action = self.basic_strategy.get_action(
            int(player_total), int(dealer_up), bool(usable_ace)
        )
        
        agreement_bonus = 0.02 if action == optimal_action else -0.01
        
        # Risk-based shaping
        risk_penalty = 0.0
        if player_total > 21:
            risk_penalty = -0.05  # Bust penalty
        elif player_total >= 18 and action == 1:  # Hit on high totals
            risk_penalty = -0.02
        elif player_total <= 11 and action == 0:  # Stand on low totals
            risk_penalty = -0.02
        
        return self.shaping_weight * (agreement_bonus + risk_penalty)
    
    def _shape_terminal_reward(self):
        """Apply terminal reward shaping based on full episode."""
        if not self.episode_actions:
            return 0.0
        
        # Strategy consistency bonus
        basic_actions = []
        for state in self.episode_states:
            if state is not None:
                player_total, dealer_up, usable_ace, _ = state
                optimal = self.basic_strategy.get_action(
                    int(player_total), int(dealer_up), bool(usable_ace)
                )
                basic_actions.append(optimal)
        
        # Calculate agreement rate for this episode
        if basic_actions and len(basic_actions) == len(self.episode_actions):
            agreements = sum(1 for a, b in zip(self.episode_actions, basic_actions) if a == b)
            agreement_rate = agreements / len(basic_actions)
            
            # Bonus for high agreement
            if agreement_rate >= 0.8:
                return 0.05 * self.shaping_weight
            elif agreement_rate <= 0.5:
                return -0.02 * self.shaping_weight
        
        return 0.0


class AdvancedDQNNetwork(nn.Module):
    """Enhanced DQN network architecture."""
    
    def __init__(self, observation_space, action_space, net_arch=[512, 256, 128]):
        super().__init__()
        
        # Input layer
        input_dim = observation_space.shape[0]
        
        # Build layers dynamically
        layers = []
        prev_dim = input_dim
        
        for layer_size in net_arch:
            layers.extend([
                nn.Linear(prev_dim, layer_size),
                nn.ReLU(),
                nn.Dropout(0.1),  # Regularization
            ])
            prev_dim = layer_size
        
        # Output layer
        layers.append(nn.Linear(prev_dim, action_space.n))
        
        self.network = nn.Sequential(*layers)
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Initialize network weights."""
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            nn.init.constant_(module.bias, 0)
    
    def forward(self, x):
        return self.network(x)


def enhanced_linear_schedule(initial: float, final: float, warmup_steps: int = 50000) -> Callable[[float], float]:
    """Enhanced learning rate schedule with warmup."""
    
    def _schedule(progress: float) -> float:
        # Convert progress (1.0 -> 0.0) to step-based
        total_steps = 1.0 / max(progress, 1e-8)  # Avoid division by zero
        current_step = (1.0 - progress) * total_steps
        
        if current_step < warmup_steps:
            # Warmup phase
            warmup_factor = current_step / warmup_steps
            return initial * warmup_factor
        else:
            # Regular schedule
            return final + (initial - final) * progress
    
    return _schedule


class PerformanceMonitorCallback(BaseCallback):
    """Monitor training performance and log metrics."""
    
    def __init__(self, eval_freq: int = 10000, verbose: int = 0):
        super().__init__(verbose)
        self.eval_freq = eval_freq
        self.best_mean_reward = -np.inf
        
    def _on_step(self) -> bool:
        if self.n_calls % self.eval_freq == 0:
            # Log training metrics
            if hasattr(self.model, 'logger') and len(self.model.ep_info_buffer) > 0:
                mean_reward = np.mean([ep_info['r'] for ep_info in self.model.ep_info_buffer])
                self.logger.record('train/mean_episode_reward', mean_reward)
                
                if mean_reward > self.best_mean_reward:
                    self.best_mean_reward = mean_reward
                    self.logger.record('train/best_mean_reward', self.best_mean_reward)
        
        return True


def create_enhanced_env(seed: int = None, shaping_weight: float = 0.1):
    """Create environment with reward shaping."""
    base_env = BlackjackEnv(seed=seed)
    basic_strategy = BasicStrategy()
    shaped_env = RewardShapingWrapper(base_env, basic_strategy, shaping_weight)
    return Monitor(shaped_env)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enhanced DQN Training for Blackjack")
    parser.add_argument("--total-steps", type=int, default=10_000_000, help="Total training steps")
    parser.add_argument("--n-envs", type=int, default=8, help="Number of parallel environments")
    parser.add_argument("--log-dir", type=str, default="runs/enhanced_training", help="Log directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--shaping-weight", type=float, default=0.1, help="Reward shaping weight")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Initial learning rate")
    parser.add_argument("--architecture", type=str, default="512,256,128", help="Network architecture")
    return parser.parse_args()


def main():
    """Enhanced training main function."""
    args = parse_args()
    set_random_seed(args.seed)
    
    # Parse architecture
    net_arch = [int(x) for x in args.architecture.split(',')]
    
    # Setup directories
    log_root = Path(args.log_dir)
    model_dir = log_root / "models"
    tb_log = log_root / "tb"
    
    for dir_path in [model_dir, tb_log]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Starting enhanced training with {args.total_steps:,} steps")
    print(f"📊 Architecture: {net_arch}")
    print(f"🎯 Reward shaping weight: {args.shaping_weight}")
    
    # Initialize W&B
    wandb_run = init_wandb(
        project="blackjack_enhanced",
        name="enhanced-dqn-agent",
        config={
            "total_timesteps": args.total_steps,
            "architecture": net_arch,
            "shaping_weight": args.shaping_weight,
            "learning_rate": args.learning_rate,
            "seed": args.seed,
        }
    )
    
    # Create vectorized environments
    vec_env = make_vec_env(
        lambda: create_enhanced_env(seed=args.seed, shaping_weight=args.shaping_weight),
        n_envs=args.n_envs,
        seed=args.seed
    )
    vec_env = VecMonitor(vec_env)
    
    # Evaluation environment
    eval_env = VecMonitor(
        make_vec_env(
            lambda: create_enhanced_env(seed=args.seed + 1000, shaping_weight=0.0),  # No shaping in eval
            n_envs=1
        )
    )
    
    # Enhanced DQN configuration
    policy_kwargs = dict(
        net_arch=net_arch,
        activation_fn=th.nn.ReLU,
    )
    
    model = DQN(
        "MlpPolicy",
        vec_env,
        learning_rate=enhanced_linear_schedule(args.learning_rate, args.learning_rate * 0.1),
        exploration_fraction=0.4,  # Longer exploration
        exploration_final_eps=0.02,  # Lower final epsilon
        exploration_initial_eps=1.0,
        buffer_size=200_000,  # Larger buffer
        batch_size=512,  # Larger batch
        target_update_interval=5_000,  # More frequent updates
        gamma=0.995,  # Higher discount factor
        train_freq=8,  # More frequent training
        gradient_steps=2,  # Multiple gradient steps
        policy_kwargs=policy_kwargs,
        tensorboard_log=None,  # Disable tensorboard to avoid dependency issues
        seed=args.seed,
        verbose=1,
        device="auto",
    )
    
    # Enhanced callbacks
    callbacks = [
        SaveBestModelCallback(
            eval_env=eval_env,
            eval_freq=25_000,
            n_eval_episodes=1000,
            save_path=model_dir,
            deterministic=True,
            verbose=1,
        ),
        PerformanceMonitorCallback(eval_freq=10_000, verbose=1)
    ]
    
    # Train model
    print(f"🎓 Starting training...")
    model.learn(
        total_timesteps=args.total_steps,
        callback=callbacks,
        progress_bar=True,
    )
    
    # Save final model
    final_path = model_dir / "enhanced_final_model"
    model.save(final_path)
    print(f"💾 Enhanced model saved to {final_path}.zip")
    
    # Cleanup
    vec_env.close()
    eval_env.close()
    if wandb_run:
        wandb_run.finish()
    
    print("✅ Enhanced training completed!")


if __name__ == "__main__":
    main() 
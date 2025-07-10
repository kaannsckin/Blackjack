#!/usr/bin/env python3
"""
Hyperparameter Optimization for Blackjack RL (FAZ 1 – F1.3)

Uses Optuna for automated hyperparameter tuning.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import os
from pathlib import Path
from typing import Any, Dict, Type

import numpy as np
import optuna
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor
from stable_baselines3.common.utils import set_random_seed
from torch.nn import functional as F

# Local utilities
from utils.callbacks import SaveBestModelCallback
from utils.tracking import init_wandb


# ---------------------------------------------------------------------------- #
def _load_env_class() -> Type:
    env_mod = importlib.import_module("rl_environment")
    for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
        if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
            return getattr(env_mod, cls_name)  # type: ignore[return-value]
    raise RuntimeError("Environment class not found in rl_environment.py")


# ---------------------------------------------------------------------------- #
def create_objective(trial: optuna.Trial) -> callable:
    """Create objective function for Optuna optimization."""
    
    def objective(trial: optuna.Trial) -> float:
        # Hyperparameters to optimize
        learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-3, log=True)
        exploration_fraction = trial.suggest_float("exploration_fraction", 0.05, 0.15)
        exploration_final_eps = trial.suggest_float("exploration_final_eps", 0.01, 0.05)
        buffer_size = trial.suggest_categorical("buffer_size", [50_000, 100_000, 200_000])
        batch_size = trial.suggest_categorical("batch_size", [512, 1024, 2048, 4096])
        train_freq = trial.suggest_categorical("train_freq", [16, 32, 64])
        gradient_steps = trial.suggest_categorical("gradient_steps", [16, 32, 64])
        
        # Network architecture
        net_arch = trial.suggest_categorical("net_arch", [
            [128, 128],
            [256, 256], 
            [512, 512],
            [256, 256, 256],
            [512, 256, 128],
        ])
        
        # Environment parameters
        n_envs = trial.suggest_categorical("n_envs", [4, 8, 16])
        total_steps = trial.suggest_categorical("total_steps", [100_000, 500_000, 1_000_000])
        
        # Create environment
        EnvCls = _load_env_class()
        
        def env_fn(**kw: Any):
            return Monitor(EnvCls(**kw))
        
        vec_env = make_vec_env(
            env_id=env_fn,
            n_envs=n_envs,
            seed=42,
        )
        vec_env = VecMonitor(vec_env)
        
        # Create model
        model = DQN(
            "MlpPolicy",
            vec_env,
            learning_rate=learning_rate,
            exploration_fraction=exploration_fraction,
            exploration_final_eps=exploration_final_eps,
            buffer_size=buffer_size,
            batch_size=batch_size,
            train_freq=train_freq,
            gradient_steps=gradient_steps,
            gamma=1.0,
            policy_kwargs=dict(
                net_arch=net_arch,
                activation_fn=F.relu,
            ),
            verbose=0,
            seed=42,
        )
        
        # Train model
        model.learn(total_timesteps=total_steps, progress_bar=False)
        
        # Evaluate model
        eval_env = Monitor(EnvCls())
        eval_env = VecMonitor(make_vec_env(lambda: eval_env, n_envs=1))
        
        # Run evaluation
        n_eval_episodes = 1000
        eval_rewards = []
        
        for _ in range(n_eval_episodes):
            obs = eval_env.reset()
            episode_reward = 0
            done = False
            
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, _ = eval_env.step(action)
                episode_reward += reward[0] if hasattr(reward, '__len__') else reward
                
                if done:
                    eval_rewards.append(episode_reward)
                    obs = eval_env.reset()
        
        # Calculate mean reward
        mean_reward = np.mean(eval_rewards)
        
        # Clean up
        vec_env.close()
        eval_env.close()
        
        return mean_reward
    
    return objective


# ---------------------------------------------------------------------------- #
def optimize_hyperparameters(
    n_trials: int = 50,
    study_name: str = "blackjack_dqn_optimization",
    storage: str = "sqlite:///optuna_study.db",
) -> None:
    """Run hyperparameter optimization."""
    
    # Create study
    study = optuna.create_study(
        direction="maximize",
        study_name=study_name,
        storage=storage,
        load_if_exists=True,
    )
    
    # Create objective
    objective = create_objective(study)
    
    # Run optimization
    print(f"Starting optimization with {n_trials} trials...")
    study.optimize(objective, n_trials=n_trials)
    
    # Print results
    print("\n" + "="*60)
    print("OPTIMIZATION RESULTS")
    print("="*60)
    print(f"Best trial: {study.best_trial.number}")
    print(f"Best value: {study.best_trial.value:.4f}")
    print(f"Best params: {study.best_trial.params}")
    
    # Save results
    results_dir = Path("optimization_results")
    results_dir.mkdir(exist_ok=True)
    
    # Save best parameters
    best_params = study.best_trial.params
    with open(results_dir / "best_params.txt", "w") as f:
        for key, value in best_params.items():
            f.write(f"{key}: {value}\n")
    
    # Save study
    import joblib
    joblib.dump(study, results_dir / "study.pkl")
    
    print(f"\nResults saved to {results_dir}")
    
    return study


# ---------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Hyperparameter optimization for Blackjack RL")
    p.add_argument("--n-trials", type=int, default=50, help="Number of optimization trials")
    p.add_argument("--study-name", type=str, default="blackjack_dqn_optimization", help="Study name")
    p.add_argument("--storage", type=str, default="sqlite:///optuna_study.db", help="Storage URL")
    return p.parse_args()


# ---------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()
    
    # Run optimization
    study = optimize_hyperparameters(
        n_trials=args.n_trials,
        study_name=args.study_name,
        storage=args.storage,
    )
    
    # Optional: Train best model
    print("\nTraining best model...")
    best_params = study.best_trial.params
    
    # Create environment with best params
    EnvCls = _load_env_class()
    
    def env_fn(**kw: Any):
        return Monitor(EnvCls(**kw))
    
    vec_env = make_vec_env(
        env_id=env_fn,
        n_envs=best_params["n_envs"],
        seed=42,
    )
    vec_env = VecMonitor(vec_env)
    
    # Create best model
    model = DQN(
        "MlpPolicy",
        vec_env,
        learning_rate=best_params["learning_rate"],
        exploration_fraction=best_params["exploration_fraction"],
        exploration_final_eps=best_params["exploration_final_eps"],
        buffer_size=best_params["buffer_size"],
        batch_size=best_params["batch_size"],
        train_freq=best_params["train_freq"],
        gradient_steps=best_params["gradient_steps"],
        gamma=1.0,
        policy_kwargs=dict(
            net_arch=best_params["net_arch"],
            activation_fn=F.relu,
        ),
        verbose=1,
        seed=42,
    )
    
    # Train best model
    model.learn(total_timesteps=5_000_000, progress_bar=True)
    
    # Save best model
    model_path = Path("optimization_results/best_model")
    model.save(model_path)
    print(f"Best model saved to {model_path}.zip")
    
    vec_env.close()


# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    main() 
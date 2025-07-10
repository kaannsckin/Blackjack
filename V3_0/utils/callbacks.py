"""Custom callbacks for RL training (FAZ 1 – F1.3)"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import VecEnv


class SaveBestModelCallback(BaseCallback):
    """Saves the best model based on evaluation performance."""
    
    def __init__(
        self,
        eval_env: VecEnv,
        eval_freq: int = 50_000,
        n_eval_episodes: int = 500,
        save_path: str | Path = "models",
        deterministic: bool = True,
        verbose: int = 1,
    ):
        super().__init__(verbose)
        self.eval_env = eval_env
        self.eval_freq = eval_freq
        self.n_eval_episodes = n_eval_episodes
        self.save_path = Path(save_path)
        self.deterministic = deterministic
        self.best_mean_reward = -np.inf
        
        # Create save directory
        self.save_path.mkdir(parents=True, exist_ok=True)
    
    def _on_step(self) -> bool:
        if self.n_calls % self.eval_freq == 0:
            # Evaluate the model
            mean_reward = self._evaluate_model()
            
            if self.verbose > 0:
                print(f"Eval mean reward: {mean_reward:.3f}")
            
            # Save if better
            if mean_reward > self.best_mean_reward:
                self.best_mean_reward = mean_reward
                model_path = self.save_path / "best_model"
                self.model.save(model_path)
                if self.verbose > 0:
                    print(f"New best model saved! Mean reward: {mean_reward:.3f}")
        
        return True
    
    def _evaluate_model(self) -> float:
        """Evaluate the model and return mean reward."""
        obs = self.eval_env.reset()
        episode_rewards = []
        episode_reward = 0
        
        for _ in range(self.n_eval_episodes):
            done = False
            while not done:
                action, _ = self.model.predict(obs, deterministic=self.deterministic)
                obs, reward, done, _ = self.eval_env.step(action)
                episode_reward += reward[0] if hasattr(reward, '__len__') else reward
                
                if done:
                    episode_rewards.append(episode_reward)
                    episode_reward = 0
                    obs = self.eval_env.reset()
        
        return np.mean(episode_rewards) 
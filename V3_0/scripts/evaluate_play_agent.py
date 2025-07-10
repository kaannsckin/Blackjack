#!/usr/bin/env python3
"""
Evaluate trained play-agent against basic strategy (FAZ 1 – F1.3).

Usage
-----
$ python scripts/evaluate_play_agent.py \
    --model-path runs/phase1/models/best_model \
    --n-episodes 10_000
"""

from __future__ import annotations

import argparse
import importlib
import inspect
from pathlib import Path
from typing import Any, Dict, List, Type

import numpy as np
import pandas as pd
from stable_baselines3 import DQN

# Local utilities
from utils.tracking import init_wandb
from utils.basic_strategy import BasicStrategy
from utils.performance_metrics import PerformanceAnalyzer


# ---------------------------------------------------------------------------- #
def _load_env_class() -> Type:
    env_mod = importlib.import_module("rl_environment")
    for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
        if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
            return getattr(env_mod, cls_name)  # type: ignore[return-value]
    raise RuntimeError("Environment class not found in rl_environment.py")


# ---------------------------------------------------------------------------- #
def basic_strategy_action(player_total: int, dealer_up: int, usable_ace: bool, is_pair: bool = False) -> int:
    """Comprehensive basic strategy implementation for comparison."""
    strategy = BasicStrategy()
    
    # Check if it's a pair
    if is_pair and len([player_total]) == 2:  # Simplified pair check
        return strategy.get_action(player_total, dealer_up, usable_ace, is_pair=True)
    
    return strategy.get_action(player_total, dealer_up, usable_ace)


# ---------------------------------------------------------------------------- #
def evaluate_model(model: DQN, env_class: Type, n_episodes: int = 10_000) -> Dict[str, Any]:
    """Evaluate model performance."""
    env = env_class()
    
    # Model evaluation
    model_rewards = []
    model_actions = []
    
    for _ in range(n_episodes):
        obs, _ = env.reset()
        episode_reward = 0
        episode_actions = []
        
        while True:
            action, _ = model.predict(obs, deterministic=True)
            episode_actions.append(action)
            obs, reward, done, _, _ = env.step(action)
            episode_reward += reward
            
            if done:
                break
        
        model_rewards.append(episode_reward)
        model_actions.extend(episode_actions)
    
    # Basic strategy evaluation
    basic_rewards = []
    basic_actions = []
    
    for _ in range(n_episodes):
        obs, _ = env.reset()
        episode_reward = 0
        episode_actions = []
        
        while True:
            player_total, dealer_up, usable_ace, _ = obs
            action = basic_strategy_action(player_total, dealer_up, bool(usable_ace))
            episode_actions.append(action)
            obs, reward, done, _, _ = env.step(action)
            episode_reward += reward
            
            if done:
                break
        
        basic_rewards.append(episode_reward)
        basic_actions.extend(episode_actions)
    
    # Calculate detailed metrics
    analyzer = PerformanceAnalyzer()
    model_metrics = analyzer.calculate_metrics(model_rewards)
    basic_metrics = analyzer.calculate_metrics(basic_rewards)
    
    return {
        "model_metrics": model_metrics,
        "basic_metrics": basic_metrics,
        "model_rewards": model_rewards,
        "basic_rewards": basic_rewards,
        "model_actions": model_actions,
        "basic_actions": basic_actions,
    }


# ---------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate trained play-agent")
    p.add_argument("--model-path", type=str, required=True, help="Path to trained model")
    p.add_argument("--n-episodes", type=int, default=10_000, help="Number of evaluation episodes")
    p.add_argument("--log-to-wandb", action="store_true", help="Log results to W&B")
    return p.parse_args()


# ---------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()
    
    # Load model
    model_path = Path(args.model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    model = DQN.load(str(model_path))
    print(f"[Evaluator] Loaded model from {model_path}")
    
    # Load environment
    EnvCls = _load_env_class()
    
    # Evaluate
    print(f"[Evaluator] Running {args.n_episodes} evaluation episodes...")
    results = evaluate_model(model, EnvCls, args.n_episodes)
    
    # Print results
    print("\n" + "="*60)
    print("COMPREHENSIVE EVALUATION RESULTS")
    print("="*60)
    
    # Model results
    model_metrics = results['model_metrics']
    print(f"\n🤖 MODEL PERFORMANCE:")
    print(f"  Expected Value: {model_metrics.ev:.4f}")
    print(f"  RTP: {model_metrics.rtp:.2f}%")
    print(f"  Win Rate: {model_metrics.win_rate:.2f}%")
    print(f"  Volatility: {model_metrics.volatility:.4f}")
    print(f"  VaR (95%): {model_metrics.var_95:.4f}")
    print(f"  Total Hands: {model_metrics.total_hands:,}")
    
    # Basic strategy results
    basic_metrics = results['basic_metrics']
    print(f"\n📚 BASIC STRATEGY PERFORMANCE:")
    print(f"  Expected Value: {basic_metrics.ev:.4f}")
    print(f"  RTP: {basic_metrics.rtp:.2f}%")
    print(f"  Win Rate: {basic_metrics.win_rate:.2f}%")
    print(f"  Volatility: {basic_metrics.volatility:.4f}")
    print(f"  VaR (95%): {basic_metrics.var_95:.4f}")
    print(f"  Total Hands: {basic_metrics.total_hands:,}")
    
    # Comparison
    ev_improvement = model_metrics.ev - basic_metrics.ev
    rtp_improvement = model_metrics.rtp - basic_metrics.rtp
    win_rate_improvement = model_metrics.win_rate - basic_metrics.win_rate
    
    print(f"\n📊 COMPARISON:")
    print(f"  EV Improvement: {ev_improvement:.4f}")
    print(f"  RTP Improvement: {rtp_improvement:.2f}%")
    print(f"  Win Rate Improvement: {win_rate_improvement:.2f}%")
    
    # Risk analysis
    analyzer = PerformanceAnalyzer()
    model_edge = analyzer.calculate_edge(model_metrics.ev)
    basic_edge = analyzer.calculate_edge(basic_metrics.ev)
    
    print(f"\n🎯 EDGE ANALYSIS:")
    print(f"  Model Edge: {model_edge:.2f}%")
    print(f"  Basic Strategy Edge: {basic_edge:.2f}%")
    print(f"  Edge Improvement: {model_edge - basic_edge:.2f}%")
    
    # Log to W&B if requested
    if args.log_to_wandb:
        wandb_run = init_wandb(
            project="blackjack_phase1",
            name="evaluation",
            config={
                "model_path": str(model_path),
                "n_episodes": args.n_episodes,
            },
        )
        
        if wandb_run is not None:
            wandb_run.log({
                "eval/model_ev": model_metrics.ev,
                "eval/model_rtp": model_metrics.rtp,
                "eval/model_win_rate": model_metrics.win_rate,
                "eval/model_volatility": model_metrics.volatility,
                "eval/basic_ev": basic_metrics.ev,
                "eval/basic_rtp": basic_metrics.rtp,
                "eval/basic_win_rate": basic_metrics.win_rate,
                "eval/basic_volatility": basic_metrics.volatility,
                "eval/ev_improvement": ev_improvement,
                "eval/rtp_improvement": rtp_improvement,
                "eval/win_rate_improvement": win_rate_improvement,
                "eval/edge_improvement": model_edge - basic_edge,
            })
            wandb_run.finish()


# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Train a DQN “play-agent” for Blackjack (FAZ 1 – F1.3).

Usage
-----
$ python scripts/train_play_agent.py \
    --total-steps 5_000_000 --log-dir runs/phase1

Hyper-params, ε-greedy ve LR çizelgesi SabitDeğil™: kolayca CLI’dan güncellenebilir.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import os
from pathlib import Path
from typing import Any, Callable, Type

import torch as th
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import VecFrameStack
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor
from stable_baselines3.common.utils import set_random_seed
from torch.nn import functional as F  # noqa: N812

# Local utilities
from utils.callbacks import SaveBestModelCallback
from utils.tracking import init_wandb, get_tb_writer


# ---------------------------------------------------------------------------- #
def linear_schedule(initial: float, final: float) -> Callable[[float], float]:
    """
    SB3 ile uyumlu lineer çizelge (training progress→ param).

    progress = 1.0 ⇒ başlangıç, progress → 0.0 ⇒ eğitim sonu.
    """

    def _schedule(progress: float) -> float:  # noqa: D401
        return final + (initial - final) * progress

    return _schedule


# ---------------------------------------------------------------------------- #
def _load_env_class() -> Type:
    env_mod = importlib.import_module("rl_environment")
    for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
        if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
            return getattr(env_mod, cls_name)  # type: ignore[return-value]
    raise RuntimeError("Environment class not found in rl_environment.py")


# ---------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Blackjack DQN trainer – FAZ 1")
    p.add_argument("--total-steps", type=int, default=5_000_000, help="Eğitim adım sayısı")
    p.add_argument("--n-envs", type=int, default=8, help="Parallel env count")
    p.add_argument("--log-dir", type=str, default="runs/phase1", help="TensorBoard/W&B log root")
    p.add_argument("--seed", type=int, default=42, help="Global RNG seed")
    return p.parse_args()


# ---------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()
    set_random_seed(args.seed)

    # --------------------------------------------------------------------- #
    # Logs & tracking
    log_root = Path(args.log_dir)
    tb_log = log_root / "tb"
    model_dir = log_root / "models"
    tb_log.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    # Validate environment
    try:
        EnvCls = _load_env_class()
        print(f"[Trainer] Loaded environment class: {EnvCls.__name__}")
    except Exception as e:
        print(f"[Trainer] Error loading environment: {e}")
        return

    wandb_run = init_wandb(
        project="blackjack_phase1",
        name="dqn-play-agent",
        config={
            "total_timesteps": args.total_steps,
            "algo": "DQN",
            "vec_envs": args.n_envs,
            "seed": args.seed,
        },
    )

    # --------------------------------------------------------------------- #
    # Env factory
    def env_fn(**kw: Any):
        return Monitor(EnvCls(**kw))

    # Vectorize env
    vec_env = make_vec_env(
        env_id=env_fn,  # callable
        n_envs=args.n_envs,
        vec_env_cls=None,
        vec_env_kwargs=None,
        seed=args.seed,
    )
    vec_env = VecMonitor(vec_env)  # episode reward/len logging

    # Optional frame stack (not strictly needed for tabular observation)
    # vec_env = VecFrameStack(vec_env, n_stack=1)

    # Separate eval env
    eval_env = Monitor(EnvCls())
    eval_env = VecMonitor(make_vec_env(lambda: eval_env, n_envs=1))

    # --------------------------------------------------------------------- #
    # DQN hyper-parameters
    policy_kwargs = dict(
        net_arch=[256, 256],
        activation_fn=F.relu,
    )

    model = DQN(
        "MlpPolicy",
        vec_env,
        learning_rate=linear_schedule(2.5e-4, 5e-5),
        exploration_fraction=0.08,  # ε lineer çizelge için
        exploration_final_eps=0.02,
        exploration_initial_eps=1.0,
        buffer_size=100_000,
        batch_size=2048,
        target_update_interval=10_000 // args.n_envs,
        gamma=1.0,  # blackjack ödül yapısı gereği
        train_freq=32,
        gradient_steps=32,
        policy_kwargs=policy_kwargs,
        tensorboard_log=str(tb_log),
        seed=args.seed,
        verbose=1,
        device="auto",
    )

    # --------------------------------------------------------------------- #
    # Callbacks
    best_callback = SaveBestModelCallback(
        eval_env=eval_env,
        eval_freq=50_000,
        n_eval_episodes=500,
        save_path=model_dir,
        deterministic=True,
        verbose=1,
    )

    # --------------------------------------------------------------------- #
    # Train
    model.learn(
        total_timesteps=args.total_steps,
        callback=[best_callback],
        progress_bar=True,
    )

    # Save final model
    final_path = model_dir / "final_model"
    model.save(final_path)
    print(f"[Trainer] Final model saved to {final_path}.zip")

    # Close envs & finish W&B
    vec_env.close()
    eval_env.close()
    if wandb_run is not None:
        wandb_run.finish()


# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Optuna-tabanlı hiper-parametre araması (FAZ 1 – F1.6).

* Öğrenme hızı, buffer_size, exploration_fraction, net_arch boyutu, γ dâhil.
* Her deneme sonunda 300 bölümlük mean-reward hesaplanır (maximize edilir).
* En iyi deneme:
    • `best_params.json`
    • `best_model.zip`
* W&B & TensorBoard logu opsiyoneldir.
"""

from __future__ import annotations

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import json
import os
import pathlib
import time
from typing import Any, Dict, List, Tuple, Type

import numpy as np
import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler
from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor
from stable_baselines3.common.callbacks import EvalCallback
try:
    from optuna.integration import TrialPruningCallback
except ImportError:
    TrialPruningCallback = None  # Eski Optuna sürümü için

# yerel modüller
from utils.callbacks import SaveBestModelCallback
from utils.tracking import init_wandb
import importlib
import inspect


# --------------------------------------------------------------------------- #
def _load_env_class() -> Type:
    env_mod = importlib.import_module("rl_environment")
    for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
        if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
            return getattr(env_mod, cls_name)  # type: ignore[return-value]
    raise RuntimeError("Environment class not found in rl_environment.py")


# --------------------------------------------------------------------------- #
def make_env(seed: int = 0):
    EnvCls = _load_env_class()
    def _f():
        env = EnvCls()  # type: ignore[call-arg]
        return Monitor(env)
    return VecMonitor(DummyVecEnv([_f]), filename=None)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
def suggest_params(trial: optuna.Trial) -> Dict[str, Any]:
    """Hiper-parametre aralığını tanımlar."""
    return {
        "learning_rate": trial.suggest_loguniform("lr", 1e-5, 5e-4),
        "buffer_size": trial.suggest_int("buffer_size", 50_000, 500_000, log=True),
        "exploration_fraction": trial.suggest_float("eps_frac", 0.02, 0.2),
        "exploration_final_eps": trial.suggest_float("eps_final", 0.01, 0.05),
        "gamma": trial.suggest_float("gamma", 0.95, 1.00),
        "batch_size": trial.suggest_categorical("batch_size", [512, 1024, 2048]),
        "net_arch": [trial.suggest_categorical("layer1", [128, 256, 512]),
                     trial.suggest_categorical("layer2", [128, 256, 512])],
    }


# --------------------------------------------------------------------------- #
def objective(trial: optuna.Trial, total_steps: int, eval_episodes: int, seed: int) -> float:
    params = suggest_params(trial)
    set_random_seed(seed)

    env = make_env(seed)
    eval_env = make_env(seed + 10)

    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=params["learning_rate"],
        buffer_size=params["buffer_size"],
        exploration_fraction=params["exploration_fraction"],
        exploration_final_eps=params["exploration_final_eps"],
        batch_size=params["batch_size"],
        gamma=params["gamma"],
        policy_kwargs=dict(net_arch=params["net_arch"]),
        verbose=0,
        seed=seed,
        device="auto",
    )

    # erken durdurma için pruner
    eval_callback = EvalCallback(
        eval_env,
        n_eval_episodes=100,
        eval_freq=25_000,
        deterministic=True,
        verbose=0,
    )
    callbacks = [eval_callback]
    if TrialPruningCallback is not None:
        callbacks.append(TrialPruningCallback(trial, eval_callback))
    model.learn(total_timesteps=total_steps, callback=callbacks, progress_bar=False)

    mean_reward, _ = evaluate_policy(
        model, eval_env, n_eval_episodes=eval_episodes, deterministic=True, progress_bar=False
    )

    env.close()
    eval_env.close()

    return mean_reward  # maximize


# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Optuna HPO – Blackjack DQN")
    p.add_argument("--n-trials", type=int, default=20)
    p.add_argument("--total-steps", type=int, default=250_000)
    p.add_argument("--eval-episodes", type=int, default=300)
    p.add_argument("--study-name", type=str, default="bj_dqn_hpo")
    p.add_argument("--storage", type=str, default=None, help="Optuna storage URI (ör. sqlite:///hpo.db)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-dir", type=str, default="runs/hpo")
    return p.parse_args()


# --------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # W&B
    wandb_run = init_wandb(
        project="blackjack_phase1",
        name="hpo",
        config=vars(args),
    )

    sampler = TPESampler(seed=args.seed)
    pruner = MedianPruner(n_startup_trials=5, n_warmup_steps=3)

    study = optuna.create_study(
        study_name=args.study_name,
        direction="maximize",
        sampler=sampler,
        pruner=pruner,
        storage=args.storage,
        load_if_exists=True,
    )

    study.optimize(
        lambda tr: objective(tr, args.total_steps, args.eval_episodes, args.seed),
        n_trials=args.n_trials,
        show_progress_bar=True,
    )

    best_params = study.best_params
    best_value = study.best_value
    print(f"[HPO] Best mean-reward={best_value:.4f}\n{best_params}")

    # ---- en iyi parametrelerle tam eğitim & model kaydet ------------------
    env = make_env(args.seed)
    model = DQN(
        "MlpPolicy",
        env,
        **{
            "learning_rate": best_params["lr"],
            "buffer_size": best_params["buffer_size"],
            "exploration_fraction": best_params["eps_frac"],
            "exploration_final_eps": best_params["eps_final"],
            "gamma": best_params["gamma"],
            "batch_size": best_params["batch_size"],
            "policy_kwargs": dict(net_arch=[best_params["layer1"], best_params["layer2"]]),
        },
        verbose=1,
        seed=args.seed,
        device="auto",
        tensorboard_log=str(out_dir / "tb"),
    )

    # en iyi modeli kaydet
    best_callback = SaveBestModelCallback(
        eval_env=make_env(args.seed + 1),
        eval_freq=50_000,
        n_eval_episodes=args.eval_episodes,
        save_path=out_dir / "models",
        deterministic=True,
        verbose=1,
    )

    model.learn(total_timesteps=args.total_steps * 2, callback=[best_callback], progress_bar=True)
    final_path = out_dir / "models" / "hpo_final_model"
    model.save(final_path)
    print(f"[HPO] Final model saved → {final_path}.zip")

    # çıktı dosyaları
    with (out_dir / "best_params.json").open("w", encoding="utf-8") as f:
        json.dump(best_params, f, indent=2)

    if wandb_run is not None:
        wandb_run.log({"best_reward": best_value, **best_params})
        wandb_run.finish()


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main() 
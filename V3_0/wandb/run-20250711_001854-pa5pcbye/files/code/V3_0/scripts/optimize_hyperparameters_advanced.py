#!/usr/bin/env python3
"""
Gelişmiş Optuna-tabanlı hiper-parametre araması (FAZ 1 – F1.6).

Özellikler:
- Hatalı denemeler trial.fail() ile işaretlenir
- Multi-seed ortalaması opsiyonel
- En iyi 5 deneme ve tüm denemeler kaydedilir
- W&B ve TensorBoard logu
- CLI ve YAML config desteği
- Exception handling ve logging
- Grid/Random/TPE sampler seçenekleri
"""

from __future__ import annotations

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import json
import logging
import os
import pathlib
import time
import yaml
from typing import Any, Dict, List, Tuple, Type

import numpy as np
import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler, RandomSampler, GridSampler
from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor
from stable_baselines3.common.callbacks import EvalCallback, BaseCallback

# yerel modüller
from utils.callbacks import SaveBestModelCallback
from utils.tracking import init_wandb
import importlib
import inspect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    """Hiper-parametre aralığını tanımlar (gelişmiş versiyon)."""
    # Net_arch as tuple for flexibility
    n_layers = trial.suggest_int("n_layers", 2, 3)
    net_arch = [trial.suggest_categorical(f"layer{i+1}", [128, 256, 512]) for i in range(n_layers)]
    
    return {
        "learning_rate": trial.suggest_loguniform("lr", 1e-5, 5e-4),
        "buffer_size": trial.suggest_int("buffer_size", 50_000, 500_000, log=True),
        "exploration_fraction": trial.suggest_float("eps_frac", 0.02, 0.2),
        "exploration_final_eps": trial.suggest_float("eps_final", 0.01, 0.05),
        "gamma": trial.suggest_float("gamma", 0.95, 1.00),
        "batch_size": trial.suggest_categorical("batch_size", [512, 1024, 2048]),
        "net_arch": net_arch,
        "n_layers": n_layers,
    }


# --------------------------------------------------------------------------- #
def objective(trial: optuna.Trial, total_steps: int, eval_episodes: int, seed: int, multi_seed: int = 1) -> float:
    """Objective function with multi-seed support and error handling."""
    params = suggest_params(trial)
    rewards = []
    
    for s in range(multi_seed):
        try:
            current_seed = seed + s
            set_random_seed(current_seed)
            env = make_env(current_seed)
            eval_env = make_env(current_seed + 100)
            
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
                seed=current_seed,
                device="auto",
            )

            # erken durdurma için pruner
            eval_callback = EvalCallback(
                eval_env,
                n_eval_episodes=20,
                eval_freq=10_000,
                deterministic=True,
                verbose=0,
            )
            
            # Custom callback for Optuna integration
            class OptunaCallback(BaseCallback):
                def __init__(self, trial, eval_callback):
                    super().__init__()
                    self.trial = trial
                    self.eval_callback = eval_callback
                    
                def _on_step(self):
                    if self.eval_callback.n_calls > 0 and self.eval_callback.best_mean_reward is not None:
                        # Report to Optuna for pruning
                        self.trial.report(self.eval_callback.best_mean_reward, step=self.eval_callback.n_calls)
                        # Prune if needed
                        if self.trial.should_prune():
                            raise optuna.TrialPruned()
                    return True
            
            optuna_callback = OptunaCallback(trial, eval_callback)
            callbacks = [eval_callback, optuna_callback]
            model.learn(total_timesteps=total_steps, callback=callbacks, progress_bar=False)

            mean_reward, _ = evaluate_policy(
                model, eval_env, n_eval_episodes=eval_episodes, deterministic=True
            )
            
            rewards.append(mean_reward)
            env.close()
            eval_env.close()
            
            logger.debug(f"Trial {trial.number}, Seed {s}: reward = {mean_reward:.4f}")
            
        except Exception as e:
            logger.error(f"Trial {trial.number}, Seed {s} failed: {e}")
            trial.set_user_attr("fail_reason", str(e))
            raise optuna.TrialPruned(f"Trial failed: {e}")
    
    avg_reward = float(np.mean(rewards))
    logger.info(f"Trial {trial.number} completed: avg_reward = {avg_reward:.4f}")
    return avg_reward


# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Gelişmiş Optuna HPO – Blackjack DQN")
    p.add_argument("--n-trials", type=int, default=20)
    p.add_argument("--total-steps", type=int, default=250_000)
    p.add_argument("--eval-episodes", type=int, default=300)
    p.add_argument("--study-name", type=str, default="bj_dqn_hpo_advanced")
    p.add_argument("--storage", type=str, default=None, help="Optuna storage URI (ör. sqlite:///hpo.db)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--multi-seed", type=int, default=1, help="Number of seeds for averaging")
    p.add_argument("--out-dir", type=str, default="runs/hpo_advanced")
    p.add_argument("--config", type=str, default=None, help="YAML config path (opsiyonel)")
    p.add_argument("--sampler", type=str, default="tpe", choices=["tpe", "random", "grid"])
    p.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return p.parse_args()


# --------------------------------------------------------------------------- #
def create_sampler(sampler_type: str, seed: int, config: Dict = None) -> Any:
    """Create sampler based on type."""
    if sampler_type == "tpe":
        return TPESampler(seed=seed)
    elif sampler_type == "random":
        return RandomSampler(seed=seed)
    elif sampler_type == "grid":
        # Grid search requires predefined parameter combinations
        grid = config.get("hpo_grid", {}) if config else {}
        if not grid:
            logger.warning("Grid sampler requires grid config, falling back to TPE")
            return TPESampler(seed=seed)
        return GridSampler(grid)
    else:
        raise ValueError(f"Unknown sampler type: {sampler_type}")


# --------------------------------------------------------------------------- #
def save_trial_results(study: optuna.Study, out_dir: pathlib.Path) -> None:
    """Save detailed trial results."""
    # En iyi 5 deneme
    trials_sorted = sorted(study.trials, key=lambda t: t.value if t.value is not None else -np.inf, reverse=True)
    top5 = []
    
    for i, trial in enumerate(trials_sorted[:5]):
        trial_info = {
            "rank": i + 1,
            "trial_number": trial.number,
            "reward": trial.value,
            "params": trial.params,
            "duration": trial.duration.total_seconds() if trial.duration else None,
            "state": trial.state.name,
        }
        top5.append(trial_info)
    
    with (out_dir / "top5_trials.json").open("w", encoding="utf-8") as f:
        json.dump(top5, f, indent=2)
    
    # Tüm denemeler
    all_trials = []
    for trial in study.trials:
        trial_info = {
            "trial_number": trial.number,
            "reward": trial.value,
            "params": trial.params,
            "duration": trial.duration.total_seconds() if trial.duration else None,
            "state": trial.state.name,
            "user_attrs": trial.user_attrs,
        }
        all_trials.append(trial_info)
    
    with (out_dir / "all_trials.json").open("w", encoding="utf-8") as f:
        json.dump(all_trials, f, indent=2)
    
    logger.info(f"Saved {len(top5)} top trials and {len(all_trials)} total trials")


# --------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load YAML config if provided
    config = {}
    if args.config:
        try:
            with open(args.config, "r") as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded config from {args.config}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

    # W&B
    wandb_run = init_wandb(
        project="blackjack_phase1",
        name="hpo_advanced",
        config={**vars(args), **config},
    )

    # Create sampler
    sampler = create_sampler(args.sampler, args.seed, config)
    pruner = MedianPruner(n_startup_trials=5, n_warmup_steps=3)

    study = optuna.create_study(
        study_name=args.study_name,
        direction="maximize",
        sampler=sampler,
        pruner=pruner,
        storage=args.storage,
        load_if_exists=True,
    )

    def _objective(trial):
        try:
            return objective(trial, args.total_steps, args.eval_episodes, args.seed, args.multi_seed)
        except Exception as e:
            logger.error(f"Trial {trial.number} failed: {e}")
            raise optuna.TrialPruned(str(e))

    logger.info(f"Starting HPO with {args.n_trials} trials, {args.multi_seed} seeds each")
    study.optimize(
        _objective,
        n_trials=args.n_trials,
        show_progress_bar=True,
    )

    best_params = study.best_params
    best_value = study.best_value
    logger.info(f"[HPO] Best mean-reward={best_value:.4f}")
    logger.info(f"[HPO] Best params: {best_params}")

    # Save trial results
    save_trial_results(study, out_dir)

    # ---- en iyi parametrelerle tam eğitim & model kaydet ------------------
    logger.info("Training final model with best parameters...")
    env = make_env(args.seed)
    
    # Reconstruct net_arch from best params
    n_layers = best_params.get("n_layers", 2)
    net_arch = [best_params.get(f"layer{i+1}", 256) for i in range(n_layers)]
    
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
            "policy_kwargs": dict(net_arch=net_arch),
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
    logger.info(f"[HPO] Final model saved → {final_path}.zip")

    # çıktı dosyaları
    with (out_dir / "best_params.json").open("w", encoding="utf-8") as f:
        json.dump(best_params, f, indent=2)

    # Summary report
    summary = {
        "best_reward": best_value,
        "best_params": best_params,
        "total_trials": len(study.trials),
        "completed_trials": len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]),
        "pruned_trials": len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED]),
        "failed_trials": len([t for t in study.trials if t.state == optuna.trial.TrialState.FAIL]),
        "multi_seed": args.multi_seed,
        "sampler": args.sampler,
    }
    
    with (out_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"[HPO] Summary: {summary}")

    if wandb_run is not None:
        wandb_run.log({"best_reward": best_value, **best_params, **summary})
        wandb_run.finish()


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main() 
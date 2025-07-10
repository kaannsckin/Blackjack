#!/usr/bin/env python3
"""
Evaluate a trained play-agent against Basic Strategy (FAZ 1 – F1.4).

Ölçülen metrikler
-----------------
• EV (Expected Value)        • RTP (%)              • Win-rate (%)
• Volatility (σ)             • VaR-95               • Edge (player/house)
• Confidence Intervals       • Statistical Tests     • Action Distribution

Çıktılar
--------
1) Sonuç tablosu stdout + markdown
2) W&B/TensorBoard logları
3) `reports/phase_1_report.md`   →  Otomatik güncellenir
4) Statistical significance test
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type, Optional

import numpy as np
from scipy import stats
from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy
from tqdm import trange

import sys          
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Yerel modüller
from utils.basic_strategy import BasicStrategy
from utils.performance_metrics import PerformanceAnalyzer, PerformanceMetrics
from utils.tracking import init_wandb

# --------------------------------------------------------------------------- #
def _load_env_class() -> Type:
    env_mod = importlib.import_module("rl_environment")
    for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
        if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
            return getattr(env_mod, cls_name)  # type: ignore[return-value]
    raise RuntimeError("Environment class not found in rl_environment.py")


# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Blackjack agent evaluator – FAZ 1")
    p.add_argument("--model-path", type=str, required=True, help="*.zip model file")
    p.add_argument("--episodes", type=int, default=100_000, help="Evaluation episode count")
    p.add_argument("--seed", type=int, default=123, help="RNG seed")
    p.add_argument("--report", type=str, default="reports/phase_1_report.md", help="Markdown output")
    p.add_argument("--confidence-level", type=float, default=0.95, help="CI confidence level")
    p.add_argument("--log-to-wandb", action="store_true", help="Log results to W&B")
    return p.parse_args()


# --------------------------------------------------------------------------- #
def run_episode(env, agent, strategy: BasicStrategy, rng: np.random.Generator) -> Tuple[float, float, List[int], List[int]]:
    """
    Tek el oynatır: agent vs basic strategy.
    Agent ödülü, basic'in ödülünü ve action sequence'lerini return eder.
    """
    # Agent elini oynat
    episode_seed = int(rng.integers(1_000_000))
    obs, _info = env.reset(seed=episode_seed)
    done, trunc = False, False
    agent_reward = 0.0
    agent_actions = []
    
    while not (done or trunc):
        action, _state = agent.predict(obs, deterministic=True)
        agent_actions.append(action)
        obs, reward, done, trunc, _ = env.step(action)
        agent_reward += reward

    # Aynı başlangıç durumunu tekrar kur ve Basic Strategy oynat
    obs, _ = env.reset(seed=episode_seed)  # env.seed() aynı desteyi kullanır
    done, trunc = False, False
    basic_reward = 0.0
    basic_actions = []
    
    while not (done or trunc):
        player_total, dealer_up, usable_ace, _tc = obs             # type: ignore[misc]
        action = strategy.get_action(player_total, dealer_up, usable_ace)
        basic_actions.append(action)
        obs, reward, done, trunc, _ = env.step(action)
        basic_reward += reward

    return agent_reward, basic_reward, agent_actions, basic_actions


# --------------------------------------------------------------------------- #
def calculate_confidence_interval(data: List[float], confidence_level: float = 0.95) -> Tuple[float, float]:
    """Calculate confidence interval for mean."""
    if len(data) < 2:
        return (np.mean(data), np.mean(data))
    
    mean = np.mean(data)
    std_err = np.std(data, ddof=1) / np.sqrt(len(data))
    t_value = stats.t.ppf((1 + confidence_level) / 2, len(data) - 1)
    margin = t_value * std_err
    
    return (mean - margin, mean + margin)


# --------------------------------------------------------------------------- #
def calculate_edge(ev: float, bet_size: float = 1.0) -> float:
    """Calculate player edge (positive) or house edge (negative)."""
    return -ev / bet_size * 100


# --------------------------------------------------------------------------- #
def analyze_action_distribution(agent_actions: List[List[int]], basic_actions: List[List[int]]) -> Dict[str, Any]:
    """Analyze action distribution differences."""
    # Flatten action lists
    agent_flat = [action for episode in agent_actions for action in episode]
    basic_flat = [action for episode in basic_actions for action in episode]
    
    # Count actions
    action_names = ["stand", "hit", "double", "split"]
    agent_counts = np.bincount(agent_flat, minlength=4)
    basic_counts = np.bincount(basic_flat, minlength=4)
    
    # Calculate percentages
    agent_total = len(agent_flat)
    basic_total = len(basic_flat)
    
    agent_pcts = agent_counts / agent_total * 100 if agent_total > 0 else np.zeros(4)
    basic_pcts = basic_counts / basic_total * 100 if basic_total > 0 else np.zeros(4)
    
    return {
        "agent_distribution": {name: pct for name, pct in zip(action_names, agent_pcts)},
        "basic_distribution": {name: pct for name, pct in zip(action_names, basic_pcts)},
        "total_actions": {"agent": agent_total, "basic": basic_total}
    }


# --------------------------------------------------------------------------- #
def evaluate(model_path: Path, episodes: int, seed: int, confidence_level: float = 0.95) -> Dict[str, Any]:
    """Comprehensive evaluation with statistical analysis."""
    rng = np.random.default_rng(seed)
    EnvCls = _load_env_class()
    env = EnvCls()
    
    try:
        model = DQN.load(model_path, env=env, print_system_info=False)
    except Exception as e:
        raise RuntimeError(f"Failed to load model from {model_path}: {e}")

    strategy = BasicStrategy()
    agent_rewards: List[float] = []
    basic_rewards: List[float] = []
    agent_actions: List[List[int]] = []
    basic_actions: List[List[int]] = []

    print(f"Evaluating {episodes:,} episodes...")
    for _ in trange(episodes, desc="Evaluating"):
        a_r, b_r, a_actions, b_actions = run_episode(env, model, strategy, rng)
        agent_rewards.append(a_r)
        basic_rewards.append(b_r)
        agent_actions.append(a_actions)
        basic_actions.append(b_actions)

    env.close()
    
    # Calculate metrics
    analyzer = PerformanceAnalyzer()
    agent_metrics = analyzer.calculate_metrics(agent_rewards)
    basic_metrics = analyzer.calculate_metrics(basic_rewards)
    
    # Calculate confidence intervals
    agent_ci = calculate_confidence_interval(agent_rewards, confidence_level)
    basic_ci = calculate_confidence_interval(basic_rewards, confidence_level)
    
    # Calculate edges
    agent_edge = calculate_edge(agent_metrics.ev)
    basic_edge = calculate_edge(basic_metrics.ev)
    
    # Statistical significance test
    t_stat, p_value = stats.ttest_ind(agent_rewards, basic_rewards)
    
    # Action distribution analysis
    action_analysis = analyze_action_distribution(agent_actions, basic_actions)
    
    return {
        "agent": {
            "ev": agent_metrics.ev,
            "ev_ci": agent_ci,
            "rtp": agent_metrics.rtp,
            "win_rate": agent_metrics.win_rate,
            "volatility": agent_metrics.volatility,
            "var_95": agent_metrics.var_95,
            "edge": agent_edge,
            "total_hands": agent_metrics.total_hands,
        },
        "basic": {
            "ev": basic_metrics.ev,
            "ev_ci": basic_ci,
            "rtp": basic_metrics.rtp,
            "win_rate": basic_metrics.win_rate,
            "volatility": basic_metrics.volatility,
            "var_95": basic_metrics.var_95,
            "edge": basic_edge,
            "total_hands": basic_metrics.total_hands,
        },
        "statistical_test": {
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < 0.05,
        },
        "action_analysis": action_analysis,
        "improvement": {
            "ev_improvement": agent_metrics.ev - basic_metrics.ev,
            "rtp_improvement": agent_metrics.rtp - basic_metrics.rtp,
            "win_rate_improvement": agent_metrics.win_rate - basic_metrics.win_rate,
            "edge_improvement": agent_edge - basic_edge,
        }
    }


# --------------------------------------------------------------------------- #
def save_report(report_path: Path, metrics: Dict[str, Any]) -> None:
    """Save comprehensive evaluation report."""
    agent = metrics["agent"]
    basic = metrics["basic"]
    stats_test = metrics["statistical_test"]
    improvement = metrics["improvement"]
    action_analysis = metrics["action_analysis"]
    
    # Main metrics table
    tbl = (
        "| Metric | Play-Agent | Basic Strategy | Improvement |\n"
        "|--------|-----------:|---------------:|------------:|\n"
        f"| EV             | {agent['ev']:+.4f} | {basic['ev']:+.4f} | {improvement['ev_improvement']:+.4f} |\n"
        f"| EV (95% CI)    | {agent['ev_ci'][0]:+.4f} - {agent['ev_ci'][1]:+.4f} | {basic['ev_ci'][0]:+.4f} - {basic['ev_ci'][1]:+.4f} | - |\n"
        f"| RTP (%)        | {agent['rtp']:.2f} | {basic['rtp']:.2f} | {improvement['rtp_improvement']:+.2f} |\n"
        f"| Win-rate (%)   | {agent['win_rate']:.2f} | {basic['win_rate']:.2f} | {improvement['win_rate_improvement']:+.2f} |\n"
        f"| Volatility     | {agent['volatility']:.4f} | {basic['volatility']:.4f} | - |\n"
        f"| VaR-95         | {agent['var_95']:.4f} | {basic['var_95']:.4f} | - |\n"
        f"| Edge (%)       | {agent['edge']:+.2f} | {basic['edge']:+.2f} | {improvement['edge_improvement']:+.2f} |\n"
    )
    
    # Statistical test results
    stats_section = (
        f"\n## Statistical Analysis\n\n"
        f"- **T-statistic:** {stats_test['t_statistic']:.4f}\n"
        f"- **P-value:** {stats_test['p_value']:.6f}\n"
        f"- **Significant difference:** {'Yes' if stats_test['significant'] else 'No'}\n"
    )
    
    # Action distribution
    action_section = "\n## Action Distribution Analysis\n\n"
    action_section += "| Action | Agent (%) | Basic Strategy (%) |\n"
    action_section += "|--------|----------:|-------------------:|\n"
    
    for action in ["stand", "hit", "double", "split"]:
        agent_pct = action_analysis["agent_distribution"][action]
        basic_pct = action_analysis["basic_distribution"][action]
        action_section += f"| {action.capitalize()} | {agent_pct:.1f} | {basic_pct:.1f} |\n"
    
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Phase 1 Evaluation Report\n\n")
        f.write("## Performance Metrics\n\n")
        f.write(tbl)
        f.write(stats_section)
        f.write(action_section)
        f.write("\n\n<!---auto-generated-->\n")

    print(f"[Evaluator] Report written to {report_path}")


# --------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()
    
    try:
        metrics = evaluate(Path(args.model_path), args.episodes, args.seed, args.confidence_level)
        
        # Print summary to stdout
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Agent EV: {metrics['agent']['ev']:.4f} (95% CI: {metrics['agent']['ev_ci'][0]:.4f} - {metrics['agent']['ev_ci'][1]:.4f})")
        print(f"Basic EV: {metrics['basic']['ev']:.4f} (95% CI: {metrics['basic']['ev_ci'][0]:.4f} - {metrics['basic']['ev_ci'][1]:.4f})")
        print(f"Improvement: {metrics['improvement']['ev_improvement']:.4f}")
        print(f"Statistical significance: {'Yes' if metrics['statistical_test']['significant'] else 'No'} (p={metrics['statistical_test']['p_value']:.6f})")
        
        # Save detailed report
        save_report(Path(args.report), metrics)
        
        # W&B logging
        if args.log_to_wandb:
            wandb_run = init_wandb(
                project="blackjack_phase1",
                name="evaluation",
                config={
                    "episodes": args.episodes,
                    "model_path": str(args.model_path),
                },
            )
            if wandb_run is not None:
                # Log all metrics
                for key, value in metrics.items():
                    if key not in ["action_analysis"]:  # Skip complex nested structures
                        wandb_run.log({f"eval/{key}": value})
                wandb_run.finish()
        
        print(f"\n✅ Evaluation completed successfully!")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        raise


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Test için argümanları manuel olarak ayarla (sadece geliştirme için)
    import sys
    if len(sys.argv) == 1:  # Eğer argüman verilmemişse
        sys.argv = [
            "evaluate_play_agent.py",
            "--model-path", "runs/phase1/models/best_model",
            "--episodes", "1000",  # Test için daha az episode
            "--report", "reports/phase_1_report.md"
        ]
    
    main()
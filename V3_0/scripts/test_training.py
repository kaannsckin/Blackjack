#!/usr/bin/env python3
"""
Quick test script for FAZ1.3 training pipeline.

Usage
-----
$ python scripts/test_training.py --steps 10_000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.train_play_agent import main as train_main
from scripts.evaluate_play_agent import main as eval_main


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Test FAZ1.3 training pipeline")
    p.add_argument("--steps", type=int, default=10_000, help="Training steps")
    p.add_argument("--n-envs", type=int, default=4, help="Number of environments")
    p.add_argument("--eval-episodes", type=int, default=1_000, help="Evaluation episodes")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    
    print("="*60)
    print("FAZ1.3 TRAINING PIPELINE TEST")
    print("="*60)
    
    # Override sys.argv for train script
    original_argv = sys.argv
    sys.argv = [
        "train_play_agent.py",
        "--total-steps", str(args.steps),
        "--n-envs", str(args.n_envs),
        "--log-dir", "runs/test",
        "--seed", "42",
    ]
    
    try:
        print("\n[Test] Starting training...")
        train_main()
        print("[Test] Training completed successfully!")
        
        # Test evaluation
        print("\n[Test] Testing evaluation...")
        sys.argv = [
            "evaluate_play_agent.py",
            "--model-path", "runs/test/models/best_model",
            "--n-episodes", str(args.eval_episodes),
        ]
        eval_main()
        print("[Test] Evaluation completed successfully!")
        
    except Exception as e:
        print(f"[Test] Error during test: {e}")
        return
    
    finally:
        sys.argv = original_argv
    
    print("\n[Test] All tests passed! ✅")


if __name__ == "__main__":
    main() 
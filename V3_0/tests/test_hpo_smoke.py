"""
HPO smoke-test – CI süre limiti için tek deneme / 1000 adım.

Amaç: optimize_hyperparameters.py betiğinin hata vermeden çalıştığını ve
best_params.json dosyasını ürettiğini doğrulamak.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import pytest


def test_hpo_basic_smoke(tmp_path: Path) -> None:
    """Test basic HPO script."""
    script = Path("scripts/optimize_hyperparameters.py")
    out_dir = tmp_path / "hpo_run"
    root_dir = Path(__file__).parent.parent

    # Daha düşük parametrelerle hızlı test
    cmd = [
        "python",
        str(script),
        "--n-trials", "1",
        "--total-steps", "500",
        "--eval-episodes", "3",
        "--out-dir", str(out_dir),
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=root_dir)
    end_time = time.time()
    
    # Check execution time (should be < 30 seconds)
    assert end_time - start_time < 30, f"HPO took too long: {end_time - start_time:.2f}s"
    
    # Check output files
    params_file = out_dir / "best_params.json"
    assert params_file.exists(), "best_params.json yazılamadı"

    with params_file.open() as f:
        data = json.load(f)
    assert "lr" in data and "buffer_size" in data
    
    print(f"✅ Basic HPO smoke test passed in {end_time - start_time:.2f}s")


def test_hpo_advanced_smoke(tmp_path: Path) -> None:
    """Test advanced HPO script."""
    script = Path("scripts/optimize_hyperparameters_advanced.py")
    out_dir = tmp_path / "hpo_advanced_run"
    root_dir = Path(__file__).parent.parent

    cmd = [
        "python",
        str(script),
        "--n-trials", "1",
        "--total-steps", "500",
        "--eval-episodes", "3",
        "--out-dir", str(out_dir),
        "--multi-seed", "1",
        "--log-level", "WARNING",
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=root_dir)
    end_time = time.time()
    
    # Check execution time (should be < 30 seconds)
    assert end_time - start_time < 30, f"Advanced HPO took too long: {end_time - start_time:.2f}s"
    
    # Check output files
    params_file = out_dir / "best_params.json"
    assert params_file.exists(), "best_params.json yazılamadı"
    
    summary_file = out_dir / "summary.json"
    assert summary_file.exists(), "summary.json yazılamadı"
    
    top5_file = out_dir / "top5_trials.json"
    assert top5_file.exists(), "top5_trials.json yazılamadı"

    with params_file.open() as f:
        data = json.load(f)
    assert "lr" in data and "buffer_size" in data
    
    with summary_file.open() as f:
        summary = json.load(f)
    assert "best_reward" in summary and "total_trials" in summary
    
    print(f"✅ Advanced HPO smoke test passed in {end_time - start_time:.2f}s")


def test_hpo_with_config(tmp_path: Path) -> None:
    """Test HPO with YAML config file."""
    script = Path("scripts/optimize_hyperparameters_advanced.py")
    out_dir = tmp_path / "hpo_config_run"
    root_dir = Path(__file__).parent.parent
    
    # Create test config
    config_file = tmp_path / "test_config.yaml"
    config_content = """
hpo_args:
  n_trials: 1
  total_steps: 500
  eval_episodes: 3
  multi_seed: 1
  sampler: "random"
    """
    
    with config_file.open("w") as f:
        f.write(config_content)

    cmd = [
        "python",
        str(script),
        "--config",
        str(config_file),
        "--out-dir",
        str(out_dir),
        "--log-level",
        "WARNING",
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=root_dir)
    end_time = time.time()
    
    # Check execution time
    assert end_time - start_time < 30, f"HPO with config took too long: {end_time - start_time:.2f}s"
    
    # Check output files
    params_file = out_dir / "best_params.json"
    assert params_file.exists(), "best_params.json yazılamadı"
    
    print(f"✅ HPO with config smoke test passed in {end_time - start_time:.2f}s")


def test_hpo_error_handling(tmp_path: Path) -> None:
    """Test HPO error handling with invalid parameters."""
    script = Path("scripts/optimize_hyperparameters_advanced.py")
    out_dir = tmp_path / "hpo_error_run"
    root_dir = Path(__file__).parent.parent

    cmd = [
        "python",
        str(script),
        "--n-trials", "1",
        "--total-steps", "500",
        "--eval-episodes", "3",
        "--out-dir", str(out_dir),
        "--sampler", "invalid_sampler",  # This should cause an error
    ]
    
    # Should fail gracefully
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=root_dir)
    assert result.returncode != 0, "Should fail with invalid sampler"
    assert "Unknown sampler type" in result.stderr or "error" in result.stderr.lower()
    
    print("✅ HPO error handling test passed")


if __name__ == "__main__":
    import tempfile
    
    # Run smoke tests
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        print("🧪 Running HPO smoke tests...")
        
        test_hpo_basic_smoke(tmp_path)
        test_hpo_advanced_smoke(tmp_path)
        test_hpo_with_config(tmp_path)
        test_hpo_error_handling(tmp_path)
        
        print("✅ All HPO smoke tests passed!") 
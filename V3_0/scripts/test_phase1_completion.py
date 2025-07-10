#!/usr/bin/env python3
"""
Phase 1 Completion Test Script

This script validates that all Phase 1 components are properly implemented and functional.
It tests environment loading, model loading, basic strategy, performance metrics,
model prediction, integration, and file presence.
"""

from __future__ import annotations

import argparse
import sys
import json
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Local imports
from utils.basic_strategy import BasicStrategy
from utils.performance_metrics import PerformanceAnalyzer


class Phase1CompletionTester:
    """Comprehensive tester for Phase 1 completion."""
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize Phase 1 completion tester.
        
        Args:
            model_path: Optional path to trained model for testing
        """
        self.model_path = model_path
        self.results = {}
        self.basic_strategy = BasicStrategy()
        self.performance_analyzer = PerformanceAnalyzer()
        
    def test_environment_loading(self) -> bool:
        """Test that RL environment can be loaded."""
        print("🔄 Testing environment loading...")
        
        try:
            import importlib
            import inspect
            from typing import Type
            
            env_mod = importlib.import_module("rl_environment")
            for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
                if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
                    EnvCls = getattr(env_mod, cls_name)
                    break
            else:
                raise RuntimeError("Environment class not found")
            
            # Test environment creation
            env = EnvCls()
            obs, _ = env.reset()
            
            # Test basic functionality
            action = env.action_space.sample()
            obs, reward, done, truncated, info = env.step(action)
            
            env.close()
            
            self.results['environment_loading'] = True
            print("✅ Environment loading test passed")
            return True
            
        except Exception as e:
            self.results['environment_loading'] = False
            print(f"❌ Environment loading test failed: {e}")
            return False
    
    def test_model_loading(self) -> bool:
        """Test that trained model can be loaded."""
        if not self.model_path:
            print("⚠️ No model path provided, skipping model loading test")
            self.results['model_loading'] = False
            return False
        
        print("🔄 Testing model loading...")
        
        try:
            from stable_baselines3 import DQN
            import importlib
            import inspect
            
            # Load environment class
            env_mod = importlib.import_module("rl_environment")
            for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
                if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
                    EnvCls = getattr(env_mod, cls_name)
                    break
            else:
                raise RuntimeError("Environment class not found")
            
            # Load model
            env = EnvCls()
            model = DQN.load(self.model_path, env=env, print_system_info=False)
            
            # Test model prediction
            obs, _ = env.reset()
            action, _ = model.predict(obs, deterministic=True)
            
            env.close()
            
            self.results['model_loading'] = True
            print("✅ Model loading test passed")
            return True
            
        except Exception as e:
            self.results['model_loading'] = False
            print(f"❌ Model loading test failed: {e}")
            return False
    
    def test_basic_strategy(self) -> bool:
        """Test basic strategy implementation."""
        print("🔄 Testing basic strategy...")
        
        try:
            # Test basic strategy with known scenarios
            test_cases = [
                (16, 10, False, 1),  # 16 vs 10 should hit
                (17, 7, False, 0),   # 17 vs 7 should stand
                (11, 5, False, 2),   # 11 vs 5 should double
                (8, 8, False, 3),    # 8,8 vs 8 should split (pair)
            ]
            
            for player_total, dealer_up, usable_ace, expected_action in test_cases:
                # For pair test, we need to set is_pair=True
                if player_total == 8 and dealer_up == 8:
                    action = self.basic_strategy.get_action(player_total, dealer_up, usable_ace, is_pair=True)
                else:
                    action = self.basic_strategy.get_action(player_total, dealer_up, usable_ace)
                
                if action != expected_action:
                    raise ValueError(f"Basic strategy failed: {player_total} vs {dealer_up} = {action}, expected {expected_action}")
            
            self.results['basic_strategy'] = True
            print("✅ Basic strategy test passed")
            return True
            
        except Exception as e:
            self.results['basic_strategy'] = False
            print(f"❌ Basic strategy test failed: {e}")
            return False
    
    def test_performance_metrics(self) -> bool:
        """Test performance metrics calculation."""
        print("🔄 Testing performance metrics...")
        
        try:
            # Test with sample rewards
            sample_rewards = [1, -1, 0, 1, -1, 1, 0, -1, 1, -1]
            metrics = self.performance_analyzer.calculate_metrics(sample_rewards)
            
            # Check that metrics have expected attributes
            required_attrs = ['ev', 'rtp', 'win_rate', 'volatility', 'var_95']
            for attr in required_attrs:
                if not hasattr(metrics, attr):
                    raise ValueError(f"Missing metric attribute: {attr}")
            
            self.results['performance_metrics'] = True
            print("✅ Performance metrics test passed")
            return True
            
        except Exception as e:
            self.results['performance_metrics'] = False
            print(f"❌ Performance metrics test failed: {e}")
            return False
    
    def test_model_prediction(self) -> bool:
        """Test model prediction functionality."""
        if not self.model_path:
            print("⚠️ No model path provided, skipping model prediction test")
            self.results['model_prediction'] = False
            return False
        
        print("🔄 Testing model prediction...")
        
        try:
            from stable_baselines3 import DQN
            import importlib
            import inspect
            
            # Load environment and model
            env_mod = importlib.import_module("rl_environment")
            for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
                if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
                    EnvCls = getattr(env_mod, cls_name)
                    break
            else:
                raise RuntimeError("Environment class not found")
            
            env = EnvCls()
            model = DQN.load(self.model_path, env=env, print_system_info=False)
            
            # Test predictions on various states
            test_states = [
                np.array([16, 10, 0.0, 0.0]),  # 16 vs 10
                np.array([17, 7, 0.0, 0.0]),   # 17 vs 7
                np.array([11, 5, 0.0, 0.0]),   # 11 vs 5
                np.array([12, 2, 0.0, 0.0]),   # 12 vs 2
            ]
            
            for state in test_states:
                action, _ = model.predict(state, deterministic=True)
                # Handle both single actions and array of actions
                if isinstance(action, np.ndarray):
                    action = action.item()
                if not isinstance(action, (int, np.integer)) or action < 0 or action > 3:
                    raise ValueError(f"Invalid action prediction: {action}")
            
            env.close()
            
            self.results['model_prediction'] = True
            print("✅ Model prediction test passed")
            return True
            
        except Exception as e:
            self.results['model_prediction'] = False
            print(f"❌ Model prediction test failed: {e}")
            return False
    
    def test_integration(self) -> bool:
        """Test AI strategy integration."""
        print("🔄 Testing AI strategy integration...")
        
        try:
            from utils.ai_play_strategy import create_ai_play_strategy
            
            if not self.model_path:
                print("⚠️ No model path provided, skipping integration test")
                self.results['integration'] = False
                return False
            
            # Test AI strategy creation
            from gymnasium import spaces
            action_space = spaces.Discrete(4)  # 4 actions: stand, hit, double, split
            ai_strategy = create_ai_play_strategy(action_space, self.model_path, "ai_test")
            
            # Test strategy with sample game state
            player_total = 16
            dealer_up = 10
            usable_ace = False
            
            # Create observation array
            obs = np.array([player_total, dealer_up, float(usable_ace), 0.0])
            
            action = ai_strategy.act(obs)
            
            if not isinstance(action, int) or action < 0 or action > 3:
                raise ValueError(f"Invalid action from AI strategy: {action}")
            
            self.results['integration'] = True
            print("✅ Integration test passed")
            return True
            
        except Exception as e:
            self.results['integration'] = False
            print(f"❌ Integration test failed: {e}")
            return False
    
    def test_visualization_script(self) -> bool:
        """Test that visualization script exists and is functional."""
        print("🔄 Testing visualization script...")
        
        try:
            viz_script = Path(__file__).parent / "visualize_policy.py"
            if not viz_script.exists():
                raise FileNotFoundError("Visualization script not found")
            
            # Test script imports
            import subprocess
            result = subprocess.run([
                sys.executable, str(viz_script), "--help"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Visualization script failed to run: {result.stderr}")
            
            self.results['visualization_script'] = True
            print("✅ Visualization script test passed")
            return True
            
        except Exception as e:
            self.results['visualization_script'] = False
            print(f"❌ Visualization script test failed: {e}")
            return False
    
    def test_config_files(self) -> bool:
        """Test that configuration files exist."""
        print("🔄 Testing configuration files...")
        
        try:
            config_dir = Path(__file__).parent.parent / "config"
            required_configs = [
                "hpo_config.yaml",
                "ai_strategy_config.yaml"
            ]
            
            missing_configs = []
            for config in required_configs:
                if not (config_dir / config).exists():
                    missing_configs.append(config)
            
            if missing_configs:
                raise FileNotFoundError(f"Missing config files: {missing_configs}")
            
            self.results['config_files'] = True
            print("✅ Configuration files test passed")
            return True
            
        except Exception as e:
            self.results['config_files'] = False
            print(f"❌ Configuration files test failed: {e}")
            return False
    
    def test_model_files(self) -> bool:
        """Test that model files exist."""
        print("🔄 Testing model files...")
        
        try:
            # Check for model files in various locations
            possible_model_paths = [
                Path("test_hpo_out/models/hpo_final_model.zip"),
                Path("runs/phase1/models/best_model.zip"),
                Path("runs/test_phase1/models/final_model.zip"),
                self.model_path
            ]
            
            found_models = []
            for path in possible_model_paths:
                if path and path.exists():
                    found_models.append(path)
            
            if not found_models:
                raise FileNotFoundError("No model files found")
            
            self.results['model_files'] = True
            print(f"✅ Model files test passed. Found: {found_models}")
            return True
            
        except Exception as e:
            self.results['model_files'] = False
            print(f"❌ Model files test failed: {e}")
            return False
    
    def test_hyperparameter_results(self) -> bool:
        """Test that hyperparameter optimization results exist."""
        print("🔄 Testing hyperparameter results...")
        
        try:
            # Check for HPO results in various locations
            possible_hpo_paths = [
                Path("test_hpo_out/best_params.json"),
                Path("runs/test_phase1/best_params.json"),
                Path("V3_0/test_hpo_out/best_params.json"),
                Path("../test_hpo_out/best_params.json")  # Check parent directory
            ]
            
            hpo_results_path = None
            for path in possible_hpo_paths:
                if path.exists():
                    hpo_results_path = path
                    break
            
            if not hpo_results_path:
                raise FileNotFoundError("HPO results not found in any expected location")
            
            # Load and validate results
            with open(hpo_results_path, 'r') as f:
                best_params = json.load(f)
            
            required_params = ['lr', 'buffer_size', 'eps_frac', 'eps_final', 'gamma', 'batch_size']
            for param in required_params:
                if param not in best_params:
                    raise ValueError(f"Missing HPO parameter: {param}")
            
            self.results['hyperparameter_results'] = True
            print("✅ Hyperparameter results test passed")
            return True
            
        except Exception as e:
            self.results['hyperparameter_results'] = False
            print(f"❌ Hyperparameter results test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all Phase 1 completion tests."""
        print("🧪 Running Phase 1 completion tests...\n")
        
        tests = [
            self.test_environment_loading,
            self.test_basic_strategy,
            self.test_performance_metrics,
            self.test_visualization_script,
            self.test_config_files,
            self.test_model_files,
            self.test_hyperparameter_results,
        ]
        
        # Add model-dependent tests if model path is provided
        if self.model_path:
            tests.extend([
                self.test_model_loading,
                self.test_model_prediction,
                self.test_integration,
            ])
        
        # Run all tests
        for test in tests:
            test()
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate test report."""
        if not self.results:
            return "❌ No test results available"
        
        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        failed_tests = total_tests - passed_tests
        
        report = f"""
# Phase 1 Completion Test Report

## Summary
- **Total Tests:** {total_tests}
- **Passed:** {passed_tests}
- **Failed:** {failed_tests}
- **Success Rate:** {passed_tests/total_tests*100:.1f}%

## Test Results

| Test | Status | Description |
|------|--------|-------------|
"""
        
        for test_name, passed in self.results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            description = {
                'environment_loading': 'RL environment can be loaded and used',
                'model_loading': 'Trained model can be loaded',
                'basic_strategy': 'Basic strategy implementation works correctly',
                'performance_metrics': 'Performance metrics calculation works',
                'model_prediction': 'Model can make predictions on game states',
                'integration': 'AI strategy integrates with game engine',
                'visualization_script': 'Policy visualization script exists and works',
                'config_files': 'Required configuration files exist',
                'model_files': 'Trained model files exist',
                'hyperparameter_results': 'HPO results exist and are valid'
            }.get(test_name, 'Unknown test')
            
            report += f"| {test_name.replace('_', ' ').title()} | {status} | {description} |\n"
        
        report += f"""
## Phase 1 Completion Status

"""
        
        if passed_tests == total_tests:
            report += "🎉 **PHASE 1 COMPLETED SUCCESSFULLY**\n"
            report += "All tests passed. Phase 1 is ready for Phase 2.\n"
        elif passed_tests >= total_tests * 0.8:
            report += "⚠️ **PHASE 1 MOSTLY COMPLETED**\n"
            report += "Most tests passed. Some issues need attention.\n"
        else:
            report += "❌ **PHASE 1 INCOMPLETE**\n"
            report += "Multiple tests failed. Phase 1 needs more work.\n"
        
        return report


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Phase 1 Completion Test")
    parser.add_argument("--model-path", type=str, help="Path to trained model for testing")
    parser.add_argument("--output-file", type=str, help="Output file for test report")
    
    args = parser.parse_args()
    
    # Create tester
    model_path = Path(args.model_path) if args.model_path else None
    tester = Phase1CompletionTester(model_path)
    
    # Run tests
    results = tester.run_all_tests()
    
    # Generate and display report
    report = tester.generate_report()
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    # Save report if requested
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(report)
        print(f"\n📄 Test report saved to: {args.output_file}")
    
    # Exit with appropriate code
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Phase 1 is complete.")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed. Phase 1 needs attention.")
        sys.exit(1)


if __name__ == "__main__":
    main() 
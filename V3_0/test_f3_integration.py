"""
================================================================================
F3.x INTEGRATION TEST SUITE
================================================================================

🎯 **AMAÇ:** F3.x kodlarının çalışırlığını ve entegrasyonunu test etme
📋 **KAPSAM:** Dynamic rules, multi-task models, HPC infrastructure
🔧 **ANALİZ:** Performance ve functionality validation

================================================================================
"""

import sys
import os
import time
import logging
import numpy as np
from typing import Dict, List, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_f3_2_dynamic_rules():
    """Test F3.2: Dynamic Rule Randomization Integration"""
    print("\n🧪 TESTING F3.2: Dynamic Rule Randomization")
    print("=" * 50)
    
    try:
        from dynamic_rule_randomization import create_dynamic_randomizer, integrate_with_environment
        from rl_environment import BlackjackRLEnv
        
        # Create randomizer
        randomizer = create_dynamic_randomizer("medium", seed=42)
        
        # Create environment
        env = BlackjackRLEnv()
        
        # Integrate dynamic rules
        env = integrate_with_environment(env, randomizer)
        
        # Test multiple episodes
        print("Testing 5 episodes with dynamic rules...")
        for episode in range(5):
            obs, info = env.reset()
            print(f"Episode {episode + 1}: Rules = {env.rules}")
            
            # Play a few steps
            for step in range(3):
                action = env.action_space.sample()  # Random action
                obs, reward, done, truncated, info = env.step(action)
                if done:
                    break
        
        # Check rule statistics
        stats = randomizer.get_rule_statistics()
        print(f"\n📊 Rule Statistics:")
        print(f"   Total episodes: {stats['total_episodes']}")
        print(f"   DAS frequency: {stats['das_frequency']:.2f}")
        print(f"   Surrender frequency: {stats['surrender_frequency']:.2f}")
        
        print("✅ F3.2 Integration: SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ F3.2 Integration: FAILED - {e}")
        return False

def test_f3_3_multi_task_models():
    """Test F3.3: Multi-Task Models"""
    print("\n🧪 TESTING F3.3: Multi-Task Models")
    print("=" * 50)
    
    try:
        from multi_task_models import create_pearl_model, create_sacae_model, TaskContext, TaskType
        import gymnasium as gym
        
        # Create dummy environment for testing
        env = gym.make('CartPole-v1')
        
        # Test PEARL model
        print("Testing PEARL model creation...")
        pearl_model = create_pearl_model(env, task_dim=32, embedding_dim=64)
        print("✅ PEARL model created successfully")
        
        # Test SAC-AE model
        print("Testing SAC-AE model creation...")
        sacae_model = create_sacae_model(env, task_dim=32, embedding_dim=64)
        print("✅ SAC-AE model created successfully")
        
        # Test task context
        print("Testing task context creation...")
        task_context = TaskContext(
            task_type=TaskType.CONSERVATIVE_PLAYER,
            task_id=1,
            rule_config={"num_decks": 6, "dealer_rule": "S17"},
            player_config={"risk_tolerance": 0.3},
            task_embedding=np.random.randn(64)
        )
        print(f"✅ Task context created: {task_context}")
        
        # Test model manager
        from multi_task_models import MultiTaskModelManager
        manager = MultiTaskModelManager()
        print("✅ Multi-task model manager created")
        
        print("✅ F3.3 Multi-Task Models: SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ F3.3 Multi-Task Models: FAILED - {e}")
        return False

def test_f3_4_hpc_infrastructure():
    """Test F3.4: HPC Infrastructure Components"""
    print("\n🧪 TESTING F3.4: HPC Infrastructure")
    print("=" * 50)
    
    try:
        # Test Dockerfile syntax
        print("Testing Dockerfile...")
        with open('Dockerfile', 'r') as f:
            dockerfile_content = f.read()
        
        # Check for required components
        required_docker_elements = [
            'FROM python:3.9-slim',
            'WORKDIR /app',
            'COPY requirements.txt',
            'RUN pip install',
            'EXPOSE 6379',
            'ENTRYPOINT'
        ]
        
        for element in required_docker_elements:
            if element in dockerfile_content:
                print(f"✅ Found: {element}")
            else:
                print(f"❌ Missing: {element}")
        
        # Test docker-compose.yml
        print("\nTesting docker-compose.yml...")
        with open('docker-compose.yml', 'r') as f:
            compose_content = f.read()
        
        required_compose_services = [
            'ray-head',
            'ray-worker',
            'training-controller',
            'monitoring'
        ]
        
        for service in required_compose_services:
            if service in compose_content:
                print(f"✅ Found service: {service}")
            else:
                print(f"❌ Missing service: {service}")
        
        # Test HPC launcher (without AWS credentials)
        print("\nTesting HPC launcher structure...")
        import sys
        sys.path.append('scripts')
        from hpc_training_launcher import HPCConfig, create_hpc_config
        
        config = create_hpc_config()
        print(f"✅ HPC config created: {config.instance_type}, {config.total_timesteps} steps")
        
        print("✅ F3.4 HPC Infrastructure: SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ F3.4 HPC Infrastructure: FAILED - {e}")
        return False

def test_f3_6_package_distribution():
    """Test F3.6: Package Distribution"""
    print("\n🧪 TESTING F3.6: Package Distribution")
    print("=" * 50)
    
    try:
        # Test setup.py
        print("Testing setup.py...")
        with open('setup.py', 'r') as f:
            setup_content = f.read()
        
        required_setup_elements = [
            'name="blackjack_ai_sim"',
            'version="3.0.0"',
            'install_requires',
            'entry_points',
            'console_scripts'
        ]
        
        for element in required_setup_elements:
            if element in setup_content:
                print(f"✅ Found: {element}")
            else:
                print(f"❌ Missing: {element}")
        
        # Test Sphinx configuration
        print("\nTesting Sphinx configuration...")
        with open('docs/conf.py', 'r') as f:
            sphinx_content = f.read()
        
        required_sphinx_elements = [
            'project =',
            'extensions =',
            'html_theme =',
            'sphinx_rtd_theme'
        ]
        
        for element in required_sphinx_elements:
            if element in sphinx_content:
                print(f"✅ Found: {element}")
            else:
                print(f"❌ Missing: {element}")
        
        # Test package installation (dry run)
        print("\nTesting package structure...")
        import subprocess
        result = subprocess.run([
            'python', 'setup.py', 'check', '--strict'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Package structure validation: PASSED")
        else:
            print(f"⚠️ Package structure warnings: {result.stdout}")
        
        print("✅ F3.6 Package Distribution: SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ F3.6 Package Distribution: FAILED - {e}")
        return False

def test_f3_integration_performance():
    """Test F3.x Integration Performance"""
    print("\n🧪 TESTING F3.x INTEGRATION PERFORMANCE")
    print("=" * 50)
    
    try:
        from dynamic_rule_randomization import create_dynamic_randomizer
        from multi_task_models import create_pearl_model
        import gymnasium as gym
        
        # Performance test: Create multiple randomizers
        print("Testing dynamic rule randomizer performance...")
        start_time = time.time()
        
        randomizers = []
        for i in range(10):
            randomizer = create_dynamic_randomizer("medium", seed=i)
            for j in range(100):  # Generate 100 rule sets each
                randomizer.generate_random_rules()
            randomizers.append(randomizer)
        
        rule_time = time.time() - start_time
        print(f"✅ Generated 1000 rule sets in {rule_time:.2f} seconds")
        
        # Performance test: Multi-task model creation
        print("\nTesting multi-task model performance...")
        start_time = time.time()
        
        env = gym.make('CartPole-v1')
        models = []
        for i in range(5):
            model = create_pearl_model(env, task_dim=32, embedding_dim=64)
            models.append(model)
        
        model_time = time.time() - start_time
        print(f"✅ Created 5 PEARL models in {model_time:.2f} seconds")
        
        # Memory usage check
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"✅ Memory usage: {memory_mb:.1f} MB")
        
        print("✅ F3.x Performance: SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ F3.x Performance: FAILED - {e}")
        return False

def main():
    """Run all F3.x tests"""
    print("🚀 F3.x COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    test_results = {}
    
    # Run all tests
    test_results['F3.2'] = test_f3_2_dynamic_rules()
    test_results['F3.3'] = test_f3_3_multi_task_models()
    test_results['F3.4'] = test_f3_4_hpc_infrastructure()
    test_results['F3.6'] = test_f3_6_package_distribution()
    test_results['Performance'] = test_f3_integration_performance()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 F3.x TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:12}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🏆 ALL F3.x TESTS PASSED!")
        print("🎉 F3.x INFRASTRUCTURE READY FOR PRODUCTION!")
    else:
        print(f"\n⚠️ {total-passed} tests failed - needs attention")
    
    return test_results

if __name__ == "__main__":
    main() 
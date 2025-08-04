#!/usr/bin/env python3
"""
Algorithm Comparison Script

Compare PPO, TD3, and SAC algorithms with the fixed environment.
"""

import sys
import time
import json
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from betting_environment_fixed import create_fixed_betting_env
from stable_baselines3 import PPO, TD3, SAC
from stable_baselines3.common.env_util import make_vec_env


def create_simple_model(algorithm: str, env, learning_rate: float = 3e-4):
    """Create model with simplified hyperparameters for quick comparison."""
    
    if algorithm.lower() == "ppo":
        return PPO(
            "MlpPolicy",
            env,
            learning_rate=learning_rate,
            n_steps=1024,
            batch_size=64,
            n_epochs=5,
            gamma=0.99,
            ent_coef=0.01,
            verbose=0
        )
    
    elif algorithm.lower() == "td3":
        # TD3 requires continuous action space - skip for now
        return None
    
    elif algorithm.lower() == "sac":
        # SAC also requires continuous action space - skip for now
        return None
    
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def evaluate_model_quick(model, env, n_episodes: int = 100):
    """Quick model evaluation."""
    episode_rewards = []
    episode_lengths = []
    bankroll_changes = []
    
    for episode in range(n_episodes):
        obs, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        initial_bankroll = env.bankroll
        
        done = False
        while not done and episode_length < 50:  # Safety limit
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            episode_length += 1
            
            if done or truncated:
                break
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        bankroll_changes.append(env.bankroll - initial_bankroll)
    
    return {
        "mean_reward": np.mean(episode_rewards),
        "std_reward": np.std(episode_rewards),
        "mean_length": np.mean(episode_lengths),
        "mean_bankroll_change": np.mean(bankroll_changes),
        "win_rate": np.mean([r > 0 for r in episode_rewards]),
        "episodes": n_episodes
    }


def train_and_evaluate(algorithm: str, steps: int = 50000):
    """Train and evaluate a single algorithm."""
    
    print(f"\n🤖 Testing {algorithm.upper()}")
    print("-" * 40)
    
    # Create environments
    train_env = make_vec_env(
        lambda: create_fixed_betting_env(
            seed=42,
            initial_bankroll=1000.0,
            min_bet=10.0,
            max_bet=100.0,
            risk_aversion=0.05
        ),
        n_envs=4,
        seed=42
    )
    
    eval_env = create_fixed_betting_env(
        seed=123,
        initial_bankroll=1000.0,
        min_bet=10.0,
        max_bet=100.0,
        risk_aversion=0.05
    )
    
    # Create model
    model = create_simple_model(algorithm, train_env)
    
    if model is None:
        print(f"   ⚠️ {algorithm.upper()} requires continuous action space - skipping")
        return None
    
    print(f"   🌍 Created environments")
    print(f"   🤖 Created {algorithm.upper()} model")
    
    # Training
    print(f"   🚀 Training for {steps:,} steps...")
    start_time = time.time()
    
    try:
        model.learn(total_timesteps=steps, progress_bar=False)
        training_time = time.time() - start_time
        
        print(f"   ✅ Training completed in {training_time:.1f}s")
        
        # Evaluation
        print(f"   🧪 Evaluating...")
        results = evaluate_model_quick(model, eval_env, n_episodes=200)
        
        print(f"   📊 Results:")
        print(f"      Mean Reward: {results['mean_reward']:+.3f}")
        print(f"      Win Rate: {results['win_rate']:.1%}")
        print(f"      Avg Length: {results['mean_length']:.1f}")
        print(f"      Bankroll Change: {results['mean_bankroll_change']:+.1f}")
        
        return {
            "algorithm": algorithm,
            "training_time": training_time,
            "training_steps": steps,
            **results
        }
        
    except Exception as e:
        print(f"   ❌ Training failed: {e}")
        return None


def main():
    """Run algorithm comparison."""
    
    print("🔬 ALGORITHM COMPARISON - Fixed Environment")
    print("=" * 50)
    
    algorithms = ["ppo"]  # Start with PPO since it works with discrete actions
    results = []
    
    for algorithm in algorithms:
        result = train_and_evaluate(algorithm, steps=50000)
        if result:
            results.append(result)
    
    # Summary
    print(f"\n{'='*50}")
    print("🏆 ALGORITHM COMPARISON SUMMARY")
    print('='*50)
    
    if results:
        # Sort by mean reward
        results.sort(key=lambda x: x['mean_reward'], reverse=True)
        
        print(f"{'Rank':<4} {'Algorithm':<8} {'Reward':<8} {'Win Rate':<9} {'Time':<6}")
        print("-" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"{i:<4} {result['algorithm'].upper():<8} "
                  f"{result['mean_reward']:+.3f}   "
                  f"{result['win_rate']:6.1%}   "
                  f"{result['training_time']:5.1f}s")
        
        best_algorithm = results[0]
        print(f"\n🏆 WINNER: {best_algorithm['algorithm'].upper()}")
        print(f"   Performance: {best_algorithm['mean_reward']:+.3f} reward")
        print(f"   Win Rate: {best_algorithm['win_rate']:.1%}")
        
        # Save results
        with open("runs/algorithm_comparison.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to: runs/algorithm_comparison.json")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if best_algorithm['mean_reward'] > 0:
            print("   ✅ Current best algorithm shows positive performance!")
            print("   🚀 Recommend scaling up training steps for production")
        elif best_algorithm['mean_reward'] > -2:
            print("   🟡 Current best algorithm shows promise")
            print("   🔧 Recommend hyperparameter tuning")
        else:
            print("   🔴 All algorithms still underperforming")
            print("   🛠️ Recommend environment or reward function changes")
        
        if best_algorithm['win_rate'] > 0.45:
            print("   🎯 Win rate is approaching realistic levels")
        else:
            print("   ⚠️ Win rate still below expected (~47-48%)")
    
    else:
        print("❌ No algorithms completed successfully")
    
    return len(results) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
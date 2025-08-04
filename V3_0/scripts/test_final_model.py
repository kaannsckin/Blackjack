#!/usr/bin/env python3
"""
Final Phase 2 Model Test

Comprehensive evaluation of the final Phase 2 betting agent.
"""

import sys
import json
import time
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from betting_environment_fixed import create_fixed_betting_env
from stable_baselines3 import PPO


def load_final_model():
    """Load the final Phase 2 model."""
    model_path = "runs/final_phase2_model/final_model"
    
    if not Path(f"{model_path}.zip").exists():
        raise FileNotFoundError(f"Final model not found: {model_path}")
    
    env = create_fixed_betting_env(
        seed=999,  # Different seed for testing
        initial_bankroll=1000.0,
        min_bet=10.0,
        max_bet=100.0,
        risk_aversion=0.05
    )
    
    model = PPO.load(model_path, env=env)
    return model, env


def comprehensive_evaluation(model, env, n_episodes: int = 1000):
    """Comprehensive evaluation of the final model."""
    
    print(f"🧪 COMPREHENSIVE EVALUATION - {n_episodes:,} episodes")
    print("=" * 60)
    
    episode_rewards = []
    episode_lengths = []
    bankroll_changes = []
    win_outcomes = []
    
    # Track betting behavior
    bet_amounts = []
    true_counts = []
    bet_decisions = []
    
    total_hands = 0
    start_time = time.time()
    
    for episode in range(n_episodes):
        obs, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        initial_bankroll = env.bankroll
        
        # Set bet manually to track decisions
        player_total = obs[0]
        dealer_up = obs[1]
        true_count = obs[3] if len(obs) > 3 else 0
        
        # Let AI decide on bet
        if hasattr(env, 'set_bet_amount'):
            # Simple bet sizing based on true count for comparison
            if true_count > 2:
                bet = 50.0
            elif true_count > 0:
                bet = 25.0
            else:
                bet = 10.0
            
            env.set_bet_amount(bet)
            bet_amounts.append(bet)
            true_counts.append(true_count)
        
        done = False
        while not done and episode_length < 50:  # Safety limit
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            episode_reward += reward
            episode_length += 1
            total_hands += 1
            
            if done or truncated:
                # Record outcome
                game_outcome = info.get('game_outcome', 0)
                win_outcomes.append(game_outcome > 0)
                break
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        bankroll_changes.append(env.bankroll - initial_bankroll)
        
        # Progress update
        if (episode + 1) % 100 == 0:
            elapsed = time.time() - start_time
            rate = (episode + 1) / elapsed
            eta = (n_episodes - episode - 1) / rate if rate > 0 else 0
            print(f"   Progress: {episode+1:,}/{n_episodes:,} ({100*(episode+1)/n_episodes:.1f}%) "
                  f"- {rate:.0f} episodes/sec - ETA: {eta:.0f}s")
    
    # Calculate comprehensive metrics
    total_time = time.time() - start_time
    
    results = {
        "episodes": n_episodes,
        "total_hands": total_hands,
        "evaluation_time": total_time,
        "episodes_per_second": n_episodes / total_time,
        
        # Performance metrics
        "mean_reward": np.mean(episode_rewards),
        "std_reward": np.std(episode_rewards),
        "min_reward": np.min(episode_rewards),
        "max_reward": np.max(episode_rewards),
        
        # Episode metrics
        "mean_episode_length": np.mean(episode_lengths),
        "std_episode_length": np.std(episode_lengths),
        "min_episode_length": np.min(episode_lengths),
        "max_episode_length": np.max(episode_lengths),
        
        # Bankroll metrics
        "mean_bankroll_change": np.mean(bankroll_changes),
        "total_bankroll_change": np.sum(bankroll_changes),
        "final_bankroll": env.bankroll,
        "bankroll_std": np.std(bankroll_changes),
        
        # Win rate metrics
        "win_rate": np.mean(win_outcomes),
        "episode_win_rate": np.mean([r > 0 for r in episode_rewards]),
        
        # Betting analysis
        "mean_bet": np.mean(bet_amounts) if bet_amounts else 0,
        "bet_std": np.std(bet_amounts) if bet_amounts else 0,
        "mean_true_count": np.mean(true_counts) if true_counts else 0,
        
        # Advanced metrics
        "sharpe_ratio": np.mean(episode_rewards) / np.std(episode_rewards) if np.std(episode_rewards) > 0 else 0,
        "profit_factor": np.sum([r for r in episode_rewards if r > 0]) / abs(np.sum([r for r in episode_rewards if r < 0])) if any(r < 0 for r in episode_rewards) else float('inf'),
        "max_drawdown": np.min(bankroll_changes) / 1000.0,  # As percentage of initial bankroll
        "max_runup": np.max(bankroll_changes) / 1000.0,
        
        # Risk metrics
        "positive_episodes": np.sum([r > 0 for r in episode_rewards]),
        "negative_episodes": np.sum([r < 0 for r in episode_rewards]),
        "neutral_episodes": np.sum([r == 0 for r in episode_rewards]),
    }
    
    return results


def print_detailed_results(results):
    """Print detailed evaluation results."""
    
    print(f"\n📊 FINAL PHASE 2 MODEL EVALUATION RESULTS")
    print("=" * 60)
    
    print(f"\n🎯 PERFORMANCE SUMMARY:")
    print(f"   Episodes: {results['episodes']:,}")
    print(f"   Total Hands: {results['total_hands']:,}")
    print(f"   Evaluation Time: {results['evaluation_time']:.1f}s")
    print(f"   Speed: {results['episodes_per_second']:.0f} episodes/sec")
    
    print(f"\n📈 REWARD METRICS:")
    print(f"   Mean Reward: {results['mean_reward']:+.3f}")
    print(f"   Std Reward: {results['std_reward']:.3f}")
    print(f"   Reward Range: {results['min_reward']:+.3f} to {results['max_reward']:+.3f}")
    print(f"   Sharpe Ratio: {results['sharpe_ratio']:.3f}")
    
    print(f"\n🎲 EPISODE METRICS:")
    print(f"   Mean Length: {results['mean_episode_length']:.2f}")
    print(f"   Length Range: {results['min_episode_length']:.0f} to {results['max_episode_length']:.0f}")
    print(f"   Positive Episodes: {results['positive_episodes']:,} ({results['positive_episodes']/results['episodes']:.1%})")
    print(f"   Negative Episodes: {results['negative_episodes']:,} ({results['negative_episodes']/results['episodes']:.1%})")
    
    print(f"\n💰 BANKROLL ANALYSIS:")
    print(f"   Mean Change: ${results['mean_bankroll_change']:+.2f}")
    print(f"   Total Change: ${results['total_bankroll_change']:+.2f}")
    print(f"   Final Bankroll: ${results['final_bankroll']:,.2f}")
    print(f"   Max Drawdown: {results['max_drawdown']:+.1%}")
    print(f"   Max Runup: {results['max_runup']:+.1%}")
    
    print(f"\n🎯 WIN RATE ANALYSIS:")
    print(f"   Hand Win Rate: {results['win_rate']:.1%}")
    print(f"   Episode Win Rate: {results['episode_win_rate']:.1%}")
    
    print(f"\n💸 BETTING BEHAVIOR:")
    print(f"   Mean Bet: ${results['mean_bet']:.2f}")
    print(f"   Bet Std: ${results['bet_std']:.2f}")
    print(f"   Mean True Count: {results['mean_true_count']:+.2f}")
    
    # Performance assessment
    print(f"\n🏆 PERFORMANCE ASSESSMENT:")
    
    grade = "F"
    assessment = "Poor"
    
    if results['mean_reward'] > 5 and results['win_rate'] > 0.47:
        grade = "A+"
        assessment = "Excellent"
    elif results['mean_reward'] > 2 and results['win_rate'] > 0.46:
        grade = "A"
        assessment = "Very Good"
    elif results['mean_reward'] > 0 and results['win_rate'] > 0.45:
        grade = "B+"
        assessment = "Good"
    elif results['mean_reward'] > -2 and results['win_rate'] > 0.42:
        grade = "B"
        assessment = "Acceptable"
    elif results['mean_reward'] > -5:
        grade = "C"
        assessment = "Needs Improvement"
    else:
        grade = "D"
        assessment = "Poor"
    
    print(f"   Overall Grade: {grade}")
    print(f"   Assessment: {assessment}")
    
    # Comparison to targets
    print(f"\n🎯 TARGET COMPARISON:")
    target_reward = 5.0
    target_win_rate = 0.48
    
    reward_vs_target = results['mean_reward'] / target_reward if target_reward != 0 else 0
    win_rate_vs_target = results['win_rate'] / target_win_rate if target_win_rate != 0 else 0
    
    print(f"   Reward vs Target: {reward_vs_target:.1%} (target: +{target_reward:.1f})")
    print(f"   Win Rate vs Target: {win_rate_vs_target:.1%} (target: {target_win_rate:.1%})")
    
    if results['mean_reward'] > 0 and results['win_rate'] > 0.45:
        print(f"   🎉 SUCCESS: Model shows positive performance!")
    elif results['mean_reward'] > -1 and results['win_rate'] > 0.40:
        print(f"   🟡 PROGRESS: Model shows promise but needs optimization")
    else:
        print(f"   🔴 NEEDS WORK: Model requires significant improvement")


def main():
    """Run comprehensive final model evaluation."""
    
    print("🎯 FINAL PHASE 2 MODEL EVALUATION")
    print("=" * 50)
    
    try:
        # Load model
        print("📦 Loading final model...")
        model, env = load_final_model()
        print("✅ Model loaded successfully")
        
        # Run evaluation
        results = comprehensive_evaluation(model, env, n_episodes=2000)
        
        # Print results
        print_detailed_results(results)
        
        # Save results
        timestamp = int(time.time())
        results_path = f"runs/final_model_evaluation_{timestamp}.json"
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: {results_path}")
        
        # Final recommendation
        print(f"\n💡 FINAL RECOMMENDATION:")
        
        if results['mean_reward'] > 0 and results['win_rate'] > 0.45:
            print("   ✅ READY FOR PHASE 3: Model performance is acceptable")
            print("   🚀 Proceed with multi-strategy development")
        elif results['mean_reward'] > -2:
            print("   🟡 CONDITIONAL: Performance promising but consider optimization")
            print("   🔧 Recommend hyperparameter tuning before Phase 3")
        else:
            print("   🔴 NOT READY: Significant improvements needed")
            print("   🛠️ Return to Phase 2 development")
        
        return True
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
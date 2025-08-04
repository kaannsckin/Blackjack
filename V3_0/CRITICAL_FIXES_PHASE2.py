#!/usr/bin/env python3
"""
CRITICAL FIXES PHASE 2 - Complete Problem Resolution
Must be solved before Phase 3:
1. Q-Value Heatmaps all ZERO -> RL model not learning
2. Policy Agreement extremely low -> AI strategy broken  
3. Win rate 1% -> Performance catastrophic
4. Environment bias -> Fixed but needs validation
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import json

class CriticalFixesDiagnostic:
    """Diagnose and fix all critical Phase 2 issues"""
    
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        
    def diagnose_q_value_issue(self):
        """Diagnose why Q-values are all zero"""
        print("🔍 DIAGNOSING Q-VALUE ISSUE")
        print("="*40)
        
        # Test if RL environment is actually learning
        try:
            from rl_environment import BlackjackRLEnv
            env = BlackjackRLEnv()
            
            print("✅ RL Environment loads successfully")
            
            # Check observation space
            obs, _ = env.reset()
            print(f"📊 Observation: {obs}")
            print(f"📊 Obs shape: {obs.shape}")
            print(f"📊 Obs space: {env.observation_space}")
            
            # Test action space
            print(f"🎯 Action space: {env.action_space}")
            
            # Test if environment completes properly
            action = env.action_space.sample()
            obs, reward, done, truncated, info = env.step(action)
            print(f"🎲 Sample action {action}: reward={reward}, done={done}")
            
            # Check if we can load a trained model
            try:
                import os
                model_paths = [
                    "runs/phase1/models/final_model.zip",
                    "runs/f2_4_production/final_model",
                    "runs/phase1_full_corrected/models/final_model.zip"
                ]
                
                for path in model_paths:
                    if os.path.exists(path):
                        print(f"✅ Found model: {path}")
                        
                        # Try to load and test
                        try:
                            from stable_baselines3 import DQN
                            model = DQN.load(path)
                            print(f"✅ Model loaded successfully from {path}")
                            
                            # Test prediction
                            action, _states = model.predict(obs, deterministic=True)
                            print(f"✅ Model prediction works: action={action}")
                            
                            # Get Q-values if possible
                            try:
                                q_values = model.q_net(obs.reshape(1, -1))
                                print(f"📊 Q-values: {q_values}")
                                if torch.all(q_values == 0):
                                    self.issues.append("Q-values are all zero - model not trained properly")
                                else:
                                    print("✅ Q-values are non-zero")
                            except Exception as e:
                                print(f"⚠️  Cannot extract Q-values: {e}")
                                
                            return True
                        except Exception as e:
                            print(f"❌ Cannot load model {path}: {e}")
                
            except ImportError:
                print("❌ Cannot import stable_baselines3")
                self.issues.append("RL training dependencies missing")
                
        except Exception as e:
            print(f"❌ RL Environment error: {e}")
            self.issues.append("RL environment not working properly")
            
        return False
    
    def diagnose_policy_agreement_issue(self):
        """Diagnose why policy agreement is so low"""
        print("\n🔍 DIAGNOSING POLICY AGREEMENT ISSUE")
        print("="*40)
        
        # Test basic strategy implementation
        try:
            from utils.basic_strategy import get_action
            
            test_cases = [
                (12, 4, False),  # Should stand
                (16, 10, False), # Should hit
                (11, 6, False),  # Should double
                (20, 8, False),  # Should stand
            ]
            
            print("📋 Testing Basic Strategy:")
            for player_total, dealer_up, usable_ace in test_cases:
                action = get_action(player_total, dealer_up, usable_ace)
                print(f"   P:{player_total} vs D:{dealer_up} -> {action}")
            
            # Now test if AI gives same actions
            print("\n📋 Testing AI Strategy:")
            
            # Load a model and test same cases
            try:
                # Test with our simple strategy
                simple_actions = []
                for player_total, dealer_up, usable_ace in test_cases:
                    # Simple strategy logic
                    if player_total >= 17:
                        ai_action = "stand"
                    elif player_total <= 11:
                        ai_action = "hit"
                    elif player_total in [12, 13, 14, 15, 16]:
                        ai_action = "stand" if dealer_up <= 6 else "hit"
                    else:
                        ai_action = "hit"
                    
                    simple_actions.append(ai_action)
                    print(f"   P:{player_total} vs D:{dealer_up} -> {ai_action}")
                
                # Compare with basic strategy
                basic_actions = [get_action(pt, du, ua) for pt, du, ua in test_cases]
                
                agreement = sum(1 for a, b in zip(basic_actions, simple_actions) if a == b)
                agreement_rate = agreement / len(test_cases)
                
                print(f"\n📊 Agreement Rate: {agreement_rate:.1%}")
                if agreement_rate < 0.7:
                    self.issues.append(f"Policy agreement too low: {agreement_rate:.1%}")
                else:
                    print("✅ Policy agreement acceptable")
                    
            except Exception as e:
                print(f"❌ AI strategy test failed: {e}")
                self.issues.append("AI strategy implementation broken")
                
        except Exception as e:
            print(f"❌ Basic strategy test failed: {e}")
            self.issues.append("Basic strategy implementation missing or broken")
    
    def diagnose_performance_issue(self):
        """Diagnose why performance is so poor"""
        print("\n🔍 DIAGNOSING PERFORMANCE ISSUE")
        print("="*40)
        
        # Test environment rewards
        print("🎮 Testing Environment Rewards:")
        
        try:
            from URGENT_ENVIRONMENT_FIX import create_fixed_betting_env_v2
            env = create_fixed_betting_env_v2(seed=42, initial_bankroll=10000.0, min_bet=25.0, max_bet=500.0)
            
            rewards = []
            outcomes = []
            
            for i in range(20):
                obs, _ = env.reset()
                env.set_bet_amount(50.0)
                
                # Test different actions
                for action in [0, 1, 2]:  # hit, stand, double
                    obs, _ = env.reset()
                    env.set_bet_amount(50.0)
                    obs, reward, done, truncated, info = env.step(action)
                    
                    if done:
                        rewards.append(reward)
                        outcomes.append(info.get('game_outcome', 'unknown'))
                        
                        if i < 5:  # Print first few for debugging
                            print(f"   Action {action}: reward={reward}, outcome={info.get('game_outcome', 'N/A')}")
            
            # Analyze rewards
            positive_rewards = sum(1 for r in rewards if r > 0)
            negative_rewards = sum(1 for r in rewards if r < 0)
            zero_rewards = sum(1 for r in rewards if r == 0)
            
            print(f"\n📊 Reward Analysis:")
            print(f"   Positive: {positive_rewards}/{len(rewards)} ({positive_rewards/len(rewards):.1%})")
            print(f"   Negative: {negative_rewards}/{len(rewards)} ({negative_rewards/len(rewards):.1%})")
            print(f"   Zero: {zero_rewards}/{len(rewards)} ({zero_rewards/len(rewards):.1%})")
            
            if positive_rewards == 0:
                self.issues.append("Environment never gives positive rewards")
            elif positive_rewards < len(rewards) * 0.3:  # Less than 30% wins
                self.issues.append(f"Win rate too low: {positive_rewards/len(rewards):.1%}")
            else:
                print("✅ Environment reward distribution looks reasonable")
                
        except Exception as e:
            print(f"❌ Environment test failed: {e}")
            self.issues.append("Fixed environment still has issues")
    
    def generate_fix_plan(self):
        """Generate comprehensive fix plan"""
        print("\n🔧 GENERATING FIX PLAN")
        print("="*40)
        
        fixes = []
        
        if any("Q-values" in issue for issue in self.issues):
            fixes.append({
                "priority": "CRITICAL",
                "issue": "Q-values all zero",
                "fix": "Retrain RL model with proper hyperparameters and fixed environment",
                "action": "train_new_model"
            })
        
        if any("Policy agreement" in issue for issue in self.issues):
            fixes.append({
                "priority": "HIGH", 
                "issue": "Policy agreement too low",
                "fix": "Debug AI strategy implementation and fix decision logic",
                "action": "fix_ai_strategy"
            })
        
        if any("Win rate" in issue or "reward" in issue for issue in self.issues):
            fixes.append({
                "priority": "CRITICAL",
                "issue": "Performance catastrophic",
                "fix": "Validate and fix environment reward calculation",
                "action": "fix_environment_rewards"
            })
        
        if any("Environment" in issue for issue in self.issues):
            fixes.append({
                "priority": "URGENT",
                "issue": "Environment issues",
                "fix": "Complete environment validation and testing",
                "action": "validate_environment"
            })
        
        print(f"📋 IDENTIFIED {len(fixes)} CRITICAL FIXES NEEDED:")
        for i, fix in enumerate(fixes, 1):
            print(f"\n{i}. [{fix['priority']}] {fix['issue']}")
            print(f"   Fix: {fix['fix']}")
            print(f"   Action: {fix['action']}")
        
        return fixes
    
    def run_full_diagnosis(self):
        """Run complete diagnosis"""
        print("🚨 CRITICAL FIXES PHASE 2 - FULL DIAGNOSIS")
        print("="*60)
        
        # Run all diagnostics
        q_value_ok = self.diagnose_q_value_issue()
        self.diagnose_policy_agreement_issue()
        self.diagnose_performance_issue()
        
        # Generate fix plan
        fixes = self.generate_fix_plan()
        
        # Summary
        print("\n" + "="*60)
        print("📊 DIAGNOSIS SUMMARY")
        print("="*60)
        
        print(f"🔴 ISSUES IDENTIFIED: {len(self.issues)}")
        for i, issue in enumerate(self.issues, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 FIXES REQUIRED: {len(fixes)}")
        critical_fixes = [f for f in fixes if f['priority'] == 'CRITICAL']
        
        if critical_fixes:
            print("\n🚨 CRITICAL FIXES MUST BE COMPLETED BEFORE PHASE 3:")
            for fix in critical_fixes:
                print(f"   • {fix['issue']}: {fix['fix']}")
        
        # Recommendation
        if len(self.issues) > 2:
            print("\n❌ RECOMMENDATION: DO NOT PROCEED TO PHASE 3")
            print("   Phase 2 has too many critical issues")
        else:
            print("\n⚠️  RECOMMENDATION: FIX ISSUES THEN PROCEED")
            print("   Some issues need resolution but Phase 3 possible after fixes")
        
        return len(self.issues) == 0

def main():
    """Main diagnostic function"""
    diagnostic = CriticalFixesDiagnostic()
    phase2_ready = diagnostic.run_full_diagnosis()
    
    if not phase2_ready:
        print("\n🛑 PHASE 2 NOT READY FOR PHASE 3")
        print("   Complete critical fixes first")
        return False
    else:
        print("\n✅ PHASE 2 READY FOR PHASE 3")
        return True

if __name__ == "__main__":
    main() 
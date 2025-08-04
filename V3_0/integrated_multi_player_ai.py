"""
================================================================================
INTEGRATED MULTI-PLAYER DYNAMIC AI SYSTEM (PHASE 3 - F3.3)
================================================================================

📋 **AMAÇ:**
   Phase 3 complete implementation - Multi-player environment + Dynamic adaptation
   Real-time opponent analysis, strategy modification, ve advanced AI training.

🎯 **F3.3 ÖZELLİKLERİ:**
   • Complete multi-player RL training environment
   • Real-time opponent behavior analysis
   • Dynamic strategy adaptation during play
   • Advanced performance tracking and optimization
   • Player profiling and counter-strategy deployment

🏗️ **ENTEGRASYON:**
   MultiPlayerBlackjackRLEnv + DynamicAdaptationEngine + Advanced Analytics

================================================================================
"""

from __future__ import annotations

import numpy as np
import gymnasium as gym
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import time
from dataclasses import dataclass
import json

# Import our core components
from multi_player_rl_environment import MultiPlayerBlackjackRLEnv, PlayerPosition, PlayerProfile, TableDynamics
from dynamic_adaptation_engine import DynamicAdaptationEngine, OpponentType, StrategyModification
from utils.basic_strategy import get_action

@dataclass
class TrainingSession:
    """Training session tracking and analytics."""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    total_episodes: int = 0
    total_rewards: float = 0.0
    
    # Performance metrics
    win_rate: float = 0.0
    avg_reward_per_episode: float = 0.0
    adaptation_switches: int = 0
    
    # Opponent analysis
    opponents_encountered: Dict[OpponentType, int] = None
    strategy_performance: Dict[StrategyModification, float] = None
    
    # Advanced metrics
    position_advantage_utilized: float = 0.0
    table_dynamics_score: float = 0.0
    
    def __post_init__(self):
        if self.opponents_encountered is None:
            self.opponents_encountered = {}
        if self.strategy_performance is None:
            self.strategy_performance = {}

class IntegratedMultiPlayerAI:
    """
    Complete Multi-Player Dynamic AI System for Phase 3.
    
    Combines multi-player environment, dynamic adaptation engine,
    and advanced analytics for comprehensive blackjack AI training.
    """
    
    def __init__(self,
                 num_players: int = 3,
                 ai_player_id: int = 1,
                 adaptation_rate: float = 0.15,
                 enable_dynamic_adaptation: bool = True,
                 enable_advanced_analytics: bool = True,
                 session_id: Optional[str] = None):
        """
        Initialize Integrated Multi-Player AI System.
        
        Args:
            num_players: Number of players at the table
            ai_player_id: Which player is the AI agent
            adaptation_rate: Rate of dynamic adaptation
            enable_dynamic_adaptation: Enable real-time strategy adaptation
            enable_advanced_analytics: Enable advanced performance tracking
            session_id: Unique identifier for this training session
        """
        self.num_players = num_players
        self.ai_player_id = ai_player_id
        self.adaptation_rate = adaptation_rate
        self.enable_dynamic_adaptation = enable_dynamic_adaptation
        self.enable_advanced_analytics = enable_advanced_analytics
        
        # Initialize core components
        self.env = MultiPlayerBlackjackRLEnv(
            num_players=num_players,
            ai_player_id=ai_player_id,
            position_awareness=True,
            opponent_modeling=True,
            dynamic_adaptation=enable_dynamic_adaptation
        )
        
        if self.enable_dynamic_adaptation:
            self.adaptation_engine = DynamicAdaptationEngine(
                ai_player_id=ai_player_id,
                adaptation_rate=adaptation_rate,
                min_observations=5,  # Faster adaptation for training
                confidence_threshold=0.6
            )
        else:
            self.adaptation_engine = None
            
        # Session tracking
        self.current_session = TrainingSession(
            session_id=session_id or f"session_{int(time.time())}",
            start_time=time.time()
        )
        
        # Performance tracking
        self.episode_rewards: List[float] = []
        self.episode_info: List[Dict] = []
        self.adaptation_history: List[Dict] = []
        
        # Advanced analytics
        if self.enable_advanced_analytics:
            self.analytics = self._initialize_analytics()
        
        # Logging
        self.logger = logging.getLogger("IntegratedMultiPlayerAI")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"Initialized Multi-Player AI: {num_players} players, AI at position {ai_player_id}")
    
    def _initialize_analytics(self) -> Dict[str, Any]:
        """Initialize advanced analytics tracking."""
        return {
            "position_performance": {pos.value: [] for pos in PlayerPosition},
            "opponent_type_performance": {t.value: [] for t in OpponentType},
            "strategy_effectiveness": {s.value: [] for s in StrategyModification},
            "table_dynamics_impact": [],
            "adaptation_timing": [],
            "decision_quality_scores": []
        }
    
    def reset(self, seed: Optional[int] = None) -> Tuple[np.ndarray, Dict]:
        """Reset environment and adaptation systems."""
        obs, info = self.env.reset(seed=seed)
        
        # Reset adaptation engine for new episode
        if self.adaptation_engine:
            self.adaptation_engine.performance_buffer.clear()
            
        return obs, info
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Enhanced step function with dynamic adaptation and analytics.
        
        Args:
            action: Base action from RL agent
            
        Returns:
            Standard gym step output with enhanced info
        """
        # Get base action
        base_action_names = ["stand", "hit", "double", "split"]
        base_action_name = base_action_names[action]
        
        # Apply dynamic adaptation if enabled
        if self.adaptation_engine and self.enable_dynamic_adaptation:
            # Get current state information
            obs = self.env._get_observation()
            hand_total = int(obs[0])
            dealer_upcard = int(obs[1])
            true_count = obs[3]
            
            # Get adapted action
            adapted_action_name = self.adaptation_engine.get_strategy_modification(
                base_action_name, hand_total, dealer_upcard, true_count
            )
            
            # Convert back to action index
            try:
                adapted_action = base_action_names.index(adapted_action_name)
            except ValueError:
                adapted_action = action  # Fallback to original
                
            # Track adaptation
            if adapted_action != action:
                self.adaptation_history.append({
                    "episode": len(self.episode_rewards),
                    "original_action": base_action_name,
                    "adapted_action": adapted_action_name,
                    "hand_total": hand_total,
                    "dealer_upcard": dealer_upcard,
                    "strategy": self.adaptation_engine.current_strategy.value
                })
        else:
            adapted_action = action
            adapted_action_name = base_action_name
        
        # Execute action in environment
        obs, reward, done, truncated, info = self.env.step(adapted_action)
        
        # Record opponent observations for adaptation
        if self.adaptation_engine:
            self._record_opponent_observations()
            self.adaptation_engine.record_performance(reward)
        
        # Enhanced info with adaptation details
        enhanced_info = info.copy()
        enhanced_info.update({
            "base_action": base_action_name,
            "adapted_action": adapted_action_name,
            "adaptation_active": self.enable_dynamic_adaptation,
            "current_strategy": self.adaptation_engine.current_strategy.value if self.adaptation_engine else "baseline"
        })
        
        # Record analytics if enabled
        if self.enable_advanced_analytics and done:
            self._record_episode_analytics(reward, enhanced_info)
        
        return obs, reward, done, truncated, enhanced_info
    
    def _record_opponent_observations(self):
        """Record opponent actions for adaptation engine."""
        if not self.adaptation_engine:
            return
            
        # Get current environment state
        current_player = self.env.current_player
        
        # Record observations for non-AI players
        for i, player in enumerate(self.env.players):
            if i == self.ai_player_id or not player.hands:
                continue
                
            hand = player.hands[0]
            if not hasattr(hand, 'last_action_recorded'):
                # Simulate opponent action observation
                hand_total, usable_ace = hand.value()
                dealer_upcard = self.env.dealer.hand.cards[0].blackjack_value()
                
                # Estimate action based on hand state (simplified)
                if hand.is_busted:
                    action = "hit"  # Led to bust
                elif len(hand.cards) == 2:
                    action = "stand"  # Simplified
                else:
                    action = "hit"
                    
                self.adaptation_engine.observe_opponent_action(
                    player_id=i,
                    action=action,
                    hand_total=hand_total,
                    dealer_upcard=dealer_upcard,
                    usable_ace=usable_ace
                )
                
                hand.last_action_recorded = True
    
    def _record_episode_analytics(self, reward: float, info: Dict):
        """Record detailed analytics for the episode."""
        if not self.enable_advanced_analytics:
            return
            
        # Position performance
        ai_position = self.env.position_map[self.ai_player_id]
        self.analytics["position_performance"][ai_position.value].append(reward)
        
        # Strategy effectiveness
        current_strategy = info.get("current_strategy", "baseline")
        self.analytics["strategy_effectiveness"][current_strategy].append(reward)
        
        # Table dynamics impact
        table_dynamics_score = self._calculate_table_dynamics_score()
        self.analytics["table_dynamics_impact"].append({
            "reward": reward,
            "dynamics_score": table_dynamics_score,
            "num_opponents": len(self.env.players) - 1
        })
        
        # Decision quality (simplified)
        decision_quality = self._calculate_decision_quality(info)
        self.analytics["decision_quality_scores"].append(decision_quality)
    
    def _calculate_table_dynamics_score(self) -> float:
        """Calculate a composite score for current table dynamics."""
        if not self.adaptation_engine:
            return 0.5
            
        # Factors: opponent diversity, adaptation confidence, position advantage
        opponent_types = len(set(data.opponent_type for data in self.adaptation_engine.opponent_data.values()))
        max_types = len(OpponentType)
        diversity_score = opponent_types / max_types
        
        # Average confidence in opponent classification
        confidences = [data.confidence for data in self.adaptation_engine.opponent_data.values()]
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Position advantage (late position is better)
        position_score = self.env._get_position_value()
        
        return (diversity_score + avg_confidence + position_score) / 3
    
    def _calculate_decision_quality(self, info: Dict) -> float:
        """Calculate decision quality score based on adaptations and outcomes."""
        base_score = 0.5
        
        # Bonus for using adaptations
        if info.get("base_action") != info.get("adapted_action"):
            base_score += 0.2
            
        # Bonus for confident opponent classification
        if self.adaptation_engine:
            classified_opponents = len([d for d in self.adaptation_engine.opponent_data.values() 
                                      if d.confidence > 0.7])
            base_score += min(0.3, classified_opponents * 0.1)
            
        return min(1.0, base_score)
    
    def train_episode(self, max_steps: int = 100) -> Tuple[float, Dict]:
        """
        Train one complete episode with dynamic adaptation.
        
        Args:
            max_steps: Maximum steps per episode
            
        Returns:
            Total episode reward and info dictionary
        """
        obs, info = self.reset()
        total_reward = 0.0
        steps = 0
        episode_info = {
            "adaptations_made": 0,
            "opponents_classified": 0,
            "strategy_switches": 0,
            "position": self.env.position_map[self.ai_player_id].value
        }
        
        # Track initial strategy
        initial_strategy = self.adaptation_engine.current_strategy if self.adaptation_engine else None
        
        while steps < max_steps:
            # Select action (for training, this would come from RL agent)
            # For demo, use basic strategy as base
            hand_total = int(obs[0])
            dealer_upcard = int(obs[1])
            usable_ace = bool(obs[2])
            
            base_action = get_action(hand_total, dealer_upcard, usable_ace)
            action_map = {"stand": 0, "hit": 1, "double": 2, "split": 3}
            action = action_map.get(base_action, 1)
            
            # Execute step
            obs, reward, done, truncated, step_info = self.step(action)
            total_reward += reward
            steps += 1
            
            # Track adaptations
            if step_info.get("base_action") != step_info.get("adapted_action"):
                episode_info["adaptations_made"] += 1
                
            if done or truncated:
                break
        
        # Final episode statistics
        if self.adaptation_engine:
            episode_info["opponents_classified"] = len([
                d for d in self.adaptation_engine.opponent_data.values() 
                if d.confidence > 0.6
            ])
            
            final_strategy = self.adaptation_engine.current_strategy
            if initial_strategy != final_strategy:
                episode_info["strategy_switches"] = 1
                
        # Record episode
        self.episode_rewards.append(total_reward)
        self.episode_info.append(episode_info)
        
        # Update session statistics
        self._update_session_stats(total_reward, episode_info)
        
        return total_reward, episode_info
    
    def _update_session_stats(self, reward: float, episode_info: Dict):
        """Update session-level statistics."""
        session = self.current_session
        session.total_episodes += 1
        session.total_rewards += reward
        session.adaptation_switches += episode_info.get("strategy_switches", 0)
        
        # Calculate running averages
        session.avg_reward_per_episode = session.total_rewards / session.total_episodes
        session.win_rate = len([r for r in self.episode_rewards if r > 0]) / len(self.episode_rewards)
        
        # Update opponent encounters
        if self.adaptation_engine:
            for data in self.adaptation_engine.opponent_data.values():
                if data.confidence > 0.6:
                    opp_type = data.opponent_type
                    session.opponents_encountered[opp_type] = session.opponents_encountered.get(opp_type, 0) + 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        summary = {
            "session_info": {
                "session_id": self.current_session.session_id,
                "episodes_completed": len(self.episode_rewards),
                "total_reward": sum(self.episode_rewards),
                "avg_reward": np.mean(self.episode_rewards) if self.episode_rewards else 0.0,
                "win_rate": len([r for r in self.episode_rewards if r > 0]) / len(self.episode_rewards) if self.episode_rewards else 0.0
            },
            "adaptation_summary": {},
            "analytics": {}
        }
        
        # Adaptation summary
        if self.adaptation_engine:
            summary["adaptation_summary"] = self.adaptation_engine.get_adaptation_summary()
            summary["adaptation_history"] = self.adaptation_history[-10:]  # Last 10 adaptations
            
        # Advanced analytics
        if self.enable_advanced_analytics and self.analytics:
            summary["analytics"] = self._generate_analytics_summary()
            
        return summary
    
    def _generate_analytics_summary(self) -> Dict[str, Any]:
        """Generate summary of advanced analytics."""
        analytics_summary = {}
        
        # Position performance analysis
        for position, rewards in self.analytics["position_performance"].items():
            if rewards:
                analytics_summary[f"{position}_performance"] = {
                    "avg_reward": np.mean(rewards),
                    "win_rate": len([r for r in rewards if r > 0]) / len(rewards),
                    "episodes": len(rewards)
                }
        
        # Strategy effectiveness
        for strategy, rewards in self.analytics["strategy_effectiveness"].items():
            if rewards:
                analytics_summary[f"{strategy}_effectiveness"] = {
                    "avg_reward": np.mean(rewards),
                    "usage_count": len(rewards),
                    "success_rate": len([r for r in rewards if r > 0]) / len(rewards)
                }
        
        # Decision quality
        if self.analytics["decision_quality_scores"]:
            analytics_summary["decision_quality"] = {
                "avg_score": np.mean(self.analytics["decision_quality_scores"]),
                "improvement_trend": self._calculate_improvement_trend()
            }
            
        return analytics_summary
    
    def _calculate_improvement_trend(self) -> str:
        """Calculate if decision quality is improving over time."""
        scores = self.analytics["decision_quality_scores"]
        if len(scores) < 10:
            return "insufficient_data"
            
        # Compare first half with second half
        mid = len(scores) // 2
        first_half = np.mean(scores[:mid])
        second_half = np.mean(scores[mid:])
        
        if second_half > first_half + 0.05:
            return "improving"
        elif second_half < first_half - 0.05:
            return "declining"
        else:
            return "stable"
    
    def save_session_data(self, filepath: str):
        """Save session data to file."""
        session_data = {
            "session": self.current_session.__dict__,
            "episode_rewards": self.episode_rewards,
            "episode_info": self.episode_info,
            "adaptation_history": self.adaptation_history,
            "performance_summary": self.get_performance_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
            
        self.logger.info(f"Session data saved to {filepath}")
    
    def load_session_data(self, filepath: str):
        """Load session data from file."""
        with open(filepath, 'r') as f:
            session_data = json.load(f)
            
        # Restore session data
        self.episode_rewards = session_data.get("episode_rewards", [])
        self.episode_info = session_data.get("episode_info", [])
        self.adaptation_history = session_data.get("adaptation_history", [])
        
        self.logger.info(f"Session data loaded from {filepath}")


# Factory function
def create_integrated_ai(**kwargs) -> IntegratedMultiPlayerAI:
    """Create Integrated Multi-Player AI with given parameters."""
    return IntegratedMultiPlayerAI(**kwargs)


# Training utilities
def run_training_session(ai_system: IntegratedMultiPlayerAI, 
                        num_episodes: int = 100,
                        save_results: bool = True) -> Dict[str, Any]:
    """
    Run a complete training session.
    
    Args:
        ai_system: Integrated AI system
        num_episodes: Number of episodes to train
        save_results: Whether to save results to file
        
    Returns:
        Training session results
    """
    print(f"🚀 Starting training session: {num_episodes} episodes")
    
    start_time = time.time()
    episode_rewards = []
    
    for episode in range(num_episodes):
        reward, info = ai_system.train_episode()
        episode_rewards.append(reward)
        
        # Progress reporting
        if (episode + 1) % 20 == 0:
            avg_reward = np.mean(episode_rewards[-20:])
            print(f"Episode {episode + 1}/{num_episodes}: Avg Reward (last 20): {avg_reward:.3f}")
            
    end_time = time.time()
    
    # Generate final results
    results = ai_system.get_performance_summary()
    results["training_info"] = {
        "episodes_trained": num_episodes,
        "training_time": end_time - start_time,
        "final_avg_reward": np.mean(episode_rewards[-50:]) if len(episode_rewards) >= 50 else np.mean(episode_rewards)
    }
    
    # Save results if requested
    if save_results:
        filename = f"training_session_{ai_system.current_session.session_id}.json"
        ai_system.save_session_data(filename)
        results["saved_to"] = filename
        
    return results


# Test the integrated system
if __name__ == "__main__":
    print("🧪 TESTING INTEGRATED MULTI-PLAYER AI SYSTEM")
    
    # Create integrated AI
    ai_system = IntegratedMultiPlayerAI(
        num_players=4,
        ai_player_id=2,  # Late-middle position
        adaptation_rate=0.2,
        enable_dynamic_adaptation=True,
        enable_advanced_analytics=True
    )
    
    print("✅ Integrated AI System created successfully")
    print(f"👥 Players: {ai_system.num_players}")
    print(f"🤖 AI Position: {ai_system.ai_player_id}")
    print(f"🎯 Adaptation: {ai_system.enable_dynamic_adaptation}")
    print(f"📊 Analytics: {ai_system.enable_advanced_analytics}")
    
    # Run a short training session
    print(f"\n🏃 Running training session...")
    results = run_training_session(ai_system, num_episodes=10, save_results=False)
    
    print(f"\n📈 TRAINING RESULTS:")
    session_info = results["session_info"]
    print(f"Episodes: {session_info['episodes_completed']}")
    print(f"Avg Reward: {session_info['avg_reward']:.3f}")
    print(f"Win Rate: {session_info['win_rate']:.1%}")
    
    # Adaptation summary
    if "adaptation_summary" in results:
        adapt_summary = results["adaptation_summary"]
        print(f"\n🎭 ADAPTATION SUMMARY:")
        print(f"Current Strategy: {adapt_summary['current_strategy']}")
        print(f"Opponents Classified: {adapt_summary['opponents_classified']}")
        
    print(f"\n✅ Integrated Multi-Player AI System test complete!") 
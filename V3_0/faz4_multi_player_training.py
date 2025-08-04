"""
================================================================================
FAZ 4.0 - COMPREHENSIVE MULTI-PLAYER TRAINING SYSTEM (F4.7)
================================================================================

📋 **AMAÇ:**
   FAZ 4.0 F4.7 - Complete multi-player training orchestration system.
   All FAZ 4.0 components entegre edilmiş comprehensive training pipeline.

🎯 **F4.7 ÖZELLİKLERİ:**
   • Hierarchical player classification training
   • Advanced budget optimization integration
   • Dynamic adaptation in multi-player scenarios
   • Comprehensive performance tracking
   • Real-world scenario simulation

🏗️ **TRAINING PIPELINE:**
   • Multi-scenario training environments
   • Progressive difficulty levels
   • Performance benchmarking
   • Model evaluation ve comparison
   • Production readiness assessment

================================================================================
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Import all FAZ 4.0 components
from faz4_enhanced_multi_player_system import FAZ4EnhancedMultiPlayerEnv, create_faz4_integrated_ai
from utils.hierarchical_player_classification import HierarchicalPlayerClassifier, MainPlayerType
from faz4_budget_optimization import FAZ4BudgetOptimizer, BudgetStrategy, OptimizationContext
from utils.basic_strategy import get_action

class TrainingScenario(Enum):
    """Training scenario types"""
    BEGINNER_TABLE = "beginner_table"           # Easy opponents
    MIXED_SKILL = "mixed_skill"                 # Variety of skill levels
    AGGRESSIVE_TABLE = "aggressive_table"       # High-risk players
    CONSERVATIVE_TABLE = "conservative_table"   # Low-risk players
    COUNTER_HEAVY = "counter_heavy"             # Multiple card counters
    CASINO_SIMULATION = "casino_simulation"     # Realistic casino environment
    STRESS_TEST = "stress_test"                 # High pressure scenarios

class TrainingDifficulty(Enum):
    """Training difficulty levels"""
    EASY = "easy"           # Favorable conditions
    MEDIUM = "medium"       # Balanced conditions
    HARD = "hard"           # Challenging conditions
    EXTREME = "extreme"     # Maximum difficulty

@dataclass
class TrainingConfiguration:
    """Configuration for training scenarios"""
    scenario: TrainingScenario
    difficulty: TrainingDifficulty
    num_players: int = 4
    ai_position: int = 2
    episode_count: int = 100
    
    # Environment settings
    enable_heat_simulation: bool = True
    enable_hierarchical_classification: bool = True
    enable_budget_optimization: bool = True
    
    # Training parameters
    adaptation_rate: float = 0.15
    learning_rate_modifier: float = 1.0
    exploration_factor: float = 0.1
    
    # Performance targets
    target_win_rate: float = 0.55
    target_avg_reward: float = 0.2
    target_consistency: float = 0.8

@dataclass
class TrainingMetrics:
    """Comprehensive training performance metrics"""
    scenario: str
    difficulty: str
    
    # Basic performance
    total_episodes: int = 0
    total_reward: float = 0.0
    avg_reward: float = 0.0
    win_rate: float = 0.0
    
    # Advanced metrics
    classification_accuracy: float = 0.0
    adaptation_success_rate: float = 0.0
    budget_optimization_score: float = 0.0
    
    # Consistency metrics
    reward_variance: float = 0.0
    performance_stability: float = 0.0
    learning_curve_trend: str = "unknown"
    
    # Player intelligence metrics
    player_type_accuracy: Dict[str, float] = field(default_factory=dict)
    table_adaptation_rate: float = 0.0
    heat_management_score: float = 0.0
    
    # Training efficiency
    training_time: float = 0.0
    convergence_episode: int = 0
    final_confidence: float = 0.0

class FAZ4MultiPlayerTrainer:
    """
    Comprehensive Multi-Player Training System for FAZ 4.0.
    
    Orchestrates training across multiple scenarios with all FAZ 4.0
    components integrated for complete system validation.
    """
    
    def __init__(self,
                 output_dir: str = "faz4_training_results",
                 enable_logging: bool = True,
                 enable_visualization: bool = True):
        """
        Initialize FAZ 4.0 Multi-Player Trainer.
        
        Args:
            output_dir: Directory for training results
            enable_logging: Enable detailed logging
            enable_visualization: Enable training visualizations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.enable_logging = enable_logging
        self.enable_visualization = enable_visualization
        
        # Training state
        self.training_sessions: List[TrainingMetrics] = []
        self.current_session: Optional[TrainingMetrics] = None
        
        # Performance tracking
        self.performance_history: Dict[str, List[float]] = {}
        self.learning_curves: Dict[str, List[float]] = {}
        
        # Component integrations
        self.hierarchical_classifier = HierarchicalPlayerClassifier()
        self.budget_optimizer = None  # Will be created per session
        
        # Training configurations
        self.training_scenarios = self._initialize_training_scenarios()
        
        # Logging
        self.logger = logging.getLogger("FAZ4MultiPlayerTrainer")
        if enable_logging:
            self.logger.setLevel(logging.INFO)
            handler = logging.FileHandler(self.output_dir / "training.log")
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.info("FAZ 4.0 Multi-Player Trainer initialized")
    
    def _initialize_training_scenarios(self) -> Dict[str, TrainingConfiguration]:
        """Initialize comprehensive training scenario configurations."""
        return {
            "beginner_friendly": TrainingConfiguration(
                scenario=TrainingScenario.BEGINNER_TABLE,
                difficulty=TrainingDifficulty.EASY,
                num_players=3,
                ai_position=2,
                episode_count=50,
                target_win_rate=0.65,
                target_avg_reward=0.3
            ),
            "mixed_practice": TrainingConfiguration(
                scenario=TrainingScenario.MIXED_SKILL,
                difficulty=TrainingDifficulty.MEDIUM,
                num_players=4,
                ai_position=2,
                episode_count=100,
                target_win_rate=0.55,
                target_avg_reward=0.2
            ),
            "aggressive_challenge": TrainingConfiguration(
                scenario=TrainingScenario.AGGRESSIVE_TABLE,
                difficulty=TrainingDifficulty.HARD,
                num_players=5,
                ai_position=3,
                episode_count=75,
                target_win_rate=0.45,
                target_avg_reward=0.1
            ),
            "conservative_exploitation": TrainingConfiguration(
                scenario=TrainingScenario.CONSERVATIVE_TABLE,
                difficulty=TrainingDifficulty.MEDIUM,
                num_players=4,
                ai_position=1,
                episode_count=60,
                target_win_rate=0.65,
                target_avg_reward=0.35
            ),
            "counter_awareness": TrainingConfiguration(
                scenario=TrainingScenario.COUNTER_HEAVY,
                difficulty=TrainingDifficulty.HARD,
                num_players=5,
                ai_position=4,
                episode_count=80,
                target_win_rate=0.50,
                target_avg_reward=0.15
            ),
            "casino_realism": TrainingConfiguration(
                scenario=TrainingScenario.CASINO_SIMULATION,
                difficulty=TrainingDifficulty.HARD,
                num_players=6,
                ai_position=3,
                episode_count=150,
                enable_heat_simulation=True,
                target_win_rate=0.52,
                target_avg_reward=0.18
            ),
            "extreme_stress": TrainingConfiguration(
                scenario=TrainingScenario.STRESS_TEST,
                difficulty=TrainingDifficulty.EXTREME,
                num_players=6,
                ai_position=1,
                episode_count=200,
                adaptation_rate=0.3,
                target_win_rate=0.48,
                target_avg_reward=0.05
            )
        }
    
    def run_comprehensive_training(self) -> Dict[str, Any]:
        """
        Run comprehensive training across all scenarios.
        
        Returns:
            Complete training results and analysis
        """
        print("🚀 STARTING FAZ 4.0 COMPREHENSIVE MULTI-PLAYER TRAINING")
        print("=" * 70)
        
        start_time = time.time()
        
        training_results = {
            "training_sessions": [],
            "overall_metrics": {},
            "scenario_rankings": {},
            "readiness_assessment": {}
        }
        
        # Run training for each scenario
        for scenario_name, config in self.training_scenarios.items():
            print(f"\n🎯 Training Scenario: {scenario_name.replace('_', ' ').title()}")
            print(f"   Difficulty: {config.difficulty.value.title()}")
            print(f"   Episodes: {config.episode_count}")
            
            session_results = self._run_training_session(scenario_name, config)
            training_results["training_sessions"].append(session_results)
            
            # Progress reporting
            print(f"   ✅ Win Rate: {session_results.win_rate:.1%}")
            print(f"   📊 Avg Reward: {session_results.avg_reward:.3f}")
            print(f"   🎯 Target Achievement: {'✅' if self._meets_targets(session_results, config) else '❌'}")
        
        end_time = time.time()
        
        # Generate comprehensive analysis
        training_results["overall_metrics"] = self._calculate_overall_metrics()
        training_results["scenario_rankings"] = self._rank_scenarios()
        training_results["readiness_assessment"] = self._assess_production_readiness()
        training_results["training_time"] = end_time - start_time
        
        # Save results
        self._save_training_results(training_results)
        
        # Generate visualizations
        if self.enable_visualization:
            self._generate_training_visualizations()
        
        print(f"\n🎉 COMPREHENSIVE TRAINING COMPLETE!")
        print(f"⏱️  Total Training Time: {end_time - start_time:.1f} seconds")
        print(f"📁 Results saved to: {self.output_dir}")
        
        return training_results
    
    def _run_training_session(self, scenario_name: str, config: TrainingConfiguration) -> TrainingMetrics:
        """Run individual training session for a scenario."""
        
        # Initialize session metrics
        session_metrics = TrainingMetrics(
            scenario=scenario_name,
            difficulty=config.difficulty.value
        )
        
        self.current_session = session_metrics
        session_start_time = time.time()
        
        # Create environment with scenario-specific settings
        env = self._create_scenario_environment(config)
        
        # Create budget optimizer for this session
        self.budget_optimizer = FAZ4BudgetOptimizer(
            initial_bankroll=10000.0,
            strategy=BudgetStrategy.HIERARCHICAL
        )
        self.budget_optimizer.set_hierarchical_classifier(self.hierarchical_classifier)
        
        # Track episode performance
        episode_rewards = []
        episode_classifications = []
        episode_adaptations = []
        
        # Training loop
        for episode in range(config.episode_count):
            episode_reward, episode_info = self._run_training_episode(env, config)
            
            episode_rewards.append(episode_reward)
            episode_classifications.append(episode_info.get("classification_accuracy", 0.0))
            episode_adaptations.append(episode_info.get("successful_adaptations", 0))
            
            # Progress tracking
            if (episode + 1) % 25 == 0:
                recent_avg = np.mean(episode_rewards[-25:])
                print(f"     Episode {episode + 1}: Recent Avg Reward = {recent_avg:.3f}")
        
        # Calculate session metrics
        session_metrics.total_episodes = config.episode_count
        session_metrics.total_reward = sum(episode_rewards)
        session_metrics.avg_reward = np.mean(episode_rewards)
        session_metrics.win_rate = len([r for r in episode_rewards if r > 0]) / len(episode_rewards)
        session_metrics.reward_variance = np.var(episode_rewards)
        
        # Advanced metrics
        session_metrics.classification_accuracy = np.mean(episode_classifications)
        session_metrics.adaptation_success_rate = np.mean(episode_adaptations) / 10  # Normalize
        session_metrics.performance_stability = self._calculate_stability(episode_rewards)
        session_metrics.learning_curve_trend = self._analyze_learning_trend(episode_rewards)
        
        # Budget optimization metrics
        if self.budget_optimizer:
            budget_summary = self.budget_optimizer.get_optimization_summary()
            session_metrics.budget_optimization_score = self._calculate_budget_score(budget_summary)
        
        session_metrics.training_time = time.time() - session_start_time
        session_metrics.final_confidence = self._calculate_final_confidence(episode_rewards)
        
        # Store performance history
        self.performance_history[scenario_name] = episode_rewards
        self.learning_curves[scenario_name] = self._calculate_moving_average(episode_rewards, 10)
        
        # Add to training sessions
        self.training_sessions.append(session_metrics)
        
        return session_metrics
    
    def _create_scenario_environment(self, config: TrainingConfiguration) -> FAZ4EnhancedMultiPlayerEnv:
        """Create environment tailored to specific training scenario."""
        env = FAZ4EnhancedMultiPlayerEnv(
            num_players=config.num_players,
            ai_player_id=config.ai_position,
            enable_faz4_features=True,
            behavior_analysis_enabled=config.enable_hierarchical_classification,
            advanced_adaptation=True,
            table_heat_simulation=config.enable_heat_simulation
        )
        
        # Set hierarchical classifier
        if config.enable_hierarchical_classification:
            env.behavior_analyzer = self.hierarchical_classifier
        
        return env
    
    def _run_training_episode(self, env: FAZ4EnhancedMultiPlayerEnv, config: TrainingConfiguration) -> Tuple[float, Dict]:
        """Run single training episode with all FAZ 4.0 features."""
        obs, info = env.reset()
        total_reward = 0.0
        steps = 0
        max_steps = 50
        
        episode_info = {
            "classification_accuracy": 0.0,
            "successful_adaptations": 0,
            "budget_decisions": 0,
            "heat_incidents": 0
        }
        
        # Episode tracking
        classifications = []
        adaptations = 0
        budget_decisions = 0
        
        while steps < max_steps:
            # Get basic strategy action
            hand_total = int(obs[0])
            dealer_upcard = int(obs[1])
            usable_ace = bool(obs[2])
            true_count = obs[3]
            
            base_action = get_action(hand_total, dealer_upcard, usable_ace)
            action_map = {"stand": 0, "hit": 1, "double": 2, "split": 3}
            action = action_map.get(base_action, 1)
            
            # Budget optimization decision
            if self.budget_optimizer and config.enable_budget_optimization:
                # Create optimization context
                context = OptimizationContext(
                    true_count=true_count,
                    table_heat_level=info.get("faz4_table_dynamics", {}).get("table_heat_level", 0.0),
                    classification_confidence=env.faz4_table_dynamics.classification_confidence,
                    session_performance=total_reward * 100
                )
                
                bet_size, bet_analysis = self.budget_optimizer.optimize_bet_size(context)
                budget_decisions += 1
            
            # Execute step
            obs, reward, done, truncated, step_info = env.step(action)
            total_reward += reward
            steps += 1
            
            # Track FAZ 4.0 metrics
            if "faz4_table_dynamics" in step_info:
                faz4_info = step_info["faz4_table_dynamics"]
                
                # Classification tracking
                if faz4_info.get("classification_confidence", 0) > 0.6:
                    classifications.append(faz4_info["classification_confidence"])
                
                # Adaptation tracking
                if step_info.get("adaptation_active", False):
                    adaptations += 1
                
                # Heat tracking
                if faz4_info.get("table_heat_level", 0) > 0.5:
                    episode_info["heat_incidents"] += 1
            
            # Update budget optimizer
            if self.budget_optimizer and config.enable_budget_optimization:
                self.budget_optimizer.update_result(reward, bet_size, context)
            
            if done or truncated:
                break
        
        # Calculate episode metrics
        episode_info["classification_accuracy"] = np.mean(classifications) if classifications else 0.0
        episode_info["successful_adaptations"] = adaptations
        episode_info["budget_decisions"] = budget_decisions
        
        return total_reward, episode_info
    
    def _meets_targets(self, metrics: TrainingMetrics, config: TrainingConfiguration) -> bool:
        """Check if training session meets target performance."""
        return (
            metrics.win_rate >= config.target_win_rate and
            metrics.avg_reward >= config.target_avg_reward
        )
    
    def _calculate_stability(self, rewards: List[float]) -> float:
        """Calculate performance stability score."""
        if len(rewards) < 10:
            return 0.0
        
        # Use coefficient of variation (inverse of stability)
        mean_reward = np.mean(rewards)
        std_reward = np.std(rewards)
        
        if abs(mean_reward) < 1e-6:
            return 0.0
        
        cv = std_reward / abs(mean_reward)
        stability = max(0.0, 1.0 - cv)
        
        return stability
    
    def _analyze_learning_trend(self, rewards: List[float]) -> str:
        """Analyze learning curve trend."""
        if len(rewards) < 20:
            return "insufficient_data"
        
        # Compare first half with second half
        mid = len(rewards) // 2
        first_half = np.mean(rewards[:mid])
        second_half = np.mean(rewards[mid:])
        
        improvement = (second_half - first_half) / (abs(first_half) + 1e-6)
        
        if improvement > 0.1:
            return "improving"
        elif improvement < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_budget_score(self, budget_summary: Dict[str, Any]) -> float:
        """Calculate budget optimization effectiveness score."""
        if not budget_summary:
            return 0.0
        
        # Composite score based on multiple factors
        performance = budget_summary["budget_metrics"]
        risk_metrics = budget_summary["risk_metrics"]
        
        # Positive return component
        return_score = max(0.0, min(1.0, performance["total_return"] + 0.5))
        
        # Risk management component
        risk_score = max(0.0, 1.0 - risk_metrics["risk_of_ruin"])
        
        # Sharpe ratio component
        sharpe_score = max(0.0, min(1.0, budget_summary["performance_metrics"]["sharpe_ratio"] + 1.0))
        
        return (return_score + risk_score + sharpe_score) / 3
    
    def _calculate_final_confidence(self, rewards: List[float]) -> float:
        """Calculate final confidence in training results."""
        if not rewards:
            return 0.0
        
        # Factors: consistency, positive trend, sample size
        consistency = self._calculate_stability(rewards)
        trend_factor = 1.0 if self._analyze_learning_trend(rewards) in ["improving", "stable"] else 0.5
        sample_factor = min(1.0, len(rewards) / 100)
        
        confidence = (consistency + trend_factor + sample_factor) / 3
        return confidence
    
    def _calculate_moving_average(self, data: List[float], window: int) -> List[float]:
        """Calculate moving average for learning curves."""
        if len(data) < window:
            return data
        
        moving_avg = []
        for i in range(len(data)):
            start_idx = max(0, i - window + 1)
            avg = np.mean(data[start_idx:i+1])
            moving_avg.append(avg)
        
        return moving_avg
    
    def _calculate_overall_metrics(self) -> Dict[str, Any]:
        """Calculate overall training metrics across all scenarios."""
        if not self.training_sessions:
            return {}
        
        # Aggregate metrics
        total_episodes = sum(s.total_episodes for s in self.training_sessions)
        avg_win_rate = np.mean([s.win_rate for s in self.training_sessions])
        avg_reward = np.mean([s.avg_reward for s in self.training_sessions])
        
        # Performance distribution
        win_rates = [s.win_rate for s in self.training_sessions]
        avg_rewards = [s.avg_reward for s in self.training_sessions]
        
        return {
            "total_episodes_trained": total_episodes,
            "average_win_rate": avg_win_rate,
            "average_reward": avg_reward,
            "win_rate_std": np.std(win_rates),
            "reward_std": np.std(avg_rewards),
            "scenarios_completed": len(self.training_sessions),
            "overall_classification_accuracy": np.mean([s.classification_accuracy for s in self.training_sessions]),
            "overall_adaptation_rate": np.mean([s.adaptation_success_rate for s in self.training_sessions])
        }
    
    def _rank_scenarios(self) -> Dict[str, Any]:
        """Rank training scenarios by performance."""
        if not self.training_sessions:
            return {}
        
        # Create performance scores
        scenario_scores = []
        for session in self.training_sessions:
            # Composite score: win_rate (40%) + avg_reward (30%) + stability (20%) + efficiency (10%)
            score = (
                session.win_rate * 0.4 +
                max(0, session.avg_reward + 0.5) * 0.3 +  # Normalize negative rewards
                session.performance_stability * 0.2 +
                session.final_confidence * 0.1
            )
            
            scenario_scores.append({
                "scenario": session.scenario,
                "difficulty": session.difficulty,
                "score": score,
                "win_rate": session.win_rate,
                "avg_reward": session.avg_reward
            })
        
        # Sort by score
        scenario_scores.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "rankings": scenario_scores,
            "best_scenario": scenario_scores[0]["scenario"],
            "worst_scenario": scenario_scores[-1]["scenario"],
            "score_range": scenario_scores[0]["score"] - scenario_scores[-1]["score"]
        }
    
    def _assess_production_readiness(self) -> Dict[str, Any]:
        """Assess overall production readiness of the system."""
        if not self.training_sessions:
            return {"ready": False, "score": 0.0}
        
        # Readiness criteria
        criteria = {
            "minimum_win_rate": 0.50,
            "minimum_avg_reward": 0.10,
            "minimum_stability": 0.60,
            "minimum_classification_accuracy": 0.70,
            "minimum_scenarios_passed": 5
        }
        
        # Check each criterion
        results = {}
        
        # Win rate check
        avg_win_rate = np.mean([s.win_rate for s in self.training_sessions])
        results["win_rate_check"] = avg_win_rate >= criteria["minimum_win_rate"]
        
        # Average reward check
        avg_reward = np.mean([s.avg_reward for s in self.training_sessions])
        results["reward_check"] = avg_reward >= criteria["minimum_avg_reward"]
        
        # Stability check
        avg_stability = np.mean([s.performance_stability for s in self.training_sessions])
        results["stability_check"] = avg_stability >= criteria["minimum_stability"]
        
        # Classification accuracy check
        avg_classification = np.mean([s.classification_accuracy for s in self.training_sessions])
        results["classification_check"] = avg_classification >= criteria["minimum_classification_accuracy"]
        
        # Scenarios passed check
        passed_scenarios = sum(1 for s in self.training_sessions if s.win_rate >= 0.48)
        results["scenarios_check"] = passed_scenarios >= criteria["minimum_scenarios_passed"]
        
        # Overall readiness
        checks_passed = sum(results.values())
        readiness_score = checks_passed / len(criteria)
        ready = readiness_score >= 0.8  # 80% of criteria must pass
        
        return {
            "ready": ready,
            "readiness_score": readiness_score,
            "checks_passed": checks_passed,
            "total_checks": len(criteria),
            "detailed_results": results,
            "criteria": criteria,
            "performance_summary": {
                "avg_win_rate": avg_win_rate,
                "avg_reward": avg_reward,
                "avg_stability": avg_stability,
                "avg_classification": avg_classification,
                "scenarios_passed": passed_scenarios
            }
        }
    
    def _save_training_results(self, results: Dict[str, Any]):
        """Save comprehensive training results."""
        # Save main results
        results_file = self.output_dir / "faz4_training_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save performance history
        history_file = self.output_dir / "performance_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.performance_history, f, indent=2)
        
        self.logger.info(f"Training results saved to {results_file}")
    
    def _generate_training_visualizations(self):
        """Generate comprehensive training visualizations."""
        try:
            # Set up the plotting style
            plt.style.use('default')
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle('FAZ 4.0 Multi-Player Training Results', fontsize=16)
            
            # 1. Win rates by scenario
            scenarios = [s.scenario for s in self.training_sessions]
            win_rates = [s.win_rate for s in self.training_sessions]
            
            axes[0, 0].bar(range(len(scenarios)), win_rates)
            axes[0, 0].set_title('Win Rates by Scenario')
            axes[0, 0].set_xticks(range(len(scenarios)))
            axes[0, 0].set_xticklabels([s.replace('_', '\n') for s in scenarios], rotation=45)
            axes[0, 0].set_ylabel('Win Rate')
            axes[0, 0].axhline(y=0.5, color='r', linestyle='--', label='Break-even')
            axes[0, 0].legend()
            
            # 2. Average rewards by scenario
            avg_rewards = [s.avg_reward for s in self.training_sessions]
            
            axes[0, 1].bar(range(len(scenarios)), avg_rewards)
            axes[0, 1].set_title('Average Rewards by Scenario')
            axes[0, 1].set_xticks(range(len(scenarios)))
            axes[0, 1].set_xticklabels([s.replace('_', '\n') for s in scenarios], rotation=45)
            axes[0, 1].set_ylabel('Average Reward')
            axes[0, 1].axhline(y=0, color='r', linestyle='--', label='Break-even')
            axes[0, 1].legend()
            
            # 3. Learning curves
            axes[0, 2].set_title('Learning Curves')
            for scenario, curve in self.learning_curves.items():
                if len(curve) > 10:  # Only plot if enough data
                    axes[0, 2].plot(curve, label=scenario.replace('_', ' ').title())
            axes[0, 2].set_xlabel('Episode')
            axes[0, 2].set_ylabel('Moving Average Reward')
            axes[0, 2].legend()
            axes[0, 2].grid(True)
            
            # 4. Classification accuracy
            classification_acc = [s.classification_accuracy for s in self.training_sessions]
            
            axes[1, 0].bar(range(len(scenarios)), classification_acc)
            axes[1, 0].set_title('Classification Accuracy')
            axes[1, 0].set_xticks(range(len(scenarios)))
            axes[1, 0].set_xticklabels([s.replace('_', '\n') for s in scenarios], rotation=45)
            axes[1, 0].set_ylabel('Accuracy')
            
            # 5. Performance stability
            stability_scores = [s.performance_stability for s in self.training_sessions]
            
            axes[1, 1].bar(range(len(scenarios)), stability_scores)
            axes[1, 1].set_title('Performance Stability')
            axes[1, 1].set_xticks(range(len(scenarios)))
            axes[1, 1].set_xticklabels([s.replace('_', '\n') for s in scenarios], rotation=45)
            axes[1, 1].set_ylabel('Stability Score')
            
            # 6. Overall performance radar
            metrics = ['Win Rate', 'Avg Reward', 'Stability', 'Classification', 'Adaptation']
            values = [
                np.mean(win_rates),
                (np.mean(avg_rewards) + 0.5),  # Normalize
                np.mean(stability_scores),
                np.mean(classification_acc),
                np.mean([s.adaptation_success_rate for s in self.training_sessions])
            ]
            
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            values += values[:1]  # Complete the circle
            angles += angles[:1]
            
            axes[1, 2].plot(angles, values, 'o-', linewidth=2)
            axes[1, 2].fill(angles, values, alpha=0.25)
            axes[1, 2].set_xticks(angles[:-1])
            axes[1, 2].set_xticklabels(metrics)
            axes[1, 2].set_title('Overall Performance Radar')
            axes[1, 2].set_ylim(0, 1)
            axes[1, 2].grid(True)
            
            plt.tight_layout()
            
            # Save visualization
            viz_file = self.output_dir / "faz4_training_visualization.png"
            plt.savefig(viz_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Training visualizations saved to {viz_file}")
            
        except Exception as e:
            self.logger.warning(f"Visualization generation failed: {e}")


# Factory function
def create_faz4_trainer(**kwargs) -> FAZ4MultiPlayerTrainer:
    """Create FAZ 4.0 Multi-Player Trainer."""
    return FAZ4MultiPlayerTrainer(**kwargs)


# Comprehensive training execution
def run_faz4_comprehensive_training():
    """Run complete FAZ 4.0 comprehensive training suite."""
    print("🎯 FAZ 4.0 COMPREHENSIVE MULTI-PLAYER TRAINING")
    print("=" * 60)
    
    trainer = create_faz4_trainer()
    results = trainer.run_comprehensive_training()
    
    # Print final summary
    print("\n" + "="*60)
    print("🏆 FAZ 4.0 TRAINING COMPLETION SUMMARY")
    print("="*60)
    
    overall = results["overall_metrics"]
    readiness = results["readiness_assessment"]
    
    print(f"📊 Overall Performance:")
    print(f"  Average Win Rate: {overall['average_win_rate']:.1%}")
    print(f"  Average Reward: {overall['average_reward']:.3f}")
    print(f"  Classification Accuracy: {overall['overall_classification_accuracy']:.1%}")
    print(f"  Total Episodes: {overall['total_episodes_trained']}")
    
    print(f"\n🎯 Production Readiness:")
    print(f"  Ready for Production: {'✅ YES' if readiness['ready'] else '❌ NO'}")
    print(f"  Readiness Score: {readiness['readiness_score']:.1%}")
    print(f"  Checks Passed: {readiness['checks_passed']}/{readiness['total_checks']}")
    
    rankings = results["scenario_rankings"]
    print(f"\n🏅 Best Performing Scenario: {rankings['best_scenario'].replace('_', ' ').title()}")
    
    return results


# Test the comprehensive training system
if __name__ == "__main__":
    print("🧪 TESTING FAZ 4.0 MULTI-PLAYER TRAINING SYSTEM")
    
    # Run quick test with reduced episodes
    trainer = FAZ4MultiPlayerTrainer()
    
    # Test single scenario
    config = TrainingConfiguration(
        scenario=TrainingScenario.MIXED_SKILL,
        difficulty=TrainingDifficulty.MEDIUM,
        episode_count=10  # Quick test
    )
    
    print("✅ FAZ 4.0 Multi-Player Trainer created")
    print(f"🎯 Testing scenario: {config.scenario.value}")
    
    # Run test session
    env = trainer._create_scenario_environment(config)
    trainer.budget_optimizer = FAZ4BudgetOptimizer(strategy=BudgetStrategy.HIERARCHICAL)
    
    # Quick episode test
    episode_reward, episode_info = trainer._run_training_episode(env, config)
    
    print(f"📊 Test Episode Results:")
    print(f"  Reward: {episode_reward:.3f}")
    print(f"  Classification Accuracy: {episode_info['classification_accuracy']:.2f}")
    print(f"  Successful Adaptations: {episode_info['successful_adaptations']}")
    print(f"  Budget Decisions: {episode_info['budget_decisions']}")
    
    print(f"\n✅ FAZ 4.0 Multi-Player Training System test complete!")
    
    # Uncomment to run full training
    # print(f"\n🚀 Running comprehensive training...")
    # results = run_faz4_comprehensive_training() 
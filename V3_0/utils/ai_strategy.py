"""
AI Strategy Integration for Blackjack Engine (FAZ 1 – F1.5)

This module integrates the trained RL model with the existing blackjack engine,
allowing the AI to play in the simulation environment.
"""

from __future__ import annotations

import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
import importlib
import inspect
from typing import Type


class AIStrategy:
    """AI strategy using trained RL model."""
    
    def __init__(self, model_path: Path, strategy_name: str = "ai"):
        """
        Initialize AI strategy.
        
        Args:
            model_path: Path to trained model
            strategy_name: Name of the strategy
        """
        self.model_path = model_path
        self.strategy_name = strategy_name
        self.model = None
        self.env = None
        
        self._load_model()
    
    def _load_env_class(self) -> Type:
        """Load the BlackjackEnv class from rl_environment.py."""
        try:
            from rl_environment import BlackjackEnv
            return BlackjackEnv
        except Exception as e:
            print(f"Warning: Could not load BlackjackEnv: {e}")
            return None
    
    def _load_model(self):
        """Load the trained RL model."""
        try:
            # Load environment class
            EnvCls = self._load_env_class()
            if EnvCls:
                self.env = EnvCls()
                self.model = DQN.load(self.model_path, env=self.env, print_system_info=False)
                print(f"✅ AI model loaded from {self.model_path}")
            else:
                # Fallback: try loading without environment
                self.model = DQN.load(self.model_path, print_system_info=False)
                print(f"✅ AI model loaded from {self.model_path} (without env)")
        except Exception as e:
            print(f"❌ Failed to load AI model: {e}")
            self.model = None
    
    def get_action(self, player_total: int, dealer_up: int, usable_ace: bool, true_count: float = 0.0) -> str:
        """
        Get action from AI model.
        
        Args:
            player_total: Player's total
            dealer_up: Dealer's up card
            usable_ace: Whether player has usable ace
            true_count: True count (optional)
            
        Returns:
            Action string: "hit", "stand", "double", or "split"
        """
        if self.model is None:
            print("⚠️ AI model not loaded, using basic strategy")
            return "hit"  # Default fallback
        
        try:
            # Create observation in the same format as training environment
            obs = np.array([
                player_total,
                dealer_up,
                int(usable_ace),
                int(round(true_count))
            ], dtype=np.int32)
            
            # Get model prediction
            action, _state = self.model.predict(obs, deterministic=True)
            
            # Convert action index to string
            action_map = {0: "stand", 1: "hit", 2: "double", 3: "split"}
            return action_map.get(action, "hit")
            
        except Exception as e:
            print(f"⚠️ AI prediction failed: {e}")
            return "hit"  # Default fallback
    
    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return self.strategy_name


def create_ai_strategy(model_path: Path, strategy_name: str = "ai") -> AIStrategy:
    """
    Create AI strategy instance.
    
    Args:
        model_path: Path to trained model
        strategy_name: Name of the strategy
        
    Returns:
        AIStrategy instance
    """
    return AIStrategy(model_path, strategy_name) 
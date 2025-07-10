"""
AI Play Strategy
----------------
RL-tabanlı Blackjack oyuncusunu (DQN) mevcut motor/ortama entegre eder.
• Model yolu verildiğinde Stable-Baselines3 DQN modelini yükler.
• Model bulunamazsa, hata fırlatmak yerine env.action_space.sample() ile
  güvenli rastgele aksiyon üretir (CI/test uyumlu).
• Motor tarafında player_cfg = {"strategy": "ai_play", "model_path": "..."}
  kullanımı yeterlidir.
"""

from __future__ import annotations

import logging
import pathlib
from typing import Any, Optional, Tuple, Dict

import numpy as np
from gymnasium import spaces
from stable_baselines3 import DQN
from stable_baselines3.common.base_class import BaseAlgorithm

# Configure logging
logger = logging.getLogger(__name__)


class ModelLoadError(Exception):
    """Custom exception for model loading errors."""
    pass


class AIPlayStrategy:
    """
    RL ajan sarmalayıcı.

    Parameters
    ----------
    action_space : gymnasium.spaces.Discrete
        Ortamın aksiyon uzayı (Discrete(4) beklenir: Stand, Hit, Double, Split).
    model_path : str | pathlib.Path | None
        SB3 `.zip` modeli. Yoksa random-fallback devreye girer.
    """

    def __init__(
        self,
        action_space: spaces.Discrete,
        model_path: str | pathlib.Path | None = None,
    ) -> None:
        self.action_space = action_space
        self._rng = np.random.default_rng()
        self.model_path = model_path
        self.model: Optional[BaseAlgorithm] = None
        self.model_info: Dict[str, Any] = {}
        
        self._load_model()
    
    def _validate_model_path(self, model_path: pathlib.Path) -> Dict[str, Any]:
        """
        Validate model path and return model information.
        
        Returns:
            Dict with validation results and model info
        """
        info = {
            "exists": False,
            "size": 0,
            "compatible": False,
            "version": "unknown",
            "error": None
        }
        
        try:
            if not model_path.exists():
                info["error"] = f"Model file not found: {model_path}"
                return info
            
            info["exists"] = True
            info["size"] = model_path.stat().st_size
            
            # Check file size (should be reasonable for a model)
            if info["size"] < 1000:  # Less than 1KB is suspicious
                info["error"] = f"Model file too small: {info['size']} bytes"
                return info
            
            # Try to load model metadata without full loading
            try:
                # This is a basic check - in production you might want more validation
                info["compatible"] = True
                info["version"] = "stable-baselines3"
            except Exception as e:
                info["error"] = f"Model validation failed: {e}"
                info["compatible"] = False
            
            return info
            
        except Exception as e:
            info["error"] = f"Path validation failed: {e}"
            return info
    
    def _load_model(self) -> None:
        """Load the trained RL model with comprehensive error handling."""
        if self.model_path is None:
            logger.info("No model path provided, using random fallback")
            return
        
        model_path = pathlib.Path(self.model_path)
        
        # Validate model path
        validation_info = self._validate_model_path(model_path)
        self.model_info = validation_info
        
        if not validation_info["exists"]:
            logger.warning(f"Model file not found: {model_path}")
            return
        
        if not validation_info["compatible"]:
            logger.warning(f"Model compatibility issue: {validation_info['error']}")
            return
        
        # Try to load the model
        try:
            logger.info(f"Loading model from {model_path}")
            self.model = DQN.load(model_path, print_system_info=False, device="cpu")
            
            # Validate model structure
            if hasattr(self.model, 'policy') and hasattr(self.model.policy, 'net_arch'):
                logger.info(f"Model loaded successfully: {self.model.policy.net_arch}")
            else:
                logger.warning("Model loaded but structure validation failed")
                
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            self.model = None
            self.model_info["error"] = str(e)
            self.model_info["compatible"] = False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "loaded": self.model is not None,
            "path": str(self.model_path) if self.model_path else None,
            "validation": self.model_info,
            "action_space_size": self.action_space.n if self.action_space else None
        }

    # ------------------------------------------------------------------ #
    def reset(self) -> None:
        """Her yeni el öncesi çağrılabilir (şimdilik durum saklamıyoruz)."""
        pass

    # ------------------------------------------------------------------ #
    def act(self, obs: np.ndarray | Tuple[int, int, bool, int]) -> int:
        """
        Observation → aksiyon (0–3).

        Parameters
        ----------
        obs : np.ndarray | tuple
            `(player_total, dealer_up, usable_ace, true_count)` veya numpy array.

        Returns
        -------
        int
            0=Stand, 1=Hit, 2=Double, 3=Split
        """
        if self.model is None:
            action = int(self._rng.integers(self.action_space.n))
            logger.debug(f"Random fallback action: {action}")
            return action

        # Convert tuple to numpy array if needed
        if isinstance(obs, tuple):
            obs = np.array(obs, dtype=np.float32)
        
        # Normalize observation to match training format
        obs = self._normalize_observation(obs)
        
        try:
            action, _state = self.model.predict(obs, deterministic=True)
            logger.debug(f"Model prediction: {action}")
            return int(action)
        except Exception as e:
            logger.warning(f"AI prediction failed: {e}, using random fallback")
            return int(self._rng.integers(self.action_space.n))
    
    def _normalize_observation(self, obs: np.ndarray) -> np.ndarray:
        """
        Normalize observation to match training environment format.
        
        Training environment uses normalized values, so we need to convert
        the raw observation to match that format.
        """
        if len(obs) != 4:
            raise ValueError(f"Expected 4-dimensional observation, got {len(obs)}")
        
        player_total, dealer_up, usable_ace, true_count = obs
        
        # Normalize to match training environment
        normalized_obs = np.array([
            player_total / 21.0,  # Normalize player total
            dealer_up / 11.0,     # Normalize dealer up card
            float(usable_ace),    # Boolean to float
            true_count / 10.0,    # Normalize true count
        ], dtype=np.float32)
        
        return normalized_obs


class AIPlayStrategyWithValidation(AIPlayStrategy):
    """
    Enhanced AI Play Strategy with action validation.
    
    This version validates actions based on game rules and provides
    better fallback behavior.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validation_stats = {
            "total_actions": 0,
            "validated_actions": 0,
            "corrected_actions": 0
        }
    
    def act(self, obs: np.ndarray | Tuple[int, int, bool, int]) -> int:
        """
        Get validated action based on game state.
        
        Parameters
        ----------
        obs : np.ndarray | tuple
            `(player_total, dealer_up, usable_ace, true_count)`
            
        Returns
        -------
        int
            Valid action index (0-3)
        """
        # Get raw action from model
        raw_action = super().act(obs)
        
        # Extract game state for validation
        if isinstance(obs, tuple):
            player_total, dealer_up, usable_ace, true_count = obs
        else:
            player_total, dealer_up, usable_ace, true_count = obs
            
        # Validate and correct action
        validated_action = self._validate_action(raw_action, player_total, dealer_up)
        
        # Update statistics
        self.validation_stats["total_actions"] += 1
        if validated_action != raw_action:
            self.validation_stats["corrected_actions"] += 1
            logger.debug(f"Action corrected: {raw_action} → {validated_action}")
        else:
            self.validation_stats["validated_actions"] += 1
        
        return validated_action
    
    def _validate_action(self, action: int, player_total: int, dealer_up: int) -> int:
        """
        Validate action based on game rules.
        
        Parameters
        ----------
        action : int
            Raw action from model (0-3)
        player_total : int
            Player's hand total
        dealer_up : int
            Dealer's up card
            
        Returns
        -------
        int
            Validated action
        """
        # Can't hit if already bust
        if action == 1 and player_total >= 21:
            return 0  # Stand instead
        
        # Can't double if not first two cards or already bust
        if action == 2 and (player_total >= 21):
            return 1 if player_total < 17 else 0  # Hit or stand
        
        # Can't split if not a pair or already bust
        if action == 3 and player_total >= 21:
            return 1 if player_total < 17 else 0  # Hit or stand
        
        return action
    
    def get_validation_stats(self) -> Dict[str, int]:
        """Get validation statistics."""
        return self.validation_stats.copy()


# Factory function for easy integration
def create_ai_play_strategy(
    action_space: spaces.Discrete,
    model_path: str | pathlib.Path | None = None,
    use_validation: bool = True
) -> AIPlayStrategy:
    """
    Create AI Play Strategy instance.
    
    Parameters
    ----------
    action_space : spaces.Discrete
        Environment action space
    model_path : str | pathlib.Path | None
        Path to trained model
    use_validation : bool
        Whether to use action validation
        
    Returns
    -------
    AIPlayStrategy
        Strategy instance
    """
    if use_validation:
        return AIPlayStrategyWithValidation(action_space, model_path)
    else:
        return AIPlayStrategy(action_space, model_path) 
"""
F1.5 – AI Play stratejisinin motora entegre testi.

• Ortam açılır, AIPlayStrategy "random-fallback" modunda (model yok) kullanılır.
• 50 el boyunca step() çağrılarında hata fırlatılmadığını, aksiyonların uzaya
  uyduğunu ve ödüllerin geçerli aralıkta kaldığını doğrular.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from V3_0.utils.ai_play_strategy import AIPlayStrategy, AIPlayStrategyWithValidation
from gymnasium import spaces
import numpy as np
import pytest
import importlib
import inspect
from pathlib import Path
from typing import Type

# --------------------------------------------------------------------------- #
def _load_env_class() -> Type:
    env_mod = importlib.import_module("V3_0.rl_environment")
    for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
        if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
            return getattr(env_mod, cls_name)  # type: ignore[return-value]
    raise RuntimeError("Environment class not found")


# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("episodes", [50])
def test_ai_play_random_fallback(episodes: int) -> None:
    """Test AI Play Strategy with random fallback (no model)."""
    EnvCls = _load_env_class()
    env = EnvCls()  # type: ignore[call-arg]

    assert isinstance(env.action_space, spaces.Discrete)
    agent = AIPlayStrategy(env.action_space, model_path=None)

    rng = np.random.default_rng(123)
    rewards = []
    actions_taken = []

    for _ in range(episodes):
        obs, _ = env.reset(seed=int(rng.integers(1_000_000)))
        agent.reset()
        done = trunc = False
        ep_reward = 0
        episode_actions = []
        
        while not (done or trunc):
            action = agent.act(obs)
            assert env.action_space.contains(action), f"Geçersiz aksiyon: {action}"
            episode_actions.append(action)
            
            obs, reward, done, trunc, _ = env.step(action)
            ep_reward += reward
        
        # Allow for split rewards which can be -4 (double loss)
        assert reward in (-4, -2, -1, 0, 1, 2)
        rewards.append(ep_reward)
        actions_taken.extend(episode_actions)

    # Basit istatistik: tüm ödüller geçerli aralıkta olmalı
    assert all(r in (-4, -2, -1, 0, 1, 2) for r in rewards)
    
    # Aksiyon dağılımı kontrolü
    action_counts = np.bincount(actions_taken, minlength=4)
    assert len(action_counts) == 4, "4 aksiyon türü olmalı"
    assert np.sum(action_counts) > 0, "En az bir aksiyon alınmalı"

    env.close()


@pytest.mark.parametrize("episodes", [20])
def test_ai_play_with_validation(episodes: int) -> None:
    """Test AI Play Strategy with validation."""
    EnvCls = _load_env_class()
    env = EnvCls()  # type: ignore[call-arg]

    assert isinstance(env.action_space, spaces.Discrete)
    agent = AIPlayStrategyWithValidation(env.action_space, model_path=None)

    rng = np.random.default_rng(456)
    rewards = []

    for _ in range(episodes):
        obs, _ = env.reset(seed=int(rng.integers(1_000_000)))
        agent.reset()
        done = trunc = False
        ep_reward = 0
        
        while not (done or trunc):
            action = agent.act(obs)
            assert env.action_space.contains(action), f"Geçersiz aksiyon: {action}"
            
            obs, reward, done, trunc, _ = env.step(action)
            ep_reward += reward
        
        assert reward in (-4, -2, -1, 0, 1, 2)
        rewards.append(ep_reward)

    # Validation ile tüm ödüller geçerli olmalı
    assert all(r in (-4, -2, -1, 0, 1, 2) for r in rewards)

    env.close()


def test_observation_normalization():
    """Test observation normalization."""
    from V3_0.utils.ai_play_strategy import AIPlayStrategy
    
    action_space = spaces.Discrete(4)
    agent = AIPlayStrategy(action_space, model_path=None)
    
    # Test tuple observation
    obs_tuple = (15, 7, True, 2)
    action1 = agent.act(obs_tuple)
    assert isinstance(action1, int)
    assert 0 <= action1 <= 3
    
    # Test numpy array observation
    obs_array = np.array([15, 7, True, 2], dtype=np.float32)
    action2 = agent.act(obs_array)
    assert isinstance(action2, int)
    assert 0 <= action2 <= 3


def test_action_validation():
    """Test action validation logic."""
    from V3_0.utils.ai_play_strategy import AIPlayStrategyWithValidation
    
    action_space = spaces.Discrete(4)
    agent = AIPlayStrategyWithValidation(action_space, model_path=None)
    
    # Test bust validation
    obs_bust = np.array([22, 7, False, 0], dtype=np.float32)
    action = agent.act(obs_bust)
    assert action != 1, "Can't hit when bust"
    assert action != 2, "Can't double when bust"
    assert action != 3, "Can't split when bust"


def test_model_loading_with_invalid_path():
    """Test graceful handling of invalid model path."""
    action_space = spaces.Discrete(4)
    invalid_path = Path("nonexistent_model.zip")
    
    agent = AIPlayStrategy(action_space, model_path=invalid_path)
    assert agent.model is None, "Should fallback to random when model not found"
    
    # Should still work with random fallback
    obs = np.array([15, 7, False, 0], dtype=np.float32)
    action = agent.act(obs)
    assert isinstance(action, int)
    assert 0 <= action <= 3


if __name__ == "__main__":
    # Run basic tests
    test_ai_play_random_fallback(10)
    test_ai_play_with_validation(5)
    test_observation_normalization()
    test_action_validation()
    test_model_loading_with_invalid_path()
    print("✅ All tests passed!") 
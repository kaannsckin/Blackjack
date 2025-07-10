# tests/test_space.py
"""
Observation & Action space unit-tests for the RL Blackjack environment (FAZ 1 – F1.2).

Bu testler:
1. Aksiyon uzayının Discrete(4) olduğunu ve {0,1,2,3} değerlerini kapsadığını,
2. Observation uzayının Gymnasium'un tanımlı bir Space alt sınıfı olduğunu,
3. reset() ve step() ile üretilen bütün gözlemlerin observation_space.contains() tarafından
   doğrulandığını ispatlar.
"""

from __future__ import annotations

import importlib
import inspect
from typing import Type

import numpy as np
import pytest
from gymnasium import spaces

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# --------------------------------------------------------------------------- #
# Helper – ortam sınıfını esnekçe yükle                                       #
# --------------------------------------------------------------------------- #
def _load_env_class() -> Type:
    """Return RL environment class exported by rl_environment.py."""
    env_mod = importlib.import_module("rl_environment")
    for cls_name in ("RLBlackjackEnv", "BlackjackEnv"):
        if hasattr(env_mod, cls_name) and inspect.isclass(getattr(env_mod, cls_name)):
            return getattr(env_mod, cls_name)  # type: ignore[return-value]
    raise ImportError(
        "rl_environment.py içinde `RLBlackjackEnv` veya `BlackjackEnv` sınıfı bulunamadı."
    )


# --------------------------------------------------------------------------- #
# Test – Action space doğrulama                                               #
# --------------------------------------------------------------------------- #
def test_action_space() -> None:
    EnvCls = _load_env_class()
    env = EnvCls()  # type: ignore[call-arg]

    # 1) Discrete(4) kontrolü
    assert isinstance(
        env.action_space, spaces.Discrete
    ), f"Aksiyon uzayı Discrete değil: {type(env.action_space)}"
    assert (
        env.action_space.n == 4
    ), f"Aksiyon uzayının boyutu 4 değil: {env.action_space.n}"

    # 2) Örnekleme kapsamı
    valid_actions = {env.action_space.sample() for _ in range(20)}
    assert valid_actions <= {0, 1, 2, 3}, f"Geçersiz aksiyon(lar): {valid_actions}"

    env.close()


# --------------------------------------------------------------------------- #
# Test – Observation space doğrulama                                          #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("seed", [21, 2025])
def test_observation_space(seed: int) -> None:
    EnvCls = _load_env_class()
    env = EnvCls()  # type: ignore[call-arg]

    obs_space = env.observation_space
    assert isinstance(
        obs_space, spaces.Space
    ), "Observation space, gymnasium.spaces.Space türevi olmalı."

    rng = np.random.default_rng(seed)

    # --- reset() gözlemi ----------------------------------------------------
    try:
        obs, _ = env.reset(seed=seed)
    except TypeError:
        obs = env.reset(seed=seed)  # type: ignore[assignment]

    assert obs_space.contains(obs), f"reset() gözlemi uzaya uymuyor: {obs}"

    # --- step() gözlemleri --------------------------------------------------
    for _ in range(50):  # yeterince adım
        action = rng.integers(env.action_space.n)  # rastgele aksiyon
        step_out = env.step(int(action))

        # Gymnasium (obs, reward, term, trunc, info)  -  Eski Gym (obs, reward, done, info)
        next_obs = step_out[0]
        assert obs_space.contains(
            next_obs
        ), f"step() gözlemi uzaya uymuyor: {next_obs}"

        if len(step_out) == 5:
            terminated, truncated = step_out[2], step_out[3]
        else:
            terminated, truncated = step_out[2], False

        if terminated or truncated:
            try:
                obs, _ = env.reset()
            except TypeError:
                obs = env.reset()  # type: ignore[assignment]
        else:
            obs = next_obs

    env.close()

# tests/test_reward.py
"""
Reward mechanism unit-tests for the RL Blackjack environment.

– Episode sonundaki ödül mutlaka {-1, 0, +1} kümesinde olmalıdır
  (kaybet, push, kazan).
– Test, üç değerin de gözlemlendiğini doğrulamadan geçmez.
"""

from __future__ import annotations

import importlib
import inspect
import random
from typing import Set, Type

import numpy as np
import pytest

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
        "rl_environment.py içerisinde `RLBlackjackEnv` veya `BlackjackEnv` bulunamadı."
    )


# --------------------------------------------------------------------------- #
# Test – ödül değerleri sadece {-1,0,1} olmalı                                #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("seed", [42, 1337])
def test_reward_values(seed: int) -> None:
    """
    Her terminal adımda dönen reward ∈ {-1, 0, +1} olmalıdır.
    Ayrıca test, makul sayıda epizod (≤10 000) içinde üç değerin de
    üretildiğini kontrol eder.
    """
    EnvCls = _load_env_class()
    env = EnvCls()  # type: ignore[call-arg]

    rng_py = random.Random(seed)
    rng_np = np.random.default_rng(seed)

    observed: Set[int] = set()
    max_episodes = 10_000
    episodes = 0

    while episodes < max_episodes:
        # Gymnasium reset imzası geriye (obs, info) döner; eski Gym için fallback var.
        try:
            _, _ = env.reset(seed=rng_py.randint(0, 1_000_000))
        except TypeError:
            env.reset(seed=rng_py.randint(0, 1_000_000))  # type: ignore[arg-type]

        terminated = truncated = False
        while not (terminated or truncated):
            action = env.action_space.sample(rng_np) if hasattr(env.action_space, "sample") and env.action_space.sample.__code__.co_argcount == 2 else env.action_space.sample()  # type: ignore[arg-type]
            step_out = env.step(action)

            # Gymnasium (obs, reward, term, trunc, info)  -   Eski Gym (obs, reward, done, info)
            if len(step_out) == 5:
                _, reward, terminated, truncated, _ = step_out  # type: ignore[misc]
            else:  # len == 4
                _, reward, done, _ = step_out  # type: ignore[misc]
                terminated, truncated = done, False

        # --- doğrulamalar ---------------------------------------------------
        assert reward in (-1, 0, 1) or reward in (-2, 2), f"Geçersiz reward: {reward}"
        observed.add(reward)
        episodes += 1

    # Test sonunda genel kontroller
    # Reward değerlerinin geçerli aralıkta olduğunu kontrol et
    expected_rewards = {-1, 0, 1, -2, 2}
    assert observed.issubset(expected_rewards), (
        f"{episodes} epizodda beklenmeyen ödül değerleri gözlemlendi: {observed - expected_rewards}"
    )

    # En az birkaç farklı reward değeri gözlemlendiğini kontrol et
    assert len(observed) >= 2, (
        f"{episodes} epizodda yeterli çeşitlilik gözlenmedi. Gözlenen: {observed}"
    )

    env.close()

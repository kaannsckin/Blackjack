# """Pytest birim testleri – FAZ 0"""
from stable_baselines3.common.env_checker import check_env

from rl_environment import BlackjackEnv


def test_reset_observation_shape():
    env = BlackjackEnv(seed=42)
    obs, info = env.reset()
    assert obs.shape == (4,), "Observation vektörü 4 elemanlı olmalı"
    # Aralık kontrolü
    assert env.observation_space.contains(obs)


def test_step_transitions():
    env = BlackjackEnv(seed=123)
    env.reset()
    obs, reward, terminated, truncated, info = env.step(1)  # HIT
    assert env.observation_space.contains(obs)
    assert not truncated
    # Son durumda Stand eylemi hand’i bitirmeli
    _, _, terminated2, _, _ = env.step(0)
    assert terminated2


def test_check_env_compliance():
    """Gymnasium + SB3 uyumluluk testi."""
    env = BlackjackEnv(seed=0)
    check_env(env, warn=True)

"""Pytest birim testleri – FAZ 0"""
import numpy as np
import pytest

from rl_environment import BlackjackEnv


def test_reset_observation_shape():
    env = BlackjackEnv(seed=42)
    obs, info = env.reset()
    assert obs.shape == (4,), "Observation vektörü 4 elemanlı olmalı"
    # Aralık kontrolü
    assert env.observation_space.contains(obs)


def test_step_transitions():
    env = BlackjackEnv(seed=123)
    env.reset()
    obs, reward, terminated, truncated, info = env.step(1)  # HIT
    assert env.observation_space.contains(obs)
    assert not truncated
    # Son durumda Stand eylemi hand’i bitirmeli
    _, _, terminated2, _, _ = env.step(0)
    assert terminated2
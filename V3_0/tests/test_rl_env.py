"""Pytest birim testleri – FAZ 0"""
import numpy as np
import pytest
from stable_baselines3.common.env_checker import check_env

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
    # Son durumda Stand eylemi hand'i bitirmeli
    _, _, terminated2, _, _ = env.step(0)
    assert terminated2


def test_check_env_compliance():
    """Gymnasium + SB3 uyumluluk testi."""
    env = BlackjackEnv(seed=0)
    check_env(env, warn=True)


if __name__ == "__main__":
    print("Manuel test başlatılıyor...\n")
    try:
        test_reset_observation_shape()
        print("✅ test_reset_observation_shape geçti.")
    except AssertionError as e:
        print(f"❌ test_reset_observation_shape başarısız: {e}")

    try:
        test_step_transitions()
        print("✅ test_step_transitions geçti.")
    except AssertionError as e:
        print(f"❌ test_step_transitions başarısız: {e}")

    try:
        test_check_env_compliance()
        print("✅ test_check_env_compliance geçti.")
    except Exception as e:
        print(f"❌ test_check_env_compliance başarısız: {e}")

def test_custom_rules_and_penetration():
    env = BlackjackEnv(rules={"num_decks": 2, "dealer_rule": "H17"}, penetration=0.8, seed=42)
    obs, _ = env.reset()
    assert env.rules["num_decks"] == 2
    assert env.penetration == 0.8
    assert env.observation_space.contains(obs)


def test_sb3_check_env():
    env = BlackjackEnv()
    check_env(env, warn=True)
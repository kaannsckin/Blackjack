"""Blackjack RL Environment
===========================
Gym‑compatible ortam. FAZ 1’de eklenecek ileri fonksiyonlara zemin hazırlar.
"""
from __future__ import annotations

import random
from typing import Any, Dict, Tuple

import numpy as np
import gymnasium as gym
from gymnasium import spaces

# === Sabitler ===
BLACKJACK: int = 21
DEALER_STAND_SOFT: int = 17
ACTIONS: Dict[int, str] = {0: "stand", 1: "hit", 2: "double", 3: "split"}


class BlackjackEnv(gym.Env):
    """Basit bir Blackjack ortamı (tek elde, çoklu oyuncu yok)."""

    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(self, seed: int | None = None) -> None:
        super().__init__()
        self.rng = random.Random(seed)

        # Gözlem: (player_total, dealer_upcard, usable_ace (bool), true_count)
        low = np.array([4, 1, 0, -20], dtype=np.int32)
        high = np.array([31, 11, 1, 20], dtype=np.int32)
        self.observation_space: spaces.Box = spaces.Box(low=low, high=high, dtype=np.int32)

        # Aksiyon alanı: 0‑Stand, 1‑Hit, 2‑Double, 3‑Split
        self.action_space: spaces.Discrete = spaces.Discrete(len(ACTIONS))

        # İç durum değişkenleri
        self.player_hand: list[int] = []
        self.dealer_hand: list[int] = []
        self.running_count: int = 0  # Hi‑Lo varsayılanı
        self.num_decks: int = 6
        self._shoe: list[int] = []

    # ------------------------------------------------------------------
    #   Yardımcı Fonksiyonlar
    # ------------------------------------------------------------------
    def _draw_card(self) -> int:
        if not self._shoe:
            self._reshuffle()
        card = self._shoe.pop()
        # Hi‑Lo running count güncelle
        self.running_count += self._hi_lo_value(card)
        return card

    def _reshuffle(self) -> None:
        self._shoe = [rank for rank in range(1, 14)] * 4 * self.num_decks
        self.rng.shuffle(self._shoe)
        self.running_count = 0

    @staticmethod
    def _hi_lo_value(card: int) -> int:
        if 2 <= card <= 6:
            return 1
        if card in {10, 11, 12, 13, 1}:  # 10‑J‑Q‑K‑A
            return -1
        return 0

    @staticmethod
    def _hand_value(hand: list[int]) -> Tuple[int, bool]:
        """(Toplam, usable_ace) döner."""
        total = sum(min(card, 10) for card in hand)
        usable_ace = 1 in hand and total + 10 <= BLACKJACK
        if usable_ace:
            total += 10
        return total, usable_ace

    # ------------------------------------------------------------------
    #   Gym API
    # ------------------------------------------------------------------
    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None):
        super().reset(seed=seed)
        self._reshuffle()

        self.player_hand = [self._draw_card(), self._draw_card()]
        self.dealer_hand = [self._draw_card(), self._draw_card()]
        obs = self._get_obs()
        info: Dict[str, Any] = {}
        return obs, info

    def step(self, action: int):
        assert self.action_space.contains(action)

        if action == 1:  # Hit
            self.player_hand.append(self._draw_card())
            player_total, _ = self._hand_value(self.player_hand)
            terminated = player_total > BLACKJACK
            if terminated:
                reward = -1.0
                return self._get_obs(), reward, True, False, {}
            return self._get_obs(), 0.0, False, False, {}

        if action == 0:  # Stand
            return self._resolve_hand()

        if action == 2:  # Double (basit: tek kart çek, 2× bahis)
            self.player_hand.append(self._draw_card())
            reward_multiplier = 2
            return self._resolve_hand(reward_multiplier)

        if action == 3:  # Split (desteklenmiyor → no‑op)
            return self._get_obs(), 0.0, False, False, {"note": "split not yet implemented"}

    def _resolve_hand(self, reward_multiplier: int = 1):
        player_total, _ = self._hand_value(self.player_hand)
        # Dealer oynasın
        while True:
            dealer_total, dealer_soft = self._hand_value(self.dealer_hand)
            if dealer_total < DEALER_STAND_SOFT or (dealer_total == DEALER_STAND_SOFT and dealer_soft):
                self.dealer_hand.append(self._draw_card())
            else:
                break

        dealer_total, _ = self._hand_value(self.dealer_hand)
        if player_total > BLACKJACK:
            reward = -1
        elif dealer_total > BLACKJACK or player_total > dealer_total:
            reward = 1
        elif player_total == dealer_total:
            reward = 0
        else:
            reward = -1
        reward *= reward_multiplier
        return self._get_obs(), float(reward), True, False, {}

    # ------------------------------------------------------------------
    def _get_obs(self) -> np.ndarray:
        player_total, usable_ace = self._hand_value(self.player_hand)
        dealer_upcard = min(self.dealer_hand[0], 10)  # 10‑J‑Q‑K hepsi 10 değeri
        true_count = self.running_count / (len(self._shoe) / 52) if self._shoe else 0
        return np.array([player_total, dealer_upcard, int(usable_ace), int(round(true_count))], dtype=np.int32)

    # ------------------------------------------------------------------
    def render(self) -> None:  # pragma: no cover
        player_total, _ = self._hand_value(self.player_hand)
        dealer_total, _ = self._hand_value(self.dealer_hand)
        print(f"Player: {self.player_hand} (total={player_total})  |  Dealer: {self.dealer_hand} (total={dealer_total})")
        print(f"Running count: {self.running_count}")
        print(f"True count: {true_count}")
        print(f"Dealer upcard: {dealer_upcard}")
        print(f"Player total: {player_total}")
        print(f"Dealer total: {dealer_total}")
        print(f"Usable ace: {usable_ace}")
        print(f"True count: {true_count}")
        print(f"Dealer upcard: {dealer_upcard}")
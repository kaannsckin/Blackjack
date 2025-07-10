"""Blackjack RL Environment – F1.0 Upgrade

Ekstra özellikler:
* `rules` sözlüğü: env.reset() sırasında varyasyon için saklanır
    - Desteklenen alanlar: num_decks, dealer_rule ("S17"|"H17"), das (bool)
* `penetration` oranı: 0‑1 arası; deste bu orandan az kaldığında otomatik reshuffle
* Observation vektörü değişmedi ancak yeni kural kimlikleri gözleme eklemek kolay.
"""
from __future__ import annotations

import random
from typing import Any, Dict, Tuple, Optional

import numpy as np
import gymnasium as gym
from gymnasium import spaces

BLACKJACK: int = 21
DEFAULT_RULES: Dict[str, Any] = {
    "num_decks": 6,
    "dealer_rule": "S17",  # veya "H17"
    "das": False,           # Double After Split
}
ACTIONS: Dict[int, str] = {0: "stand", 1: "hit", 2: "double", 3: "split"}


class BlackjackEnv(gym.Env):
    """Tek oyunculu, Gymnasium‑uyumlu Blackjack ortamı."""

    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(
        self,
        *,
        seed: int | None = None,
        rules: Optional[Dict[str, Any]] = None,
        penetration: float = 0.75,
    ) -> None:
        super().__init__()
        self.rng = random.Random(seed)

        # Kural & penetrasyon
        self.rules = {**DEFAULT_RULES, **(rules or {})}
        self.penetration = np.clip(penetration, 0.05, 0.95)

        # Observation: (player_total, dealer_upcard, usable_ace, true_count)
        self.observation_space = spaces.Box(low=np.array([4, 1, 0, -20]), high=np.array([31, 11, 1, 20]), dtype=np.int32)
        self.action_space = spaces.Discrete(len(ACTIONS))

        # İç durum
        self.player_hands: list[list[int]] = [[]]  # Çoklu el desteği
        self.dealer_hand: list[int] = []
        self.running_count: int = 0
        self._shoe: list[int] = []
        self._initial_shoe_size: int = 52 * self.rules["num_decks"]
        self._current_hand_idx: int = 0  # Hangi el oynanıyor
        self._split_count: int = 0  # Split sayısı (max 3)

    # ---------------------- yardımcı ----------------------
    def _reshuffle(self) -> None:
        self._shoe = [r for r in range(1, 14)] * 4 * self.rules["num_decks"]
        self.rng.shuffle(self._shoe)
        self.running_count = 0

    def _draw_card(self) -> int:
        if not self._shoe or len(self._shoe) / self._initial_shoe_size < (1 - self.penetration):
            self._reshuffle()
        card = self._shoe.pop()
        self.running_count += self._hi_lo_value(card)
        return card

    @staticmethod
    def _hi_lo_value(card: int) -> int:
        if 2 <= card <= 6:
            return 1
        if card in {1, 10, 11, 12, 13}:  # A,10,J,Q,K
            return -1
        return 0

    @staticmethod
    def _hand_value(hand: list[int]) -> Tuple[int, bool]:
        total = sum(min(c, 10) for c in hand)
        usable_ace = 1 in hand and total + 10 <= BLACKJACK
        if usable_ace:
            total += 10
        return total, usable_ace

    # ---------------------- Gym API ----------------------
    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None):
        if seed is not None:
            self.rng.seed(seed)
        self._reshuffle()
        self.player_hands = [[self._draw_card(), self._draw_card()]]
        self.dealer_hand = [self._draw_card(), self._draw_card()]
        self._current_hand_idx = 0
        self._split_count = 0
        return self._get_obs(), {}

    def step(self, action: int):
        assert self.action_space.contains(action)
        current_hand = self.player_hands[self._current_hand_idx]
        
        if action == 1:  # hit
            current_hand.append(self._draw_card())
            if self._hand_value(current_hand)[0] > BLACKJACK:
                return self._next_hand_or_resolve()
            return self._get_obs(), 0.0, False, False, {}
        if action == 0:  # stand
            return self._next_hand_or_resolve()
        if action == 2:  # double
            current_hand.append(self._draw_card())
            return self._next_hand_or_resolve(reward_multiplier=2)
        if action == 3:  # split
            return self._handle_split()
        return self._get_obs(), 0.0, False, False, {"note": "invalid action"}

    def _resolve_all_hands(self, reward_multiplier: int = 1):
        """Resolve all player hands against dealer."""
        # Dealer plays
        while True:
            d_total, d_soft = self._hand_value(self.dealer_hand)
            stand_on_soft = self.rules["dealer_rule"] == "S17"
            if d_total < 17 or (d_total == 17 and not stand_on_soft and d_soft):
                self.dealer_hand.append(self._draw_card())
            else:
                break
        
        d_total, _ = self._hand_value(self.dealer_hand)
        
        # Calculate total reward from all hands
        total_reward = 0
        for hand in self.player_hands:
            p_total, _ = self._hand_value(hand)
            if p_total > BLACKJACK:
                hand_reward = -1
            elif d_total > BLACKJACK or p_total > d_total:
                hand_reward = 1
            elif p_total == d_total:
                hand_reward = 0
            else:
                hand_reward = -1
            total_reward += hand_reward
        
        # Episode bittiğinde, gözlem olarak sıfır vektörü döndür
        terminal_obs = np.zeros(self.observation_space.shape, dtype=np.int32)
        return terminal_obs, float(total_reward * reward_multiplier), True, False, {}
    
    def _resolve_hand(self, reward_multiplier: int = 1):
        """Legacy method - now redirects to _resolve_all_hands."""
        return self._resolve_all_hands(reward_multiplier)

    def _get_obs(self):
        current_hand = self.player_hands[self._current_hand_idx]
        if not current_hand:  # Handle empty hand
            return np.array([0, 1, 0, 0], dtype=np.int32)
        
        p_total, ace = self._hand_value(current_hand)
        dealer_up = min(self.dealer_hand[0], 10) if self.dealer_hand else 1
        decks_rem = len(self._shoe) / 52 if self._shoe else 1
        tc = self.running_count / decks_rem
        return np.array([p_total, dealer_up, int(ace), int(round(tc))], dtype=np.int32)

    def _handle_split(self):
        """Handle split action - full implementation."""
        current_hand = self.player_hands[self._current_hand_idx]
        
        # Check if split is possible
        if (len(current_hand) != 2 or 
            current_hand[0] != current_hand[1] or 
            self._split_count >= 3):  # Max 3 splits (4 hands total)
            return self._get_obs(), -1.0, True, False, {"note": "split not allowed"}
        
        # Perform split
        card1, card2 = current_hand
        self.player_hands[self._current_hand_idx] = [card1, self._draw_card()]
        self.player_hands.insert(self._current_hand_idx + 1, [card2, self._draw_card()])
        self._split_count += 1
        
        # Continue with current hand
        return self._get_obs(), 0.0, False, False, {"note": "split successful"}
    
    def _next_hand_or_resolve(self, reward_multiplier: int = 1):
        """Move to next hand or resolve all hands."""
        self._current_hand_idx += 1
        
        if self._current_hand_idx < len(self.player_hands):
            # More hands to play
            return self._get_obs(), 0.0, False, False, {}
        else:
            # All hands done, resolve
            return self._resolve_all_hands(reward_multiplier)



    # ------------------------------------------------------------------
    def render(self) -> None:  # pragma: no cover
        current_hand = self.player_hands[self._current_hand_idx]
        player_total, _ = self._hand_value(current_hand)
        dealer_total, _ = self._hand_value(self.dealer_hand)
        print(f"Player Hand {self._current_hand_idx + 1}: {current_hand} (total={player_total})")
        print(f"All Player Hands: {self.player_hands}")
        print(f"Dealer: {self.dealer_hand} (total={dealer_total})")
        print(f"Running count: {self.running_count}")

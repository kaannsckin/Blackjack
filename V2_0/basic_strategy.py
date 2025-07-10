# basic_strategy.py
"""In-code Blackjack basic strategy (4–8 decks, S17, DAS) with no circular import.
Uses forward references for type hints to avoid importing blackjack_engine at runtime."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only for type checking; avoids circular import at runtime
    from blackjack_engine import Hand, Card

class BasicStrategy:
    """Determines the optimal action for a given player hand and dealer up‑card."""

    def action(self, hand: 'Hand', dealer_up: 'Card', can_double: bool, can_split: bool) -> str:  # noqa: F821
        total = hand.value()
        dealer = dealer_up.card_value()

        # ---- Pair splits ----
        if len(hand.cards) == 2 and can_split and hand.cards[0].card_value() == hand.cards[1].card_value():
            pair_val = hand.cards[0].card_value()
            if pair_val in {1, 8}:   # Always split A,A and 8,8
                return "split"
            if pair_val in {5, 10}:  # Never split 5,5 or 10,10
                pass
            elif pair_val in {2, 3, 7} and 2 <= dealer <= 7:
                return "split"
            elif pair_val == 6 and 2 <= dealer <= 6:
                return "split"
            elif pair_val == 9 and (2 <= dealer <= 6 or dealer in {8, 9}):
                return "split"

        # ---- Soft hands ----
        if hand.is_soft():
            if total >= 19:
                return "stand"
            if total == 18:
                if 2 <= dealer <= 6:
                    return "double" if can_double else "stand"
                if dealer in {7, 8}:
                    return "stand"
                return "hit"
            if 13 <= total <= 17:
                if 4 <= dealer <= 6:
                    return "double" if can_double else "hit"
                return "hit"

        # ---- Hard hands ----
        if total >= 17:
            return "stand"
        if 13 <= total <= 16:
            return "stand" if 2 <= dealer <= 6 else "hit"
        if total == 12:
            return "stand" if 4 <= dealer <= 6 else "hit"
        if total == 11:
            return "double" if can_double else "hit"
        if total == 10:
            return "double" if can_double and 2 <= dealer <= 9 else "hit"
        if total == 9:
            return "double" if can_double and 3 <= dealer <= 6 else "hit"
        return "hit"

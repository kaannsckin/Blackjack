"""Comprehensive Basic Strategy for Blackjack (FAZ 1 – F1.3)

Implements complete basic strategy including:
- Hard hands
- Soft hands  
- Pair splitting
- Double down rules
- Surrender (optional)
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional


class BasicStrategy:
    """Complete basic strategy implementation for 6-deck, S17, DAS rules."""
    
    def __init__(self, rules: Optional[Dict] = None):
        self.rules = rules or {
            "num_decks": 6,
            "dealer_rule": "S17",  # S17 or H17
            "das": True,           # Double After Split
            "surrender": False,    # Surrender allowed
        }
    
    def get_action(
        self, 
        player_total: int, 
        dealer_up: int, 
        usable_ace: bool,
        can_double: bool = True,
        can_split: bool = True,
        is_pair: bool = False,
    ) -> int:
        """
        Get optimal action for given situation.
        
        Returns:
            0: stand, 1: hit, 2: double, 3: split
        """
        # Pair splitting
        if is_pair and can_split:
            return self._get_pair_action(player_total, dealer_up)
        
        # Soft hands (with usable ace)
        if usable_ace:
            return self._get_soft_action(player_total, dealer_up, can_double)
        
        # Hard hands
        return self._get_hard_action(player_total, dealer_up, can_double)
    
    def _get_pair_action(self, pair_value: int, dealer_up: int) -> int:
        """Get action for pair splitting."""
        # Always split Aces and 8s
        if pair_value in [1, 8]:
            return 3  # split
        
        # Never split 5s and 10s
        if pair_value in [5, 10]:
            return 1  # hit (will be handled by hard/soft logic)
        
        # Conditional splits
        if pair_value == 9:
            if dealer_up in [7, 10, 11]:  # 10, J, Q, K, A
                return 0  # stand
            else:
                return 3  # split
        
        if pair_value == 7:
            if dealer_up <= 7:
                return 3  # split
            else:
                return 1  # hit
        
        if pair_value == 6:
            if dealer_up <= 6:
                return 3  # split
            else:
                return 1  # hit
        
        if pair_value == 4:
            if dealer_up in [5, 6]:
                return 3  # split
            else:
                return 1  # hit
        
        if pair_value in [2, 3]:
            if dealer_up <= 7:
                return 3  # split
            else:
                return 1  # hit
        
        return 1  # hit (default)
    
    def _get_soft_action(self, total: int, dealer_up: int, can_double: bool) -> int:
        """Get action for soft hands (with usable ace)."""
        if total >= 20:
            return 0  # stand
        
        if total == 19:
            if dealer_up == 6 and can_double:
                return 2  # double
            else:
                return 0  # stand
        
        if total == 18:
            if dealer_up <= 6 and can_double:
                return 2  # double
            elif dealer_up in [7, 8]:
                return 0  # stand
            else:
                return 1  # hit
        
        if total == 17:
            if dealer_up in [3, 4, 5, 6] and can_double:
                return 2  # double
            else:
                return 1  # hit
        
        if total == 16:
            if dealer_up in [4, 5, 6] and can_double:
                return 2  # double
            else:
                return 1  # hit
        
        if total == 15:
            if dealer_up in [4, 5, 6] and can_double:
                return 2  # double
            else:
                return 1  # hit
        
        if total == 14:
            if dealer_up in [4, 5, 6] and can_double:
                return 2  # double
            else:
                return 1  # hit
        
        if total == 13:
            if dealer_up in [5, 6] and can_double:
                return 2  # double
            else:
                return 1  # hit
        
        # A,2 through A,6
        return 1  # hit
    
    def _get_hard_action(self, total: int, dealer_up: int, can_double: bool) -> int:
        """Get action for hard hands."""
        if total >= 17:
            return 0  # stand
        
        if total == 16:
            if dealer_up <= 6:
                return 0  # stand
            else:
                return 1  # hit
        
        if total == 15:
            if dealer_up <= 6:
                return 0  # stand
            else:
                return 1  # hit
        
        if total == 14:
            if dealer_up <= 6:
                return 0  # stand
            else:
                return 1  # hit
        
        if total == 13:
            if dealer_up <= 6:
                return 0  # stand
            else:
                return 1  # hit
        
        if total == 12:
            if dealer_up in [4, 5, 6]:
                return 0  # stand
            else:
                return 1  # hit
        
        if total == 11:
            if can_double:
                return 2  # double
            else:
                return 1  # hit
        
        if total == 10:
            if dealer_up <= 9 and can_double:
                return 2  # double
            else:
                return 1  # hit
        
        if total == 9:
            if dealer_up in [3, 4, 5, 6] and can_double:
                return 2  # double
            else:
                return 1  # hit
        
        # 8 and below
        return 1  # hit


# Strategy tables for reference
HARD_TOTALS = {
    17: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # stand on all
    16: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],  # stand vs 2-6, hit vs 7+
    15: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    14: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    13: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    12: [1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],  # stand vs 4-6
    11: [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],  # always double
    10: [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],  # double vs 2-9
    9:  [1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1],  # double vs 3-6
    8:  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # always hit
}

SOFT_TOTALS = {
    20: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # always stand
    19: [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0],  # double vs 6
    18: [2, 2, 2, 2, 2, 2, 0, 0, 1, 1, 1],  # double vs 2-6, stand vs 7-8
    17: [1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1],  # double vs 3-6
    16: [1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1],  # double vs 4-6
    15: [1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1],
    14: [1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1],
    13: [1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1],  # double vs 5-6
    12: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # always hit
}

PAIR_SPLITS = {
    11: [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],  # A,A - always split
    10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 10,10 - never split
    9:  [3, 3, 3, 3, 3, 3, 0, 3, 3, 0, 0],  # 9,9 - split except vs 7,10,A
    8:  [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],  # 8,8 - always split
    7:  [3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1],  # 7,7 - split vs 2-7
    6:  [3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1],  # 6,6 - split vs 2-6
    5:  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 5,5 - never split
    4:  [1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1],  # 4,4 - split vs 5-6
    3:  [3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1],  # 3,3 - split vs 2-7
    2:  [3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1],  # 2,2 - split vs 2-7
} 
# deviations.py – extended deviation (index play) engine
"""Advanced deviation support with flags for soft hands, pair, surrender, etc."""
from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass(frozen=True)
class DeviationRule:
    """Represents a single index play.

    Attributes
    ----------
    hard_total / soft_total / pair_val : exactly **one** of these should be non-None.
    dealer_up : dealer up-card value (2-11 where 11 = Ace).
    threshold : True Count threshold.
    cmp : ">=" or "<=" – comparison operator.
    alt_action : alternate action ("stand", "hit", "double", "split", "surrender").
    notes : free-text for debugging / logging.
    """
    hard_total: Optional[int] = None
    soft_total: Optional[int] = None
    pair_val: Optional[int] = None
    dealer_up: int = 2
    threshold: float = 0.0
    cmp: str = ">="
    alt_action: str = "stand"
    notes: str = ""

    def matches(self, hand) -> bool:
        """Return True if this rule applies to `hand`."""
        if self.hard_total is not None:
            return not hand.is_soft() and hand.value() == self.hard_total
        if self.soft_total is not None:
            return hand.is_soft() and hand.value() == self.soft_total
        if self.pair_val is not None:
            return (
                len(hand.cards) == 2
                and hand.cards[0].card_value() == self.pair_val
                and hand.cards[1].card_value() == self.pair_val
            )
        return False  # should not happen

class DeviationEngine:
    def __init__(self, rules: List[DeviationRule]):
        self.rules = rules

    def check(self, hand, dealer_up_val: int, tc: float) -> Optional[str]:
        for r in self.rules:
            if not r.matches(hand):
                continue
            if r.dealer_up != dealer_up_val:
                continue
            if (r.cmp == ">=" and tc >= r.threshold) or (r.cmp == "<=" and tc <= r.threshold):
                return r.alt_action
        return None

# ---------------------------------------------------------------------------
# JSON helper – allows soft/hard/pair keys.
# Example JSON entry:
# {"soft_total": 19, "dealer_up": 6, "threshold": 1, "cmp": ">=", "alt_action": "double"}
# ---------------------------------------------------------------------------

def load_index_plays(path: str) -> List[DeviationRule]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        return []
    rules: List[DeviationRule] = []
    for item in raw:
        rules.append(DeviationRule(**item))
    return rules
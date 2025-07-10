from typing import Dict

class CardCounter:
    """Keeps running & true counts for various counting systems."""

    # -------- value tables -------------------------------------------------
    _HI_LO: Dict[str, int] = {
        **{str(n): +1 for n in range(2, 7)},
        **{str(n): 0 for n in (7, 8, 9)},
        **{v: -1 for v in ("10", "J", "Q", "K", "A")},
    }
    _OMEGA_II: Dict[str, int] = {
        **{v: +1 for v in ("2", "3", "7")},
        **{v: +2 for v in ("4", "5", "6")},
        "9": -1,
        **{v: -2 for v in ("10", "J", "Q", "K", "A")},
        "8": 0,
    }
    _WONG_HALVES: Dict[str, float] = {
        "2": 0.5, "3": 1, "4": 1, "5": 1.5, "6": 1, "7": 0.5,
        "8": 0, "9": -0.5,
        **{v: -1 for v in ("10", "J", "Q", "K", "A")},
    }
    _TABLES = {
        "hi_lo": _HI_LO,
        "omega_ii": _OMEGA_II,
        "wong_halves": _WONG_HALVES,
    }

    # ----------------------------------------------------------------------
    def __init__(self, system: str, num_decks: int):
        if system not in self._TABLES:
            raise ValueError("Unknown counting system")
        self.system = system
        self.table = self._TABLES[system]
        self.running: float = 0.0
        self.decks_remaining: float = num_decks

    # ----------------------------------------------------------------------
    def update(self, card_value: str):
        self.running += self.table[card_value]

    def set_decks_remaining(self, cards_left: int):
        self.decks_remaining = max(cards_left / 52, 0.01)

    # ----------------------------------------------------------------------
    @property
    def true_count(self) -> float:
        return self.running / self.decks_remaining if self.decks_remaining > 0 else 0.0

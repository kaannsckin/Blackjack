# counting_systems.py
from typing import Dict

class CardCounter:
    def __init__(self, system: str, decks_remaining: float):
        self.running_count = 0
        self.system = system
        self.decks_remaining = decks_remaining

    # ----------------------------- değer tabloları --------------------------
    _HI_LO: Dict[str, int] = {**{str(n): +1 for n in range(2, 7)},
                              **{str(n): 0  for n in (7, 8, 9)},
                              **{v: -1 for v in ['10', 'J', 'Q', 'K', 'A']}}
    _OMEGA_II: Dict[str, int] = {**{v: +1 for v in ('2', '3', '7')},
                                 **{v: +2 for v in ('4', '5', '6')},
                                 **{'9': -1},
                                 **{v: -2 for v in ('10', 'J', 'Q', 'K', 'A')},
                                 **{'8': 0}}
    _WONG_HALVES: Dict[str, float] = {'2': +0.5, '3': +1, '4': +1,
                                      '5': +1.5, '6': +1, '7': +0.5,
                                      '8': 0, '9': -0.5,
                                      **{v: -1 for v in ('10', 'J', 'Q', 'K', 'A')}}

    _SYSTEMS = {"hi_lo": _HI_LO,
                "omega_ii": _OMEGA_II,
                "wong_halves": _WONG_HALVES}

    # ------------------------ ana metotlar ----------------------------------
    def update(self, card_value: str):
        self.running_count += self._SYSTEMS[self.system][card_value]

    @property
    def true_count(self) -> float:
        if self.decks_remaining <= 0:
            return 0
        return self.running_count / self.decks_remaining

# betting.py – betting ramps synced with True Count & deviation risk
"""Provides flat, classic spread and dynamic Kelly betting functions.
The dynamic Kelly ramp uses per-TC edge estimates and bankroll volatility to
return an optimal fraction-of-bankroll wager.
"""
from typing import Callable

###############################################################################
# PARAMETERS (tweak as needed)
###############################################################################

# Estimated player edge (%) per True Count for Hi‑Lo in 6‑deck, S17, DAS game.
EDGE_BY_TC = {
    -2: -2.5,   # heavy negative edge
    -1: -1.0,
     0: -0.5,
     1:  0.2,
     2:  0.5,
     3:  1.0,
     4:  1.5,
     5:  2.0,
     6:  2.5,
}
# Volatility (standard deviation of one hand) – typical 1.15 for 6‑deck
SIGMA = 1.15

# Classic bet spread table (min_bet × multiplier)
SPREAD_TABLE = {
    -999: 1,   # TC < 0
     0:   1,   # TC 0
     1:   2,
     2:   4,
     3:   6,
     4:   8,
     5:  10,
}
###############################################################################

# ---------------------------------------------------------------------------
# Helper – map TC to edge %
# ---------------------------------------------------------------------------

def _edge_from_tc(tc: float) -> float:
    """Interpolate edge for fractional TC values."""
    # clamp range
    lo = max(min(int(tc), 6), -2)
    hi = lo + 1 if tc - lo > 0 and lo < 6 else lo
    if lo == hi:
        return EDGE_BY_TC[lo]
    # linear interpolate
    edge = EDGE_BY_TC[lo] + (EDGE_BY_TC[hi] - EDGE_BY_TC[lo]) * (tc - lo)
    return edge

# ---------------------------------------------------------------------------
# Betting functions
# ---------------------------------------------------------------------------

def flat(min_bet: int, tc: float, bankroll: int, **_) -> int:
    return min_bet

def spread(min_bet: int, tc: float, bankroll: int, **_) -> int:
    mult = 1
    for tc_thresh, m in sorted(SPREAD_TABLE.items()):
        if tc >= tc_thresh:
            mult = m
    return min_bet * mult

def kelly(min_bet: int, tc: float, bankroll: int, risk_fraction: float = 1.0, **_) -> int:
    """Kelly criterion with edge from TC and sigma. risk_fraction∈[0,1]."""
    edge_pct = _edge_from_tc(tc) / 100.0
    if edge_pct <= 0:
        return min_bet  # no advantage: bet minimum
    kelly_fraction = (edge_pct / (SIGMA ** 2)) * risk_fraction
    wager = bankroll * kelly_fraction
    # Never below table min
    return max(min_bet, int(wager))

BETTING_FUNCTIONS: dict[str, Callable[..., int]] = {
    "flat": flat,
    "spread": spread,
    "kelly": kelly,
}

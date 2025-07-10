import logging
from collections import defaultdict
from math import sqrt
from typing import List, Dict, Optional
from counting_systems import CardCounter
from blackjack_engine import BlackjackGame

logger = logging.getLogger(__name__)

class BlackjackSimulation:
    """Run many rounds and print Wilson 95% CI for overall win rate."""

    def __init__(self, num_games: int, players_cfg: List[Dict], num_decks: int, count_system: str = "hi_lo"):
        self.num_games = num_games
        self.players_cfg = players_cfg
        self.num_decks = num_decks
        self.counter = CardCounter(count_system, num_decks)
        self.records: List[Dict] = []

    # ------------------------------------------------------------------
    def run(self):
        for g in range(self.num_games):
            game = BlackjackGame(self.players_cfg, self.num_decks, self.counter, g)
            res = game.play()
            self.records.extend(res["logs"])
            if (g + 1) % 10_000 == 0:
                logger.info("%d / %d rounds completed", g + 1, self.num_games)
        self._summary()

    # ------------------------------------------------------------------
    def _summary(self):
        buckets = defaultdict(lambda: {"kazandi": 0, "kaybetti": 0, "push": 0})
        sonuc_map = {2: "kazandi", 1: "push", 0: "kaybetti"}
        wins = 0
        total_hands = 0
        for rec in self.records:
            if rec.get("sonuc") is None:
                continue
            total_hands += 1
            if rec["sonuc"] == 2:
                wins += 1
            tc = rec.get("true_count", 0)
            tc_bucket = ">+2" if tc > 2 else "-2-+2" if -2 <= tc <= 2 else "<-2"
            key = (rec["player_hand_val"], rec["dealer_up"], tc_bucket, rec["action"])
            sonuc_str = sonuc_map.get(rec["sonuc"], "kaybetti")
            buckets[key][sonuc_str] += 1

        logger.info("=== Outcome Summary ===")
        for (h_val, d_up, tc_b, act), res in buckets.items():
            total = sum(res.values())
            win_rate = res["kazandi"] * 100 / total if total else 0
            logger.info(
                "Hand=%s Dealer=%s TC=%s Act=%s -> Win %.2f%% (%d)",
                h_val,
                d_up,
                tc_b,
                act,
                win_rate,
                total,
            )

        # Wilson 95% CI for overall player win probability
        if total_hands:
            p_hat = wins / total_hands
            z = 1.96
            denom = 1 + z**2 / total_hands
            centre = p_hat + z**2 / (2 * total_hands)
            adj = z * sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total_hands)) / total_hands)
            ci_low = (centre - adj) / denom
            ci_high = (centre + adj) / denom
            logger.info(
                "Overall win‑rate %.3f (Wilson 95%% CI: %.3f – %.3f) based on %d hands",
                p_hat,
                ci_low,
                ci_high,
                total_hands,
            )

# ----------------------------------------------------------------------
class TestSimulation:
    """Mini simulation that prints every action for debugging."""

    def __init__(self, num_test_rounds: int = 10, players_cfg: Optional[List[Dict]] = None, num_decks: int = 6, count_system: str = "hi_lo"):
        if players_cfg is None:
            players_cfg = [
                {"strategy": "smart", "bet_style": "spread"},
                {"strategy": "smart", "bet_style": "kelly"},
            ]
        self.num_test_rounds = num_test_rounds
        self.players_cfg = players_cfg
        self.num_decks = num_decks
        self.counter = CardCounter(count_system, num_decks)

    def run(self):
        print(f"\n=== Test Simulation: {self.num_test_rounds} Tur ===\n")
        for g in range(1, self.num_test_rounds + 1):
            print(f"--- Tur {g} ---")
            game = BlackjackGame(self.players_cfg, self.num_decks, self.counter, g)
            game._deal_initial()
            dealer_up = game.dealer.hand.cards[0]
            print(f"Krupiye açık kartı: {dealer_up.value}")
            for idx, p in enumerate(game.players, 1):
                print(f"Oyuncu {idx} eli: {p.hands[0].value()}")
            print("… (debug moves skipped) …")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    players_cfg = [
        {"strategy": "smart", "bet_style": "spread"},
        {"strategy": "smart", "bet_style": "kelly"},
    ]
    sim = BlackjackSimulation(20_000, players_cfg, num_decks=6)
    sim.run()

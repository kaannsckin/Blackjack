# =============================================================
# simulation.py (refactored)
# =============================================================
"""Monte‑Carlo simulation harness for the refactored blackjack engine."""
import logging
from collections import Counter
from typing import List
from blackjack import BlackjackGame, Deck  # self‑import

logger = logging.getLogger(__name__)


class BlackjackSimulation:
    def __init__(self, num_games: int, num_players: int, player_types: List[str], num_decks: int):
        self.num_games = num_games
        self.num_players = num_players
        self.player_types = player_types
        self.num_decks = num_decks
        self.card_statistics: Counter = Counter()
        self.player_scores: List[int] = [0] * num_players  # +ve for wins, -ve for losses
        self.total_rounds: int = 0
        self.initial_deck_stats_collected: bool = False

    # ------------------------------------------------------------------
    def _track_cards(self, game: BlackjackGame) -> None:
        for player in game.players:
            for hand in player.hands:
                for card in hand.cards:
                    self.card_statistics[card.value] += 1
        for card in game.dealer.hand.cards:
            self.card_statistics[card.value] += 1

    # ------------------------------------------------------------------
    def _update_win_stats(self, results):
        dealer_total = results["dealer"]
        for i in range(self.num_players):
            base = f"player_{i+1}"
            h = 1
            while f"{base}_hand_{h}" in results:
                res = results[f"{base}_hand_{h}"]
                player_total = res["total"]
                double = res["double"]
                points = 2 if double else 1
                # Determine outcome
                if player_total > 21:
                    self.player_scores[i] -= points
                elif dealer_total > 21 or player_total > dealer_total:
                    self.player_scores[i] += points
                elif player_total < dealer_total:
                    self.player_scores[i] -= points
                # tie: 0
                h += 1

    # ------------------------------------------------------------------
    def _calculate_card_percentages(self, draws_done):
        percentages = {v: (c / draws_done) * 100 for v, c in self.card_statistics.items()}
        logger.info("Card percentages after 75 %% of shoe: ")
        for v, pct in sorted(percentages.items()):
            logger.info("Card %s: %.2f%%", v, pct)

    # ------------------------------------------------------------------
    def _update_deck_stats(self, deck: Deck):
        remaining = deck.cards_remaining()
        total_initial = 52 * deck.num_decks
        # collect once when 75 % consumed
        if not self.initial_deck_stats_collected and remaining <= total_initial * 0.25:
            self._calculate_card_percentages(total_initial - remaining)
            self.initial_deck_stats_collected = True

    # ------------------------------------------------------------------
    def run(self):
        for g in range(self.num_games):
            game = BlackjackGame(self.num_players, self.player_types, self.num_decks)
            self.total_rounds += 1
            self._track_cards(game)
            results = game.play()
            self._update_deck_stats(game.deck)
            self._update_win_stats(results)
            if (g + 1) % 10000 == 0:
                logger.info("Progress: %d / %d games completed", g + 1, self.num_games)

        self._print_summary()

    # ------------------------------------------------------------------
    def _print_summary(self):
        logger.info("\n=== Final Simulation Statistics ===")
        for i, score in enumerate(self.player_scores, start=1):
            win_pct = (score / self.total_rounds) * 100 if self.total_rounds else 0
            logger.info("Player %d win percentage: %.2f%%", i, win_pct)
        logger.info("Simulation complete – %d rounds played.\n", self.total_rounds)


# ----------------------------------------------------------------------
if __name__ == "__main__":
    TOTAL_GAMES = 100_000
    NUM_PLAYERS = 4
    PLAYER_TYPES = ["akilli", "aptal", "aptal", "akilli"]
    NUM_DECKS = 4

    sim = BlackjackSimulation(TOTAL_GAMES, NUM_PLAYERS, PLAYER_TYPES, NUM_DECKS)
    sim.run()

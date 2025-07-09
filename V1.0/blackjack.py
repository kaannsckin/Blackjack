# =============================================================
# Blackjack.py (refactored)
# =============================================================
"""
Refactored blackjack engine with constants, logging, penetration control,
re-usable action dispatch and cleaner percentage handling.  Designed so that
simulation modules can import without further boiler-plate.
"""
import random
import logging
from typing import List, Dict, Callable, Any

# ---------------------------------------------------------------------------
# Logging configuration – INFO by default, DEBUG for verbose simulation runs
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Game constants  – single source of truth for rule changes / scenario tests
# ---------------------------------------------------------------------------
BLACKJACK: int = 21
DEALER_STAND_SOFT: int = 17  # Dealer stands on all 17 incl. soft 17 (S17).
ACE_HIGH: int = 11
ACE_LOW: int = 1
# 0.25  means shuffle when 75 % of the shoe has been used (penetration 75 %).
MIN_PENETRATION_RATIO: float = 0.25

# Type aliases
CardValue = str  # '2'..'10', 'J', 'Q', 'K', 'A'
Suit = str       # 'Hearts', 'Diamonds', 'Clubs', 'Spades'

# ---------------------------------------------------------------------------
# Card & Deck
# ---------------------------------------------------------------------------
class Card:
    """Represents a single card."""
    def __init__(self, value: CardValue, suit: Suit) -> None:
        self.value = value
        self.suit = suit

    # ---------------------------------------------------------------------
    def card_value(self) -> int:
        if self.value in {"J", "Q", "K"}:
            return 10
        if self.value == "A":
            return ACE_HIGH
        return int(self.value)

    # ---------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.value} of {self.suit}"


class Deck:
    """A shoe of *num_decks* freshly shuffled decks."""
    suits: List[Suit] = ["Hearts", "Diamonds", "Clubs", "Spades"]
    values: List[CardValue] = [
        "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A",
    ]

    # ---------------------------------------------------------------------
    def __init__(self, num_decks: int = 1) -> None:
        self.num_decks = num_decks
        self._total_cards_initial: int = 52 * num_decks
        self.reset()

    # ---------------------------------------------------------------------
    def reset(self) -> None:
        """(Re)build and shuffle the shoe."""
        self.cards: List[Card] = [
            Card(value, suit)
            for value in self.values
            for suit in self.suits
        ] * self.num_decks
        random.shuffle(self.cards)
        logger.info("Deck reshuffled – new shoe in play.")

    # ---------------------------------------------------------------------
    def _check_penetration(self) -> None:
        """Shuffle automatically once penetration threshold reached."""
        if len(self.cards) <= MIN_PENETRATION_RATIO * self._total_cards_initial:
            self.reset()

    # ---------------------------------------------------------------------
    def deal_card(self) -> Card:
        if not self.cards:
            self.reset()
        card = self.cards.pop()
        self._check_penetration()
        return card

    # Convenience for simulators -----------------------------------------
    def cards_remaining(self) -> int:
        return len(self.cards)


# ---------------------------------------------------------------------------
# Hand entity (player or dealer hand)
# ---------------------------------------------------------------------------
class Hand:
    def __init__(self) -> None:
        self.cards: List[Card] = []
        self.is_double: bool = False  # true if doubled-down

    # ---------------------------------------------------------------------
    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    # ---------------------------------------------------------------------
    def value(self) -> int:
        total = sum(c.card_value() for c in self.cards)
        num_aces = sum(c.value == "A" for c in self.cards)
        # Adjust for soft aces
        while total > BLACKJACK and num_aces:
            total -= 10  # convert an ACE from 11 to 1
            num_aces -= 1
        return total

    # ---------------------------------------------------------------------
    def is_soft(self) -> bool:
        return any(c.value == "A" for c in self.cards) and self.value() <= BLACKJACK

    # ---------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return ", ".join(str(c) for c in self.cards)


# ---------------------------------------------------------------------------
# Player & Dealer
# ---------------------------------------------------------------------------
class Player:
    """A blackjack player with a selectable strategy."""
    def __init__(self, strategy_type: str):
        self.hands: List[Hand] = [Hand()]
        self.strategy_type = strategy_type  # "akilli" vs "aptal"
        self.split_eligible: bool = True

    # ---------------------------------------------------------------------
    def split_hand(self, deck: Deck) -> None:
        if len(self.hands) == 1 and self.split_eligible:
            h = self.hands[0]
            first_card, second_card = h.cards
            self.hands = [Hand(), Hand()]
            self.hands[0].add_card(first_card)
            self.hands[1].add_card(second_card)
            # each new hand draws one additional card
            self.hands[0].add_card(deck.deal_card())
            self.hands[1].add_card(deck.deal_card())
            self.split_eligible = False

    # ---------------------------------------------------------------------
    def make_move(self, dealer_card: Card, deck: Deck, hand_index: int = 0) -> str:
        if self.strategy_type == "akilli":
            return self._smart_strategy(dealer_card, hand_index)
        return self._dumb_strategy(hand_index)

    # ---------------------------------------------------------------------
    def _smart_strategy(self, dealer_card: Card, hand_index: int = 0) -> str:
        # simplified basic-strategy subset (enough for refactoring demo)
        current = self.hands[hand_index]
        total = current.value()
        dealer_val = dealer_card.card_value()

        # Stand on hard 17+
        if total >= DEALER_STAND_SOFT:
            return "stand"

        # basic draw / double logic demo
        if total in {9, 10, 11}:
            return "double" if dealer_val < 10 else "hit"
        if total <= 11:
            return "hit"
        # else between 12-16
        return "stand" if dealer_val <= 6 else "hit"

    # ---------------------------------------------------------------------
    def _dumb_strategy(self, hand_index: int = 0) -> str:
        total = self.hands[hand_index].value()
        if total <= 10:
            return "hit"
        if 10 < total <= 16:
            return "hit" if random.random() < 0.5 else "stand"
        return "stand"


class Dealer:
    def __init__(self):
        self.hand = Hand()

    # ---------------------------------------------------------------------
    def play(self, deck: Deck) -> None:
        while self.hand.value() < DEALER_STAND_SOFT:
            self.hand.add_card(deck.deal_card())


# ---------------------------------------------------------------------------
# BlackjackGame wrapper – one round per instance
# ---------------------------------------------------------------------------
class BlackjackGame:
    def __init__(self, num_players: int, player_types: List[str], num_decks: int):
        self.deck = Deck(num_decks)
        self.players = [Player(player_types[i]) for i in range(num_players)]
        self.dealer = Dealer()

    # ---------------------------------------------------------------------
    def _deal_initial(self) -> None:
        for player in self.players:
            player.hands[0].add_card(self.deck.deal_card())
            player.hands[0].add_card(self.deck.deal_card())
        self.dealer.hand.add_card(self.deck.deal_card())
        self.dealer.hand.add_card(self.deck.deal_card())

    # ---------------------------------------------------------------------
    def _execute_action(self, player: Player, hand_index: int, action: str) -> None:
        """Execute the chosen action using a small dispatch table."""
        current = player.hands[hand_index]

        def _hit():
            current.add_card(self.deck.deal_card())

        def _double():
            current.is_double = True
            current.add_card(self.deck.deal_card())

        def _split():
            player.split_hand(self.deck)

        dispatch: Dict[str, Callable[[], Any]] = {
            "hit": _hit,
            "double": _double,
            "split": _split,
            "stand": lambda: None,
        }
        dispatch.get(action, lambda: None)()

    # ---------------------------------------------------------------------
    def play(self) -> Dict[str, Any]:
        self._deal_initial()
        logger.debug("Dealer shows %s", self.dealer.hand.cards[0])

        # Player turns ----------------------------------------------------
        for idx, player in enumerate(self.players, start=1):
            hand_idx = 0
            while hand_idx < len(player.hands):
                while True:
                    action = player.make_move(self.dealer.hand.cards[0], self.deck, hand_idx)
                    self._execute_action(player, hand_idx, action)
                    # break conditions
                    total = player.hands[hand_idx].value()
                    if action in {"stand", "double"} or total > BLACKJACK or action == "split":
                        break
                hand_idx += 1

        # Dealer plays ----------------------------------------------------
        self.dealer.play(self.deck)
        dealer_total = self.dealer.hand.value()

        # Compile results -------------------------------------------------
        results: Dict[str, Any] = {"dealer": dealer_total}
        for p_idx, player in enumerate(self.players, start=1):
            for h_idx, hand in enumerate(player.hands, start=1):
                results[f"player_{p_idx}_hand_{h_idx}"] = {
                    "total": hand.value(),
                    "double": hand.is_double,
                }
        return results
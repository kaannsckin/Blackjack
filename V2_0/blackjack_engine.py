import random, logging
from typing import List, Dict, Any, Optional
from counting_systems import CardCounter
from betting import BETTING_FUNCTIONS
from deviations import DeviationEngine, load_index_plays
from basic_strategy import BasicStrategy

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

BLACKJACK = 21
DEALER_STAND_SOFT = 17
ACE_HIGH = 11
MIN_PENETRATION_RATIO = 0.25

# ----------------- Card & Deck -----------------
class Card:
    def __init__(self, value: str, suit: str):
        self.value, self.suit = value, suit
    def card_value(self):
        if self.value in {"J", "Q", "K"}: return 10
        if self.value == "A": return ACE_HIGH
        return int(self.value)
    def __repr__(self):
        return f"{self.value} of {self.suit}"

class Deck:
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    values = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    def __init__(self, num_decks: int, counter: CardCounter):
        self.num_decks = num_decks
        self.counter = counter
        self._initial = 52 * num_decks
        self.reset()
    def reset(self):
        self.cards = [Card(v, s) for v in self.values for s in self.suits] * self.num_decks
        random.shuffle(self.cards)
        logger.info("Deck reshuffled – new shoe")
        self.counter.running = 0
        self._update_counter_decks()
    def _update_counter_decks(self):
        self.counter.set_decks_remaining(len(self.cards))
    def _check_penetration(self):
        if len(self.cards) <= self._initial * MIN_PENETRATION_RATIO:
            self.reset()
    def deal_card(self):
        if not self.cards:
            self.reset()
        card = self.cards.pop()
        self.counter.update(card.value)
        self._update_counter_decks()
        self._check_penetration()
        return card
    def cards_remaining(self):
        return len(self.cards)

# ----------------- Hand -----------------
class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        self.is_double = False
        self.bet: int = 0
    def add_card(self, card):
        self.cards.append(card)
    def value(self):
        total = sum(c.card_value() for c in self.cards)
        aces = sum(c.value == "A" for c in self.cards)
        while total > BLACKJACK and aces:
            total -= 10
            aces -= 1
        return total
    def is_soft(self):
        return any(c.value == "A" for c in self.cards) and self.value() <= BLACKJACK

# ----------------- Player -----------------
class Player:
    def __init__(self, strategy: str, bet_style: str = "flat", bankroll: int = 1000, min_bet: int = 10):
        self.hands = [Hand()]
        self.strategy = strategy
        self.split_ok = True
        self.betting_fn = BETTING_FUNCTIONS[bet_style]
        self.bankroll = bankroll
        self.min_bet = min_bet
    def wager(self, tc: float):
        bet = self.betting_fn(self.min_bet, tc, bankroll=self.bankroll)
        self.bankroll -= bet
        return bet
    def payout(self, hand_total, dealer_total):
        if hand_total > 21: return 0
        if dealer_total > 21 or hand_total > dealer_total: return 2
        if hand_total == dealer_total: return 1
        return 0
    def make_move(self, dealer_card, deck, tc: float, idx: int = 0):
        if hasattr(self, "strategy_engine"):
            return self.strategy_engine.decide(self, dealer_card, deck, idx)
        # dumb fallback
        v = self.hands[idx].value()
        if v <= 10: return "hit"
        if v <= 16: return "hit" if random.random() < 0.5 else "stand"
        return "stand"

class Dealer:
    def __init__(self):
        self.hand = Hand()
    def play(self, deck):
        while self.hand.value() < DEALER_STAND_SOFT:
            self.hand.add_card(deck.deal_card())

# ----------------- Game -----------------
class BlackjackGame:
    """Plays one full round and returns dealer total & decision logs."""
    def __init__(self, players_cfg: List[Dict[str, Any]], num_decks: int, counter: CardCounter, game_id: int):
        self.counter = counter
        self.deck = Deck(num_decks, self.counter)
        self.gid = game_id

        # Build players
        self.players: List[Player] = []
        for cfg in players_cfg:
            p = Player(**cfg)
            strat = cfg.get("strategy", "dumb")
            if strat in {"basic", "smart"}:
                basic = BasicStrategy()
                rules = load_index_plays(cfg.get("index_plays_file", "data/index_plays.json")) if strat == "smart" else []
                dev_engine = DeviationEngine(rules)
                from counting import StrategyEngine
                p.strategy_engine = StrategyEngine(basic, dev_engine, self.counter)
            self.players.append(p)
        self.dealer = Dealer()
        self.logs: List[Dict[str, Any]] = []

    # ------------- helpers -------------
    def _deal_initial(self):
        for p in self.players:
            p.hands[0].add_card(self.deck.deal_card())
            p.hands[0].add_card(self.deck.deal_card())
            tc = self.counter.true_count
            p.hands[0].bet = p.wager(tc)
        self.dealer.hand.add_card(self.deck.deal_card())

    def _record(self, hand: Hand, dealer_up: Card, tc: float, act: str, outcome: Optional[int] = None):
        self.logs.append({
            "tur_id": self.gid,
            "player_hand_val": hand.value(),
            "dealer_up": dealer_up.value,
            "true_count": round(tc, 2),
            "action": act,
            "sonuc": outcome,
        })

    # ------------- main -------------
    def play(self):
        self._deal_initial()
        dealer_up = self.dealer.hand.cards[0]

        # Player turns
        for player in self.players:
            idx = 0
            while idx < len(player.hands):
                hand = player.hands[idx]
                while True:
                    tc = self.counter.true_count
                    act = player.make_move(dealer_up, self.deck, tc, idx)
                    self._record(hand, dealer_up, tc, act)
                    if act == "hit":
                        hand.add_card(self.deck.deal_card())
                        if hand.value() > BLACKJACK:
                            break
                    elif act == "double":
                        extra = min(player.bankroll, hand.bet)
                        player.bankroll -= extra
                        hand.bet += extra
                        hand.is_double = True
                        hand.add_card(self.deck.deal_card())
                        break
                    elif act == "split" and player.split_ok and len(hand.cards) == 2 and hand.cards[0].card_value() == hand.cards[1].card_value():
                        player.split_ok = False
                        c1, c2 = hand.cards
                        h1, h2 = Hand(), Hand()
                        h1.add_card(c1); h2.add_card(c2)
                        h1.add_card(self.deck.deal_card()); h2.add_card(self.deck.deal_card())
                        h1.bet = h2.bet = hand.bet
                        player.bankroll -= hand.bet
                        player.hands[idx] = h1
                        player.hands.insert(idx + 1, h2)
                        hand = player.hands[idx]
                        continue
                    else:
                        break
                idx += 1

        # Dealer turn
        self.dealer.play(self.deck)
        dealer_total = self.dealer.hand.value()

        # Settlement
        for player in self.players:
            for hand in player.hands:
                outcome = player.payout(hand.value(), dealer_total)
                for rec in self.logs:
                    if rec["sonuc"] is None:
                        rec["sonuc"] = outcome
                        break

        return {"dealer": dealer_total, "logs": self.logs}
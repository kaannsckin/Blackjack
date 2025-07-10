# counting.py
from basic_strategy import BasicStrategy
from deviations import DeviationEngine
from counting_systems import CardCounter

class StrategyEngine:
    """Combines basic strategy, deviation indices and a running CardCounter."""

    def __init__(self, basic: BasicStrategy, deviations: DeviationEngine, counter: CardCounter):
        self.basic = basic
        self.deviations = deviations
        self.counter = counter

    def decide(self, player, dealer_up, deck, hand_index: int = 0) -> str:
        # gecikmeli import – circular import'ı önler
        from blackjack_engine import Hand

        hand: Hand = player.hands[hand_index]
        can_double = len(hand.cards) == 2
        base_action = self.basic.action(hand, dealer_up, can_double, player.split_ok)
        tc = self.counter.true_count
        dev_action = self.deviations.check(hand.value(), dealer_up.card_value(), tc)
        return dev_action or base_action
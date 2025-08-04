"""
V3_0 Simulation Engine for F2.5 Motor Entegrasyonu

Enhanced simulation engine with AI betting strategy support.
Extends V2_0 architecture with modern RL integration.
"""

from __future__ import annotations

import random
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

# Local imports
from utils.basic_strategy import BasicStrategy
from utils.ai_play_strategy import create_ai_play_strategy
from utils.ai_betting_strategy import create_ai_betting_strategy, BettingConfig


@dataclass
class PlayerConfig:
    """Configuration for player strategies and settings."""
    name: str = "Player1"
    play_strategy: str = "basic"  # "basic", "ai_play", "random"
    bet_strategy: str = "flat"    # "flat", "tc_based", "ai_bet"
    bankroll: float = 10000.0
    min_bet: float = 10.0
    max_bet: float = 500.0
    
    # AI model paths (optional)
    play_model_path: Optional[str] = None
    bet_model_path: Optional[str] = None
    bet_algorithm: str = "ppo"  # for AI betting
    
    # Strategy-specific parameters
    flat_bet_amount: float = 10.0
    tc_bet_multiplier: float = 2.0  # multiply min_bet by (TC * multiplier)
    
    # Risk management
    risk_threshold: float = 0.01  # 1% risk of ruin
    stop_loss: Optional[float] = None  # Stop if bankroll drops below this
    stop_win: Optional[float] = None   # Stop if bankroll rises above this


@dataclass 
class GameConfig:
    """Configuration for game rules and environment."""
    num_decks: int = 6
    penetration: float = 0.75
    dealer_rule: str = "S17"  # "S17" or "H17"
    das: bool = True  # Double After Split
    surrender: bool = False
    blackjack_payout: float = 1.5  # 3:2 payout
    
    # Simulation parameters
    num_hands: int = 10000
    seed: Optional[int] = 42
    track_count: bool = True


class Card:
    """Simple card representation."""
    
    def __init__(self, value: int):
        """
        Initialize card.
        
        Args:
            value: Card value (1=Ace, 11-13=Face cards)
        """
        self.value = value
    
    def blackjack_value(self) -> int:
        """Get blackjack value (face cards = 10)."""
        return min(self.value, 10)
    
    def __repr__(self) -> str:
        if self.value == 1:
            return "A"
        elif self.value <= 10:
            return str(self.value)
        elif self.value == 11:
            return "J"
        elif self.value == 12:
            return "Q"
        else:
            return "K"


class Deck:
    """Multi-deck shoe with card counting support."""
    
    def __init__(self, num_decks: int = 6, seed: Optional[int] = None):
        self.num_decks = num_decks
        self.rng = random.Random(seed)
        self.cards: List[Card] = []
        self.dealt_cards: List[Card] = []
        self.running_count = 0
        self._initial_cards = num_decks * 52
        self._shuffle()
    
    def _shuffle(self) -> None:
        """Create and shuffle new shoe."""
        self.cards = []
        for _ in range(self.num_decks):
            for value in range(1, 14):  # A, 2-10, J, Q, K
                for _ in range(4):  # 4 suits
                    self.cards.append(Card(value))
        
        self.rng.shuffle(self.cards)
        self.dealt_cards = []
        self.running_count = 0
    
    def deal_card(self) -> Card:
        """Deal one card and update count."""
        if not self.cards:
            self._shuffle()
        
        card = self.cards.pop()
        self.dealt_cards.append(card)
        
        # Update Hi-Lo count
        self.running_count += self._hi_lo_value(card.blackjack_value())
        
        return card
    
    @staticmethod
    def _hi_lo_value(card_value: int) -> int:
        """Get Hi-Lo count value for card."""
        if 2 <= card_value <= 6:
            return 1
        elif card_value == 10 or card_value == 1:  # 10, J, Q, K, A
            return -1
        else:
            return 0
    
    def true_count(self) -> float:
        """Calculate true count."""
        remaining_decks = len(self.cards) / 52
        if remaining_decks <= 0:
            return 0.0
        return self.running_count / remaining_decks
    
    def penetration_reached(self, penetration: float) -> bool:
        """Check if penetration point is reached."""
        dealt_ratio = len(self.dealt_cards) / self._initial_cards
        return dealt_ratio >= penetration


class Hand:
    """Blackjack hand with betting information."""
    
    def __init__(self, bet_amount: float = 0.0):
        self.cards: List[Card] = []
        self.bet_amount = bet_amount
        self.is_doubled = False
        self.is_split = False
        self.is_busted = False
        self.is_blackjack = False
    
    def add_card(self, card: Card) -> None:
        """Add card to hand."""
        self.cards.append(card)
        self._update_status()
    
    def value(self) -> Tuple[int, bool]:
        """Get hand value and usable ace status."""
        total = sum(card.blackjack_value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.value == 1)
        
        # Handle aces
        usable_ace = False
        if aces > 0 and total + 10 <= 21:
            total += 10
            usable_ace = True
        
        return total, usable_ace
    
    def _update_status(self) -> None:
        """Update hand status flags."""
        total, _ = self.value()
        self.is_busted = total > 21
        self.is_blackjack = len(self.cards) == 2 and total == 21
    
    def can_split(self) -> bool:
        """Check if hand can be split."""
        return (len(self.cards) == 2 and 
                self.cards[0].blackjack_value() == self.cards[1].blackjack_value())
    
    def can_double(self) -> bool:
        """Check if hand can be doubled."""
        return len(self.cards) == 2 and not self.is_split


class Player:
    """
    Enhanced player with AI betting strategy support.
    
    F2.5 Implementation: Supports multiple betting strategies including AI.
    """
    
    def __init__(self, config: PlayerConfig):
        """Initialize player with configuration."""
        self.config = config
        self.bankroll = config.bankroll
        self.initial_bankroll = config.bankroll
        self.hands: List[Hand] = []
        
        # Initialize logger first (needed for strategy initialization)
        self.logger = logging.getLogger(f"Player-{config.name}")
        
        # Strategy initialization
        self.play_strategy = self._init_play_strategy()
        self.bet_strategy = self._init_bet_strategy()
        
        # Statistics tracking
        self.stats = {
            "hands_played": 0,
            "hands_won": 0,
            "hands_lost": 0,
            "hands_pushed": 0,
            "total_bet": 0.0,
            "total_winnings": 0.0,
            "max_bankroll": config.bankroll,
            "min_bankroll": config.bankroll,
            "blackjacks": 0,
            "splits": 0,
            "doubles": 0,
        }
    
    def _init_play_strategy(self):
        """Initialize playing strategy."""
        if self.config.play_strategy == "basic":
            return BasicStrategy()
        elif self.config.play_strategy == "ai_play":
            if not self.config.play_model_path:
                self.logger.warning("AI play strategy requested but no model path provided. Using basic strategy.")
                return BasicStrategy()
            
            from gymnasium import spaces
            action_space = spaces.Discrete(4)  # stand, hit, double, split
            
            try:
                return create_ai_play_strategy(
                    action_space=action_space,
                    model_path=self.config.play_model_path,
                    use_validation=True
                )
            except Exception as e:
                self.logger.error(f"Failed to load AI play strategy: {e}. Using basic strategy.")
                return BasicStrategy()
        elif self.config.play_strategy == "random":
            return None  # Will use random decisions
        else:
            self.logger.warning(f"Unknown play strategy: {self.config.play_strategy}. Using basic strategy.")
            return BasicStrategy()
    
    def _init_bet_strategy(self):
        """Initialize betting strategy."""
        if self.config.bet_strategy == "ai_bet":
            if not self.config.bet_model_path:
                self.logger.warning("AI bet strategy requested but no model path provided. Using flat betting.")
                return None
            
            try:
                return create_ai_betting_strategy(
                    model_path=self.config.bet_model_path,
                    algorithm=self.config.bet_algorithm,
                    min_bet=self.config.min_bet,
                    max_bet=self.config.max_bet,
                    initial_bankroll=self.config.bankroll
                )
            except Exception as e:
                self.logger.error(f"Failed to load AI bet strategy: {e}. Using flat betting.")
                return None
        else:
            return None  # Will use built-in betting logic
    
    def decide_bet(self, true_count: float, dealer_upcard: Optional[int] = None) -> float:
        """
        Decide bet amount for next hand.
        
        Args:
            true_count: Current true count
            dealer_upcard: Dealer's upcard (for AI betting context)
            
        Returns:
            Bet amount in units
        """
        if self.config.bet_strategy == "ai_bet" and self.bet_strategy is not None:
            # AI betting strategy
            # Use dummy values for player context since this is pre-hand
            player_total = 20  # Neutral value for pre-hand betting
            usable_ace = False
            previous_result = getattr(self, '_last_result', None)
            
            bet_amount = self.bet_strategy.decide_bet(
                player_total=player_total,
                dealer_up=dealer_upcard or 5,  # Use 5 as neutral if not provided
                usable_ace=usable_ace,
                true_count=true_count,
                current_bankroll=self.bankroll,
                previous_result=previous_result
            )
        elif self.config.bet_strategy == "tc_based":
            # True count based betting
            if true_count <= 1:
                bet_amount = self.config.min_bet
            else:
                multiplier = min(true_count * self.config.tc_bet_multiplier, 10)  # Cap at 10x
                bet_amount = min(self.config.min_bet * multiplier, self.config.max_bet)
        else:
            # Flat betting
            bet_amount = self.config.flat_bet_amount or self.config.min_bet
        
        # Apply bankroll constraints
        bet_amount = self._constrain_bet(bet_amount)
        
        return bet_amount
    
    def _constrain_bet(self, bet_amount: float) -> float:
        """Apply bankroll and rule constraints to bet."""
        # Minimum/maximum constraints
        bet_amount = max(self.config.min_bet, min(bet_amount, self.config.max_bet))
        
        # Can't bet more than bankroll
        bet_amount = min(bet_amount, self.bankroll)
        
        # Don't bet more than 20% of bankroll (risk management)
        max_bankroll_bet = self.bankroll * 0.2
        bet_amount = min(bet_amount, max_bankroll_bet)
        
        return round(bet_amount, 2)
    
    def decide_action(
        self, 
        hand: Hand, 
        dealer_upcard: Card, 
        true_count: float,
        can_split: bool = True,
        can_double: bool = True
    ) -> str:
        """
        Decide playing action for given hand.
        
        Args:
            hand: Current hand
            dealer_upcard: Dealer's upcard
            true_count: Current true count
            can_split: Whether splitting is allowed
            can_double: Whether doubling is allowed
            
        Returns:
            Action string: "stand", "hit", "double", "split"
        """
        if self.config.play_strategy == "random":
            # Random strategy for testing
            if can_split and hand.can_split() and random.random() < 0.1:
                return "split"
            elif can_double and hand.can_double() and random.random() < 0.1:
                return "double"
            elif random.random() < 0.5:
                return "hit"
            else:
                return "stand"
        
        # Use strategy engine
        hand_value, usable_ace = hand.value()
        
        if hasattr(self.play_strategy, 'get_action'):
            # Basic strategy interface
            action_int = self.play_strategy.get_action(
                player_total=hand_value,
                dealer_up=dealer_upcard.blackjack_value(),
                usable_ace=usable_ace,
                can_double=can_double and hand.can_double(),
                can_split=can_split and hand.can_split(),
                is_pair=hand.can_split()
            )
            
            # Convert to string
            action_map = {0: "stand", 1: "hit", 2: "double", 3: "split"}
            return action_map.get(action_int, "stand")
        
        elif hasattr(self.play_strategy, 'decide'):
            # AI strategy interface
            try:
                # Prepare observation for AI
                obs = np.array([hand_value, dealer_upcard.blackjack_value(), 
                               int(usable_ace), true_count], dtype=np.float32)
                
                action_int = self.play_strategy.decide(obs)
                action_map = {0: "stand", 1: "hit", 2: "double", 3: "split"}
                action = action_map.get(action_int, "stand")
                
                # Validate action constraints
                if action == "split" and not (can_split and hand.can_split()):
                    action = "hit" if hand_value < 17 else "stand"
                elif action == "double" and not (can_double and hand.can_double()):
                    action = "hit" if hand_value < 17 else "stand"
                
                return action
                
            except Exception as e:
                self.logger.warning(f"AI strategy decision failed: {e}. Using basic fallback.")
                # Fallback to simple strategy
                if hand_value < 12:
                    return "hit"
                elif hand_value > 16:
                    return "stand"
                else:
                    return "hit" if dealer_upcard.blackjack_value() >= 7 else "stand"
        
        # Fallback strategy
        if hand_value < 12:
            return "hit"
        elif hand_value > 16:
            return "stand"
        else:
            return "hit" if dealer_upcard.blackjack_value() >= 7 else "stand"
    
    def update_bankroll(self, amount: float) -> None:
        """Update bankroll and statistics."""
        self.bankroll += amount
        self.stats["max_bankroll"] = max(self.stats["max_bankroll"], self.bankroll)
        self.stats["min_bankroll"] = min(self.stats["min_bankroll"], self.bankroll)
        
        # Update AI betting strategy if using it
        if (self.config.bet_strategy == "ai_bet" and 
            self.bet_strategy is not None and 
            hasattr(self.bet_strategy, 'update_result')):
            self.bet_strategy.update_result(amount)
        
        # Store for next betting decision
        self._last_result = amount
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get player performance statistics."""
        total_hands = self.stats["hands_played"]
        if total_hands == 0:
            return self.stats
        
        win_rate = self.stats["hands_won"] / total_hands
        bankroll_change = self.bankroll - self.initial_bankroll
        roi = bankroll_change / self.initial_bankroll
        
        enhanced_stats = {
            **self.stats,
            "current_bankroll": self.bankroll,
            "initial_bankroll": self.initial_bankroll,
            "bankroll_change": bankroll_change,
            "roi": roi,
            "win_rate": win_rate,
            "avg_bet": self.stats["total_bet"] / total_hands if total_hands > 0 else 0,
            "profit_per_hand": bankroll_change / total_hands if total_hands > 0 else 0,
        }
        
        # Add AI betting strategy stats if available
        if (self.config.bet_strategy == "ai_bet" and 
            self.bet_strategy is not None and 
            hasattr(self.bet_strategy, 'get_statistics')):
            ai_stats = self.bet_strategy.get_statistics()
            enhanced_stats["ai_betting_stats"] = ai_stats
        
        return enhanced_stats
    
    def should_stop_playing(self) -> bool:
        """Check if player should stop based on stop-loss/stop-win."""
        if self.config.stop_loss and self.bankroll <= self.config.stop_loss:
            return True
        if self.config.stop_win and self.bankroll >= self.config.stop_win:
            return True
        return False


class Dealer:
    """Dealer with standard H17/S17 rules."""
    
    def __init__(self, rule: str = "S17"):
        """
        Initialize dealer.
        
        Args:
            rule: "S17" (stand on soft 17) or "H17" (hit on soft 17)
        """
        self.rule = rule
        self.hand = Hand()
    
    def should_hit(self) -> bool:
        """Determine if dealer should hit."""
        total, usable_ace = self.hand.value()
        
        if total < 17:
            return True
        elif total == 17:
            return self.rule == "H17" and usable_ace
        else:
            return False
    
    def play(self, deck: Deck) -> None:
        """Play dealer hand according to rules."""
        while self.should_hit():
            self.hand.add_card(deck.deal_card())


def create_default_player_config(
    name: str = "Player1",
    play_strategy: str = "basic",
    bet_strategy: str = "flat",
    bankroll: float = 10000.0,
    **kwargs
) -> PlayerConfig:
    """
    Factory function for creating player configurations.
    
    Args:
        name: Player name
        play_strategy: Playing strategy type
        bet_strategy: Betting strategy type
        bankroll: Initial bankroll
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured PlayerConfig
    """
    return PlayerConfig(
        name=name,
        play_strategy=play_strategy,
        bet_strategy=bet_strategy,
        bankroll=bankroll,
        **kwargs
    ) 
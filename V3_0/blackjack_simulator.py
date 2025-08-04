"""
Blackjack Simulator for F2.5 Motor Entegrasyonu

Complete simulation engine that orchestrates games with AI betting integration.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
from pathlib import Path

from simulation_engine import (
    Player, Dealer, Deck, Hand, Card,
    PlayerConfig, GameConfig, create_default_player_config
)


@dataclass
class SimulationResults:
    """Results from a simulation run."""
    players_stats: List[Dict[str, Any]]
    game_config: GameConfig
    total_hands: int
    elapsed_time: float
    hands_per_second: float


class BlackjackSimulator:
    """
    Main blackjack simulator with AI betting integration.
    
    F2.5 Implementation: Complete game orchestration with AI strategies.
    """
    
    def __init__(self, game_config: GameConfig, players_config: List[PlayerConfig]):
        """
        Initialize simulator.
        
        Args:
            game_config: Game rules and simulation parameters
            players_config: List of player configurations
        """
        self.game_config = game_config
        self.players_config = players_config
        
        # Initialize components
        self.deck = Deck(game_config.num_decks, game_config.seed)
        self.dealer = Dealer(game_config.dealer_rule)
        self.players = [Player(config) for config in players_config]
        
        # Simulation state
        self.hands_played = 0
        self.total_hands_target = game_config.num_hands
        
        # Logging
        self.logger = logging.getLogger("BlackjackSimulator")
        self.logger.setLevel(logging.INFO)
        
        # Performance tracking
        self.start_time = None
        self.end_time = None
    
    def run_simulation(self, verbose: bool = False) -> SimulationResults:
        """
        Run complete simulation.
        
        Args:
            verbose: Whether to print progress updates
            
        Returns:
            Simulation results
        """
        self.logger.info(f"Starting simulation: {self.total_hands_target} hands")
        if verbose:
            print(f"🎯 Starting {self.total_hands_target:,} hand simulation...")
            print(f"   Players: {len(self.players)}")
            print(f"   Decks: {self.game_config.num_decks}")
            print(f"   Penetration: {self.game_config.penetration:.1%}")
        
        self.start_time = time.time()
        
        try:
            while self.hands_played < self.total_hands_target:
                # Check if any player should stop
                active_players = [p for p in self.players if not p.should_stop_playing()]
                if not active_players:
                    self.logger.info("All players stopped playing (stop-loss/win reached)")
                    break
                
                # Play one hand
                self._play_hand(active_players)
                self.hands_played += 1
                
                # Progress updates
                if verbose and self.hands_played % 1000 == 0:
                    elapsed = time.time() - self.start_time
                    rate = self.hands_played / elapsed
                    eta = (self.total_hands_target - self.hands_played) / rate
                    print(f"   Hand {self.hands_played:,}/{self.total_hands_target:,} "
                          f"({self.hands_played/self.total_hands_target:.1%}) "
                          f"- {rate:.0f} hands/sec - ETA: {eta:.0f}s")
                
                # Shuffle check
                if self.deck.penetration_reached(self.game_config.penetration):
                    self.deck = Deck(self.game_config.num_decks, self.game_config.seed)
                    if verbose and self.hands_played % 1000 == 0:
                        print("   🔄 Deck shuffled")
        
        except KeyboardInterrupt:
            self.logger.info(f"Simulation interrupted at hand {self.hands_played}")
            if verbose:
                print("\n⚠️  Simulation interrupted by user")
        
        except Exception as e:
            self.logger.error(f"Simulation error: {e}")
            if verbose:
                print(f"\n❌ Simulation error: {e}")
            raise
        
        self.end_time = time.time()
        
        # Generate results
        results = self._generate_results()
        
        if verbose:
            self._print_summary(results)
        
        return results
    
    def _play_hand(self, players: List[Player]) -> None:
        """Play one complete hand."""
        # Reset dealer
        self.dealer.hand = Hand()
        
        # Reset player hands and get bets
        for player in players:
            player.hands = [Hand()]
            
            # Get bet amount
            true_count = self.deck.true_count() if self.game_config.track_count else 0.0
            bet_amount = player.decide_bet(true_count)
            
            # Update bankroll and set bet
            player.bankroll -= bet_amount
            player.hands[0].bet_amount = bet_amount
            player.stats["total_bet"] += bet_amount
        
        # Deal initial cards
        for _ in range(2):
            for player in players:
                player.hands[0].add_card(self.deck.deal_card())
            self.dealer.hand.add_card(self.deck.deal_card())
        
        # Check for dealer blackjack
        dealer_total, _ = self.dealer.hand.value()
        dealer_blackjack = self.dealer.hand.is_blackjack
        
        # Process each player
        for player in players:
            for hand_idx, hand in enumerate(player.hands):
                # Skip if dealer has blackjack (unless player also has blackjack)
                if dealer_blackjack and not hand.is_blackjack:
                    continue
                
                # Player decision loop
                if not hand.is_blackjack:
                    self._play_player_hand(player, hand_idx, hand)
        
        # Dealer plays (unless all players busted or have blackjack)
        need_dealer_play = any(
            not hand.is_busted and not (dealer_blackjack and not hand.is_blackjack)
            for player in players
            for hand in player.hands
        )
        
        if need_dealer_play and not dealer_blackjack:
            self.dealer.play(self.deck)
        
        # Resolve all hands and update bankrolls
        self._resolve_hands(players)
    
    def _play_player_hand(self, player: Player, hand_idx: int, hand: Hand) -> None:
        """Play one player hand to completion."""
        true_count = self.deck.true_count() if self.game_config.track_count else 0.0
        
        while not hand.is_busted and not hand.is_blackjack:
            # Get action
            action = player.decide_action(
                hand=hand,
                dealer_upcard=self.dealer.hand.cards[0],
                true_count=true_count,
                can_split=len(player.hands) < 4,  # Limit splits
                can_double=True
            )
            
            if action == "stand":
                break
            elif action == "hit":
                hand.add_card(self.deck.deal_card())
            elif action == "double":
                hand.add_card(self.deck.deal_card())
                hand.is_doubled = True
                hand.bet_amount *= 2
                player.bankroll -= hand.bet_amount / 2  # Additional bet
                player.stats["total_bet"] += hand.bet_amount / 2
                player.stats["doubles"] += 1
                break
            elif action == "split":
                if hand.can_split() and len(player.hands) < 4:
                    self._split_hand(player, hand_idx)
                    player.stats["splits"] += 1
                else:
                    # Fallback to hit if split not possible
                    hand.add_card(self.deck.deal_card())
            else:
                # Invalid action, default to hit
                hand.add_card(self.deck.deal_card())
    
    def _split_hand(self, player: Player, hand_idx: int) -> None:
        """Split a hand into two hands."""
        original_hand = player.hands[hand_idx]
        
        # Create new hand with second card
        new_hand = Hand(original_hand.bet_amount)
        new_hand.add_card(original_hand.cards.pop())
        new_hand.is_split = True
        
        # Mark original hand as split
        original_hand.is_split = True
        
        # Add cards to both hands
        original_hand.add_card(self.deck.deal_card())
        new_hand.add_card(self.deck.deal_card())
        
        # Update bankroll for additional bet
        player.bankroll -= new_hand.bet_amount
        player.stats["total_bet"] += new_hand.bet_amount
        
        # Add new hand to player
        player.hands.append(new_hand)
    
    def _resolve_hands(self, players: List[Player]) -> None:
        """Resolve all hands against dealer and update statistics."""
        dealer_total, _ = self.dealer.hand.value()
        dealer_busted = self.dealer.hand.is_busted
        dealer_blackjack = self.dealer.hand.is_blackjack
        
        for player in players:
            total_winnings = 0.0
            
            for hand in player.hands:
                player.stats["hands_played"] += 1
                hand_total, _ = hand.value()
                
                # Determine outcome
                if hand.is_busted:
                    # Player busted - lose
                    outcome = "lose"
                    payout = 0.0
                elif hand.is_blackjack and not dealer_blackjack:
                    # Player blackjack - win 3:2
                    outcome = "blackjack"
                    payout = hand.bet_amount * (1 + self.game_config.blackjack_payout)
                    player.stats["blackjacks"] += 1
                elif dealer_blackjack and not hand.is_blackjack:
                    # Dealer blackjack - lose
                    outcome = "lose"
                    payout = 0.0
                elif dealer_busted:
                    # Dealer busted - win even money
                    outcome = "win"
                    payout = hand.bet_amount * 2
                elif hand_total > dealer_total:
                    # Player higher - win even money
                    outcome = "win"
                    payout = hand.bet_amount * 2
                elif hand_total == dealer_total:
                    # Tie - push
                    outcome = "push"
                    payout = hand.bet_amount
                else:
                    # Player lower - lose
                    outcome = "lose"
                    payout = 0.0
                
                # Update statistics
                if outcome == "win" or outcome == "blackjack":
                    player.stats["hands_won"] += 1
                elif outcome == "lose":
                    player.stats["hands_lost"] += 1
                else:  # push
                    player.stats["hands_pushed"] += 1
                
                # Update bankroll
                total_winnings += payout
                player.stats["total_winnings"] += payout
            
            # Update player bankroll
            player.update_bankroll(total_winnings)
    
    def _generate_results(self) -> SimulationResults:
        """Generate simulation results."""
        elapsed_time = (self.end_time or time.time()) - self.start_time
        hands_per_second = self.hands_played / elapsed_time if elapsed_time > 0 else 0
        
        players_stats = [player.get_statistics() for player in self.players]
        
        return SimulationResults(
            players_stats=players_stats,
            game_config=self.game_config,
            total_hands=self.hands_played,
            elapsed_time=elapsed_time,
            hands_per_second=hands_per_second
        )
    
    def _print_summary(self, results: SimulationResults) -> None:
        """Print simulation summary."""
        print(f"\n🎯 SIMULATION COMPLETE")
        print(f"{'='*50}")
        print(f"Total Hands: {results.total_hands:,}")
        print(f"Elapsed Time: {results.elapsed_time:.1f}s")
        print(f"Speed: {results.hands_per_second:.0f} hands/sec")
        print()
        
        for i, stats in enumerate(results.players_stats):
            config = self.players_config[i]
            print(f"👤 {config.name} ({config.play_strategy}/{config.bet_strategy})")
            print(f"   Bankroll: ${stats['initial_bankroll']:,.0f} → ${stats['current_bankroll']:,.0f}")
            print(f"   Change: ${stats['bankroll_change']:+,.0f} ({stats['roi']:+.2%})")
            print(f"   Win Rate: {stats['win_rate']:.1%}")
            print(f"   Avg Bet: ${stats['avg_bet']:.2f}")
            print(f"   Hands: {stats['hands_played']:,}")
            
            if 'ai_betting_stats' in stats:
                ai_stats = stats['ai_betting_stats']
                print(f"   AI Decisions: {ai_stats['ai_decision_ratio']:.1%}")
                print(f"   Recent Avg Bet: ${ai_stats['recent_avg_bet']:.2f}")
            
            print()


def run_ai_betting_demo(
    bet_model_path: str,
    play_model_path: Optional[str] = None,
    num_hands: int = 10000,
    verbose: bool = True
) -> SimulationResults:
    """
    Run demonstration of AI betting strategy.
    
    Args:
        bet_model_path: Path to trained betting model
        play_model_path: Path to trained playing model (optional)
        num_hands: Number of hands to simulate
        verbose: Whether to show progress
        
    Returns:
        Simulation results
    """
    # Game configuration
    game_config = GameConfig(
        num_hands=num_hands,
        num_decks=6,
        penetration=0.75,
        dealer_rule="S17",
        seed=42
    )
    
    # Player configurations
    players_config = [
        # AI betting + basic strategy
        PlayerConfig(
            name="AI_Betting_Basic",
            play_strategy="basic",
            bet_strategy="ai_bet",
            bet_model_path=bet_model_path,
            bankroll=10000.0,
            min_bet=10.0,
            max_bet=500.0
        ),
        
        # Flat betting + basic strategy (comparison)
        PlayerConfig(
            name="Flat_Basic",
            play_strategy="basic",
            bet_strategy="flat",
            flat_bet_amount=25.0,
            bankroll=10000.0,
            min_bet=10.0,
            max_bet=500.0
        ),
        
        # True count betting + basic strategy (comparison)
        PlayerConfig(
            name="TC_Basic",
            play_strategy="basic",
            bet_strategy="tc_based",
            tc_bet_multiplier=2.0,
            bankroll=10000.0,
            min_bet=10.0,
            max_bet=500.0
        )
    ]
    
    # Add AI playing strategy if model provided
    if play_model_path:
        players_config.append(
            PlayerConfig(
                name="AI_Both",
                play_strategy="ai_play",
                bet_strategy="ai_bet",
                play_model_path=play_model_path,
                bet_model_path=bet_model_path,
                bankroll=10000.0,
                min_bet=10.0,
                max_bet=500.0
            )
        )
    
    # Run simulation
    simulator = BlackjackSimulator(game_config, players_config)
    return simulator.run_simulation(verbose=verbose)


def save_results(results: SimulationResults, output_path: str) -> None:
    """Save simulation results to JSON file."""
    output_data = {
        "simulation_info": {
            "total_hands": results.total_hands,
            "elapsed_time": results.elapsed_time,
            "hands_per_second": results.hands_per_second,
            "game_config": {
                "num_decks": results.game_config.num_decks,
                "penetration": results.game_config.penetration,
                "dealer_rule": results.game_config.dealer_rule,
                "blackjack_payout": results.game_config.blackjack_payout
            }
        },
        "players": results.players_stats
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"📄 Results saved to: {output_path}")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python blackjack_simulator.py <bet_model_path> [play_model_path] [num_hands]")
        sys.exit(1)
    
    bet_model_path = sys.argv[1]
    play_model_path = sys.argv[2] if len(sys.argv) > 2 else None
    num_hands = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
    
    try:
        results = run_ai_betting_demo(
            bet_model_path=bet_model_path,
            play_model_path=play_model_path,
            num_hands=num_hands,
            verbose=True
        )
        
        # Save results
        output_path = f"runs/simulation_results_{int(time.time())}.json"
        save_results(results, output_path)
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        sys.exit(1) 
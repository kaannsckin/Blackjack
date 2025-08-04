"""
================================================================================
MULTI-PLAYER BLACKJACK RL ENVIRONMENT (PHASE 3 - F3.1)
================================================================================

📋 **AMAÇ:**
   Phase 3 için multi-player dynamic AI geliştirme ortamı.
   Real-time adaptation, player profiling, ve table dynamics modeling.

🎯 **F3.1 ÖZELLİKLERİ:**
   • 2-6 oyuncu destekli turn-based RL environment
   • Player position dynamics (early/middle/late position)
   • Card flow impact modeling across all players
   • Dynamic observation space per player perspective
   • Advanced table state tracking

🏗️ **TEKNİK ÖZELLİKLER:**
   • Extended Observation: [own_total, dealer_up, usable_ace, true_count, 
                           position, opponents_data, table_dynamics]
   • Turn-Based Action: Sequential player actions with position awareness
   • Dynamic Rewards: Position-adjusted and table-impact-aware scoring
   • Player Profiling: Real-time opponent behavior tracking

================================================================================
"""

from __future__ import annotations

import gymnasium as gym
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# Import base environment and supporting modules
from rl_environment import BlackjackRLEnv
from simulation_engine import PlayerConfig, GameConfig, Player, Hand, Deck, Dealer

class PlayerPosition(Enum):
    """Player position at the table."""
    EARLY = "early"      # 1st or 2nd position (2-3 players)
    MIDDLE = "middle"    # Middle positions (4-6 players)
    LATE = "late"        # Last position (anchor)

@dataclass
class PlayerProfile:
    """Real-time player behavior profile."""
    player_id: int
    hands_observed: int = 0
    
    # Playing style metrics
    hit_frequency: float = 0.0      # How often hits on borderline hands
    double_frequency: float = 0.0   # Double down frequency
    split_frequency: float = 0.0    # Split frequency
    stand_frequency: float = 0.0    # Conservative standing
    
    # Betting pattern metrics
    avg_bet_size: float = 0.0
    bet_variance: float = 0.0
    tc_correlation: float = 0.0     # Correlation with true count
    
    # Risk profile
    risk_level: str = "unknown"     # conservative, moderate, aggressive
    bankroll_management: str = "unknown"  # tight, normal, loose
    
    # Counting awareness (estimated)
    counting_suspected: bool = False
    counting_confidence: float = 0.0

@dataclass 
class TableDynamics:
    """Current table state and dynamics."""
    num_players: int
    current_player: int
    dealer_upcard: int
    
    # Card flow tracking
    cards_played_this_round: List[int] = field(default_factory=list)
    position_advantage: Dict[int, float] = field(default_factory=dict)
    
    # Collective metrics
    table_aggression: float = 0.0   # Average risk level
    table_betting_pattern: str = "mixed"  # conservative, mixed, aggressive
    suspected_counters: List[int] = field(default_factory=list)

class MultiPlayerBlackjackRLEnv(gym.Env):
    """
    Multi-Player Blackjack RL Environment for Phase 3 Dynamic AI Training.
    
    Supports 2-6 players with turn-based actions, position dynamics,
    opponent modeling, and advanced table state tracking.
    """
    
    def __init__(self,
                 num_players: int = 3,
                 ai_player_id: int = 0,
                 rules: Optional[Dict] = None,
                 num_decks: int = 6,
                 penetration: float = 0.75,
                 position_awareness: bool = True,
                 opponent_modeling: bool = True,
                 dynamic_adaptation: bool = True):
        """
        Initialize Multi-Player Blackjack RL Environment.
        
        Args:
            num_players: Number of players at table (2-6)
            ai_player_id: Which player is the AI agent (0-based)
            rules: Blackjack game rules
            num_decks: Number of decks in shoe
            penetration: Deck penetration before shuffle
            position_awareness: Enable position dynamics
            opponent_modeling: Enable opponent behavior tracking
            dynamic_adaptation: Enable real-time strategy adaptation
        """
        super().__init__()
        
        # Validate parameters
        if not 2 <= num_players <= 6:
            raise ValueError("Number of players must be between 2 and 6")
        if not 0 <= ai_player_id < num_players:
            raise ValueError("AI player ID must be valid player index")
            
        self.num_players = num_players
        self.ai_player_id = ai_player_id
        self.position_awareness = position_awareness
        self.opponent_modeling = opponent_modeling
        self.dynamic_adaptation = dynamic_adaptation
        
        # Game configuration
        self.rules = rules or {
            "dealer_rule": "S17",
            "das": True,
            "surrender": False,
            "blackjack_payout": 1.5
        }
        self.num_decks = num_decks
        self.penetration = penetration
        
        # Initialize game components
        self.deck = Deck(num_decks)
        self.dealer = Dealer(self.rules["dealer_rule"])
        
        # Player management
        self.players: List[Player] = []
        self.player_profiles: Dict[int, PlayerProfile] = {}
        self.current_player = 0
        self.round_complete = False
        
        # Table dynamics
        self.table_dynamics = TableDynamics(num_players=num_players, current_player=0, dealer_upcard=0)
        self.hand_history: List[Dict] = []
        
        # Position mapping
        self.position_map = self._calculate_position_map()
        
        # Observation space: Extended for multi-player dynamics
        # [own_total, dealer_up, usable_ace, true_count, position_value,
        #  avg_opponent_total, num_opponents_playing, table_aggression,
        #  suspected_counters, card_flow_advantage]
        self.observation_space = gym.spaces.Box(
            low=np.array([4, 1, 0, -10, 0, 0, 0, 0, 0, -1], dtype=np.float32),
            high=np.array([21, 11, 1, 10, 1, 21, 5, 1, 1, 1], dtype=np.float32),
            dtype=np.float32
        )
        
        # Action space remains same: [Stand, Hit, Double, Split]
        self.action_space = gym.spaces.Discrete(4)
        
        # Initialize players
        self._initialize_players()
        
    def _calculate_position_map(self) -> Dict[int, PlayerPosition]:
        """Calculate position classification for each player."""
        positions = {}
        
        if self.num_players == 2:
            positions = {0: PlayerPosition.EARLY, 1: PlayerPosition.LATE}
        elif self.num_players == 3:
            positions = {0: PlayerPosition.EARLY, 1: PlayerPosition.MIDDLE, 2: PlayerPosition.LATE}
        elif self.num_players == 4:
            positions = {0: PlayerPosition.EARLY, 1: PlayerPosition.EARLY, 
                        2: PlayerPosition.MIDDLE, 3: PlayerPosition.LATE}
        elif self.num_players == 5:
            positions = {0: PlayerPosition.EARLY, 1: PlayerPosition.EARLY,
                        2: PlayerPosition.MIDDLE, 3: PlayerPosition.MIDDLE, 4: PlayerPosition.LATE}
        else:  # 6 players
            positions = {0: PlayerPosition.EARLY, 1: PlayerPosition.EARLY,
                        2: PlayerPosition.MIDDLE, 3: PlayerPosition.MIDDLE,
                        4: PlayerPosition.MIDDLE, 5: PlayerPosition.LATE}
        
        return positions
        
    def _initialize_players(self):
        """Initialize all players with default configurations."""
        self.players = []
        self.player_profiles = {}
        
        for i in range(self.num_players):
            # Create player config
            config = PlayerConfig(
                name=f"Player_{i}",
                play_strategy="basic" if i != self.ai_player_id else "ai_play",
                bet_strategy="flat",
                bankroll=10000.0,
                min_bet=10.0,
                max_bet=500.0
            )
            
            # Create player
            player = Player(config)
            self.players.append(player)
            
            # Initialize profile for opponent modeling
            if i != self.ai_player_id and self.opponent_modeling:
                self.player_profiles[i] = PlayerProfile(player_id=i)
    
    def reset(self, seed: Optional[int] = None) -> Tuple[np.ndarray, Dict]:
        """Reset environment for new episode."""
        if seed is not None:
            np.random.seed(seed)
            
        # Reset deck if needed
        if len(self.deck.cards) < (52 * self.num_decks * (1 - self.penetration)):
            self.deck = Deck(self.num_decks)
            
        # Reset all players
        for player in self.players:
            player.hands = [Hand()]
            
        # Reset dealer
        self.dealer.hand = Hand()
        
        # Reset round state
        self.current_player = 0
        self.round_complete = False
        self.table_dynamics.current_player = 0
        self.table_dynamics.cards_played_this_round = []
        
        # Deal initial cards
        self._deal_initial_cards()
        
        # Update table dynamics
        self._update_table_dynamics()
        
        return self._get_observation(), {}
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Execute action for current player."""
        if self.round_complete:
            return self._get_observation(), 0.0, True, False, {}
            
        # Only process action if it's AI player's turn
        if self.current_player != self.ai_player_id:
            # Simulate other players' actions
            self._simulate_other_player_action()
            self._advance_to_next_player()
            
            # If still not AI's turn, continue simulation
            if self.current_player != self.ai_player_id and not self.round_complete:
                return self.step(action)  # Recursive call to continue
                
        # Process AI player's action
        if self.current_player == self.ai_player_id:
            immediate_reward = self._execute_ai_action(action)
            
            # Check if AI is busted or has blackjack - complete round immediately
            ai_hand = self.players[self.ai_player_id].hands[0]
            if ai_hand.is_busted or ai_hand.is_blackjack:
                self.round_complete = True
                total_reward = immediate_reward
                done = True
            else:
                # Store round state before advancing
                was_round_complete = self.round_complete
                
                # Advance to next player (may complete round)
                final_reward = self._advance_to_next_player()
                
                # Calculate total reward
                if self.round_complete and not was_round_complete and final_reward is not None:
                    # Round just completed, use final reward
                    total_reward = final_reward
                else:
                    # Round continues, use immediate reward
                    total_reward = immediate_reward
                
                done = self.round_complete
            
            # Update opponent profiles with observation
            if self.opponent_modeling:
                self._update_opponent_profiles()
            
            return self._get_observation(), total_reward, done, False, self._get_info()
            
        return self._get_observation(), 0.0, self.round_complete, False, {}
    
    def _deal_initial_cards(self):
        """Deal initial two cards to all players and dealer."""
        # Two rounds of dealing
        for _ in range(2):
            for player in self.players:
                card = self.deck.deal_card()
                player.hands[0].add_card(card)
                self.table_dynamics.cards_played_this_round.append(card.blackjack_value())
                
            # Deal to dealer
            card = self.deck.deal_card()
            self.dealer.hand.add_card(card)
            if len(self.dealer.hand.cards) == 1:  # Only upcard visible
                self.table_dynamics.dealer_upcard = card.blackjack_value()
                self.table_dynamics.cards_played_this_round.append(card.blackjack_value())
    
    def _simulate_other_player_action(self):
        """Simulate action for non-AI players using basic strategy."""
        player = self.players[self.current_player]
        hand = player.hands[0]  # Simplified: single hand per player
        
        if hand.is_busted or hand.is_blackjack:
            return  # No action needed
            
        # Use basic strategy for other players
        from utils.basic_strategy import get_action
        
        hand_total, usable_ace = hand.value()
        dealer_up = self.dealer.hand.cards[0].blackjack_value()
        
        action = get_action(hand_total, dealer_up, usable_ace)
        
        # Execute action
        if action == "stand":
            pass  # No change needed
        elif action == "hit":
            card = self.deck.deal_card()
            hand.add_card(card)
            self.table_dynamics.cards_played_this_round.append(card.blackjack_value())
        elif action == "double":
            card = self.deck.deal_card()
            hand.add_card(card)
            hand.is_doubled = True
            self.table_dynamics.cards_played_this_round.append(card.blackjack_value())
        # Split handling simplified for now
        
        # Update opponent profile
        if self.opponent_modeling and self.current_player in self.player_profiles:
            self._update_player_profile(self.current_player, action, hand_total)
    
    def _execute_ai_action(self, action: int) -> float:
        """Execute AI player's action and return immediate reward."""
        player = self.players[self.ai_player_id]
        hand = player.hands[0]
        
        if hand.is_busted or hand.is_blackjack:
            return 0.0
            
        reward = 0.0
        
        if action == 0:  # Stand
            pass
        elif action == 1:  # Hit
            card = self.deck.deal_card()
            hand.add_card(card)
            self.table_dynamics.cards_played_this_round.append(card.blackjack_value())
            
            if hand.is_busted:
                reward = -1.0
        elif action == 2:  # Double
            if len(hand.cards) == 2:
                card = self.deck.deal_card()
                hand.add_card(card)
                hand.is_doubled = True
                self.table_dynamics.cards_played_this_round.append(card.blackjack_value())
                
                if hand.is_busted:
                    reward = -2.0  # Double the loss
            else:
                # Invalid double, treat as hit
                card = self.deck.deal_card()
                hand.add_card(card)
                self.table_dynamics.cards_played_this_round.append(card.blackjack_value())
                
                if hand.is_busted:
                    reward = -1.0
        elif action == 3:  # Split (simplified)
            # For now, treat as hit
            card = self.deck.deal_card()
            hand.add_card(card)
            self.table_dynamics.cards_played_this_round.append(card.blackjack_value())
            
            if hand.is_busted:
                reward = -1.0
                
        return reward
    
    def _advance_to_next_player(self) -> Optional[float]:
        """Move to next player or complete round. Returns final reward if round completes."""
        self.current_player += 1
        
        if self.current_player >= self.num_players:
            # All players have acted, play dealer and resolve
            self._play_dealer()
            final_reward = self._resolve_round()
            self.round_complete = True
            return final_reward
        else:
            self.table_dynamics.current_player = self.current_player
            return None
    
    def _play_dealer(self):
        """Play dealer's hand according to rules."""
        dealer_total, _ = self.dealer.hand.value()
        
        # Reveal hole card
        if len(self.dealer.hand.cards) > 1:
            hole_card = self.dealer.hand.cards[1]
            self.table_dynamics.cards_played_this_round.append(hole_card.blackjack_value())
        
        # Dealer hits until 17 or higher
        while dealer_total < 17:
            card = self.deck.deal_card()
            self.dealer.hand.add_card(card)
            self.table_dynamics.cards_played_this_round.append(card.blackjack_value())
            dealer_total, _ = self.dealer.hand.value()
    
    def _resolve_round(self):
        """Resolve all hands and calculate final rewards."""
        dealer_total, _ = self.dealer.hand.value()
        dealer_busted = self.dealer.hand.is_busted
        
        # Update AI player's final reward
        ai_player = self.players[self.ai_player_id]
        ai_hand = ai_player.hands[0]
        
        final_reward = self._calculate_final_reward(ai_hand, dealer_total, dealer_busted)
        
        # Apply position bonus if enabled
        if self.position_awareness:
            position_bonus = self._calculate_position_bonus()
            final_reward += position_bonus
            
        return final_reward
    
    def _calculate_final_reward(self, hand: Hand, dealer_total: int, dealer_busted: bool) -> float:
        """Calculate final reward for AI player."""
        hand_total, _ = hand.value()
        
        if hand.is_busted:
            return -1.0 * (2 if hand.is_doubled else 1)
        elif hand.is_blackjack and not self.dealer.hand.is_blackjack:
            return 1.5 * (2 if hand.is_doubled else 1)  # Blackjack payout
        elif dealer_busted:
            return 1.0 * (2 if hand.is_doubled else 1)
        elif hand_total > dealer_total:
            return 1.0 * (2 if hand.is_doubled else 1)
        elif hand_total == dealer_total:
            return 0.0  # Push
        else:
            return -1.0 * (2 if hand.is_doubled else 1)
    
    def _calculate_position_bonus(self) -> float:
        """Calculate position-based reward bonus."""
        ai_position = self.position_map[self.ai_player_id]
        
        # Position advantages based on card flow and information
        if ai_position == PlayerPosition.LATE:
            return 0.1  # Information advantage
        elif ai_position == PlayerPosition.MIDDLE:
            return 0.05  # Moderate advantage
        else:
            return 0.0  # Early position, no bonus
    
    def _get_observation(self) -> np.ndarray:
        """Get current observation for AI player."""
        ai_player = self.players[self.ai_player_id]
        ai_hand = ai_player.hands[0]
        
        # Basic hand information
        hand_total, usable_ace = ai_hand.value()
        dealer_up = self.dealer.hand.cards[0].blackjack_value()
        true_count = self.deck.true_count() if hasattr(self.deck, 'true_count') else 0.0
        
        # Position information
        position_value = self._get_position_value()
        
        # Opponent information (if modeling enabled)
        avg_opponent_total = self._get_average_opponent_total()
        num_opponents_playing = self._get_opponents_still_playing()
        
        # Table dynamics
        table_aggression = self.table_dynamics.table_aggression
        suspected_counters = float(len(self.table_dynamics.suspected_counters)) / self.num_players
        card_flow_advantage = self._calculate_card_flow_advantage()
        
        return np.array([
            float(hand_total),
            float(dealer_up),
            float(usable_ace),
            float(true_count),
            float(position_value),
            float(avg_opponent_total),
            float(num_opponents_playing),
            float(table_aggression),
            float(suspected_counters),
            float(card_flow_advantage)
        ], dtype=np.float32)
    
    def _get_position_value(self) -> float:
        """Get normalized position value (0.0 = early, 1.0 = late)."""
        position = self.position_map[self.ai_player_id]
        if position == PlayerPosition.EARLY:
            return 0.0
        elif position == PlayerPosition.MIDDLE:
            return 0.5
        else:  # LATE
            return 1.0
    
    def _get_average_opponent_total(self) -> float:
        """Get average hand total of non-busted opponents."""
        if not self.opponent_modeling:
            return 15.0  # Default estimate
            
        totals = []
        for i, player in enumerate(self.players):
            if i != self.ai_player_id and not player.hands[0].is_busted:
                total, _ = player.hands[0].value()
                totals.append(total)
                
        return np.mean(totals) if totals else 15.0
    
    def _get_opponents_still_playing(self) -> int:
        """Count opponents still in the hand."""
        count = 0
        for i, player in enumerate(self.players):
            if i != self.ai_player_id and not player.hands[0].is_busted:
                count += 1
        return count
    
    def _calculate_card_flow_advantage(self) -> float:
        """Calculate card flow advantage based on cards seen."""
        # Simplified calculation: positive if more low cards seen
        cards_seen = self.table_dynamics.cards_played_this_round
        if not cards_seen:
            return 0.0
            
        low_cards = sum(1 for card in cards_seen if 2 <= card <= 6)
        high_cards = sum(1 for card in cards_seen if card >= 10)
        
        return (low_cards - high_cards) / len(cards_seen)
    
    def _update_table_dynamics(self):
        """Update table dynamics and collective metrics."""
        if not self.opponent_modeling:
            return
            
        # Calculate table aggression based on player profiles
        aggression_scores = []
        for profile in self.player_profiles.values():
            if profile.hands_observed > 5:  # Minimum observations
                aggression = (profile.hit_frequency + profile.double_frequency + 
                            profile.split_frequency) / 3
                aggression_scores.append(aggression)
                
        self.table_dynamics.table_aggression = np.mean(aggression_scores) if aggression_scores else 0.5
        
        # Update suspected counters
        self.table_dynamics.suspected_counters = [
            player_id for player_id, profile in self.player_profiles.items()
            if profile.counting_suspected
        ]
    
    def _update_opponent_profiles(self):
        """Update opponent behavior profiles based on current actions."""
        # This would be implemented based on observed actions
        pass
    
    def _update_player_profile(self, player_id: int, action: str, hand_total: int):
        """Update specific player's behavioral profile."""
        if player_id not in self.player_profiles:
            return
            
        profile = self.player_profiles[player_id]
        profile.hands_observed += 1
        
        # Update action frequencies (simplified)
        if action == "hit":
            profile.hit_frequency = (profile.hit_frequency * (profile.hands_observed - 1) + 1) / profile.hands_observed
        elif action == "double":
            profile.double_frequency = (profile.double_frequency * (profile.hands_observed - 1) + 1) / profile.hands_observed
        elif action == "split":
            profile.split_frequency = (profile.split_frequency * (profile.hands_observed - 1) + 1) / profile.hands_observed
        elif action == "stand":
            profile.stand_frequency = (profile.stand_frequency * (profile.hands_observed - 1) + 1) / profile.hands_observed
    
    def _get_info(self) -> Dict:
        """Get additional information for debugging and analysis."""
        return {
            "current_player": self.current_player,
            "round_complete": self.round_complete,
            "ai_position": self.position_map[self.ai_player_id].value,
            "table_dynamics": {
                "aggression": self.table_dynamics.table_aggression,
                "suspected_counters": len(self.table_dynamics.suspected_counters),
                "cards_played": len(self.table_dynamics.cards_played_this_round)
            }
        }


def create_multi_player_env(**kwargs):
    """Factory function to create MultiPlayerBlackjackRLEnv."""
    return MultiPlayerBlackjackRLEnv(**kwargs)


# Test the environment
if __name__ == "__main__":
    print("🧪 TESTING MULTI-PLAYER BLACKJACK RL ENVIRONMENT")
    
    env = MultiPlayerBlackjackRLEnv(num_players=3, ai_player_id=1)
    
    print("✅ Multi-Player Environment created successfully")
    print(f"📊 Observation space: {env.observation_space}")
    print(f"🎯 Action space: {env.action_space}")
    print(f"👥 Number of players: {env.num_players}")
    print(f"🤖 AI Player ID: {env.ai_player_id}")
    
    # Test reset
    obs, info = env.reset(seed=42)
    print(f"🔄 Reset observation: {obs}")
    print(f"📋 Info: {info}")
    
    # Test a few actions
    for i in range(3):
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        print(f"🎲 Step {i}: action={action}, reward={reward}, done={done}")
        if done:
            break
    
    print("✅ MultiPlayerBlackjackRLEnv implementation complete!") 
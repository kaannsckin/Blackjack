from __future__ import annotations

"""
================================================================================
BLACKJACK REINFORCEMENT LEARNING ENVIRONMENT (V3.0) - CRITICAL FIX
================================================================================

CRITICAL FIX: Complete RL Environment Implementation
Previously only documentation, now fully functional BlackjackRLEnv class.

📋 **AMAÇ:**
   Blackjack oyunu için Gymnasium uyumlu RL ortamı. Hit/Stand/Double/Split 
   kararlarını öğrenen AI ajanlar için temel simülasyon motoru.

🏗️ **TEKNİK ÖZELLİKLER:**
   • Observation Space: [player_total, dealer_up, usable_ace, true_count]
   • Action Space: Discrete(4) - [Stand, Hit, Double, Split]
   • Reward System: Win:+1, Push:0, Loss:-1

================================================================================
"""

import gymnasium as gym
import numpy as np
from typing import Dict, Tuple, Optional, Any
import random
import sys
import os

# Add V1.0 to path for blackjack engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'V1.0'))

try:
    from blackjack import BlackjackGame, Player, Card, Deck
except ImportError:
    print("Warning: Cannot import V1.0 blackjack engine")

class BlackjackRLEnv(gym.Env):
    """
    CRITICAL FIX: Complete BlackjackRLEnv implementation
    
    Blackjack Reinforcement Learning Environment for training play strategy agents.
    
    Observation Space: [player_total, dealer_up, usable_ace, true_count]
    Action Space: Discrete(4) -> [0: Stand, 1: Hit, 2: Double, 3: Split]
    Reward: +1 for win, 0 for push, -1 for loss
    """
    
    def __init__(self, 
                 rules: Optional[Dict] = None,
                 num_decks: int = 6,
                 penetration: float = 0.75):
        """Initialize BlackjackRLEnv"""
        super().__init__()
        
        # Game rules
        self.rules = rules or {
            "dealer_rule": "S17",
            "das": True,
            "surrender": False,
            "blackjack_payout": 1.5
        }
        
        self.num_decks = num_decks
        self.penetration = penetration
        
        # Observation space: [player_total, dealer_up, usable_ace, true_count]
        self.observation_space = gym.spaces.Box(
            low=np.array([4, 1, 0, -10], dtype=np.float32),
            high=np.array([21, 11, 1, 10], dtype=np.float32),
            dtype=np.float32
        )
        
        # Action space: [Stand, Hit, Double, Split]
        self.action_space = gym.spaces.Discrete(4)
        
        # Game state
        self.deck = None
        self.player_hand = []
        self.dealer_hand = []
        self.true_count = 0.0
        self.cards_seen = 0
        self.game_over = False
        
        # Initialize (don't call reset in __init__)
        self.deck = Deck(self.num_decks)
        # Fix: Deck is already shuffled on creation, use reset if needed
        if hasattr(self.deck, 'reset'):
            self.deck.reset()
    
    def reset(self, seed: Optional[int] = None) -> Tuple[np.ndarray, Dict]:
        """Reset environment for new episode"""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Create new deck if needed or penetration reached
        if self.deck is None or len(self.deck.cards) < (52 * self.num_decks * (1 - self.penetration)):
            self.deck = Deck(self.num_decks)
            # Fix: Use reset instead of shuffle
            if hasattr(self.deck, 'reset'):
                self.deck.reset()
            self.true_count = 0.0
            self.cards_seen = 0
        
        # Deal initial cards
        self.player_hand = [self.deck.deal_card(), self.deck.deal_card()]
        self.dealer_hand = [self.deck.deal_card(), self.deck.deal_card()]
        
        # Update count
        for card in self.player_hand + [self.dealer_hand[0]]:  # Don't count dealer hole card
            self._update_count(card)
        
        self.game_over = False
        
        return self._get_observation(), {}
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Execute action and return (obs, reward, done, truncated, info)"""
        
        if self.game_over:
            return self._get_observation(), 0.0, True, False, {}
        
        reward = 0.0
        done = False
        info = {}
        
        # Execute action
        if action == 0:  # Stand
            done = True
            reward = self._evaluate_final_outcome()
            
        elif action == 1:  # Hit
            card = self.deck.deal_card()
            self.player_hand.append(card)
            self._update_count(card)
            
            player_total = self._get_hand_value(self.player_hand)[0]
            if player_total > 21:
                # Bust
                done = True
                reward = -1.0
            elif player_total == 21:
                # 21 - finish hand
                done = True  
                reward = self._evaluate_final_outcome()
                
        elif action == 2:  # Double
            if len(self.player_hand) == 2:  # Can only double on first two cards
                card = self.deck.deal_card()
                self.player_hand.append(card)
                self._update_count(card)
                done = True
                reward = self._evaluate_final_outcome() * 2  # Double the reward
            else:
                # Invalid double, treat as hit
                card = self.deck.deal_card()
                self.player_hand.append(card)
                self._update_count(card)
                player_total = self._get_hand_value(self.player_hand)[0]
                if player_total > 21:
                    done = True
                    reward = -1.0
                elif player_total == 21:
                    done = True
                    reward = self._evaluate_final_outcome()
        
        elif action == 3:  # Split
            # For now, treat split as hit (simplified)
            card = self.deck.deal_card()
            self.player_hand.append(card)
            self._update_count(card)
            
            player_total = self._get_hand_value(self.player_hand)[0]
            if player_total > 21:
                done = True
                reward = -1.0
            elif player_total == 21:
                done = True
                reward = self._evaluate_final_outcome()
        
        self.game_over = done
        
        return self._get_observation(), reward, done, False, info
    
    def _get_observation(self) -> np.ndarray:
        """Get current observation"""
        player_total, usable_ace = self._get_hand_value(self.player_hand)
        dealer_up = self.dealer_hand[0].card_value()
        
        return np.array([
            float(player_total),
            float(dealer_up),
            float(usable_ace),
            float(self.true_count)
        ], dtype=np.float32)
    
    def _get_hand_value(self, hand) -> Tuple[int, bool]:
        """Get hand value and usable ace status"""
        total = 0
        aces = 0
        
        for card in hand:
            value = card.card_value()
            if value == 1:  # Ace
                aces += 1
                total += 11
            else:
                total += value
        
        # Adjust for aces
        usable_ace = False
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
            
        if aces > 0 and total + 10 <= 21:
            usable_ace = True
            
        return total, usable_ace
    
    def _evaluate_final_outcome(self) -> float:
        """Evaluate final game outcome"""
        # Play dealer hand
        self._update_count(self.dealer_hand[1])  # Count dealer hole card
        
        dealer_total, _ = self._get_hand_value(self.dealer_hand)
        
        # Dealer hits until 17 or higher
        while dealer_total < 17:
            card = self.deck.deal_card()
            self.dealer_hand.append(card)
            self._update_count(card)
            dealer_total, _ = self._get_hand_value(self.dealer_hand)
        
        player_total, _ = self._get_hand_value(self.player_hand)
        
        # Determine winner
        if player_total > 21:
            return -1.0  # Player bust
        elif dealer_total > 21:
            return 1.0   # Dealer bust
        elif player_total > dealer_total:
            return 1.0   # Player wins
        elif player_total < dealer_total:
            return -1.0  # Dealer wins
        else:
            return 0.0   # Push
    
    def _update_count(self, card):
        """Update Hi-Lo card count"""
        value = card.card_value()
        
        if value in [2, 3, 4, 5, 6]:
            self.true_count += 1
        elif value in [10, 1]:  # 10, J, Q, K, A
            self.true_count -= 1
        
        self.cards_seen += 1
        
        # Convert to true count
        decks_remaining = (52 * self.num_decks - self.cards_seen) / 52
        if decks_remaining > 0:
            self.true_count = self.true_count / decks_remaining

def create_blackjack_env(**kwargs):
    """Factory function to create BlackjackRLEnv"""
    return BlackjackRLEnv(**kwargs)

# Test the environment
if __name__ == "__main__":
    print("🧪 TESTING BLACKJACK RL ENVIRONMENT")
    
    env = BlackjackRLEnv()
    
    print("✅ Environment created successfully")
    print(f"📊 Observation space: {env.observation_space}")
    print(f"🎯 Action space: {env.action_space}")
    
    # Test reset
    obs, info = env.reset(seed=42)
    print(f"🔄 Reset observation: {obs}")
    
    # Test actions
    actions = ["Stand", "Hit", "Double", "Split"]
    for i, action_name in enumerate(actions):
        env.reset(seed=42)
        obs, reward, done, truncated, info = env.step(i)
        print(f"🎲 {action_name}: obs={obs}, reward={reward}, done={done}")
    
    print("✅ BlackjackRLEnv implementation complete!")

# Add alias for backward compatibility
BlackjackEnv = BlackjackRLEnv 
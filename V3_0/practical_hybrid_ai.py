"""
PRACTICAL HYBRID AI

The smartest approach: Take proven simple AI + add ONLY features that actually work.
No over-engineering, no academic complexity - pure practical performance focus.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
import time
import json


class PracticalCardCounter:
    """Simplified but effective card counting."""
    
    def __init__(self):
        self.running_count = 0
        self.cards_seen = 0
        self.true_count = 0
        
    def update_count(self, cards: List[str]):
        """Update Hi-Lo count with dealt cards."""
        
        hi_lo_values = {
            '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
            '7': 0, '8': 0, '9': 0,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        }
        
        for card in cards:
            self.running_count += hi_lo_values.get(card, 0)
            self.cards_seen += 1
        
        # Estimate true count
        decks_remaining = max(1, (312 - self.cards_seen) / 52)  # 6 deck shoe
        self.true_count = self.running_count / decks_remaining
        
    def get_bet_multiplier(self) -> float:
        """Get bet multiplier based on true count."""
        
        if self.true_count <= 0:
            return 1.0  # Minimum bet
        elif self.true_count <= 1:
            return 1.5  # Slight increase
        elif self.true_count <= 2:
            return 2.0  # Moderate increase
        elif self.true_count <= 3:
            return 3.0  # Strong increase
        else:
            return 4.0  # Maximum spread


class PracticalBankrollManager:
    """Simple but effective bankroll management."""
    
    def __init__(self, initial_bankroll: float):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.session_high = initial_bankroll
        self.max_bet_percentage = 0.03  # Max 3% of bankroll
        
    def update_bankroll(self, change: float):
        """Update bankroll and track high water mark."""
        self.current_bankroll += change
        if self.current_bankroll > self.session_high:
            self.session_high = self.current_bankroll
    
    def get_max_bet(self) -> float:
        """Get maximum safe bet size."""
        return self.current_bankroll * self.max_bet_percentage
    
    def should_reduce_bets(self) -> bool:
        """Check if we should reduce bet sizes due to losses."""
        # If down more than 20% from high, be more conservative
        drawdown = (self.session_high - self.current_bankroll) / self.session_high
        return drawdown > 0.20


class PracticalHybridAI:
    """
    Practical Hybrid AI: Proven performance + selective enhancements.
    
    Philosophy: Start with what works, add only proven improvements.
    """
    
    def __init__(self, initial_bankroll: float = 10000):
        self.initial_bankroll = initial_bankroll
        
        # Core components
        self.card_counter = PracticalCardCounter()
        self.bankroll_manager = PracticalBankrollManager(initial_bankroll)
        
        # Performance tracking
        self.hands_played = 0
        self.recent_results = deque(maxlen=20)
        self.session_data = []
        
        # Simple state tracking
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
        print(f"🎯 PRACTICAL HYBRID AI INITIALIZED")
        print(f"   💰 Bankroll: ${initial_bankroll:,.2f}")
        print(f"   🧠 Features: Card Counting + Bankroll Management + Basic Strategy")
        
    def decide_play_action(self, player_total: int, dealer_up: int, 
                          usable_ace: bool = False,
                          can_double: bool = True,
                          can_split: bool = False) -> int:
        """
        Enhanced basic strategy with true count deviations.
        Proven to work in practice.
        """
        
        true_count = self.card_counter.true_count
        
        # Basic strategy matrix (proven)
        if usable_ace:
            # Soft totals
            if player_total >= 19:
                return 0  # Stand
            elif player_total == 18:
                if dealer_up <= 6 and can_double:
                    return 2  # Double
                elif dealer_up <= 8:
                    return 0  # Stand
                else:
                    return 1  # Hit
            else:
                if player_total <= 17 and dealer_up <= 6 and can_double:
                    return 2  # Double
                else:
                    return 1  # Hit
        else:
            # Hard totals with count deviations
            if player_total >= 17:
                return 0  # Stand
                
            elif player_total == 16:
                # Key deviation: 16 vs 10
                if dealer_up == 10 and true_count >= 0:
                    return 0  # Stand with positive count
                elif dealer_up >= 7:
                    return 1  # Hit
                else:
                    return 0  # Stand
                    
            elif player_total == 15:
                # Deviation: 15 vs 10
                if dealer_up == 10 and true_count >= 4:
                    return 0  # Stand with very high count
                elif dealer_up >= 7:
                    return 1  # Hit
                else:
                    return 0  # Stand
                    
            elif player_total == 12:
                # Deviations: 12 vs 2,3
                if dealer_up in [2, 3]:
                    if true_count >= 3:
                        return 0  # Stand with high count
                    else:
                        return 1  # Hit
                elif dealer_up in [4, 5, 6]:
                    return 0  # Stand
                else:
                    return 1  # Hit
                    
            elif player_total == 11:
                if can_double:
                    return 2  # Always double 11
                else:
                    return 1  # Hit
                    
            elif player_total == 10:
                if dealer_up <= 9 and can_double:
                    return 2  # Double
                else:
                    return 1  # Hit
                    
            elif player_total == 9:
                if dealer_up in [3, 4, 5, 6] and can_double:
                    return 2  # Double
                else:
                    return 1  # Hit
                    
            else:
                return 1  # Hit
    
    def decide_bet_size(self, min_bet: float, max_bet: float,
                       cards_seen: List[str] = None) -> float:
        """
        Practical bet sizing: Card counting + bankroll management + progression.
        """
        
        # Update card count if new cards seen
        if cards_seen:
            self.card_counter.update_count(cards_seen)
        
        # Base bet from card counting
        count_multiplier = self.card_counter.get_bet_multiplier()
        base_bet = min_bet * count_multiplier
        
        # Bankroll constraints
        max_safe_bet = self.bankroll_manager.get_max_bet()
        base_bet = min(base_bet, max_safe_bet, max_bet)
        
        # Conservative adjustment if in drawdown
        if self.bankroll_manager.should_reduce_bets():
            base_bet *= 0.7  # Reduce bets by 30% when in significant drawdown
        
        # Simple progression on wins/losses
        if len(self.recent_results) >= 3:
            recent_results = list(self.recent_results)[-3:]
            
            # If winning consistently, slightly increase
            if all(r > 0 for r in recent_results):
                base_bet *= 1.2
                
            # If losing consistently, be more conservative  
            elif all(r <= 0 for r in recent_results):
                base_bet *= 0.8
        
        # Final constraints
        final_bet = max(min_bet, min(base_bet, max_bet))
        
        return round(final_bet, 2)
    
    def update_result(self, bet_size: float, outcome: float, 
                     cards_seen: List[str] = None):
        """Update AI with hand result."""
        
        self.hands_played += 1
        self.recent_results.append(outcome)
        
        # Update bankroll
        self.bankroll_manager.update_bankroll(outcome)
        
        # Update card count
        if cards_seen:
            self.card_counter.update_count(cards_seen)
        
        # Track streaks
        if outcome > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Session data
        self.session_data.append({
            'hand': self.hands_played,
            'bet_size': bet_size,
            'outcome': outcome,
            'bankroll': self.bankroll_manager.current_bankroll,
            'true_count': self.card_counter.true_count,
            'count_multiplier': self.card_counter.get_bet_multiplier()
        })
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        
        if self.hands_played == 0:
            return {}
        
        # Calculate metrics
        total_roi = ((self.bankroll_manager.current_bankroll - self.initial_bankroll) / 
                    self.initial_bankroll)
        
        win_rate = sum(1 for r in self.recent_results if r > 0) / len(self.recent_results) if self.recent_results else 0
        
        # TC-Bet correlation
        if len(self.session_data) > 10:
            df = pd.DataFrame(self.session_data)
            tc_bet_corr = np.corrcoef(df['true_count'], df['bet_size'])[0, 1]
            bet_spread = df['bet_size'].max() / df['bet_size'].min() if df['bet_size'].min() > 0 else 1
        else:
            tc_bet_corr = 0
            bet_spread = 1
        
        # Sharpe ratio
        if len(self.recent_results) > 5:
            returns = list(self.recent_results)
            sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe = 0
        
        return {
            'hands_played': self.hands_played,
            'current_bankroll': self.bankroll_manager.current_bankroll,
            'total_roi': total_roi,
            'win_rate': win_rate,
            'tc_bet_correlation': tc_bet_corr,
            'bet_spread': bet_spread,
            'sharpe_ratio': sharpe,
            'true_count': self.card_counter.true_count,
            'consecutive_wins': self.consecutive_wins,
            'consecutive_losses': self.consecutive_losses
        }
    
    def get_grade(self) -> str:
        """Calculate performance grade."""
        
        metrics = self.get_performance_metrics()
        
        if not metrics:
            return "N/A"
        
        score = 0
        
        # TC correlation (25 points)
        if metrics['tc_bet_correlation'] > 0.7:
            score += 25
        elif metrics['tc_bet_correlation'] > 0.4:
            score += 15
        elif metrics['tc_bet_correlation'] > 0.1:
            score += 5
        
        # Bet spread (25 points)
        if metrics['bet_spread'] > 4:
            score += 25
        elif metrics['bet_spread'] > 2:
            score += 15
        elif metrics['bet_spread'] > 1.5:
            score += 5
        
        # ROI (25 points)
        if metrics['total_roi'] > 0.05:
            score += 25
        elif metrics['total_roi'] > 0:
            score += 15
        elif metrics['total_roi'] > -0.02:
            score += 5
        
        # Win rate (25 points)
        if metrics['win_rate'] > 0.47:
            score += 25
        elif metrics['win_rate'] > 0.43:
            score += 15
        elif metrics['win_rate'] > 0.40:
            score += 5
        
        # Grade assignment
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"
    
    def save_session(self, filename: str = None) -> str:
        """Save session results."""
        
        if filename is None:
            timestamp = int(time.time())
            filename = f"runs/practical_hybrid_session_{timestamp}.json"
        
        metrics = self.get_performance_metrics()
        
        session_summary = {
            'session_data': self.session_data,
            'final_metrics': metrics,
            'final_grade': self.get_grade(),
            'configuration': {
                'initial_bankroll': self.initial_bankroll,
                'hands_played': self.hands_played,
                'approach': 'Practical Hybrid AI'
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(session_summary, f, indent=2, default=str)
        
        print(f"💾 Session saved to: {filename}")
        return filename


def create_practical_hybrid_ai(initial_bankroll: float = 10000) -> PracticalHybridAI:
    """Create a practical hybrid AI system."""
    return PracticalHybridAI(initial_bankroll) 
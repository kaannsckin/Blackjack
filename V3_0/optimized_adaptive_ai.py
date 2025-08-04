"""
OPTIMIZED ADAPTIVE SIMPLE AI - Tuned Crisis Sensitivity

Based on test results: Crisis management works but too sensitive.
Optimized thresholds for better performance while maintaining protection.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
import time
import json
from enum import Enum


class CrisisLevel(Enum):
    """Different crisis levels for adaptive response."""
    NORMAL = "normal"           
    MINOR_STRESS = "minor"      
    MODERATE_CRISIS = "moderate" 
    SEVERE_CRISIS = "severe"    


class OptimizedRiskManager:
    """Optimized risk management with tuned sensitivity."""
    
    def __init__(self, initial_bankroll: float):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.peak_bankroll = initial_bankroll
        
        # Crisis tracking
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        self.current_drawdown = 0.0
        self.max_historical_drawdown = 0.0
        
        # Long-term statistics
        self.session_hands = 0
        self.total_wagered = 0.0
        self.total_won = 0.0
        self.long_term_roi = 0.0
        
        # OPTIMIZED parameters (less sensitive)
        self.base_risk_tolerance = 0.03  # Increased from 0.02
        self.crisis_multipliers = {
            CrisisLevel.NORMAL: 1.0,
            CrisisLevel.MINOR_STRESS: 0.9,    # Less aggressive reduction
            CrisisLevel.MODERATE_CRISIS: 0.7,  # Moderate reduction
            CrisisLevel.SEVERE_CRISIS: 0.4     # Significant but not extreme
        }
        
    def update_performance(self, bet_size: float, outcome: float):
        """Update performance tracking and crisis detection."""
        
        self.session_hands += 1
        self.current_bankroll += outcome
        self.total_wagered += bet_size
        
        if outcome > 0:
            self.total_won += outcome
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        
        # Update peak and drawdown
        if self.current_bankroll > self.peak_bankroll:
            self.peak_bankroll = self.current_bankroll
            self.current_drawdown = 0.0
        else:
            self.current_drawdown = (self.peak_bankroll - self.current_bankroll) / self.peak_bankroll
            self.max_historical_drawdown = max(self.max_historical_drawdown, self.current_drawdown)
        
        # Update long-term ROI
        if self.total_wagered > 0:
            self.long_term_roi = (self.total_won - self.total_wagered) / self.total_wagered
    
    def detect_crisis_level(self) -> CrisisLevel:
        """OPTIMIZED crisis detection - less sensitive thresholds."""
        
        # Factor 1: Consecutive losses (HIGHER thresholds)
        loss_factor = 0
        if self.consecutive_losses >= 20:      # Was 15
            loss_factor = 3  # Severe
        elif self.consecutive_losses >= 15:    # Was 10
            loss_factor = 2  # Moderate
        elif self.consecutive_losses >= 8:     # Was 5
            loss_factor = 1  # Minor
        
        # Factor 2: Current drawdown (HIGHER thresholds)
        drawdown_factor = 0
        if self.current_drawdown >= 0.35:      # Was 0.25 (35% vs 25%)
            drawdown_factor = 3  # Severe
        elif self.current_drawdown >= 0.20:    # Was 0.15 (20% vs 15%)
            drawdown_factor = 2  # Moderate
        elif self.current_drawdown >= 0.12:    # Was 0.08 (12% vs 8%)
            drawdown_factor = 1  # Minor
        
        # Factor 3: Bankroll vs initial (LOWER thresholds)
        bankroll_factor = 0
        bankroll_ratio = self.current_bankroll / self.initial_bankroll
        if bankroll_ratio <= 0.6:             # Was 0.7 (more tolerance)
            bankroll_factor = 3  # Severe
        elif bankroll_ratio <= 0.75:          # Was 0.85 (more tolerance)
            bankroll_factor = 2  # Moderate
        elif bankroll_ratio <= 0.90:          # Was 0.95 (more tolerance)
            bankroll_factor = 1  # Minor
        
        # Determine overall crisis level
        max_factor = max(loss_factor, drawdown_factor, bankroll_factor)
        
        if max_factor >= 3:
            return CrisisLevel.SEVERE_CRISIS
        elif max_factor >= 2:
            return CrisisLevel.MODERATE_CRISIS
        elif max_factor >= 1:
            return CrisisLevel.MINOR_STRESS
        else:
            return CrisisLevel.NORMAL
    
    def get_adaptive_risk_multiplier(self) -> float:
        """Get risk multiplier based on current crisis level."""
        
        crisis_level = self.detect_crisis_level()
        base_multiplier = self.crisis_multipliers[crisis_level]
        
        # OPTIMIZED: Less extreme adjustments
        if self.consecutive_losses >= 25:      # Was 20
            base_multiplier *= 0.7             # Was 0.5 (less extreme)
        
        # OPTIMIZED: More generous boost when winning
        if self.consecutive_wins >= 3 and self.current_drawdown < 0.05:  # Was 5 wins
            base_multiplier *= 1.15            # Was 1.1 (slightly more aggressive)
        
        return base_multiplier
    
    def get_max_bet_size(self, base_max: float) -> float:
        """Get maximum bet size considering adaptive risk."""
        
        # OPTIMIZED: Slightly higher base risk tolerance
        bankroll_max = self.current_bankroll * self.base_risk_tolerance
        
        # Apply crisis multiplier
        risk_multiplier = self.get_adaptive_risk_multiplier()
        adaptive_max = bankroll_max * risk_multiplier
        
        # Never exceed base maximum
        return min(adaptive_max, base_max)


class OptimizedAdaptiveAI:
    """
    Optimized Adaptive Simple AI: Better performance + crisis protection.
    
    Optimizations:
    - Higher crisis thresholds (less sensitive)
    - Better risk/return balance
    - Maintained proven Simple AI base
    """
    
    def __init__(self, initial_bankroll: float = 10000):
        self.initial_bankroll = initial_bankroll
        
        # Core components
        self.risk_manager = OptimizedRiskManager(initial_bankroll)
        
        # Simple tracking (proven from Simple AI)
        self.hands_played = 0
        self.recent_results = deque(maxlen=20)
        self.session_data = []
        
        print(f"🎯 OPTIMIZED ADAPTIVE AI INITIALIZED")
        print(f"   💰 Initial Bankroll: ${initial_bankroll:,.2f}")
        print(f"   🧠 Features: Proven Simple AI + Optimized Crisis Management")
        print(f"   ⚖️ Balance: Performance + Protection")
        
    def decide_play_action(self, player_total: int, dealer_up: int,
                          usable_ace: bool = False) -> int:
        """
        PROVEN Simple AI basic strategy - UNCHANGED.
        """
        
        # EXACT same logic as proven Simple AI
        if usable_ace:
            if player_total >= 19:
                return 0  # Stand
            elif player_total == 18:
                return 0 if dealer_up <= 8 else 1
            else:
                return 1  # Hit
        else:
            if player_total >= 17:
                return 0  # Stand
            elif player_total <= 11:
                return 1  # Hit
            elif player_total in [9, 10, 11] and dealer_up <= 6:
                return 2 if 2 in [0, 1, 2, 3] else 1  # Double if available
            elif player_total <= 16 and dealer_up >= 7:
                return 1  # Hit
            else:
                return 0  # Stand
    
    def decide_bet_size(self, min_bet: float, max_bet: float) -> float:
        """
        OPTIMIZED adaptive bet sizing.
        """
        
        # Start with proven Simple AI bet logic
        base_bet = min_bet
        
        # Simple AI's proven progression (KEEP THIS)
        if len(self.recent_results) >= 3:
            recent_results_list = list(self.recent_results)
            recent_wins = sum(1 for r in recent_results_list[-3:] if r > 0)
            if recent_wins >= 2:
                base_bet *= 1.25  # Slightly more aggressive than 1.2
        
        # OPTIMIZED: Less aggressive crisis reduction
        crisis_level = self.risk_manager.detect_crisis_level()
        
        if crisis_level == CrisisLevel.NORMAL:
            enhanced_bet = base_bet * 1.05     # Slight boost when normal
        elif crisis_level == CrisisLevel.MINOR_STRESS:
            enhanced_bet = base_bet * 0.95     # Minor reduction
        elif crisis_level == CrisisLevel.MODERATE_CRISIS:
            enhanced_bet = base_bet * 0.8      # Moderate reduction
        else:  # SEVERE_CRISIS
            enhanced_bet = base_bet * 0.6      # Significant but not extreme
        
        # Apply adaptive risk limits
        max_adaptive_bet = self.risk_manager.get_max_bet_size(max_bet)
        final_bet = max(min_bet, min(enhanced_bet, max_adaptive_bet))
        
        return round(final_bet, 2)
    
    def update_result(self, bet_size: float, outcome: float):
        """Update with hand result and perform adaptive analysis."""
        
        self.hands_played += 1
        self.recent_results.append(outcome)
        
        # Update risk manager
        self.risk_manager.update_performance(bet_size, outcome)
        
        # Session data
        crisis_level = self.risk_manager.detect_crisis_level()
        self.session_data.append({
            'hand': self.hands_played,
            'bet_size': bet_size,
            'outcome': outcome,
            'bankroll': self.risk_manager.current_bankroll,
            'crisis_level': crisis_level.value,
            'consecutive_losses': self.risk_manager.consecutive_losses,
            'drawdown': self.risk_manager.current_drawdown
        })
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        
        if self.hands_played == 0:
            return {}
        
        current_bankroll = self.risk_manager.current_bankroll
        total_roi = (current_bankroll - self.initial_bankroll) / self.initial_bankroll
        
        crisis_level = self.risk_manager.detect_crisis_level()
        
        wins = sum(1 for r in self.recent_results if r > 0)
        win_rate = wins / len(self.recent_results) if self.recent_results else 0
        
        risk_multiplier = self.risk_manager.get_adaptive_risk_multiplier()
        
        return {
            'hands_played': self.hands_played,
            'current_bankroll': current_bankroll,
            'total_roi': total_roi,
            'win_rate': win_rate,
            'current_crisis_level': crisis_level.value,
            'consecutive_losses': self.risk_manager.consecutive_losses,
            'consecutive_wins': self.risk_manager.consecutive_wins,
            'current_drawdown': self.risk_manager.current_drawdown,
            'max_drawdown': self.risk_manager.max_historical_drawdown,
            'risk_multiplier': risk_multiplier,
            'long_term_roi': self.risk_manager.long_term_roi
        }
    
    def get_status_report(self) -> str:
        """Get human-readable status report."""
        
        metrics = self.get_performance_metrics()
        if not metrics:
            return "No data yet"
        
        crisis_level = metrics['current_crisis_level']
        status_emoji = {
            'normal': '✅',
            'minor': '🟡', 
            'moderate': '🟠',
            'severe': '🔴'
        }
        
        report = f"""
🎯 OPTIMIZED ADAPTIVE AI STATUS
{'='*40}
📊 Performance:
   Hands: {metrics['hands_played']:,}
   Bankroll: ${metrics['current_bankroll']:,.2f}
   ROI: {metrics['total_roi']:+.2%}
   Win Rate: {metrics['win_rate']:.1%}

🚨 Crisis Status:
   Level: {status_emoji.get(crisis_level, '❓')} {crisis_level.upper()}
   Losses: {metrics['consecutive_losses']}
   Drawdown: {metrics['current_drawdown']:.1%}
   Risk Mult: {metrics['risk_multiplier']:.2f}x
"""
        return report
    
    def save_session(self, filename: str = None) -> str:
        """Save session results."""
        
        if filename is None:
            timestamp = int(time.time())
            filename = f"runs/optimized_adaptive_session_{timestamp}.json"
        
        metrics = self.get_performance_metrics()
        
        session_summary = {
            'session_data': self.session_data,
            'final_metrics': metrics,
            'configuration': {
                'initial_bankroll': self.initial_bankroll,
                'hands_played': self.hands_played,
                'approach': 'Optimized Adaptive AI',
                'philosophy': 'Proven base + optimized crisis management'
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(session_summary, f, indent=2, default=str)
        
        print(f"💾 Session saved to: {filename}")
        return filename


def create_optimized_adaptive_ai(initial_bankroll: float = 10000) -> OptimizedAdaptiveAI:
    """Create optimized adaptive AI with tuned crisis sensitivity."""
    return OptimizedAdaptiveAI(initial_bankroll) 
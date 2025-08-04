#!/usr/bin/env python3
"""
B: Enhanced Adaptive AI - Optimized Crisis Management + Better Betting Strategy
Improvement over optimized_adaptive_ai.py with:
- More sophisticated crisis detection
- Dynamic learning rate adjustment  
- Multi-timeframe analysis
- Enhanced risk management
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import deque
import time
# Simple basic strategy implementation for Enhanced AI

@dataclass
class CrisisMetrics:
    """Enhanced crisis detection metrics"""
    current_drawdown: float = 0.0
    max_drawdown: float = 0.0
    volatility: float = 0.0
    consecutive_losses: int = 0
    recent_win_rate: float = 0.0
    kelly_fraction: float = 0.0
    risk_of_ruin: float = 0.0

class EnhancedAdaptiveAI:
    """
    B: Enhanced Adaptive AI with sophisticated crisis management
    """
    
    def __init__(self, initial_bankroll: float):
        print("🚀 ENHANCED ADAPTIVE AI INITIALIZING")
        
        # Core parameters
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.total_hands = 0
        self.total_won = 0.0
        self.total_wagered = 0.0
        
        # Enhanced metrics tracking
        self.bankroll_history = deque(maxlen=1000)
        self.result_history = deque(maxlen=500)
        self.bet_history = deque(maxlen=500)
        self.return_history = deque(maxlen=200)
        
        # Multi-timeframe windows
        self.short_window = deque(maxlen=50)   # Last 50 hands
        self.medium_window = deque(maxlen=200)  # Last 200 hands
        self.long_window = deque(maxlen=500)    # Last 500 hands
        
        # Enhanced crisis management
        self.crisis_metrics = CrisisMetrics()
        self.crisis_threshold = 0.12  # 12% drawdown triggers crisis
        self.severe_crisis_threshold = 0.20  # 20% triggers severe measures
        
        # Adaptive parameters
        self.base_bet_multiplier = 1.0
        self.learning_rate = 0.01
        self.momentum = 0.95
        self.adaptation_speed = 0.1
        
        # Risk management
        self.max_risk_per_hand = 0.02  # Max 2% of bankroll per hand
        self.kelly_multiplier = 0.25   # Conservative Kelly fraction
        
        print(f"   💰 Initial Bankroll: ${initial_bankroll:,.2f}")
        print(f"   🧠 Features: Multi-timeframe + Enhanced Crisis + Kelly Criterion")
        print(f"   ⚖️ Philosophy: Sophisticated Risk + Adaptive Learning")
    
    def update_metrics(self, bet_size: float, result: float) -> None:
        """Enhanced metric tracking with multi-timeframe analysis"""
        self.total_hands += 1
        self.total_wagered += bet_size
        self.total_won += result
        self.current_bankroll += result
        
        # Multi-timeframe tracking
        hand_return = result / bet_size if bet_size > 0 else 0
        self.short_window.append(hand_return)
        self.medium_window.append(hand_return)
        self.long_window.append(hand_return)
        
        # History tracking
        self.bankroll_history.append(self.current_bankroll)
        self.result_history.append(result)
        self.bet_history.append(bet_size)
        self.return_history.append(hand_return)
        
        # Update crisis metrics
        self._update_crisis_metrics()
    
    def _update_crisis_metrics(self) -> None:
        """Sophisticated crisis detection algorithm"""
        if len(self.bankroll_history) < 10:
            return
            
        # Calculate drawdown
        peak_bankroll = max(self.bankroll_history)
        self.crisis_metrics.current_drawdown = (peak_bankroll - self.current_bankroll) / peak_bankroll
        self.crisis_metrics.max_drawdown = max(self.crisis_metrics.max_drawdown, self.crisis_metrics.current_drawdown)
        
        # Calculate volatility (standard deviation of returns)
        if len(self.return_history) >= 20:
            self.crisis_metrics.volatility = np.std(list(self.return_history))
        
        # Count consecutive losses
        consecutive = 0
        for result in reversed(self.result_history):
            if result < 0:
                consecutive += 1
            else:
                break
        self.crisis_metrics.consecutive_losses = consecutive
        
        # Recent win rate (last 50 hands)
        if len(self.result_history) >= 20:
            recent_results = list(self.result_history)[-50:]
            wins = sum(1 for r in recent_results if r > 0)
            self.crisis_metrics.recent_win_rate = wins / len(recent_results)
        
        # Kelly fraction estimation
        if len(self.return_history) >= 30:
            returns = list(self.return_history)
            mean_return = np.mean(returns)
            variance = np.var(returns)
            if variance > 0:
                self.crisis_metrics.kelly_fraction = mean_return / variance
            
        # Risk of ruin estimation (simplified)
        if self.current_bankroll > 0:
            relative_bankroll = self.current_bankroll / self.initial_bankroll
            self.crisis_metrics.risk_of_ruin = max(0, 1 - relative_bankroll) ** 2
    
    def get_crisis_level(self) -> str:
        """Enhanced crisis level determination"""
        metrics = self.crisis_metrics
        
        # Severe crisis conditions
        if (metrics.current_drawdown > self.severe_crisis_threshold or
            metrics.consecutive_losses >= 15 or
            metrics.recent_win_rate < 0.15 or
            metrics.risk_of_ruin > 0.3):
            return "severe"
        
        # Major crisis conditions  
        elif (metrics.current_drawdown > self.crisis_threshold or
              metrics.consecutive_losses >= 10 or
              metrics.recent_win_rate < 0.25 or
              metrics.volatility > 1.5):
            return "major"
        
        # Minor crisis conditions
        elif (metrics.current_drawdown > 0.06 or
              metrics.consecutive_losses >= 6 or
              metrics.recent_win_rate < 0.35):
            return "minor"
        
        # Normal conditions
        else:
            return "normal"
    
    def decide_bet_size(self, min_bet: float, max_bet: float, true_count: float = 0.0) -> float:
        """Enhanced betting strategy with Kelly criterion and crisis adaptation"""
        crisis_level = self.get_crisis_level()
        
        # Base bet calculation using Kelly criterion
        if len(self.return_history) >= 20 and self.current_bankroll > 0:
            # Kelly fraction with safety multiplier
            kelly_bet = self.current_bankroll * abs(self.crisis_metrics.kelly_fraction) * self.kelly_multiplier
            base_bet = max(min_bet, min(kelly_bet, max_bet * 0.5))
        else:
            base_bet = min_bet * 2  # Conservative start
        
        # True count adjustment (card counting bonus)
        count_multiplier = 1.0
        if true_count > 1:
            count_multiplier = 1 + (true_count - 1) * 0.3  # 30% increase per TC unit
        elif true_count < -1:
            count_multiplier = max(0.5, 1 + true_count * 0.2)  # Reduce bet on negative count
        
        # Crisis adjustments
        crisis_multiplier = self._get_crisis_multiplier(crisis_level)
        
        # Multi-timeframe momentum
        momentum_multiplier = self._calculate_momentum_multiplier()
        
        # Final bet calculation
        final_bet = base_bet * count_multiplier * crisis_multiplier * momentum_multiplier
        
        # Risk limits
        max_risk_bet = self.current_bankroll * self.max_risk_per_hand
        final_bet = min(final_bet, max_risk_bet)
        
        # Bounds checking
        final_bet = max(min_bet, min(final_bet, max_bet))
        
        return round(final_bet, 2)
    
    def _get_crisis_multiplier(self, crisis_level: str) -> float:
        """Get betting multiplier based on crisis level"""
        if crisis_level == "severe":
            return 0.3  # Severe reduction
        elif crisis_level == "major":
            return 0.5  # Major reduction
        elif crisis_level == "minor":
            return 0.7  # Minor reduction
        else:
            return 1.0  # Normal betting
    
    def _calculate_momentum_multiplier(self) -> float:
        """Calculate momentum-based multiplier from multi-timeframe analysis"""
        if len(self.short_window) < 10:
            return 1.0
            
        # Short-term momentum
        short_returns = list(self.short_window)[-10:]
        short_momentum = np.mean(short_returns) if short_returns else 0
        
        # Medium-term trend
        if len(self.medium_window) >= 50:
            medium_returns = list(self.medium_window)[-50:]
            medium_trend = np.mean(medium_returns)
        else:
            medium_trend = 0
        
        # Combined momentum score
        momentum_score = (short_momentum * 0.7 + medium_trend * 0.3)
        
        # Convert to multiplier (conservative)
        if momentum_score > 0.1:
            return min(1.3, 1 + momentum_score * 2)
        elif momentum_score < -0.1:
            return max(0.7, 1 + momentum_score * 1.5)
        else:
            return 1.0
    
    def decide_play_action(self, player_total: int, dealer_up: int, usable_ace: bool) -> str:
        """Enhanced play strategy with adaptive basic strategy"""
        crisis_level = self.get_crisis_level()
        
        # Get basic strategy action
        basic_action = self._get_basic_action(player_total, dealer_up, usable_ace)
        
        # Crisis modifications (more conservative)
        if crisis_level in ["severe", "major"]:
            # More conservative in crisis
            if basic_action == "double" and player_total >= 10:
                return "hit"  # Avoid doubling in crisis
            elif basic_action == "split" and player_total != 16:  # Only split Aces in crisis
                return "hit"
        
        # Momentum-based adjustments
        if len(self.short_window) >= 10:
            recent_performance = np.mean(list(self.short_window)[-10:])
            
            # If doing well, be slightly more aggressive
            if recent_performance > 0.15 and crisis_level == "normal":
                if basic_action == "hit" and player_total == 12 and dealer_up <= 6:
                    return "stand"  # Slightly more aggressive
                    
            # If doing poorly, be more conservative
            elif recent_performance < -0.15:
                if basic_action == "stand" and player_total <= 16 and dealer_up >= 7:
                    return "hit"  # More conservative
        
        return basic_action
    
    def update_result(self, bet_size: float, result: float) -> None:
        """Update AI with hand result and adapt parameters"""
        self.update_metrics(bet_size, result)
        
        # Adaptive learning
        self._adapt_parameters(result, bet_size)
    
    def _adapt_parameters(self, result: float, bet_size: float) -> None:
        """Adapt AI parameters based on recent performance"""
        if len(self.return_history) < 20:
            return
            
        recent_performance = np.mean(list(self.return_history)[-20:])
        
        # Adjust learning rate based on performance
        if recent_performance < -0.1:
            self.learning_rate = min(0.05, self.learning_rate * 1.1)  # Learn faster when losing
        elif recent_performance > 0.05:
            self.learning_rate = max(0.005, self.learning_rate * 0.95)  # Learn slower when winning
        
        # Adjust adaptation speed
        volatility = np.std(list(self.return_history)[-20:])
        self.adaptation_speed = max(0.05, min(0.3, volatility * 0.2))
    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        if self.total_wagered == 0:
            return {"error": "No hands played yet"}
        
        # Basic metrics
        total_roi = (self.total_won - self.total_wagered) / self.total_wagered
        current_roi = (self.current_bankroll - self.initial_bankroll) / self.initial_bankroll
        
        # Win rate
        if len(self.result_history) > 0:
            wins = sum(1 for r in self.result_history if r > 0)
            win_rate = wins / len(self.result_history)
        else:
            win_rate = 0
        
        # Sharpe ratio
        if len(self.return_history) >= 10:
            returns = list(self.return_history)
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe = mean_return / std_return if std_return > 0 else 0
        else:
            sharpe = 0
        
        crisis_level = self.get_crisis_level()
        
        return {
            "hands_played": self.total_hands,
            "current_bankroll": self.current_bankroll,
            "total_roi": total_roi,
            "current_roi": current_roi,
            "win_rate": win_rate,
            "sharpe_ratio": sharpe,
            "current_crisis_level": crisis_level,
            "max_drawdown": self.crisis_metrics.max_drawdown,
            "consecutive_losses": self.crisis_metrics.consecutive_losses,
            "recent_win_rate": self.crisis_metrics.recent_win_rate,
            "volatility": self.crisis_metrics.volatility,
            "risk_of_ruin": self.crisis_metrics.risk_of_ruin,
            "kelly_fraction": self.crisis_metrics.kelly_fraction
        }
    
    def _get_basic_action(self, player_total: int, dealer_up: int, usable_ace: bool) -> str:
        """Simple basic strategy implementation"""
        # Blackjack - always stand
        if player_total == 21:
            return "stand"
        
        # Bust protection
        if player_total > 21:
            return "stand"
        
        # Soft hands (with usable ace)
        if usable_ace:
            if player_total >= 19:
                return "stand"
            elif player_total == 18:
                return "stand" if dealer_up in [2, 7, 8] else "hit"
            else:
                return "hit"
        
        # Hard hands
        if player_total >= 17:
            return "stand"
        elif player_total <= 11:
            return "hit"
        elif player_total in [12, 13, 14, 15, 16]:
            return "stand" if dealer_up <= 6 else "hit"
        else:
            return "hit"
    
    def get_status_report(self) -> str:
        """Generate detailed status report"""
        metrics = self.get_performance_metrics()
        
        if "error" in metrics:
            return metrics["error"]
        
        crisis_emoji = {
            "normal": "🟢",
            "minor": "🟡", 
            "major": "🟠",
            "severe": "🔴"
        }
        
        report = f"""
🚀 ENHANCED ADAPTIVE AI STATUS
========================================
📊 Performance:
   Hands: {metrics['hands_played']}
   Bankroll: ${metrics['current_bankroll']:,.2f}
   ROI: {metrics['current_roi']:+.1%}
   Win Rate: {metrics['win_rate']:.1%}
   Sharpe Ratio: {metrics['sharpe_ratio']:.3f}

🚨 Crisis Management:
   Level: {crisis_emoji.get(metrics['current_crisis_level'], '❓')} {metrics['current_crisis_level'].upper()}
   Max Drawdown: {metrics['max_drawdown']:.1%}
   Consecutive Losses: {metrics['consecutive_losses']}
   Recent Win Rate: {metrics['recent_win_rate']:.1%}

📈 Advanced Metrics:
   Volatility: {metrics['volatility']:.3f}
   Kelly Fraction: {metrics['kelly_fraction']:.3f}
   Risk of Ruin: {metrics['risk_of_ruin']:.1%}
   Learning Rate: {self.learning_rate:.4f}
"""
        return report

def create_enhanced_adaptive_ai(initial_bankroll: float) -> EnhancedAdaptiveAI:
    """Factory function to create Enhanced Adaptive AI"""
    return EnhancedAdaptiveAI(initial_bankroll) 
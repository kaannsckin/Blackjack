"""Performance Metrics for Blackjack RL (FAZ 1 – F1.3)

Implements:
- EV (Expected Value) calculation
- RTP (Return to Player) analysis  
- Risk metrics (VaR, volatility)
- Win rate and edge analysis
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Container for all performance metrics."""
    ev: float  # Expected Value
    rtp: float  # Return to Player (%)
    win_rate: float  # Win rate (%)
    push_rate: float  # Push rate (%)
    loss_rate: float  # Loss rate (%)
    volatility: float  # Standard deviation
    var_95: float  # 95% Value at Risk
    max_win: float  # Maximum single hand win
    max_loss: float  # Maximum single hand loss
    total_hands: int  # Total hands played
    total_bets: float  # Total amount bet
    net_profit: float  # Net profit/loss


class PerformanceAnalyzer:
    """Analyze blackjack performance metrics."""
    
    def __init__(self, bet_size: float = 1.0):
        self.bet_size = bet_size
    
    def calculate_metrics(self, rewards: List[float], bets: Optional[List[float]] = None) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics."""
        rewards = np.array(rewards)
        
        if bets is None:
            bets = np.full_like(rewards, self.bet_size)
        else:
            bets = np.array(bets)
        
        # Basic statistics
        total_hands = len(rewards)
        total_bets = np.sum(bets)
        net_profit = np.sum(rewards * bets)
        
        # Win/loss rates
        wins = rewards > 0
        losses = rewards < 0
        pushes = rewards == 0
        
        win_rate = np.mean(wins) * 100
        loss_rate = np.mean(losses) * 100
        push_rate = np.mean(pushes) * 100
        
        # EV and RTP
        ev = np.mean(rewards)
        rtp = (net_profit / total_bets) * 100 if total_bets > 0 else 0
        
        # Risk metrics
        volatility = np.std(rewards)
        var_95 = np.percentile(rewards, 5)  # 95% VaR (5th percentile)
        
        # Extremes
        max_win = np.max(rewards) if len(rewards) > 0 else 0
        max_loss = np.min(rewards) if len(rewards) > 0 else 0
        
        return PerformanceMetrics(
            ev=ev,
            rtp=rtp,
            win_rate=win_rate,
            push_rate=push_rate,
            loss_rate=loss_rate,
            volatility=volatility,
            var_95=var_95,
            max_win=max_win,
            max_loss=max_loss,
            total_hands=total_hands,
            total_bets=total_bets,
            net_profit=net_profit,
        )
    
    def analyze_session(self, session_results: List[Dict]) -> PerformanceMetrics:
        """Analyze a session of game results."""
        rewards = []
        bets = []
        
        for result in session_results:
            rewards.append(result.get('reward', 0))
            bets.append(result.get('bet', self.bet_size))
        
        return self.calculate_metrics(rewards, bets)
    
    def compare_strategies(
        self, 
        strategy_results: Dict[str, List[float]], 
        confidence_level: float = 0.95
    ) -> pd.DataFrame:
        """Compare multiple strategies."""
        comparison = []
        
        for strategy_name, rewards in strategy_results.items():
            metrics = self.calculate_metrics(rewards)
            
            # Calculate confidence intervals
            n = len(rewards)
            if n > 0:
                se = metrics.volatility / np.sqrt(n)
                z_score = 1.96  # 95% confidence
                ci_lower = metrics.ev - z_score * se
                ci_upper = metrics.ev + z_score * se
            else:
                ci_lower = ci_upper = 0
            
            comparison.append({
                'Strategy': strategy_name,
                'EV': metrics.ev,
                'EV_CI_Lower': ci_lower,
                'EV_CI_Upper': ci_upper,
                'RTP (%)': metrics.rtp,
                'Win Rate (%)': metrics.win_rate,
                'Volatility': metrics.volatility,
                'VaR_95': metrics.var_95,
                'Total Hands': metrics.total_hands,
            })
        
        return pd.DataFrame(comparison)
    
    def calculate_edge(self, ev: float, bet_size: float = 1.0) -> float:
        """Calculate house edge or player edge."""
        return -ev / bet_size * 100  # Negative for house edge, positive for player edge
    
    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate Kelly Criterion for optimal bet sizing."""
        if avg_loss == 0:
            return 0
        
        p = win_rate / 100
        q = 1 - p
        b = avg_win / abs(avg_loss)
        
        kelly = (b * p - q) / b
        return max(0, min(kelly, 0.25))  # Cap at 25% for safety
    
    def calculate_risk_of_ruin(
        self, 
        bankroll: float, 
        ev: float, 
        volatility: float, 
        bet_size: float = 1.0
    ) -> float:
        """Calculate risk of ruin using random walk approximation."""
        if volatility == 0:
            return 0 if ev > 0 else 1
        
        edge = ev / bet_size
        variance = volatility ** 2
        
        if edge <= 0:
            return 1.0
        
        # Risk of ruin formula
        ror = np.exp(-2 * edge * bankroll / variance)
        return min(ror, 1.0)


def calculate_session_metrics(session_data: List[Dict]) -> Dict:
    """Calculate session-level metrics."""
    analyzer = PerformanceAnalyzer()
    
    # Extract rewards
    rewards = [game['reward'] for game in session_data]
    bets = [game.get('bet', 1.0) for game in session_data]
    
    # Calculate metrics
    metrics = analyzer.calculate_metrics(rewards, bets)
    
    # Additional session metrics
    session_length = len(session_data)
    avg_hands_per_hour = session_length / (session_data[-1].get('timestamp', session_length) / 3600)
    
    # Streak analysis
    streaks = []
    current_streak = 0
    current_sign = 0
    
    for reward in rewards:
        if reward > 0:
            if current_sign == 1:
                current_streak += 1
            else:
                if current_streak > 0:
                    streaks.append(current_streak)
                current_streak = 1
                current_sign = 1
        elif reward < 0:
            if current_sign == -1:
                current_streak += 1
            else:
                if current_streak > 0:
                    streaks.append(-current_streak)
                current_streak = 1
                current_sign = -1
        else:
            if current_streak > 0:
                streaks.append(current_streak if current_sign == 1 else -current_streak)
            current_streak = 0
            current_sign = 0
    
    if current_streak > 0:
        streaks.append(current_streak if current_sign == 1 else -current_streak)
    
    max_winning_streak = max([s for s in streaks if s > 0], default=0)
    max_losing_streak = abs(min([s for s in streaks if s < 0], default=0))
    
    return {
        'metrics': metrics,
        'session_length': session_length,
        'avg_hands_per_hour': avg_hands_per_hour,
        'max_winning_streak': max_winning_streak,
        'max_losing_streak': max_losing_streak,
        'avg_streak_length': np.mean([abs(s) for s in streaks]) if streaks else 0,
    } 
"""
================================================================================
ADVANCED BETTING ENVIRONMENT (Phase 2 - F2.3)
================================================================================

📋 **AMAÇ:**
   F2.3 için ultra-sophisticated betting environment. Tüm advanced features
   tek environment'ta: multiple card counting systems, hand history tracking,
   table dynamics, deck composition analysis, advanced risk metrics.

🎯 **F2.3 ADVANCED ÖZELLİKLERİ:**
   • Multiple Card Counting: Hi-Lo, KO, Red Seven, Omega II
   • Hand History Tracking: Son N el'in detaylı geçmişi
   • Table Dynamics: Betting patterns, win streaks, table statistics  
   • Deck Composition: Kalan kartların detaylı analizi
   • Advanced Risk Metrics: Kelly Criterion, Risk of Ruin, Sharpe Ratio
   • True Count Sophistication: Multiple normalization methods
   • Penetration Analysis: Deck kesimi ve shuffling effects

🏗️ **ENHANCED OBSERVATION SPACE:**
   [player_total, dealer_up, usable_ace, 
    hi_lo_tc, ko_tc, red7_tc, omega2_tc,
    bankroll_ratio, prev_result, 
    hand_history_features(10), 
    deck_composition_features(13),
    table_dynamics_features(8),
    risk_metrics(5)]
   
   Total: ~45 dimensional observation space

================================================================================
"""

from __future__ import annotations

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Any, Dict, Tuple, Optional, Union, List
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import math

from betting_action_environment import BettingActionEnv, ActionConfig, ActionSpaceType


class CardCountingSystem(Enum):
    """Different card counting systems."""
    HI_LO = "hi_lo"
    KO = "ko"  # Knockout
    RED_SEVEN = "red_seven"
    OMEGA_II = "omega_ii"
    HALVES = "halves"


@dataclass
class AdvancedConfig:
    """Configuration for advanced betting environment."""
    # Card counting systems to track
    counting_systems: List[CardCountingSystem] = field(
        default_factory=lambda: [CardCountingSystem.HI_LO, CardCountingSystem.KO, CardCountingSystem.RED_SEVEN]
    )
    
    # Hand history tracking
    hand_history_size: int = 20  # Track last N hands
    detailed_history: bool = True  # Track detailed hand info vs summary
    
    # Deck composition tracking
    track_deck_composition: bool = True
    composition_normalization: str = "remaining_ratio"  # "count", "ratio", "remaining_ratio"
    
    # Table dynamics
    track_table_dynamics: bool = True
    betting_pattern_window: int = 50  # Analyze betting patterns over N hands
    
    # Risk metrics
    calculate_kelly: bool = True
    real_time_sharpe: bool = True
    advanced_ror: bool = True  # More sophisticated Risk of Ruin calculation
    
    # True count enhancements
    tc_smoothing: bool = True  # Smooth true count fluctuations
    multiple_tc_norms: bool = True  # Different normalization methods


@dataclass
class HandRecord:
    """Detailed record of a single hand."""
    hand_number: int
    initial_cards: List[int]
    final_cards: List[int]
    dealer_up: int
    dealer_final: List[int]
    actions_taken: List[int]  # Sequence of actions
    bet_amount: float
    net_result: float
    true_counts: Dict[str, float]  # TC at hand start for each system
    bankroll_before: float
    bankroll_after: float
    split_hands: int = 0
    doubled: bool = False


@dataclass
class TableDynamics:
    """Table-level statistics and patterns."""
    total_hands: int = 0
    win_rate: float = 0.0
    average_bet: float = 0.0
    betting_volatility: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    max_win_streak: int = 0
    max_loss_streak: int = 0
    hands_since_shuffle: int = 0
    penetration_reached: float = 0.0


class AdvancedBettingEnv(BettingActionEnv):
    """
    Ultra-sophisticated betting environment with all advanced features.
    
    F2.3 Complete Implementation: Everything needed for professional-level RL training.
    """
    
    def __init__(
        self,
        *,
        seed: Optional[int] = None,
        rules: Optional[Dict[str, Any]] = None,
        penetration: float = 0.75,
        initial_bankroll: float = 1000.0,
        action_config: Optional[ActionConfig] = None,
        advanced_config: Optional[AdvancedConfig] = None,
        risk_aversion: float = 0.1,
    ) -> None:
        """Initialize advanced betting environment."""
        super().__init__(
            seed=seed,
            rules=rules,
            penetration=penetration,
            initial_bankroll=initial_bankroll,
            action_config=action_config,
            risk_aversion=risk_aversion,
        )
        
        self.advanced_config = advanced_config or AdvancedConfig()
        
        # Initialize card counting systems
        self._init_counting_systems()
        
        # Initialize hand history tracking
        self.hand_history: deque[HandRecord] = deque(maxlen=self.advanced_config.hand_history_size)
        self.current_hand_number = 0
        
        # Initialize deck composition tracking
        if self.advanced_config.track_deck_composition:
            self._init_deck_composition()
        
        # Initialize table dynamics
        if self.advanced_config.track_table_dynamics:
            self.table_dynamics = TableDynamics()
            self.recent_results = deque(maxlen=self.advanced_config.betting_pattern_window)
            self.recent_bets = deque(maxlen=self.advanced_config.betting_pattern_window)
        
        # Initialize risk metrics
        self.episode_returns = deque(maxlen=1000)  # For Sharpe ratio calculation
        self.drawdown_tracking = {"peak": initial_bankroll, "max_dd": 0.0}
        
        # Enhanced observation space
        self._setup_advanced_observation_space()
    
    def _init_counting_systems(self) -> None:
        """Initialize multiple card counting systems."""
        self.counting_systems = {}
        
        for system in self.advanced_config.counting_systems:
            self.counting_systems[system.value] = {
                "running_count": 0,
                "true_count": 0.0,
                "smoothed_tc": 0.0,
                "cards_seen": 0,
            }
    
    def _init_deck_composition(self) -> None:
        """Initialize deck composition tracking."""
        # Track remaining cards of each rank (A, 2, 3, ..., K)
        num_decks = self.rules["num_decks"]
        self.deck_composition = {
            rank: 4 * num_decks for rank in range(1, 14)  # A=1, K=13
        }
        self.total_cards_seen = 0
    
    def _setup_advanced_observation_space(self) -> None:
        """Setup enhanced observation space with all advanced features."""
        obs_features = []
        
        # Base features (7)
        obs_features.extend([
            (4, 31),    # player_total
            (1, 11),    # dealer_up
            (0, 1),     # usable_ace
            (-20, 20),  # primary_true_count
            (0.0, 10.0), # bankroll_ratio
            (-10.0, 10.0), # prev_result_normalized
            (0.0, 1.0),  # penetration_ratio
        ])
        
        # Card counting systems (variable, up to 4 systems * 2 features each = 8)
        for system in self.advanced_config.counting_systems:
            obs_features.extend([
                (-20, 20),   # running_count_normalized
                (-10, 10),   # true_count
            ])
        
        # Hand history features (10)
        if self.advanced_config.detailed_history:
            obs_features.extend([
                (-1, 1),     # last_hand_result_normalized
                (-1, 1),     # avg_last_5_results
                (-1, 1),     # avg_last_10_results
                (0, 1),      # win_rate_last_20
                (0, 10),     # avg_bet_last_10_normalized
                (0, 1),      # recent_volatility
                (0, 1),      # recent_double_rate
                (0, 1),      # recent_split_rate
                (-5, 5),     # current_win_streak
                (-5, 5),     # current_loss_streak
            ])
        
        # Deck composition features (13 card ranks)
        if self.advanced_config.track_deck_composition:
            for rank in range(1, 14):  # A through K
                obs_features.append((0.0, 1.0))  # remaining_ratio
        
        # Table dynamics features (8)
        if self.advanced_config.track_table_dynamics:
            obs_features.extend([
                (0, 1),      # overall_win_rate
                (0, 5),      # betting_volatility_normalized
                (0, 1),      # hands_since_shuffle_ratio
                (-10, 10),   # recent_trend (positive = winning)
                (0, 1),      # big_bet_success_rate
                (0, 1),      # small_bet_success_rate
                (0, 1),      # action_diversity_index
                (0, 1),      # decision_confidence_score
            ])
        
        # Risk metrics (5)
        obs_features.extend([
            (0.0, 100.0),  # risk_of_ruin_pct
            (-2.0, 5.0),   # kelly_criterion_bet
            (-5.0, 5.0),   # sharpe_ratio
            (0.0, 1.0),    # max_drawdown_ratio
            (0.0, 2.0),    # bankroll_growth_rate
        ])
        
        # Create observation space
        low = np.array([low for low, high in obs_features], dtype=np.float32)
        high = np.array([high for low, high in obs_features], dtype=np.float32)
        
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)
        
        print(f"🔧 Advanced observation space initialized: {self.observation_space.shape[0]} features")
    
    def _update_card_counting(self, card: int) -> None:
        """Update all card counting systems."""
        for system_name, system_data in self.counting_systems.items():
            value = self._get_card_count_value(card, system_name)
            system_data["running_count"] += value
            system_data["cards_seen"] += 1
            
            # Calculate true count
            decks_remaining = len(self._shoe) / 52 if self._shoe else 0.1
            system_data["true_count"] = system_data["running_count"] / max(decks_remaining, 0.1)
            
            # Smooth true count if enabled
            if self.advanced_config.tc_smoothing:
                alpha = 0.3  # Smoothing factor
                system_data["smoothed_tc"] = (
                    alpha * system_data["true_count"] + 
                    (1 - alpha) * system_data["smoothed_tc"]
                )
    
    def _get_card_count_value(self, card: int, system: str) -> int:
        """Get card counting value for specific system."""
        if system == "hi_lo":
            if 2 <= card <= 6:
                return 1
            elif card in {1, 10, 11, 12, 13}:
                return -1
            return 0
        
        elif system == "ko":  # Knockout
            if card in {2, 3, 4, 5, 6, 7}:
                return 1
            elif card in {1, 10, 11, 12, 13}:
                return -1
            return 0
        
        elif system == "red_seven":
            if card in {2, 3, 4, 5, 6}:
                return 1
            elif card == 7:
                return 0.5  # Simplified: would need suit info for true Red Seven
            elif card in {1, 10, 11, 12, 13}:
                return -1
            return 0
        
        elif system == "omega_ii":
            omega_values = {1: -1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 1, 
                          8: 0, 9: -1, 10: -2, 11: -2, 12: -2, 13: -2}
            return omega_values.get(card, 0)
        
        return 0
    
    def _update_deck_composition(self, card: int) -> None:
        """Update deck composition tracking."""
        if self.advanced_config.track_deck_composition:
            self.deck_composition[card] = max(0, self.deck_composition[card] - 1)
            self.total_cards_seen += 1
    
    def _calculate_hand_history_features(self) -> np.ndarray:
        """Calculate hand history-based features."""
        if not self.hand_history:
            return np.zeros(10, dtype=np.float32)
        
        recent_hands = list(self.hand_history)
        
        # Last hand result
        last_result = recent_hands[-1].net_result if recent_hands else 0
        last_result_norm = np.clip(last_result / 10.0, -1, 1)
        
        # Average results
        if len(recent_hands) >= 5:
            avg_last_5 = np.mean([h.net_result for h in recent_hands[-5:]])
            avg_last_5_norm = np.clip(avg_last_5 / 10.0, -1, 1)
        else:
            avg_last_5_norm = 0
        
        if len(recent_hands) >= 10:
            avg_last_10 = np.mean([h.net_result for h in recent_hands[-10:]])
            avg_last_10_norm = np.clip(avg_last_10 / 10.0, -1, 1)
        else:
            avg_last_10_norm = 0
        
        # Win rate
        if len(recent_hands) >= 20:
            wins = sum(1 for h in recent_hands[-20:] if h.net_result > 0)
            win_rate = wins / 20
        else:
            wins = sum(1 for h in recent_hands if h.net_result > 0)
            win_rate = wins / max(len(recent_hands), 1)
        
        # Betting patterns
        if len(recent_hands) >= 10:
            recent_bets = [h.bet_amount for h in recent_hands[-10:]]
            avg_bet_norm = np.mean(recent_bets) / 100.0  # Normalize by max bet
            bet_volatility = np.std(recent_bets) / max(np.mean(recent_bets), 1)
        else:
            avg_bet_norm = 0
            bet_volatility = 0
        
        # Action rates
        if recent_hands:
            double_rate = sum(1 for h in recent_hands if h.doubled) / len(recent_hands)
            split_rate = sum(1 for h in recent_hands if h.split_hands > 0) / len(recent_hands)
        else:
            double_rate = split_rate = 0
        
        # Streaks (simplified for observation)
        win_streak = max(-5, min(5, self.table_dynamics.consecutive_wins if hasattr(self, 'table_dynamics') else 0))
        loss_streak = max(-5, min(5, -self.table_dynamics.consecutive_losses if hasattr(self, 'table_dynamics') else 0))
        
        return np.array([
            last_result_norm, avg_last_5_norm, avg_last_10_norm, win_rate,
            avg_bet_norm, bet_volatility, double_rate, split_rate,
            win_streak, loss_streak
        ], dtype=np.float32)
    
    def _calculate_deck_composition_features(self) -> np.ndarray:
        """Calculate deck composition features."""
        if not self.advanced_config.track_deck_composition:
            return np.zeros(13, dtype=np.float32)
        
        total_original = sum(4 * self.rules["num_decks"] for _ in range(13))
        remaining_ratios = []
        
        for rank in range(1, 14):
            original_count = 4 * self.rules["num_decks"]
            remaining_ratio = self.deck_composition[rank] / original_count
            remaining_ratios.append(remaining_ratio)
        
        return np.array(remaining_ratios, dtype=np.float32)
    
    def _calculate_table_dynamics_features(self) -> np.ndarray:
        """Calculate table dynamics features."""
        if not self.advanced_config.track_table_dynamics:
            return np.zeros(8, dtype=np.float32)
        
        td = self.table_dynamics
        
        # Overall win rate
        win_rate = td.win_rate
        
        # Betting volatility (normalized)
        betting_vol = min(td.betting_volatility / 50.0, 5.0)  # Cap at 5
        
        # Hands since shuffle ratio
        total_cards = 52 * self.rules["num_decks"]
        cards_dealt = total_cards - len(self._shoe) if self._shoe else total_cards
        shuffle_progress = min(cards_dealt / (total_cards * self.penetration), 1.0)
        
        # Recent trend (last 10 hands)
        if len(self.recent_results) >= 10:
            recent_sum = sum(list(self.recent_results)[-10:])
            recent_trend = np.clip(recent_sum / 10.0, -10, 10)
        else:
            recent_trend = 0
        
        # Bet size success rates
        if self.recent_bets and self.recent_results:
            bets_array = np.array(list(self.recent_bets))
            results_array = np.array(list(self.recent_results))
            
            # Big bet success (>= 75th percentile)
            if len(bets_array) >= 4:
                big_bet_threshold = np.percentile(bets_array, 75)
                big_bet_mask = bets_array >= big_bet_threshold
                big_bet_success = np.mean(results_array[big_bet_mask] > 0) if big_bet_mask.any() else 0.5
                
                # Small bet success (<= 25th percentile)
                small_bet_threshold = np.percentile(bets_array, 25)
                small_bet_mask = bets_array <= small_bet_threshold
                small_bet_success = np.mean(results_array[small_bet_mask] > 0) if small_bet_mask.any() else 0.5
            else:
                big_bet_success = small_bet_success = 0.5
        else:
            big_bet_success = small_bet_success = 0.5
        
        # Action diversity (simplified)
        action_diversity = min(len(set(self.action_stats["play_actions"])) / 4.0, 1.0)
        
        # Decision confidence (based on consistency)
        decision_confidence = 1.0 - min(self.action_stats["invalid_actions"] / max(self.action_stats["total_actions"], 1), 1.0)
        
        return np.array([
            win_rate, betting_vol, shuffle_progress, recent_trend,
            big_bet_success, small_bet_success, action_diversity, decision_confidence
        ], dtype=np.float32)
    
    def _calculate_risk_metrics(self) -> np.ndarray:
        """Calculate advanced risk metrics."""
        # Risk of Ruin
        if self.advanced_config.advanced_ror:
            ror = self._calculate_advanced_ror()
        else:
            ror = self._calculate_risk_of_ruin()
        
        # Kelly Criterion bet sizing
        kelly_bet = self._calculate_kelly_criterion() if self.advanced_config.calculate_kelly else 0
        
        # Sharpe Ratio
        sharpe = self._calculate_sharpe_ratio() if self.advanced_config.real_time_sharpe else 0
        
        # Max Drawdown
        max_dd_ratio = self.drawdown_tracking["max_dd"] / max(self.initial_bankroll, 1)
        
        # Bankroll growth rate
        growth_rate = (self.bankroll / self.initial_bankroll) - 1
        
        return np.array([ror, kelly_bet, sharpe, max_dd_ratio, growth_rate], dtype=np.float32)
    
    def _calculate_advanced_ror(self) -> float:
        """Calculate sophisticated Risk of Ruin."""
        if self.bankroll <= 0:
            return 100.0
        
        # Use recent performance to estimate win probability and average win/loss
        if len(self.episode_returns) >= 20:
            returns = np.array(list(self.episode_returns))
            win_prob = np.mean(returns > 0)
            avg_win = np.mean(returns[returns > 0]) if np.any(returns > 0) else 1
            avg_loss = abs(np.mean(returns[returns < 0])) if np.any(returns < 0) else 1
            
            # Simplified gambler's ruin formula
            if win_prob == 0.5:
                ror = 1.0 / (1.0 + self.bankroll / avg_loss)
            else:
                q_over_p = (1 - win_prob) / win_prob
                ror_ratio = (avg_loss / avg_win)
                if q_over_p * ror_ratio >= 1:
                    ror = 1.0
                else:
                    ror = (q_over_p * ror_ratio) ** (self.bankroll / avg_loss)
        else:
            # Fallback to simple calculation
            ror = super()._calculate_risk_of_ruin()
        
        return min(ror * 100, 100.0)
    
    def _calculate_kelly_criterion(self) -> float:
        """Calculate Kelly Criterion optimal bet size."""
        if len(self.episode_returns) < 10:
            return 1.0  # Conservative default
        
        returns = np.array(list(self.episode_returns))
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        
        if len(wins) == 0 or len(losses) == 0:
            return 1.0
        
        win_prob = len(wins) / len(returns)
        avg_win_ratio = np.mean(wins) / np.mean(abs(losses))
        
        # Kelly formula: f = (bp - q) / b
        # where b = avg_win_ratio, p = win_prob, q = loss_prob
        kelly_fraction = (avg_win_ratio * win_prob - (1 - win_prob)) / avg_win_ratio
        
        # Convert to bet sizing (as multiple of current bet)
        kelly_bet = max(0.1, min(5.0, kelly_fraction * 2))  # Cap between 0.1 and 5
        
        return kelly_bet
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate real-time Sharpe ratio."""
        if len(self.episode_returns) < 5:
            return 0.0
        
        returns = np.array(list(self.episode_returns))
        if np.std(returns) == 0:
            return 0.0
        
        # Annualized Sharpe (assuming 1000 hands per year)
        sharpe = (np.mean(returns) * np.sqrt(1000)) / np.std(returns)
        return np.clip(sharpe, -5, 5)
    
    def _draw_card(self) -> int:
        """Override to update advanced counting systems."""
        card = super()._draw_card()
        
        # Update all counting systems
        self._update_card_counting(card)
        
        # Update deck composition
        self._update_deck_composition(card)
        
        return card
    
    def _get_enhanced_obs(self) -> np.ndarray:
        """Get comprehensive enhanced observation."""
        # Base observation
        try:
            base_obs = super()._get_obs()
        except IndexError:
            base_obs = np.array([0, 1, 0, 0], dtype=np.int32)
        
        # Build comprehensive observation
        obs_components = []
        
        # Base features
        obs_components.extend([
            float(base_obs[0]),  # player_total
            float(base_obs[1]),  # dealer_up
            float(base_obs[2]),  # usable_ace
            float(base_obs[3]),  # primary_true_count (Hi-Lo)
            self.bankroll / self.initial_bankroll,  # bankroll_ratio
            np.clip(self.previous_result / self.max_bet, -10.0, 10.0),  # prev_result
            len(self._shoe) / (52 * self.rules["num_decks"]) if self._shoe else 0,  # penetration
        ])
        
        # Card counting systems
        for system_name in [s.value for s in self.advanced_config.counting_systems]:
            if system_name in self.counting_systems:
                system_data = self.counting_systems[system_name]
                obs_components.extend([
                    np.clip(system_data["running_count"] / 20.0, -1, 1),  # normalized running count
                    np.clip(system_data["true_count"] / 10.0, -1, 1),     # normalized true count
                ])
        
        # Hand history features
        if self.advanced_config.detailed_history:
            history_features = self._calculate_hand_history_features()
            obs_components.extend(history_features)
        
        # Deck composition features
        if self.advanced_config.track_deck_composition:
            composition_features = self._calculate_deck_composition_features()
            obs_components.extend(composition_features)
        
        # Table dynamics features
        if self.advanced_config.track_table_dynamics:
            dynamics_features = self._calculate_table_dynamics_features()
            obs_components.extend(dynamics_features)
        
        # Risk metrics
        risk_features = self._calculate_risk_metrics()
        obs_components.extend(risk_features)
        
        return np.array(obs_components, dtype=np.float32)
    
    def step(self, action: Union[np.ndarray, Dict]):
        """Enhanced step with comprehensive tracking."""
        # Execute step
        obs, reward, done, truncated, info = super().step(action)
        
        if done:
            # Create detailed hand record
            hand_record = HandRecord(
                hand_number=self.current_hand_number,
                initial_cards=self.player_hands[0][:2] if self.player_hands else [],
                final_cards=self.player_hands[0] if self.player_hands else [],
                dealer_up=self.dealer_hand[0] if self.dealer_hand else 0,
                dealer_final=self.dealer_hand.copy() if self.dealer_hand else [],
                actions_taken=[info.get("play_action", 0)],
                bet_amount=info.get("bet_amount", self.current_bet),
                net_result=info.get("net_units", 0),
                true_counts={name: data["true_count"] for name, data in self.counting_systems.items()},
                bankroll_before=self.bankroll - info.get("net_units", 0),
                bankroll_after=self.bankroll,
                split_hands=self._split_count,
                doubled=info.get("play_action", 0) == 2,
            )
            
            # Update hand history
            self.hand_history.append(hand_record)
            self.current_hand_number += 1
            
            # Update table dynamics
            if self.advanced_config.track_table_dynamics:
                self._update_table_dynamics(hand_record)
            
            # Update episode returns for risk calculations
            self.episode_returns.append(hand_record.net_result)
            
            # Update drawdown tracking
            if self.bankroll > self.drawdown_tracking["peak"]:
                self.drawdown_tracking["peak"] = self.bankroll
            
            current_dd = (self.drawdown_tracking["peak"] - self.bankroll) / self.drawdown_tracking["peak"]
            if current_dd > self.drawdown_tracking["max_dd"]:
                self.drawdown_tracking["max_dd"] = current_dd
            
            # Enhanced info
            info.update({
                "hand_number": self.current_hand_number,
                "advanced_metrics": self._get_advanced_metrics_summary(),
            })
        
        return obs, reward, done, truncated, info
    
    def _update_table_dynamics(self, hand_record: HandRecord) -> None:
        """Update table dynamics with new hand data."""
        td = self.table_dynamics
        td.total_hands += 1
        
        # Update win rate
        is_win = hand_record.net_result > 0
        td.win_rate = ((td.win_rate * (td.total_hands - 1)) + int(is_win)) / td.total_hands
        
        # Update betting statistics
        self.recent_bets.append(hand_record.bet_amount)
        self.recent_results.append(hand_record.net_result)
        
        if len(self.recent_bets) > 1:
            td.average_bet = np.mean(list(self.recent_bets))
            td.betting_volatility = np.std(list(self.recent_bets))
        
        # Update streaks
        if hand_record.net_result > 0:
            td.consecutive_wins += 1
            td.consecutive_losses = 0
            td.max_win_streak = max(td.max_win_streak, td.consecutive_wins)
        elif hand_record.net_result < 0:
            td.consecutive_losses += 1
            td.consecutive_wins = 0
            td.max_loss_streak = max(td.max_loss_streak, td.consecutive_losses)
        else:
            td.consecutive_wins = td.consecutive_losses = 0
        
        # Update penetration
        total_cards = 52 * self.rules["num_decks"]
        cards_remaining = len(self._shoe) if self._shoe else 0
        td.penetration_reached = 1.0 - (cards_remaining / total_cards)
        td.hands_since_shuffle = td.total_hands  # Simplified
    
    def _get_advanced_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        summary = {
            "observation_dim": self.observation_space.shape[0],
            "card_counting_systems": {
                name: {
                    "running_count": data["running_count"],
                    "true_count": round(data["true_count"], 2),
                }
                for name, data in self.counting_systems.items()
            },
            "hand_history_size": len(self.hand_history),
        }
        
        if self.advanced_config.track_deck_composition:
            high_value_remaining = sum(self.deck_composition[rank] for rank in [1, 10, 11, 12, 13])
            low_value_remaining = sum(self.deck_composition[rank] for rank in range(2, 7))
            summary["deck_composition"] = {
                "high_value_cards_remaining": high_value_remaining,
                "low_value_cards_remaining": low_value_remaining,
                "total_cards_seen": self.total_cards_seen,
            }
        
        if self.advanced_config.track_table_dynamics:
            summary["table_dynamics"] = {
                "total_hands": self.table_dynamics.total_hands,
                "win_rate": round(self.table_dynamics.win_rate, 3),
                "current_win_streak": self.table_dynamics.consecutive_wins,
                "current_loss_streak": self.table_dynamics.consecutive_losses,
                "penetration": round(self.table_dynamics.penetration_reached, 3),
            }
        
        # Risk metrics
        risk_metrics = self._calculate_risk_metrics()
        summary["risk_metrics"] = {
            "risk_of_ruin_pct": round(risk_metrics[0], 2),
            "kelly_criterion": round(risk_metrics[1], 2),
            "sharpe_ratio": round(risk_metrics[2], 2),
            "max_drawdown_pct": round(risk_metrics[3] * 100, 2),
            "bankroll_growth_pct": round(risk_metrics[4] * 100, 2),
        }
        
        return summary
    
    def reset(self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None):
        """Reset with comprehensive state initialization."""
        obs, info = super().reset(seed=seed, options=options)
        
        # Reset advanced tracking on new shoe
        if options and options.get("new_shoe", False):
            for system_data in self.counting_systems.values():
                system_data["running_count"] = 0
                system_data["true_count"] = 0.0
                system_data["smoothed_tc"] = 0.0
            
            if self.advanced_config.track_deck_composition:
                self._init_deck_composition()
            
            self.drawdown_tracking["peak"] = self.bankroll
        
        return self._get_enhanced_obs(), info


# Testing function for F2.3
def test_advanced_environment():
    """Test advanced environment functionality."""
    print("🧪 Testing Advanced Betting Environment (F2.3)...")
    
    # Test with all advanced features enabled
    advanced_config = AdvancedConfig(
        counting_systems=[CardCountingSystem.HI_LO, CardCountingSystem.KO, CardCountingSystem.RED_SEVEN],
        hand_history_size=10,
        detailed_history=True,
        track_deck_composition=True,
        track_table_dynamics=True,
        calculate_kelly=True,
        real_time_sharpe=True,
        advanced_ror=True,
    )
    
    env = AdvancedBettingEnv(
        seed=42, 
        initial_bankroll=1000,
        advanced_config=advanced_config
    )
    
    print(f"   ✅ Observation space: {env.observation_space.shape[0]} dimensions")
    
    # Test episode
    obs, _ = env.reset()
    print(f"   ✅ Initial observation shape: {obs.shape}")
    print(f"   ✅ Sample observation values: {obs[:10]}")
    
    # Run a few steps
    for i in range(5):
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        
        if done:
            print(f"   ✅ Episode {i+1}: reward={reward:.3f}, done={done}")
            if "advanced_metrics" in info:
                metrics = info["advanced_metrics"]
                print(f"      🎯 Card counts: {metrics['card_counting_systems']}")
                print(f"      📊 Risk metrics: {metrics['risk_metrics']}")
            
            obs, _ = env.reset()
    
    print("✅ Advanced environment test: PASSED")


if __name__ == "__main__":
    test_advanced_environment() 
"""
F2.7 Risk & Güvenlik Analizi Module

Comprehensive risk analysis and safety controls for AI betting strategies.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


@dataclass
class RiskMetrics:
    """Risk analysis metrics for betting strategies."""
    
    # Performance metrics
    total_return: float = 0.0
    roi: float = 0.0
    win_rate: float = 0.0
    avg_bet: float = 0.0
    
    # Risk metrics
    risk_of_ruin: float = 0.0
    max_drawdown: float = 0.0
    max_runup: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    
    # Kelly criterion
    kelly_percentage: float = 0.0
    kelly_violation: bool = False
    
    # Safety metrics
    consecutive_losses: int = 0
    max_consecutive_losses: int = 0
    bet_size_violations: int = 0
    extreme_risk_periods: int = 0
    
    # Advanced metrics
    var_95: float = 0.0  # Value at Risk (95%)
    cvar_95: float = 0.0  # Conditional VaR (95%)
    calmar_ratio: float = 0.0  # Return / Max Drawdown


@dataclass
class RiskLimits:
    """Risk management limits and thresholds."""
    
    # Core limits
    max_risk_of_ruin: float = 0.01  # 1% max RoR
    max_drawdown_limit: float = 0.20  # 20% max drawdown
    max_bet_percentage: float = 0.10  # 10% of bankroll per bet
    
    # Kelly limits
    max_kelly_multiplier: float = 0.25  # Max 25% of Kelly
    min_kelly_threshold: float = 0.02  # Min 2% edge required
    
    # Consecutive loss limits
    max_consecutive_losses: int = 10
    stop_loss_percentage: float = 0.15  # Stop at 15% loss
    
    # Volatility limits
    max_daily_volatility: float = 0.05  # 5% daily vol limit
    max_period_volatility: float = 0.20  # 20% period vol limit


class RiskAnalyzer:
    """
    Comprehensive risk analysis for betting strategies.
    
    F2.7 Implementation: Analyzes AI betting performance and implements safety controls.
    """
    
    def __init__(self, risk_limits: Optional[RiskLimits] = None):
        """
        Initialize risk analyzer.
        
        Args:
            risk_limits: Risk management limits (uses defaults if None)
        """
        self.risk_limits = risk_limits or RiskLimits()
        self.logger = logging.getLogger(__name__)
        
    def analyze_strategy_performance(
        self, 
        simulation_results: Dict[str, Any],
        detailed_history: Optional[List[Dict]] = None
    ) -> Dict[str, RiskMetrics]:
        """
        Analyze risk metrics for all strategies in simulation results.
        
        Args:
            simulation_results: Results from blackjack simulation
            detailed_history: Optional detailed hand-by-hand history
            
        Returns:
            Dictionary of strategy name -> risk metrics
        """
        analysis_results = {}
        
        for i, player_stats in enumerate(simulation_results['players']):
            strategy_name = f"Player_{i+1}"
            
            # Extract basic metrics
            initial_bankroll = player_stats.get('initial_bankroll', 50000)
            final_bankroll = player_stats.get('current_bankroll', initial_bankroll)
            total_hands = player_stats.get('hands_played', 0)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(
                player_stats, initial_bankroll, final_bankroll, total_hands
            )
            
            # Add strategy-specific analysis
            if 'ai_betting_stats' in player_stats:
                risk_metrics = self._analyze_ai_specific_risks(risk_metrics, player_stats)
            
            analysis_results[strategy_name] = risk_metrics
        
        return analysis_results
    
    def _calculate_risk_metrics(
        self, 
        player_stats: Dict[str, Any], 
        initial_bankroll: float,
        final_bankroll: float,
        total_hands: int
    ) -> RiskMetrics:
        """Calculate comprehensive risk metrics for a strategy."""
        
        # Basic performance
        total_return = final_bankroll - initial_bankroll
        roi = total_return / initial_bankroll if initial_bankroll > 0 else 0.0
        win_rate = player_stats.get('win_rate', 0.0)
        avg_bet = player_stats.get('avg_bet', 0.0)
        
        # Risk calculations
        max_bankroll = player_stats.get('max_bankroll', final_bankroll)
        min_bankroll = player_stats.get('min_bankroll', final_bankroll)
        
        max_drawdown = (initial_bankroll - min_bankroll) / initial_bankroll
        max_runup = (max_bankroll - initial_bankroll) / initial_bankroll
        
        # Risk of Ruin estimation (simplified)
        risk_of_ruin = self._estimate_risk_of_ruin(
            initial_bankroll, avg_bet, win_rate, roi
        )
        
        # Volatility estimation
        volatility = self._estimate_volatility(player_stats, total_hands)
        
        # Sharpe ratio (risk-adjusted return)
        sharpe_ratio = roi / volatility if volatility > 0 else 0.0
        
        # Kelly criterion
        kelly_percentage = self._calculate_kelly_percentage(win_rate, avg_bet, total_return)
        kelly_violation = avg_bet > kelly_percentage * initial_bankroll * self.risk_limits.max_kelly_multiplier
        
        # Advanced risk metrics
        var_95 = -1.645 * volatility * np.sqrt(total_hands) if total_hands > 0 else 0.0
        cvar_95 = var_95 * 1.2  # Approximation
        calmar_ratio = abs(roi / max_drawdown) if max_drawdown > 0 else 0.0
        
        return RiskMetrics(
            total_return=total_return,
            roi=roi,
            win_rate=win_rate,
            avg_bet=avg_bet,
            risk_of_ruin=risk_of_ruin,
            max_drawdown=max_drawdown,
            max_runup=max_runup,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            kelly_percentage=kelly_percentage,
            kelly_violation=kelly_violation,
            var_95=var_95,
            cvar_95=cvar_95,
            calmar_ratio=calmar_ratio
        )
    
    def _analyze_ai_specific_risks(
        self, 
        base_metrics: RiskMetrics, 
        player_stats: Dict[str, Any]
    ) -> RiskMetrics:
        """Add AI-specific risk analysis."""
        
        ai_stats = player_stats['ai_betting_stats']
        
        # Check for AI decision consistency
        ai_ratio = ai_stats.get('ai_decision_ratio', 0.0)
        fallback_ratio = ai_stats.get('fallback_decision_ratio', 0.0)
        
        # Flag high fallback usage as risk
        if fallback_ratio > 0.1:  # More than 10% fallback
            base_metrics.extreme_risk_periods += 1
            self.logger.warning(f"High AI fallback ratio: {fallback_ratio:.1%}")
        
        # Analyze bet size consistency
        recent_avg_bet = ai_stats.get('recent_avg_bet', 0.0)
        if abs(recent_avg_bet - base_metrics.avg_bet) > base_metrics.avg_bet * 0.5:
            base_metrics.bet_size_violations += 1
        
        return base_metrics
    
    def _estimate_risk_of_ruin(
        self, 
        bankroll: float, 
        avg_bet: float, 
        win_rate: float, 
        roi: float
    ) -> float:
        """Estimate risk of ruin using simplified formula."""
        
        if avg_bet <= 0 or bankroll <= 0:
            return 1.0
        
        # Units in bankroll
        units = bankroll / avg_bet
        
        # Win probability and expected value per bet
        p_win = win_rate
        p_lose = 1 - win_rate
        
        # Expected return per unit bet
        expected_return = roi * bankroll / (avg_bet * units) if units > 0 else -1.0
        
        # Simplified RoR formula (assumes even money payouts)
        if expected_return >= 0:
            # Positive expectation
            q_over_p = p_lose / p_win if p_win > 0 else float('inf')
            if q_over_p >= 1:
                return 1.0
            else:
                ror = (q_over_p ** units)
                return min(ror, 1.0)
        else:
            # Negative expectation - eventual ruin
            return 1.0
    
    def _estimate_volatility(self, player_stats: Dict[str, Any], total_hands: int) -> float:
        """Estimate strategy volatility."""
        
        # Use range-based volatility estimation
        max_bankroll = player_stats.get('max_bankroll', 0)
        min_bankroll = player_stats.get('min_bankroll', 0)
        initial_bankroll = player_stats.get('initial_bankroll', 1)
        
        if max_bankroll > min_bankroll and initial_bankroll > 0:
            # Range as percentage of initial bankroll
            range_pct = (max_bankroll - min_bankroll) / initial_bankroll
            
            # Normalize by square root of time (hands)
            volatility = range_pct / np.sqrt(max(total_hands, 1)) * np.sqrt(252)  # Annualized
            return volatility
        
        return 0.1  # Default volatility estimate
    
    def _calculate_kelly_percentage(
        self, 
        win_rate: float, 
        avg_bet: float, 
        total_return: float
    ) -> float:
        """Calculate optimal Kelly percentage."""
        
        if win_rate <= 0.5 or avg_bet <= 0:
            return 0.0
        
        # Simplified Kelly: f = (bp - q) / b
        # where b = odds received, p = win probability, q = lose probability
        
        # Assume even money payouts for simplification
        b = 1.0  # Even money
        p = win_rate
        q = 1 - win_rate
        
        kelly_fraction = (b * p - q) / b
        return max(0.0, kelly_fraction)
    
    def check_risk_violations(self, risk_metrics: RiskMetrics) -> List[str]:
        """Check for risk limit violations."""
        
        violations = []
        
        # Check RoR limit
        if risk_metrics.risk_of_ruin > self.risk_limits.max_risk_of_ruin:
            violations.append(f"Risk of Ruin violation: {risk_metrics.risk_of_ruin:.2%} > {self.risk_limits.max_risk_of_ruin:.2%}")
        
        # Check drawdown limit
        if risk_metrics.max_drawdown > self.risk_limits.max_drawdown_limit:
            violations.append(f"Max Drawdown violation: {risk_metrics.max_drawdown:.2%} > {self.risk_limits.max_drawdown_limit:.2%}")
        
        # Check Kelly violations
        if risk_metrics.kelly_violation:
            violations.append(f"Kelly Criterion violation: Bet size exceeds safe Kelly limit")
        
        # Check consecutive losses
        if risk_metrics.max_consecutive_losses > self.risk_limits.max_consecutive_losses:
            violations.append(f"Consecutive losses: {risk_metrics.max_consecutive_losses} > {self.risk_limits.max_consecutive_losses}")
        
        # Check extreme risk periods
        if risk_metrics.extreme_risk_periods > 0:
            violations.append(f"Extreme risk periods detected: {risk_metrics.extreme_risk_periods}")
        
        return violations
    
    def generate_risk_report(
        self, 
        analysis_results: Dict[str, RiskMetrics],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive risk analysis report."""
        
        report = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "risk_limits": self.risk_limits.__dict__,
            "strategies": {},
            "summary": {}
        }
        
        # Analyze each strategy
        all_violations = []
        strategy_rankings = []
        
        for strategy_name, metrics in analysis_results.items():
            
            # Check violations
            violations = self.check_risk_violations(metrics)
            all_violations.extend(violations)
            
            # Strategy analysis
            strategy_analysis = {
                "metrics": metrics.__dict__,
                "violations": violations,
                "risk_score": self._calculate_risk_score(metrics),
                "recommendation": self._generate_recommendation(metrics, violations)
            }
            
            report["strategies"][strategy_name] = strategy_analysis
            
            # For ranking
            strategy_rankings.append({
                "name": strategy_name,
                "risk_score": strategy_analysis["risk_score"],
                "roi": metrics.roi,
                "sharpe": metrics.sharpe_ratio,
                "max_dd": metrics.max_drawdown,
                "ror": metrics.risk_of_ruin
            })
        
        # Summary analysis
        strategy_rankings.sort(key=lambda x: x["risk_score"])
        
        report["summary"] = {
            "total_violations": len(all_violations),
            "strategies_analyzed": len(analysis_results),
            "best_strategy": strategy_rankings[0]["name"] if strategy_rankings else None,
            "worst_strategy": strategy_rankings[-1]["name"] if strategy_rankings else None,
            "overall_risk_level": self._assess_overall_risk(all_violations, strategy_rankings),
            "recommendations": self._generate_overall_recommendations(strategy_rankings, all_violations)
        }
        
        # Save report if path provided
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Risk analysis report saved to: {output_path}")
        
        return report
    
    def _calculate_risk_score(self, metrics: RiskMetrics) -> float:
        """Calculate overall risk score (0-100, lower is better)."""
        
        score = 0.0
        
        # RoR component (0-40 points)
        ror_score = min(40, metrics.risk_of_ruin * 4000)  # 1% RoR = 40 points
        score += ror_score
        
        # Drawdown component (0-25 points)
        dd_score = min(25, metrics.max_drawdown * 125)  # 20% DD = 25 points
        score += dd_score
        
        # Volatility component (0-20 points)
        vol_score = min(20, metrics.volatility * 100)  # 20% vol = 20 points
        score += vol_score
        
        # Negative ROI penalty (0-15 points)
        if metrics.roi < 0:
            roi_score = min(15, abs(metrics.roi) * 30)  # -50% ROI = 15 points
            score += roi_score
        
        return min(100, score)
    
    def _generate_recommendation(
        self, 
        metrics: RiskMetrics, 
        violations: List[str]
    ) -> str:
        """Generate strategy-specific recommendation."""
        
        if len(violations) == 0 and metrics.roi > 0 and metrics.risk_of_ruin < 0.005:
            return "✅ RECOMMENDED: Good risk-reward profile with acceptable safety margins."
        
        elif len(violations) == 0 and metrics.roi > 0:
            return "⚠️ CAUTION: Positive returns but monitor risk levels closely."
        
        elif metrics.risk_of_ruin > 0.05:
            return "🔴 NOT RECOMMENDED: Unacceptably high risk of ruin."
        
        elif metrics.roi < -0.1:
            return "🔴 NOT RECOMMENDED: Significant negative returns."
        
        elif len(violations) > 2:
            return "🔴 NOT RECOMMENDED: Multiple risk violations detected."
        
        else:
            return "⚠️ NEEDS IMPROVEMENT: Address identified risks before deployment."
    
    def _assess_overall_risk(
        self, 
        violations: List[str], 
        rankings: List[Dict]
    ) -> str:
        """Assess overall portfolio risk level."""
        
        if len(violations) == 0:
            return "LOW"
        elif len(violations) <= 2:
            return "MODERATE"
        elif len(violations) <= 5:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _generate_overall_recommendations(
        self, 
        rankings: List[Dict], 
        violations: List[str]
    ) -> List[str]:
        """Generate overall portfolio recommendations."""
        
        recommendations = []
        
        if len(violations) > 0:
            recommendations.append("🔧 Address all identified risk violations before live deployment")
        
        if rankings:
            best_strategy = rankings[0]
            if best_strategy["ror"] > 0.01:
                recommendations.append("⚠️ Even best strategy exceeds 1% RoR target")
            
            # AI-specific recommendations
            ai_strategies = [r for r in rankings if "AI" in r["name"]]
            if ai_strategies:
                ai_strategy = ai_strategies[0]
                if ai_strategy["risk_score"] > 50:
                    recommendations.append("🤖 AI strategy needs performance optimization")
                if ai_strategy["roi"] < 0:
                    recommendations.append("🤖 AI strategy showing negative returns - requires retraining")
        
        recommendations.append("📊 Implement real-time risk monitoring before live trading")
        recommendations.append("🛡️ Set up automatic stop-loss triggers at 15% drawdown")
        
        return recommendations


def analyze_simulation_results(results_file: str, output_dir: str = "runs/risk_analysis/") -> Dict[str, Any]:
    """
    Convenience function to analyze simulation results file.
    
    Args:
        results_file: Path to simulation results JSON
        output_dir: Directory to save analysis outputs
        
    Returns:
        Risk analysis report
    """
    # Load results
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Analyze risks
    analyzer = RiskAnalyzer()
    analysis = analyzer.analyze_strategy_performance(results)
    
    # Generate report
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"{output_dir}/risk_report_{timestamp}.json"
    
    report = analyzer.generate_risk_report(analysis, report_path)
    
    return report 
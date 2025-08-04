#!/usr/bin/env python3
"""
F2.8: Politika Görselleştirme
Policy Visualization - True Count ↔ Bet Distribution, Sharpe Ratio Analysis
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Dict, Tuple
import os
from datetime import datetime

# Set style for better plots
try:
    plt.style.use('seaborn-v0_8')
except OSError:
    try:
        plt.style.use('seaborn')
    except OSError:
        plt.style.use('default')
sns.set_palette("husl")

class BettingPolicyVisualizer:
    """F2.8: Betting Policy Visualization Dashboard"""
    
    def __init__(self, output_dir: str = "runs/policy_visualization"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def visualize_tc_bet_distribution(self, 
                                    true_counts: List[float], 
                                    bet_sizes: List[float],
                                    strategy_name: str = "AI Strategy") -> str:
        """
        F2.8: True Count ↔ Bet Size Distribution Analysis
        
        Args:
            true_counts: List of true count values
            bet_sizes: List of corresponding bet sizes  
            strategy_name: Name of the betting strategy
            
        Returns:
            Path to saved plot
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'F2.8: Betting Policy Analysis - {strategy_name}', fontsize=16, fontweight='bold')
        
        # 1. Scatter plot: True Count vs Bet Size
        ax1.scatter(true_counts, bet_sizes, alpha=0.6, s=30)
        ax1.set_xlabel('True Count')
        ax1.set_ylabel('Bet Size ($)')
        ax1.set_title('True Count vs Bet Size Distribution')
        ax1.grid(True, alpha=0.3)
        
        # Add trend line
        if len(true_counts) > 1:
            z = np.polyfit(true_counts, bet_sizes, 1)
            p = np.poly1d(z)
            ax1.plot(true_counts, p(true_counts), "r--", alpha=0.8, label=f'Trend: y={z[0]:.2f}x+{z[1]:.2f}')
            ax1.legend()
        
        # 2. Heatmap: TC bins vs Bet bins
        tc_bins = np.linspace(min(true_counts), max(true_counts), 10)
        bet_bins = np.linspace(min(bet_sizes), max(bet_sizes), 8)
        
        tc_digitized = np.digitize(true_counts, tc_bins)
        bet_digitized = np.digitize(bet_sizes, bet_bins)
        
        heatmap_data = np.zeros((len(bet_bins)-1, len(tc_bins)-1))
        for tc_idx, bet_idx in zip(tc_digitized, bet_digitized):
            if 1 <= tc_idx <= len(tc_bins)-1 and 1 <= bet_idx <= len(bet_bins)-1:
                heatmap_data[bet_idx-1, tc_idx-1] += 1
                
        sns.heatmap(heatmap_data, ax=ax2, cmap='YlOrRd', annot=True, fmt='.0f')
        ax2.set_title('Betting Frequency Heatmap')
        ax2.set_xlabel('True Count Bins')
        ax2.set_ylabel('Bet Size Bins')
        
        # 3. Box plot: Bet distribution by TC ranges
        df = pd.DataFrame({'TC': true_counts, 'Bet': bet_sizes})
        df['TC_Range'] = pd.cut(df['TC'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
        
        df.boxplot(column='Bet', by='TC_Range', ax=ax3)
        ax3.set_title('Bet Size Distribution by True Count Range')
        ax3.set_xlabel('True Count Range')
        ax3.set_ylabel('Bet Size ($)')
        
        # 4. Histogram: Bet size frequency
        ax4.hist(bet_sizes, bins=20, alpha=0.7, edgecolor='black')
        ax4.axvline(np.mean(bet_sizes), color='red', linestyle='--', label=f'Mean: ${np.mean(bet_sizes):.2f}')
        ax4.axvline(np.median(bet_sizes), color='green', linestyle='--', label=f'Median: ${np.median(bet_sizes):.2f}')
        ax4.set_xlabel('Bet Size ($)')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Bet Size Distribution')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tc_bet_distribution_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def visualize_sharpe_trend(self, 
                             episodes: List[int],
                             returns: List[float],
                             strategy_name: str = "AI Strategy") -> str:
        """
        F2.8: Sharpe Ratio Trend Analysis
        
        Args:
            episodes: Episode numbers
            returns: Returns per episode
            strategy_name: Strategy name
            
        Returns:
            Path to saved plot
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'F2.8: Sharpe Ratio & Performance Analysis - {strategy_name}', fontsize=16, fontweight='bold')
        
        # Calculate rolling statistics
        window = min(100, len(returns) // 10)  # Rolling window
        if window < 2:
            window = 2
            
        returns_series = pd.Series(returns)
        rolling_mean = returns_series.rolling(window=window).mean()
        rolling_std = returns_series.rolling(window=window).std()
        
        # Calculate Sharpe ratio (assuming risk-free rate = 0)
        sharpe_ratio = rolling_mean / rolling_std
        sharpe_ratio = sharpe_ratio.fillna(0)
        
        # 1. Returns over time
        ax1.plot(episodes, returns, alpha=0.3, color='blue', label='Episode Returns')
        ax1.plot(episodes, rolling_mean.values, color='red', linewidth=2, label=f'Rolling Mean ({window} episodes)')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Return')
        ax1.set_title('Returns Over Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Sharpe ratio over time
        ax2.plot(episodes, sharpe_ratio.values, color='green', linewidth=2, label='Rolling Sharpe Ratio')
        ax2.axhline(y=1.0, color='red', linestyle='--', label='Sharpe = 1.0 (Good)')
        ax2.axhline(y=2.0, color='orange', linestyle='--', label='Sharpe = 2.0 (Excellent)')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Sharpe Ratio')
        ax2.set_title('Sharpe Ratio Trend')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Risk-Return scatter
        episode_chunks = np.array_split(np.arange(len(returns)), 10)
        chunk_returns = []
        chunk_volatility = []
        
        for chunk in episode_chunks:
            if len(chunk) > 1:
                chunk_data = [returns[i] for i in chunk]
                chunk_returns.append(np.mean(chunk_data))
                chunk_volatility.append(np.std(chunk_data))
        
        if chunk_returns and chunk_volatility:
            ax3.scatter(chunk_volatility, chunk_returns, s=100, alpha=0.7)
            ax3.set_xlabel('Risk (Volatility)')
            ax3.set_ylabel('Expected Return')
            ax3.set_title('Risk-Return Profile')
            ax3.grid(True, alpha=0.3)
            
            # Add annotations for each point
            for i, (vol, ret) in enumerate(zip(chunk_volatility, chunk_returns)):
                ax3.annotate(f'P{i+1}', (vol, ret), xytext=(5, 5), textcoords='offset points')
        
        # 4. Performance distribution
        ax4.hist(returns, bins=30, alpha=0.7, edgecolor='black', density=True)
        ax4.axvline(np.mean(returns), color='red', linestyle='--', label=f'Mean: {np.mean(returns):.3f}')
        ax4.axvline(np.median(returns), color='green', linestyle='--', label=f'Median: {np.median(returns):.3f}')
        
        # Add normal distribution overlay
        mu, sigma = np.mean(returns), np.std(returns)
        x = np.linspace(min(returns), max(returns), 100)
        y = ((1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2))
        ax4.plot(x, y, 'k-', linewidth=2, label='Normal Distribution')
        
        ax4.set_xlabel('Return')
        ax4.set_ylabel('Density')
        ax4.set_title('Return Distribution')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sharpe_trend_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_policy_comparison(self, 
                               strategies_data: Dict[str, Dict],
                               title: str = "Betting Strategy Comparison") -> str:
        """
        F2.8: Multi-strategy Comparison Dashboard
        
        Args:
            strategies_data: Dict with strategy names as keys and data dicts as values
                           Each data dict should have: 'true_counts', 'bet_sizes', 'returns'
            title: Plot title
            
        Returns:
            Path to saved plot
        """
        n_strategies = len(strategies_data)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'F2.8: {title}', fontsize=16, fontweight='bold')
        
        colors = plt.cm.tab10(np.linspace(0, 1, n_strategies))
        
        # 1. TC vs Bet Size comparison
        ax1 = axes[0, 0]
        for i, (name, data) in enumerate(strategies_data.items()):
            ax1.scatter(data['true_counts'], data['bet_sizes'], 
                       alpha=0.6, color=colors[i], label=name, s=20)
        ax1.set_xlabel('True Count')
        ax1.set_ylabel('Bet Size ($)')
        ax1.set_title('Strategy Comparison: TC vs Bet Size')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Return comparison box plot
        ax2 = axes[0, 1]
        returns_data = [data['returns'] for data in strategies_data.values()]
        strategy_names = list(strategies_data.keys())
        
        box_plot = ax2.boxplot(returns_data, labels=strategy_names, patch_artist=True)
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax2.set_ylabel('Returns')
        ax2.set_title('Return Distribution Comparison')
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.get_xticklabels(), rotation=45)
        
        # 3. Performance metrics table
        ax3 = axes[1, 0]
        ax3.axis('off')
        
        metrics_data = []
        for name, data in strategies_data.items():
            returns = data['returns']
            bet_sizes = data['bet_sizes']
            
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe = mean_return / std_return if std_return > 0 else 0
            max_drawdown = self._calculate_max_drawdown(returns)
            avg_bet = np.mean(bet_sizes)
            
            metrics_data.append([
                name,
                f"{mean_return:.3f}",
                f"{std_return:.3f}",
                f"{sharpe:.3f}",
                f"{max_drawdown:.3f}",
                f"${avg_bet:.2f}"
            ])
        
        headers = ['Strategy', 'Mean Return', 'Std Return', 'Sharpe', 'Max DD', 'Avg Bet']
        table = ax3.table(cellText=metrics_data, colLabels=headers, 
                         cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        ax3.set_title('Performance Metrics Comparison', pad=20)
        
        # 4. Cumulative returns
        ax4 = axes[1, 1]
        for i, (name, data) in enumerate(strategies_data.items()):
            returns = data['returns']
            cumulative_returns = np.cumsum(returns)
            episodes = range(len(returns))
            ax4.plot(episodes, cumulative_returns, color=colors[i], 
                    linewidth=2, label=name, alpha=0.8)
        
        ax4.set_xlabel('Episode')
        ax4.set_ylabel('Cumulative Return')
        ax4.set_title('Cumulative Returns Comparison')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"policy_comparison_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown from returns series"""
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        return float(np.min(drawdown))
    
    def generate_summary_report(self, 
                              strategies_data: Dict[str, Dict],
                              output_file: str = None) -> str:
        """
        F2.8: Generate comprehensive policy analysis report
        
        Args:
            strategies_data: Strategy comparison data
            output_file: Output file path (optional)
            
        Returns:
            Path to saved report
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"policy_report_{timestamp}.md")
        
        with open(output_file, 'w') as f:
            f.write("# F2.8: Betting Policy Analysis Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Strategy Performance Summary\n\n")
            f.write("| Strategy | Mean Return | Std Return | Sharpe Ratio | Max Drawdown | Avg Bet Size |\n")
            f.write("|----------|-------------|------------|--------------|--------------|---------------|\n")
            
            for name, data in strategies_data.items():
                returns = data['returns']
                bet_sizes = data['bet_sizes']
                
                mean_ret = np.mean(returns)
                std_ret = np.std(returns)
                sharpe = mean_ret / std_ret if std_ret > 0 else 0
                max_dd = self._calculate_max_drawdown(returns)
                avg_bet = np.mean(bet_sizes)
                
                f.write(f"| {name} | {mean_ret:.4f} | {std_ret:.4f} | {sharpe:.4f} | {max_dd:.4f} | ${avg_bet:.2f} |\n")
            
            f.write("\n## Betting Strategy Analysis\n\n")
            for name, data in strategies_data.items():
                tc_data = data['true_counts']
                bet_data = data['bet_sizes']
                
                correlation = np.corrcoef(tc_data, bet_data)[0, 1] if len(tc_data) > 1 else 0
                
                f.write(f"### {name}\n")
                f.write(f"- **TC-Bet Correlation:** {correlation:.4f}\n")
                f.write(f"- **Bet Range:** ${min(bet_data):.2f} - ${max(bet_data):.2f}\n")
                f.write(f"- **Total Episodes:** {len(data['returns'])}\n\n")
            
            f.write("## Recommendations\n\n")
            
            # Find best strategy by Sharpe ratio
            best_strategy = max(strategies_data.keys(), 
                              key=lambda name: np.mean(strategies_data[name]['returns']) / 
                                              (np.std(strategies_data[name]['returns']) + 1e-8))
            
            f.write(f"- **Best Performing Strategy:** {best_strategy} (highest Sharpe ratio)\n")
            f.write(f"- **Risk Management:** Monitor max drawdown levels\n")
            f.write(f"- **Betting Optimization:** Consider TC-bet correlation patterns\n")
            
        return output_file


def demo_f2_8_visualization():
    """F2.8 Demo: Policy Visualization Dashboard"""
    print("🎯 F2.8 POLITIKA GÖRSELLEŞTİRME DEMO")
    
    # Create visualizer
    viz = BettingPolicyVisualizer()
    
    # Generate sample data for different strategies
    np.random.seed(42)
    n_episodes = 1000
    
    # Strategy 1: AI Adaptive (our optimized AI)
    true_counts_ai = np.random.normal(0, 2, n_episodes)
    bet_sizes_ai = 25 + 100 * np.maximum(0, true_counts_ai) + np.random.normal(0, 10, n_episodes)
    bet_sizes_ai = np.clip(bet_sizes_ai, 25, 500)
    returns_ai = np.random.normal(-0.005, 0.1, n_episodes) + 0.01 * true_counts_ai
    
    # Strategy 2: Fixed Betting
    true_counts_fixed = true_counts_ai  # Same TC environment
    bet_sizes_fixed = np.full(n_episodes, 50)  # Fixed $50 bets
    returns_fixed = np.random.normal(-0.01, 0.08, n_episodes)
    
    # Strategy 3: Basic Card Counting
    bet_sizes_basic = 25 + 25 * np.maximum(0, true_counts_ai)
    bet_sizes_basic = np.clip(bet_sizes_basic, 25, 200)
    returns_basic = np.random.normal(-0.008, 0.09, n_episodes) + 0.005 * true_counts_ai
    
    # Create visualizations
    print("   📊 Creating TC-Bet Distribution Analysis...")
    tc_bet_plot = viz.visualize_tc_bet_distribution(
        true_counts_ai, bet_sizes_ai, "Optimized Adaptive AI"
    )
    print(f"   ✅ Saved: {tc_bet_plot}")
    
    print("   📈 Creating Sharpe Ratio Trend Analysis...")
    episodes = list(range(n_episodes))
    sharpe_plot = viz.visualize_sharpe_trend(
        episodes, returns_ai, "Optimized Adaptive AI"
    )
    print(f"   ✅ Saved: {sharpe_plot}")
    
    print("   🔄 Creating Strategy Comparison...")
    strategies_data = {
        "Optimized Adaptive AI": {
            "true_counts": true_counts_ai,
            "bet_sizes": bet_sizes_ai,
            "returns": returns_ai
        },
        "Fixed Betting": {
            "true_counts": true_counts_fixed,
            "bet_sizes": bet_sizes_fixed,
            "returns": returns_fixed
        },
        "Basic Card Counting": {
            "true_counts": true_counts_ai,
            "bet_sizes": bet_sizes_basic,
            "returns": returns_basic
        }
    }
    
    comparison_plot = viz.create_policy_comparison(strategies_data)
    print(f"   ✅ Saved: {comparison_plot}")
    
    print("   📝 Generating Summary Report...")
    report_path = viz.generate_summary_report(strategies_data)
    print(f"   ✅ Saved: {report_path}")
    
    print("\n🎉 F2.8 Politika Görselleştirme Tamamlandı!")
    print(f"📁 Tüm dosyalar: {viz.output_dir}")
    
    return viz.output_dir


if __name__ == "__main__":
    demo_f2_8_visualization() 
#!/usr/bin/env python3
"""
Performance Visualization Module
Creates charts for strategy vs benchmark analysis
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Set style for better-looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_performance_comparison_chart(strategy_data, benchmark_data, title="Strategy vs Benchmark Performance"):
    """
    Create a line chart comparing strategy vs benchmark performance over time
    
    Parameters:
    strategy_data: DataFrame with Date and TotalPortfolio columns
    benchmark_data: DataFrame with Date and TotalPortfolio columns
    title: Chart title
    
    Returns:
    matplotlib Figure object
    """
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot both strategies
    ax.plot(strategy_data['Date'], strategy_data['TotalPortfolio'], 
            label='Your Strategy (10% Dynamic)', linewidth=2, color='#2E8B57')
    ax.plot(benchmark_data['Date'], benchmark_data['TotalPortfolio'], 
            label='SPY Buy & Hold', linewidth=2, color='#4169E1')
    
    # Formatting
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Portfolio Value ($)', fontsize=12)
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Tight layout
    plt.tight_layout()
    
    return fig

def create_portfolio_composition_chart(strategy_data, title="Portfolio Composition Over Time"):
    """
    Create a stacked area chart showing cash vs invested value over time
    
    Parameters:
    strategy_data: DataFrame with Date, CashBalance, and PositionValue columns
    title: Chart title
    
    Returns:
    matplotlib Figure object
    """
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Prepare data for stacked area chart
    dates = strategy_data['Date']
    cash = strategy_data['CashBalance']
    invested = strategy_data['PositionValue']
    
    # Create stacked area chart
    ax.fill_between(dates, 0, cash, label='Cash Balance', alpha=0.7, color='#FFD700')
    ax.fill_between(dates, cash, cash + invested, label='Invested Value', alpha=0.7, color='#32CD32')
    
    # Add total portfolio line
    total_portfolio = strategy_data['TotalPortfolio']
    ax.plot(dates, total_portfolio, label='Total Portfolio', linewidth=2, color='#000000')
    
    # Formatting
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Portfolio Value ($)', fontsize=12)
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Tight layout
    plt.tight_layout()
    
    return fig

def create_rolling_performance_chart(strategy_data, benchmark_data, window=30, title="Rolling 30-Day Performance"):
    """
    Create a chart showing rolling performance comparison
    
    Parameters:
    strategy_data: DataFrame with Date and TotalPortfolio columns
    benchmark_data: DataFrame with benchmark data
    window: Rolling window size in days
    title: Chart title
    
    Returns:
    matplotlib Figure object
    """
    
    # Merge data on date
    merged = pd.merge(strategy_data, benchmark_data, on='Date', suffixes=('_strategy', '_benchmark'))
    
    # Calculate rolling returns
    merged['Strategy_Return'] = merged['TotalPortfolio_strategy'].pct_change()
    merged['Benchmark_Return'] = merged['TotalPortfolio_benchmark'].pct_change()
    
    # Calculate rolling cumulative returns
    merged['Strategy_Rolling'] = merged['Strategy_Return'].rolling(window=window).apply(lambda x: (1 + x).prod() - 1)
    merged['Benchmark_Rolling'] = merged['Benchmark_Return'].rolling(window=window).apply(lambda x: (1 + x).prod() - 1)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot rolling performance
    ax.plot(merged['Date'], merged['Strategy_Rolling'] * 100, 
            label=f'Your Strategy ({window}-day rolling)', linewidth=2, color='#2E8B57')
    ax.plot(merged['Date'], merged['Benchmark_Rolling'] * 100, 
            label=f'SPY Buy & Hold ({window}-day rolling)', linewidth=2, color='#4169E1')
    
    # Add zero line
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Formatting
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel(f'Rolling {window}-Day Return (%)', fontsize=12)
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    
    # Tight layout
    plt.tight_layout()
    
    return fig

def create_performance_metrics_chart(comparison_metrics, title="Performance Metrics Comparison"):
    """
    Create a bar chart comparing key performance metrics
    
    Parameters:
    comparison_metrics: Dictionary with performance metrics
    title: Chart title
    
    Returns:
    matplotlib Figure object
    """
    
    # Extract metrics for comparison
    metrics = ['Total Return', 'Sharpe Ratio', 'Max Drawdown']
    strategy_values = [
        comparison_metrics['strategy_total_return'],
        comparison_metrics['strategy_sharpe'],
        abs(comparison_metrics['strategy_max_drawdown'])  # Make positive for display
    ]
    benchmark_values = [
        comparison_metrics['benchmark_total_return'],
        comparison_metrics['benchmark_sharpe'],
        abs(comparison_metrics['benchmark_max_drawdown'])  # Make positive for display
    ]
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set up bar positions
    x = np.arange(len(metrics))
    width = 0.35
    
    # Create bars
    bars1 = ax.bar(x - width/2, strategy_values, width, label='Your Strategy', color='#2E8B57', alpha=0.8)
    bars2 = ax.bar(x + width/2, benchmark_values, width, label='SPY Buy & Hold', color='#4169E1', alpha=0.8)
    
    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=10)
    
    add_value_labels(bars1)
    add_value_labels(bars2)
    
    # Formatting
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Metrics', fontsize=12)
    ax.set_ylabel('Values', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Tight layout
    plt.tight_layout()
    
    return fig

def create_drawdown_chart(strategy_data, benchmark_data, title="Drawdown Analysis"):
    """
    Create a chart showing drawdowns for both strategies
    
    Parameters:
    strategy_data: DataFrame with Date and TotalPortfolio columns
    benchmark_data: DataFrame with benchmark data
    title: Chart title
    
    Returns:
    matplotlib Figure object
    """
    
    # Merge data on date
    merged = pd.merge(strategy_data, benchmark_data, on='Date', suffixes=('_strategy', '_benchmark'))
    
    # Calculate returns
    merged['Strategy_Return'] = merged['TotalPortfolio_strategy'].pct_change()
    merged['Benchmark_Return'] = merged['TotalPortfolio_benchmark'].pct_change()
    
    # Calculate cumulative returns
    merged['Strategy_CumReturn'] = (1 + merged['Strategy_Return'].fillna(0)).cumprod() - 1
    merged['Benchmark_CumReturn'] = (1 + merged['Benchmark_Return'].fillna(0)).cumprod() - 1
    
    # Calculate drawdowns
    strategy_peak = merged['Strategy_CumReturn'].expanding().max()
    strategy_drawdown = (merged['Strategy_CumReturn'] - strategy_peak) / (1 + strategy_peak) * 100
    
    benchmark_peak = merged['Benchmark_CumReturn'].expanding().max()
    benchmark_drawdown = (merged['Benchmark_CumReturn'] - benchmark_peak) / (1 + benchmark_peak) * 100
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot drawdowns
    ax.fill_between(merged['Date'], strategy_drawdown, 0, 
                   label='Your Strategy Drawdown', alpha=0.7, color='#DC143C')
    ax.fill_between(merged['Date'], benchmark_drawdown, 0, 
                   label='SPY Buy & Hold Drawdown', alpha=0.7, color='#FF6347')
    
    # Add zero line
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    # Formatting
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.legend(fontsize=12, loc='lower left')
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    
    # Tight layout
    plt.tight_layout()
    
    return fig

def save_charts_to_files(strategy_data, benchmark_data, comparison_metrics, output_dir='charts'):
    """
    Create and save all performance charts to files
    
    Parameters:
    strategy_data: DataFrame with strategy daily balances
    benchmark_data: DataFrame with benchmark daily balances
    comparison_metrics: Dictionary with performance metrics
    output_dir: Directory to save chart files
    
    Returns:
    List of saved file paths
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        # 1. Performance Comparison Chart
        fig1 = create_performance_comparison_chart(strategy_data, benchmark_data)
        file1 = os.path.join(output_dir, f'performance_comparison_{timestamp}.png')
        fig1.savefig(file1, dpi=300, bbox_inches='tight')
        saved_files.append(file1)
        plt.close(fig1)
        
        # 2. Portfolio Composition Chart
        fig2 = create_portfolio_composition_chart(strategy_data)
        file2 = os.path.join(output_dir, f'portfolio_composition_{timestamp}.png')
        fig2.savefig(file2, dpi=300, bbox_inches='tight')
        saved_files.append(file2)
        plt.close(fig2)
        
        # 3. Rolling Performance Chart
        fig3 = create_rolling_performance_chart(strategy_data, benchmark_data)
        file3 = os.path.join(output_dir, f'rolling_performance_{timestamp}.png')
        fig3.savefig(file3, dpi=300, bbox_inches='tight')
        saved_files.append(file3)
        plt.close(fig3)
        
        # 4. Performance Metrics Chart
        fig4 = create_performance_metrics_chart(comparison_metrics)
        file4 = os.path.join(output_dir, f'performance_metrics_{timestamp}.png')
        fig4.savefig(file4, dpi=300, bbox_inches='tight')
        saved_files.append(file4)
        plt.close(fig4)
        
        # 5. Drawdown Chart
        fig5 = create_drawdown_chart(strategy_data, benchmark_data)
        file5 = os.path.join(output_dir, f'drawdown_analysis_{timestamp}.png')
        fig5.savefig(file5, dpi=300, bbox_inches='tight')
        saved_files.append(file5)
        plt.close(fig5)
        
        print(f"✅ Saved {len(saved_files)} charts to {output_dir}/")
        for file in saved_files:
            print(f"   📊 {os.path.basename(file)}")
            
    except Exception as e:
        print(f"❌ Error creating charts: {e}")
    
    return saved_files

def display_charts(strategy_data, benchmark_data, comparison_metrics):
    """
    Display all performance charts in a grid layout
    
    Parameters:
    strategy_data: DataFrame with strategy daily balances
    benchmark_data: DataFrame with benchmark daily balances
    comparison_metrics: Dictionary with performance metrics
    """
    
    # Create a 2x3 grid of subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Complete Performance Analysis Dashboard', fontsize=20, fontweight='bold')
    
    # 1. Performance Comparison (top-left)
    ax1 = axes[0, 0]
    ax1.plot(strategy_data['Date'], strategy_data['TotalPortfolio'], 
             label='Your Strategy', linewidth=2, color='#2E8B57')
    ax1.plot(benchmark_data['Date'], benchmark_data['TotalPortfolio'], 
             label='SPY Buy & Hold', linewidth=2, color='#4169E1')
    ax1.set_title('Portfolio Value Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # 2. Portfolio Composition (top-middle)
    ax2 = axes[0, 1]
    ax2.fill_between(strategy_data['Date'], 0, strategy_data['CashBalance'], 
                    label='Cash', alpha=0.7, color='#FFD700')
    ax2.fill_between(strategy_data['Date'], strategy_data['CashBalance'], 
                    strategy_data['CashBalance'] + strategy_data['PositionValue'], 
                    label='Invested', alpha=0.7, color='#32CD32')
    ax2.set_title('Portfolio Composition')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # 3. Performance Metrics (top-right)
    ax3 = axes[0, 2]
    metrics = ['Total Return', 'Sharpe Ratio', 'Max Drawdown']
    strategy_vals = [comparison_metrics['strategy_total_return'], 
                    comparison_metrics['strategy_sharpe'],
                    abs(comparison_metrics['strategy_max_drawdown'])]
    benchmark_vals = [comparison_metrics['benchmark_total_return'], 
                     comparison_metrics['benchmark_sharpe'],
                     abs(comparison_metrics['benchmark_max_drawdown'])]
    
    x = np.arange(len(metrics))
    width = 0.35
    ax3.bar(x - width/2, strategy_vals, width, label='Your Strategy', color='#2E8B57', alpha=0.8)
    ax3.bar(x + width/2, benchmark_vals, width, label='SPY Buy & Hold', color='#4169E1', alpha=0.8)
    ax3.set_title('Key Performance Metrics')
    ax3.set_xticks(x)
    ax3.set_xticklabels(metrics, rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Rolling Performance (bottom-left)
    ax4 = axes[1, 0]
    merged = pd.merge(strategy_data, benchmark_data, on='Date', suffixes=('_strategy', '_benchmark'))
    merged['Strategy_Return'] = merged['TotalPortfolio_strategy'].pct_change()
    merged['Benchmark_Return'] = merged['TotalPortfolio_benchmark'].pct_change()
    merged['Strategy_Rolling'] = merged['Strategy_Return'].rolling(30).apply(lambda x: (1 + x).prod() - 1) * 100
    merged['Benchmark_Rolling'] = merged['Benchmark_Return'].rolling(30).apply(lambda x: (1 + x).prod() - 1) * 100
    
    ax4.plot(merged['Date'], merged['Strategy_Rolling'], label='Your Strategy', linewidth=2, color='#2E8B57')
    ax4.plot(merged['Date'], merged['Benchmark_Rolling'], label='SPY Buy & Hold', linewidth=2, color='#4169E1')
    ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax4.set_title('Rolling 30-Day Performance')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Drawdown Analysis (bottom-middle)
    ax5 = axes[1, 1]
    strategy_peak = merged['Strategy_Return'].cumsum().expanding().max()
    strategy_drawdown = (merged['Strategy_Return'].cumsum() - strategy_peak) * 100
    benchmark_peak = merged['Benchmark_Return'].cumsum().expanding().max()
    benchmark_drawdown = (merged['Benchmark_Return'].cumsum() - benchmark_peak) * 100
    
    ax5.fill_between(merged['Date'], strategy_drawdown, 0, label='Your Strategy', alpha=0.7, color='#DC143C')
    ax5.fill_between(merged['Date'], benchmark_drawdown, 0, label='SPY Buy & Hold', alpha=0.7, color='#FF6347')
    ax5.set_title('Drawdown Analysis')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Performance Summary (bottom-right)
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    # Create text summary
    summary_text = f"""
    PERFORMANCE SUMMARY
    
    Strategy Return: {comparison_metrics['strategy_total_return']:.2f}%
    Benchmark Return: {comparison_metrics['benchmark_total_return']:.2f}%
    Alpha: {comparison_metrics['alpha']:.2f}%
    
    Win Rate: {comparison_metrics['win_rate']:.1f}%
    Outperforming Days: {comparison_metrics['outperforming_days']:.0f}/{comparison_metrics['total_days']:.0f}
    
    Final Values:
    Strategy: ${comparison_metrics['final_strategy_value']:,.0f}
    Benchmark: ${comparison_metrics['final_benchmark_value']:,.0f}
    """
    
    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    # Format all date axes
    for ax in [axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        for label in ax.get_xticklabels():
            label.set_rotation(45)
    
    plt.tight_layout()
    plt.show()
    
    return fig

if __name__ == "__main__":
    print("📊 Performance Visualization Module")
    print("This module provides charting functions for strategy vs benchmark analysis")
    print("\nUsage:")
    print("from visualization import create_performance_comparison_chart")
    print("fig = create_performance_comparison_chart(strategy_data, benchmark_data)")
    print("plt.show()")

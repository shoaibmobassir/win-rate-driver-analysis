"""
Utility functions for visualization and reporting.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def plot_win_rate_trend(df: pd.DataFrame, 
                       segment_col: str,
                       time_col: str = 'created_quarter',
                       save_path: Optional[str] = None):
    """
    Plot win rate trend by segment over time.
    
    Args:
        df: Sales DataFrame
        segment_col: Column to segment by
        time_col: Time column
        save_path: Optional path to save figure
    """
    trend_data = df.groupby([time_col, segment_col]).agg({
        'outcome': lambda x: (x == 'Won').sum() / len(x),
        'deal_id': 'count'
    }).reset_index()
    trend_data.columns = [time_col, segment_col, 'win_rate', 'deal_count']
    
    # Filter segments with sufficient data
    min_deals = 10
    trend_data = trend_data[trend_data['deal_count'] >= min_deals]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    for segment in trend_data[segment_col].unique():
        segment_data = trend_data[trend_data[segment_col] == segment]
        ax.plot(segment_data[time_col].astype(str), 
               segment_data['win_rate'], 
               marker='o', 
               label=segment,
               linewidth=2)
    
    ax.set_xlabel('Time Period', fontsize=12)
    ax.set_ylabel('Win Rate', fontsize=12)
    ax.set_title(f'Win Rate Trend by {segment_col}', fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_driver_importance(drivers: dict, save_path: Optional[str] = None):
    """
    Plot driver importance (coefficients) from decision engine.
    
    Args:
        drivers: Dictionary with 'positive_drivers' and 'negative_drivers'
        save_path: Optional path to save figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Negative drivers
    neg_drivers = drivers['negative_drivers'][:10]
    if neg_drivers:
        neg_features = [d['feature'] for d in neg_drivers]
        neg_coefs = [d['coefficient'] for d in neg_drivers]
        
        ax1.barh(neg_features, neg_coefs, color='#d62728')
        ax1.set_xlabel('Coefficient (Negative Impact)', fontsize=12)
        ax1.set_title('Top Negative Drivers', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
    
    # Positive drivers
    pos_drivers = drivers['positive_drivers'][:10]
    if pos_drivers:
        pos_features = [d['feature'] for d in pos_drivers]
        pos_coefs = [d['coefficient'] for d in pos_drivers]
        
        ax2.barh(pos_features, pos_coefs, color='#2ca02c')
        ax2.set_xlabel('Coefficient (Positive Impact)', fontsize=12)
        ax2.set_title('Top Positive Drivers', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def create_summary_table(df: pd.DataFrame, 
                        groupby_col: str) -> pd.DataFrame:
    """
    Create summary table with key metrics by segment.
    
    Args:
        df: Sales DataFrame
        groupby_col: Column to group by
        
    Returns:
        Summary DataFrame
    """
    from src.metrics import win_rate, revenue_weighted_win_rate, deal_friction_index, median_sales_cycle
    
    summary = df.groupby(groupby_col).agg({
        'deal_id': 'count',
        'deal_amount': ['sum', 'mean'],
        'sales_cycle_days': 'median',
        'outcome': lambda x: (x == 'Won').sum() / len(x)
    })
    
    summary.columns = ['deal_count', 'total_acv', 'avg_acv', 'median_cycle', 'win_rate']
    
    # Add RWWR
    rwwr_dict = {}
    for segment in df[groupby_col].unique():
        segment_data = df[df[groupby_col] == segment]
        rwwr_dict[segment] = revenue_weighted_win_rate(segment_data)
    
    summary['rwwr'] = summary.index.map(rwwr_dict)
    
    # Add DFI
    dfi_dict = {}
    for segment in df[groupby_col].unique():
        segment_data = df[df[groupby_col] == segment]
        dfi = deal_friction_index(segment_data)
        dfi_dict[segment] = dfi if not pd.isna(dfi) else np.nan
    
    summary['dfi'] = summary.index.map(dfi_dict)
    
    return summary.sort_values('total_acv', ascending=False)

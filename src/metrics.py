"""
Custom metrics for sales intelligence analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def revenue_weighted_win_rate(df: pd.DataFrame, 
                              groupby_cols: Optional[list] = None) -> pd.Series:
    """
    Calculate Revenue-Weighted Win Rate (RWWR).
    
    RWWR = Sum(ACV of won deals) / Sum(ACV of all closed deals)
    
    This metric reveals revenue impact, not just deal count impact.
    A flat win rate can hide losing big deals.
    
    Args:
        df: DataFrame with 'deal_amount' and 'outcome' columns
        groupby_cols: Optional list of columns to group by
        
    Returns:
        Series with RWWR values
    """
    if groupby_cols:
        grouped = df.groupby(groupby_cols)
        won_acv = grouped.apply(lambda x: x[x['outcome'] == 'Won']['deal_amount'].sum())
        total_acv = grouped['deal_amount'].sum()
    else:
        won_acv = df[df['outcome'] == 'Won']['deal_amount'].sum()
        total_acv = df['deal_amount'].sum()
    
    rwwr = won_acv / total_acv
    return rwwr


def deal_friction_index(df: pd.DataFrame, 
                       groupby_cols: Optional[list] = None) -> pd.Series:
    """
    Calculate Deal Friction Index (DFI).
    
    DFI = Median days-to-close (lost deals) / Median days-to-close (won deals)
    
    Interpretation:
    - DFI > 1.0: Lost deals take longer than won deals (qualification issues)
    - DFI < 1.0: Lost deals close faster (early disqualification, good)
    - DFI ≈ 1.0: Similar cycle lengths
    
    Args:
        df: DataFrame with 'sales_cycle_days' and 'outcome' columns
        groupby_cols: Optional list of columns to group by
        
    Returns:
        Series with DFI values
    """
    if groupby_cols:
        grouped = df.groupby(groupby_cols)
        
        def calc_dfi(group):
            lost_median = group[group['outcome'] == 'Lost']['sales_cycle_days'].median()
            won_median = group[group['outcome'] == 'Won']['sales_cycle_days'].median()
            
            if pd.isna(won_median) or won_median == 0:
                return np.nan
            if pd.isna(lost_median):
                return np.nan
            
            return lost_median / won_median
        
        dfi = grouped.apply(calc_dfi)
    else:
        lost_median = df[df['outcome'] == 'Lost']['sales_cycle_days'].median()
        won_median = df[df['outcome'] == 'Won']['sales_cycle_days'].median()
        
        if pd.isna(won_median) or won_median == 0:
            return np.nan
        if pd.isna(lost_median):
            return np.nan
        
        dfi = lost_median / won_median
    
    return dfi


def win_rate(df: pd.DataFrame, groupby_cols: Optional[list] = None) -> pd.Series:
    """
    Calculate standard win rate.
    
    Args:
        df: DataFrame with 'outcome' column
        groupby_cols: Optional list of columns to group by
        
    Returns:
        Series with win rate values
    """
    if groupby_cols:
        grouped = df.groupby(groupby_cols)
        wins = grouped['outcome'].apply(lambda x: (x == 'Won').sum())
        total = grouped['outcome'].count()
    else:
        wins = (df['outcome'] == 'Won').sum()
        total = len(df)
    
    return wins / total


def median_sales_cycle(df: pd.DataFrame, 
                      outcome: Optional[str] = None,
                      groupby_cols: Optional[list] = None) -> pd.Series:
    """
    Calculate median sales cycle length.
    
    Args:
        df: DataFrame with 'sales_cycle_days' column
        outcome: Optional filter by 'Won' or 'Lost'
        groupby_cols: Optional list of columns to group by
        
    Returns:
        Series with median cycle lengths
    """
    data = df.copy()
    
    if outcome:
        data = data[data['outcome'] == outcome]
    
    if groupby_cols:
        return data.groupby(groupby_cols)['sales_cycle_days'].median()
    else:
        return data['sales_cycle_days'].median()


def loss_concentration_score(df: pd.DataFrame, 
                            segment_col: str) -> Dict[str, float]:
    """
    Calculate loss concentration score for a segment.
    
    Higher score = losses are more concentrated in this segment.
    
    Args:
        df: DataFrame with sales data
        segment_col: Column name to segment by
        
    Returns:
        Dictionary mapping segment values to concentration scores
    """
    segment_loss_rate = df.groupby(segment_col).apply(
        lambda x: (x['outcome'] == 'Lost').sum() / len(x)
    )
    
    overall_loss_rate = (df['outcome'] == 'Lost').sum() / len(df)
    
    concentration = segment_loss_rate / overall_loss_rate
    
    return concentration.to_dict()


def win_rate_delta_by_segment(df: pd.DataFrame,
                              segment_col: str,
                              time_period_col: str = 'created_quarter',
                              recent_quarters: int = 2,
                              previous_quarters: int = 2) -> pd.Series:
    """
    Calculate Win Rate Delta by Segment (WRΔ).
    
    WRΔ(segment) = Win Rate (Last N Quarters) - Win Rate (Previous N Quarters)
    
    This metric answers "what changed?" - CROs don't ask "what is the win rate",
    they ask "what changed?"
    
    Positive values = improving win rate
    Negative values = declining win rate
    
    Args:
        df: DataFrame with sales data
        segment_col: Column to segment by (e.g., 'acv_bucket', 'industry', 'region')
        time_period_col: Column for time periods (e.g., 'created_quarter')
        recent_quarters: Number of recent quarters to use
        previous_quarters: Number of previous quarters to compare against
        
    Returns:
        Series with WRΔ values indexed by segment
    """
    # Get unique periods sorted
    periods = sorted(df[time_period_col].unique())
    
    if len(periods) < recent_quarters + previous_quarters:
        # Not enough data
        return pd.Series(dtype=float)
    
    # Split into recent and previous periods
    recent_periods = periods[-recent_quarters:]
    previous_periods = periods[-(recent_quarters + previous_quarters):-recent_quarters]
    
    recent_data = df[df[time_period_col].isin(recent_periods)]
    previous_data = df[df[time_period_col].isin(previous_periods)]
    
    # Calculate win rates by segment for each period
    recent_wr = recent_data.groupby(segment_col).apply(
        lambda x: (x['outcome'] == 'Won').sum() / len(x)
    )
    
    previous_wr = previous_data.groupby(segment_col).apply(
        lambda x: (x['outcome'] == 'Won').sum() / len(x)
    )
    
    # Calculate delta
    wr_delta = recent_wr - previous_wr
    
    return wr_delta


def loss_concentration_ratio(df: pd.DataFrame,
                             segment_col: str,
                             top_n: int = 3) -> Dict[str, float]:
    """
    Calculate Loss Concentration Ratio (LCR).
    
    LCR = % of all losses coming from top N segments
    
    Example: "42% of losses come from Enterprise + Paid Leads"
    
    This shows whether the problem is systemic or localized.
    High concentration = fix the few things causing most losses (80/20).
    
    Args:
        df: DataFrame with sales data
        segment_col: Column to segment by
        top_n: Number of top segments to consider
        
    Returns:
        Dictionary with:
        - 'top_segments': List of top N segments by loss count
        - 'concentration_ratio': Percentage of losses from top N segments
        - 'segment_loss_pct': Dict mapping segment to % of total losses
    """
    # Count losses by segment
    losses = df[df['outcome'] == 'Lost']
    total_losses = len(losses)
    
    if total_losses == 0:
        return {
            'top_segments': [],
            'concentration_ratio': 0.0,
            'segment_loss_pct': {}
        }
    
    segment_loss_counts = losses.groupby(segment_col).size()
    segment_loss_counts = segment_loss_counts.sort_values(ascending=False)
    
    top_segments = segment_loss_counts.head(top_n).index.tolist()
    top_loss_count = segment_loss_counts.head(top_n).sum()
    
    concentration_ratio = top_loss_count / total_losses
    
    segment_loss_pct = {
        seg: (count / total_losses) * 100
        for seg, count in segment_loss_counts.items()
    }
    
    return {
        'top_segments': top_segments,
        'concentration_ratio': float(concentration_ratio),
        'segment_loss_pct': segment_loss_pct
    }


def sales_rep_win_rate_variance(df: pd.DataFrame) -> float:
    """
    Calculate Sales Rep Win Rate Variance (SRWV).
    
    SRWV = Standard Deviation of win rates across reps
    
    Interpretation:
    - High variance (> 0.15) = process problem, not just people
    - Low variance (< 0.10) = consistent process, individual coaching needed
    
    This helps decide: coaching vs process fixes
    
    Args:
        df: DataFrame with 'sales_rep_id' and 'outcome' columns
        
    Returns:
        Standard deviation of win rates across reps
    """
    if 'sales_rep_id' not in df.columns:
        return np.nan
    
    rep_win_rates = df.groupby('sales_rep_id').apply(
        lambda x: (x['outcome'] == 'Won').sum() / len(x)
    )
    
    if len(rep_win_rates) < 2:
        return np.nan
    
    variance = rep_win_rates.std()
    return float(variance)

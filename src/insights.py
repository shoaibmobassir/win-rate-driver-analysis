"""
Business insight generation functions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from src.metrics import revenue_weighted_win_rate, deal_friction_index, win_rate


def generate_segment_insight(df: pd.DataFrame, 
                            segment_col: str,
                            time_period_col: str = 'created_quarter') -> Dict:
    """
    Generate insight about win rate decline by segment.
    
    Args:
        df: Sales DataFrame
        segment_col: Column to segment by (e.g., 'acv_bucket', 'industry')
        time_period_col: Column for time periods (e.g., 'created_quarter')
        
    Returns:
        Dictionary with insight details
    """
    # Calculate win rate by segment and time period
    segment_win_rate = df.groupby([time_period_col, segment_col], observed=False).apply(
        lambda x: (x['outcome'] == 'Won').sum() / len(x), include_groups=False
    ).unstack(fill_value=0)
    
    # Calculate RWWR by segment and time period
    segment_rwwr = {}
    for period in df[time_period_col].unique():
        period_data = df[df[time_period_col] == period]
        for segment in df[segment_col].unique():
            segment_data = period_data[period_data[segment_col] == segment]
            if len(segment_data) > 0:
                rwwr = revenue_weighted_win_rate(segment_data)
                segment_rwwr[(period, segment)] = rwwr
    
    # Find segments with declining win rate
    if len(segment_win_rate.columns) > 1 and len(segment_win_rate) > 1:
        recent_periods = segment_win_rate.tail(2)
        earlier_periods = segment_win_rate.head(max(1, len(segment_win_rate) - 2))
        
        if len(earlier_periods) > 0:
            recent_avg = recent_periods.mean()
            earlier_avg = earlier_periods.mean()
            decline = earlier_avg - recent_avg
            
            worst_segment = decline.idxmax()
            worst_decline = decline.max()
            
            return {
                'type': 'segment_decline',
                'segment_column': segment_col,
                'worst_segment': worst_segment,
                'win_rate_decline': float(worst_decline),
                'what': f"Win rate dropped most in {segment_col}='{worst_segment}' segment",
                'why_matters': f"Focusing on this segment could have the biggest impact on overall win rate recovery",
                'action': f"Review pricing, competition, and sales process for {worst_segment} deals. Consider targeted enablement."
            }
    
    return {
        'type': 'segment_decline',
        'message': 'Insufficient data for trend analysis'
    }


def generate_lead_source_insight(df: pd.DataFrame) -> Dict:
    """
    Generate insight about lead source quality impact.
    
    Args:
        df: Sales DataFrame
        
    Returns:
        Dictionary with insight details
    """
    source_metrics = df.groupby('lead_source').agg({
        'outcome': lambda x: (x == 'Won').sum() / len(x),
        'sales_cycle_days': 'median',
        'deal_amount': 'mean',
        'deal_id': 'count'
    }).rename(columns={
        'outcome': 'win_rate',
        'sales_cycle_days': 'median_cycle',
        'deal_amount': 'avg_acv',
        'deal_id': 'deal_count'
    })
    
    # Calculate RWWR by source
    source_rwwr = {}
    for source in df['lead_source'].unique():
        source_data = df[df['lead_source'] == source]
        source_rwwr[source] = revenue_weighted_win_rate(source_data)
    
    source_metrics['rwwr'] = source_metrics.index.map(source_rwwr)
    
    # Find problematic sources
    low_win_rate = source_metrics[source_metrics['win_rate'] < source_metrics['win_rate'].median()]
    long_cycles = source_metrics[source_metrics['median_cycle'] > source_metrics['median_cycle'].median()]
    
    problematic = low_win_rate.index.intersection(long_cycles.index)
    
    if len(problematic) > 0:
        worst_source = problematic[0]
        worst_win_rate = source_metrics.loc[worst_source, 'win_rate']
        worst_cycle = source_metrics.loc[worst_source, 'median_cycle']
        
        return {
            'type': 'lead_source_quality',
            'worst_source': worst_source,
            'win_rate': float(worst_win_rate),
            'median_cycle': float(worst_cycle),
            'what': f"Deals from '{worst_source}' source have lower win rate ({worst_win_rate:.1%}) and longer cycles ({worst_cycle:.0f} days)",
            'why_matters': f"Marketing spend on {worst_source} is inflating pipeline volume without quality. This wastes sales time and resources.",
            'action': f"Rebalance marketing spend toward higher-intent sources. Tighten MQL→SQL qualification criteria for {worst_source} leads."
        }
    
    return {
        'type': 'lead_source_quality',
        'message': 'No significant lead source quality issues detected'
    }


def generate_rep_performance_insight(df: pd.DataFrame) -> Dict:
    """
    Generate insight about rep-level performance patterns.
    
    Args:
        df: Sales DataFrame
        
    Returns:
        Dictionary with insight details
    """
    rep_metrics = df.groupby('sales_rep_id').agg({
        'outcome': lambda x: (x == 'Won').sum() / len(x),
        'sales_cycle_days': 'median',
        'deal_id': 'count'
    }).rename(columns={
        'outcome': 'win_rate',
        'sales_cycle_days': 'median_cycle',
        'deal_id': 'deal_count'
    })
    
    # Calculate DFI by rep
    rep_dfi = {}
    for rep in df['sales_rep_id'].unique():
        rep_data = df[df['sales_rep_id'] == rep]
        dfi = deal_friction_index(rep_data)
        if not pd.isna(dfi):
            rep_dfi[rep] = dfi
    
    rep_metrics['dfi'] = rep_metrics.index.map(rep_dfi)
    
    # Find reps with high volume but high DFI (activity vs effectiveness)
    high_volume = rep_metrics[rep_metrics['deal_count'] >= rep_metrics['deal_count'].median()]
    high_dfi = rep_metrics[rep_metrics['dfi'] > 1.2]  # Lost deals take 20%+ longer
    
    problematic_reps = high_volume.index.intersection(high_dfi.index)
    
    if len(problematic_reps) > 0:
        worst_rep = problematic_reps[0]
        rep_deal_count = rep_metrics.loc[worst_rep, 'deal_count']
        rep_dfi_val = rep_metrics.loc[worst_rep, 'dfi']
        rep_win_rate = rep_metrics.loc[worst_rep, 'win_rate']
        
        return {
            'type': 'rep_performance',
            'rep_id': worst_rep,
            'deal_count': int(rep_deal_count),
            'dfi': float(rep_dfi_val),
            'win_rate': float(rep_win_rate),
            'what': f"Rep {worst_rep} has normal deal volume ({rep_deal_count} deals) but high Deal Friction Index ({rep_dfi_val:.2f})",
            'why_matters': f"Activity looks fine, but effectiveness is not. This rep is spending too much time on deals that won't close, indicating qualification issues.",
            'action': f"Provide coaching to {worst_rep} on deal qualification and exit discipline. Review their qualification criteria and early-stage discovery process."
        }
    
    return {
        'type': 'rep_performance',
        'message': 'No significant rep performance patterns detected'
    }


def format_insight(insight: Dict) -> str:
    """
    Format an insight dictionary into a readable business message.
    
    Args:
        insight: Insight dictionary
        
    Returns:
        Formatted string
    """
    if 'message' in insight:
        return insight['message']
    
    parts = [
        f"**What:** {insight.get('what', 'N/A')}",
        f"**Why it matters:** {insight.get('why_matters', 'N/A')}",
        f"**Recommended action:** {insight.get('action', 'N/A')}"
    ]
    
    return "\n\n".join(parts)

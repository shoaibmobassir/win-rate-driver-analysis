"""
Data loading and validation utilities for SkyGeni sales data.
"""

import pandas as pd
from typing import Tuple, Optional
from pathlib import Path


def load_sales_data(file_path: str) -> pd.DataFrame:
    """
    Load sales data from CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with sales data
    """
    df = pd.read_csv(file_path)
    
    # Convert date columns
    df['created_date'] = pd.to_datetime(df['created_date'])
    df['closed_date'] = pd.to_datetime(df['closed_date'])
    
    # Ensure outcome is categorical
    df['outcome'] = df['outcome'].astype('category')
    
    return df


def validate_data(df: pd.DataFrame) -> Tuple[bool, list]:
    """
    Validate sales data for common issues.
    
    Args:
        df: Sales DataFrame
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check for missing values in critical columns
    critical_cols = ['deal_id', 'created_date', 'closed_date', 'deal_amount', 
                     'outcome', 'sales_cycle_days']
    for col in critical_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            issues.append(f"Missing values in {col}: {df[col].isnull().sum()}")
    
    # Check for invalid outcomes
    valid_outcomes = ['Won', 'Lost']
    if 'outcome' in df.columns:
        invalid = df[~df['outcome'].isin(valid_outcomes)]
        if len(invalid) > 0:
            issues.append(f"Invalid outcome values: {invalid['outcome'].unique()}")
    
    # Check for negative deal amounts
    if 'deal_amount' in df.columns:
        negative = df[df['deal_amount'] < 0]
        if len(negative) > 0:
            issues.append(f"Negative deal amounts: {len(negative)} deals")
    
    # Check for invalid date ranges
    if 'created_date' in df.columns and 'closed_date' in df.columns:
        invalid_dates = df[df['closed_date'] < df['created_date']]
        if len(invalid_dates) > 0:
            issues.append(f"Deals with closed_date before created_date: {len(invalid_dates)}")
    
    # Check for unrealistic sales cycles
    if 'sales_cycle_days' in df.columns:
        negative_cycles = df[df['sales_cycle_days'] < 0]
        if len(negative_cycles) > 0:
            issues.append(f"Negative sales cycle days: {len(negative_cycles)} deals")
        
        very_long_cycles = df[df['sales_cycle_days'] > 365]
        if len(very_long_cycles) > 0:
            issues.append(f"Sales cycles > 365 days: {len(very_long_cycles)} deals")
    
    is_valid = len(issues) == 0
    return is_valid, issues


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived features useful for analysis.
    
    Args:
        df: Sales DataFrame
        
    Returns:
        DataFrame with additional features
    """
    df = df.copy()
    
    # ACV buckets
    df['acv_bucket'] = pd.cut(
        df['deal_amount'],
        bins=[0, 10000, 30000, 50000, float('inf')],
        labels=['SMB (<$10k)', 'Mid-Market ($10k-$30k)', 'Enterprise ($30k-$50k)', 'Large Enterprise (>$50k)']
    )
    
    # Sales cycle buckets
    df['cycle_bucket'] = pd.cut(
        df['sales_cycle_days'],
        bins=[0, 30, 60, 90, float('inf')],
        labels=['Fast (<30d)', 'Medium (30-60d)', 'Slow (60-90d)', 'Very Slow (>90d)']
    )
    
    # Quarter and year
    df['created_quarter'] = df['created_date'].dt.to_period('Q')
    df['created_year'] = df['created_date'].dt.year
    
    # Binary outcome for modeling
    df['is_won'] = (df['outcome'] == 'Won').astype(int)
    
    return df

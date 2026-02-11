"""
Win Rate Driver Analysis Decision Engine.

Identifies which deal attributes drive wins vs losses and how drivers changed over time.
Converts model output into ranked, actionable decisions for sales leadership.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from typing import Dict, List, Tuple, Optional
import warnings
import joblib
import os
from datetime import datetime
warnings.filterwarnings('ignore')

from src.metrics import win_rate_delta_by_segment, revenue_weighted_win_rate


class WinRateDriverAnalyzer:
    """
    Analyzes drivers of win rate using logistic regression.
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.coefficients = None
        self.df_fitted = None  # Store the data used for fitting
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for modeling.
        
        Args:
            df: Sales DataFrame
            
        Returns:
            Tuple of (features_df, target_series)
        """
        features_df = df.copy()
        
        # Categorical features to encode
        categorical_features = ['industry', 'region', 'product_type', 'lead_source', 
                              'deal_stage', 'acv_bucket', 'cycle_bucket']
        
        # Encode categorical features
        for feature in categorical_features:
            if feature in features_df.columns:
                if feature not in self.label_encoders:
                    self.label_encoders[feature] = LabelEncoder()
                    features_df[feature] = self.label_encoders[feature].fit_transform(
                        features_df[feature].astype(str)
                    )
                else:
                    # Handle unseen categories
                    features_df[feature] = features_df[feature].astype(str)
                    known_classes = set(self.label_encoders[feature].classes_)
                    features_df[feature] = features_df[feature].apply(
                        lambda x: x if x in known_classes else 'unknown'
                    )
                    # Add 'unknown' to encoder if needed
                    if 'unknown' not in self.label_encoders[feature].classes_:
                        self.label_encoders[feature].classes_ = np.append(
                            self.label_encoders[feature].classes_, 'unknown'
                        )
                    features_df[feature] = self.label_encoders[feature].transform(
                        features_df[feature]
                    )
        
        # Numerical features
        numerical_features = ['deal_amount', 'sales_cycle_days']
        
        # Select features
        feature_cols = [f for f in categorical_features + numerical_features 
                       if f in features_df.columns]
        
        X = features_df[feature_cols].fillna(0)
        y = features_df['is_won']
        
        self.feature_names = feature_cols
        
        return X, y
    
    def fit(self, df: pd.DataFrame):
        """
        Fit the win rate driver model.
        
        Args:
            df: Sales DataFrame
        """
        self.df_fitted = df.copy()
        X, y = self.prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Fit logistic regression
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.model.fit(X_train_scaled, y_train)
        
        # Store coefficients
        self.coefficients = pd.DataFrame({
            'feature': self.feature_names,
            'coefficient': self.model.coef_[0]
        })
        
        # Store training metadata
        self.training_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.training_samples = len(X_train)
        self.test_samples = len(X_test)
        self.train_accuracy = self.model.score(X_train_scaled, y_train)
        self.test_accuracy = self.model.score(X_test_scaled, y_test)
        
        return self
    
    def save_model(self, filepath: str):
        """
        Save the trained model and all necessary components.
        
        Args:
            filepath: Path to save the model (without extension)
        """
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'coefficients': self.coefficients,
            'training_date': self.training_date,
            'training_samples': self.training_samples,
            'test_samples': self.test_samples,
            'train_accuracy': self.train_accuracy,
            'test_accuracy': self.test_accuracy
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model
        joblib.dump(model_data, filepath)
        print(f"[OK] Model saved to {filepath}")
    
    @classmethod
    def load_model(cls, filepath: str):
        """
        Load a saved model.
        
        Args:
            filepath: Path to the saved model
            
        Returns:
            WinRateDriverAnalyzer instance with loaded model
        """
        model_data = joblib.load(filepath)
        
        analyzer = cls()
        analyzer.model = model_data['model']
        analyzer.scaler = model_data['scaler']
        analyzer.label_encoders = model_data['label_encoders']
        analyzer.feature_names = model_data['feature_names']
        analyzer.coefficients = model_data['coefficients']
        analyzer.training_date = model_data.get('training_date', 'Unknown')
        analyzer.training_samples = model_data.get('training_samples', 0)
        analyzer.test_samples = model_data.get('test_samples', 0)
        analyzer.train_accuracy = model_data.get('train_accuracy', 0)
        analyzer.test_accuracy = model_data.get('test_accuracy', 0)
        
        return analyzer
    
    def calculate_revenue_exposure(self, df: pd.DataFrame, feature_name: str) -> float:
        """
        Calculate revenue exposure for a feature.
        
        Revenue Exposure = % of total pipeline ACV affected by this feature
        
        Args:
            df: Sales DataFrame
            feature_name: Feature name to calculate exposure for
            
        Returns:
            Percentage of total ACV (0-1)
        """
        if feature_name not in df.columns:
            return 0.0
        
        # For categorical features, calculate % of ACV in each category
        if feature_name in ['acv_bucket', 'industry', 'region', 'product_type', 
                           'lead_source', 'deal_stage', 'cycle_bucket']:
            total_acv = df['deal_amount'].sum()
            if total_acv == 0:
                return 0.0
            # Return max exposure across categories (worst case)
            exposure_by_category = df.groupby(feature_name)['deal_amount'].sum() / total_acv
            return float(exposure_by_category.max())
        else:
            # For numerical features, assume all deals are affected
            return 1.0
    
    def calculate_recent_trend(self, df: pd.DataFrame, feature_name: str) -> Dict[str, float]:
        """
        Calculate recent trend for a feature.
        
        Compares win rate in last 2 quarters vs previous 2 quarters.
        
        Args:
            df: Sales DataFrame
            feature_name: Feature name to analyze
            
        Returns:
            Dictionary with 'trend_delta' (change in win rate) and 'direction' ('improving'/'worsening')
        """
        if feature_name not in df.columns or 'created_quarter' not in df.columns:
            return {'trend_delta': 0.0, 'direction': 'stable'}
        
        try:
            wr_delta = win_rate_delta_by_segment(
                df, 
                segment_col=feature_name,
                time_period_col='created_quarter',
                recent_quarters=2,
                previous_quarters=2
            )
            
            if len(wr_delta) == 0:
                return {'trend_delta': 0.0, 'direction': 'stable'}
            
            # Get the worst (most negative) delta for negative drivers
            # or best (most positive) delta for positive drivers
            avg_delta = wr_delta.mean()
            
            if avg_delta < -0.05:  # 5% decline
                direction = 'worsening'
            elif avg_delta > 0.05:  # 5% improvement
                direction = 'improving'
            else:
                direction = 'stable'
            
            return {
                'trend_delta': float(avg_delta),
                'direction': direction
            }
        except Exception:
            return {'trend_delta': 0.0, 'direction': 'stable'}
    
    def calculate_wrds(self, feature_name: str, coefficient: float, 
                      df: Optional[pd.DataFrame] = None) -> float:
        """
        Calculate Win Rate Driver Score (WRDS).
        
        WRDS = Impact Strength × Revenue Exposure × Recent Trend Multiplier
        
        Args:
            feature_name: Feature name
            coefficient: Model coefficient (impact strength)
            df: Optional DataFrame for exposure/trend calculation
            
        Returns:
            WRDS score
        """
        impact_strength = abs(coefficient)
        
        if df is None:
            df = self.df_fitted
        
        if df is None:
            return impact_strength
        
        revenue_exposure = self.calculate_revenue_exposure(df, feature_name)
        trend_info = self.calculate_recent_trend(df, feature_name)
        
        # Trend multiplier: 1.5 if worsening, 1.0 if stable, 0.8 if improving (for negative drivers)
        # For positive drivers, reverse: 1.5 if improving, 1.0 if stable
        if coefficient < 0:  # Negative driver
            if trend_info['direction'] == 'worsening':
                trend_multiplier = 1.5
            elif trend_info['direction'] == 'improving':
                trend_multiplier = 0.8
            else:
                trend_multiplier = 1.0
        else:  # Positive driver
            if trend_info['direction'] == 'improving':
                trend_multiplier = 1.5
            elif trend_info['direction'] == 'worsening':
                trend_multiplier = 0.8
            else:
                trend_multiplier = 1.0
        
        wrds = impact_strength * revenue_exposure * trend_multiplier
        return float(wrds)
    
    def get_action_mapping(self, feature_name: str, coefficient: float) -> Dict[str, List[str]]:
        """
        Map drivers to likely issues and suggested actions.
        
        Args:
            feature_name: Feature name
            coefficient: Model coefficient
            
        Returns:
            Dictionary with 'likely_issues' and 'suggested_actions'
        """
        is_negative = coefficient < 0
        
        # Map feature types to actions
        action_map = {
            'acv_bucket': {
                'likely_issues': [
                    'Pricing objections',
                    'Competitive pressure',
                    'Longer procurement cycles',
                    'Budget constraints'
                ],
                'suggested_actions': [
                    'Exec sponsorship on top 20 deals',
                    'Pricing review and competitive analysis',
                    'Deal desk involvement earlier',
                    'ROI calculator and case studies'
                ]
            },
            'industry': {
                'likely_issues': [
                    'Industry-specific requirements',
                    'Compliance concerns',
                    'Budget cycles',
                    'Competitive landscape'
                ],
                'suggested_actions': [
                    'Industry-specific enablement',
                    'Compliance documentation',
                    'Timing alignment with budget cycles',
                    'Competitive battle cards'
                ]
            },
            'region': {
                'likely_issues': [
                    'Local competition',
                    'Market maturity',
                    'Language/cultural barriers',
                    'Time zone challenges'
                ],
                'suggested_actions': [
                    'Local market analysis',
                    'Regional sales support',
                    'Localized content and demos',
                    'Time zone-aligned coverage'
                ]
            },
            'lead_source': {
                'likely_issues': [
                    'Lead quality',
                    'Intent mismatch',
                    'Timing issues',
                    'Qualification gaps'
                ],
                'suggested_actions': [
                    'Rebalance marketing spend',
                    'Tighten MQL→SQL qualification',
                    'Improve lead scoring',
                    'Better handoff process'
                ]
            },
            'product_type': {
                'likely_issues': [
                    'Product-market fit',
                    'Feature gaps',
                    'Integration complexity',
                    'Support requirements'
                ],
                'suggested_actions': [
                    'Product roadmap alignment',
                    'Integration support',
                    'Technical enablement',
                    'Customer success involvement'
                ]
            },
            'cycle_bucket': {
                'likely_issues': [
                    'Qualification issues',
                    'Chasing bad deals too long',
                    'Pricing friction',
                    'Process inefficiencies'
                ],
                'suggested_actions': [
                    'Improve early-stage disqualification',
                    'Tighten MEDDICC / ICP enforcement',
                    'Pricing transparency',
                    'Streamline approval processes'
                ]
            }
        }
        
        # Find matching feature type
        for feature_type, actions in action_map.items():
            if feature_type in feature_name.lower() or feature_name.lower() in feature_type:
                return actions
        
        # Default actions
        return {
            'likely_issues': [
                'Process inefficiencies',
                'Resource constraints',
                'Competitive pressure'
            ],
            'suggested_actions': [
                'Review sales process',
                'Enablement and training',
                'Competitive analysis'
            ]
        }
    
    def get_drivers(self, top_n: int = 10, include_wrds: bool = True) -> Dict[str, List]:
        """
        Get top positive and negative drivers with WRDS scoring.
        
        Args:
            top_n: Number of top drivers to return
            include_wrds: Whether to calculate WRDS scores
            
        Returns:
            Dictionary with 'positive_drivers' and 'negative_drivers'
        """
        if self.coefficients is None:
            return {'positive_drivers': [], 'negative_drivers': []}
        
        # Calculate WRDS for each feature
        driver_scores = []
        for _, row in self.coefficients.iterrows():
            feature = row['feature']
            coef = row['coefficient']
            
            wrds = self.calculate_wrds(feature, coef) if include_wrds else abs(coef)
            revenue_exposure = self.calculate_revenue_exposure(self.df_fitted, feature) if self.df_fitted is not None else 0.0
            trend_info = self.calculate_recent_trend(self.df_fitted, feature) if self.df_fitted is not None else {'trend_delta': 0.0, 'direction': 'stable'}
            action_mapping = self.get_action_mapping(feature, coef)
            
            driver_scores.append({
                'feature': feature,
                'coefficient': float(coef),
                'wrds': wrds,
                'revenue_exposure': revenue_exposure,
                'trend_delta': trend_info['trend_delta'],
                'trend_direction': trend_info['direction'],
                'action_mapping': action_mapping
            })
        
        # Sort by WRDS (or coefficient if WRDS not included)
        driver_df = pd.DataFrame(driver_scores)
        driver_df = driver_df.sort_values('wrds' if include_wrds else 'coefficient', ascending=False)
        
        # Split positive and negative
        positive_drivers_list = driver_df[driver_df['coefficient'] > 0].head(top_n)
        negative_drivers_list = driver_df[driver_df['coefficient'] < 0].tail(top_n).sort_values('wrds' if include_wrds else 'coefficient', ascending=False)
        
        # Format for business readability
        positive_drivers = []
        for _, row in positive_drivers_list.iterrows():
            positive_drivers.append({
                'feature': row['feature'],
                'coefficient': row['coefficient'],
                'impact': "↑",
                'interpretation': self._interpret_coefficient(row['feature'], row['coefficient']),
                'wrds': row['wrds'],
                'revenue_exposure': row['revenue_exposure'],
                'trend_delta': row['trend_delta'],
                'trend_direction': row['trend_direction'],
                'likely_issues': row['action_mapping']['likely_issues'],
                'suggested_actions': row['action_mapping']['suggested_actions']
            })
        
        negative_drivers = []
        for _, row in negative_drivers_list.iterrows():
            negative_drivers.append({
                'feature': row['feature'],
                'coefficient': row['coefficient'],
                'impact': "↓",
                'interpretation': self._interpret_coefficient(row['feature'], row['coefficient']),
                'wrds': row['wrds'],
                'revenue_exposure': row['revenue_exposure'],
                'trend_delta': row['trend_delta'],
                'trend_direction': row['trend_direction'],
                'likely_issues': row['action_mapping']['likely_issues'],
                'suggested_actions': row['action_mapping']['suggested_actions']
            })
        
        return {
            'positive_drivers': positive_drivers,
            'negative_drivers': negative_drivers
        }
    
    def _interpret_coefficient(self, feature: str, coefficient: float) -> str:
        """
        Interpret coefficient in business terms.
        
        Args:
            feature: Feature name
            coefficient: Coefficient value
            
        Returns:
            Business interpretation string
        """
        direction = "increases" if coefficient > 0 else "decreases"
        magnitude = abs(coefficient)
        
        if magnitude < 0.1:
            strength = "slightly"
        elif magnitude < 0.5:
            strength = "moderately"
        else:
            strength = "strongly"
        
        return f"{strength} {direction} win probability"
    
    def compare_periods(self, df_baseline: pd.DataFrame, 
                       df_recent: pd.DataFrame) -> Dict:
        """
        Compare drivers between baseline and recent periods.
        
        Args:
            df_baseline: Baseline period data
            df_recent: Recent period data
            
        Returns:
            Dictionary with comparison results
        """
        # Fit baseline model
        baseline_analyzer = WinRateDriverAnalyzer()
        baseline_analyzer.fit(df_baseline)
        baseline_drivers = baseline_analyzer.get_drivers()
        
        # Use current analyzer for recent period (already fitted)
        recent_drivers = self.get_drivers()
        
        # Store baseline analyzer for potential saving
        self.baseline_analyzer = baseline_analyzer
        
        # Find drivers that changed
        baseline_features = {d['feature']: d['coefficient'] 
                           for d in baseline_drivers['negative_drivers']}
        recent_features = {d['feature']: d['coefficient'] 
                         for d in recent_drivers['negative_drivers']}
        
        changed_drivers = []
        for feature in set(list(baseline_features.keys()) + list(recent_features.keys())):
            baseline_coef = baseline_features.get(feature, 0)
            recent_coef = recent_features.get(feature, 0)
            
            if abs(baseline_coef - recent_coef) > 0.1:  # Significant change
                changed_drivers.append({
                    'feature': feature,
                    'baseline_coef': baseline_coef,
                    'recent_coef': recent_coef,
                    'change': recent_coef - baseline_coef,
                    'direction': 'worsened' if recent_coef < baseline_coef else 'improved'
                })
        
        return {
            'baseline_drivers': baseline_drivers,
            'recent_drivers': recent_drivers,
            'changed_drivers': changed_drivers
        }


def generate_actionable_outputs(analyzer: WinRateDriverAnalyzer, 
                                period_comparison: Dict = None,
                                df: Optional[pd.DataFrame] = None) -> str:
    """
    Generate business-readable outputs from the decision engine.
    
    This function produces ranked, actionable decisions - not just analysis.
    
    Args:
        analyzer: Fitted WinRateDriverAnalyzer
        period_comparison: Optional period comparison results
        df: Optional DataFrame for revenue calculations
        
    Returns:
        Formatted business report
    """
    drivers = analyzer.get_drivers(include_wrds=True)
    
    if df is None:
        df = analyzer.df_fitted
    
    report = ["# Win Rate Driver Analysis - Decision Engine Output\n"]
    report.append("This system tells leadership what changed, where revenue is leaking, ")
    report.append("and what to focus on this quarter—not just what the win rate is.\n")
    
    report.append("## Top Negative Drivers (Hurting Win Rate)\n")
    report.append("| Driver | Impact | Revenue at Risk | What Changed |")
    report.append("|--------|--------|-----------------|--------------|")
    
    for i, driver in enumerate(drivers['negative_drivers'][:5], 1):
        # Calculate revenue at risk
        if df is not None and driver['feature'] in df.columns:
            feature_data = df[df[driver['feature']].notna()]
            if len(feature_data) > 0:
                total_acv = df['deal_amount'].sum()
                feature_acv = feature_data['deal_amount'].sum()
                revenue_at_risk = feature_acv * abs(driver['coefficient']) * 0.1  # Rough estimate
                revenue_str = f"${revenue_at_risk/1e6:.1f}M"
            else:
                revenue_str = "N/A"
        else:
            revenue_str = "N/A"
        
        trend_str = f"Win rate {driver['trend_delta']:.1%} ({driver['trend_direction']})"
        
        report.append(f"| {driver['feature']} | {driver['impact']} {driver['interpretation']} | {revenue_str} | {trend_str} |")
        
        # Add action details
        report.append("")
        report.append(f"**Likely Issues:**")
        for issue in driver.get('likely_issues', []):
            report.append(f"- {issue}")
        report.append("")
        report.append(f"**Suggested Actions:**")
        for action in driver.get('suggested_actions', []):
            report.append(f"- {action}")
        report.append("")
    
    report.append("## Top Positive Drivers (Improving Win Rate)\n")
    report.append("| Driver | Impact | Revenue Upside |")
    report.append("|--------|--------|----------------|")
    
    for i, driver in enumerate(drivers['positive_drivers'][:5], 1):
        # Calculate revenue upside
        if df is not None and driver['feature'] in df.columns:
            feature_data = df[df[driver['feature']].notna()]
            if len(feature_data) > 0:
                feature_acv = feature_data['deal_amount'].sum()
                revenue_upside = feature_acv * driver['coefficient'] * 0.1  # Rough estimate
                revenue_str = f"${revenue_upside/1e6:.1f}M"
            else:
                revenue_str = "N/A"
        else:
            revenue_str = "N/A"
        
        report.append(f"| {driver['feature']} | {driver['impact']} {driver['interpretation']} | {revenue_str} |")
    
    if period_comparison and period_comparison.get('changed_drivers'):
        report.append("")
        report.append("## Drivers That Changed Over Time\n")
        report.append("| Driver | Direction | Baseline | Recent | Change |")
        report.append("|--------|-----------|----------|--------|--------|")
        
        changed = sorted(period_comparison['changed_drivers'], 
                        key=lambda x: abs(x['change']), reverse=True)
        for driver in changed[:5]:
            report.append(f"| {driver['feature']} | {driver['direction']} | "
                         f"{driver['baseline_coef']:.3f} | {driver['recent_coef']:.3f} | "
                         f"{driver['change']:.3f} |")
    
    report.append("")
    report.append("## How to Use This Analysis\n")
    report.append("1. **Prioritize Pipeline**: Focus sales efforts on deals with positive drivers")
    report.append("2. **Adjust Sales Focus**: Redirect resources away from segments with negative drivers")
    report.append("3. **Align Marketing + Sales**: Improve lead quality for sources with negative drivers")
    report.append("4. **Enablement**: Provide targeted coaching on deals with negative driver patterns")
    report.append("5. **Strategic Planning**: Investigate why certain drivers changed over time")
    
    return "\n".join(report)

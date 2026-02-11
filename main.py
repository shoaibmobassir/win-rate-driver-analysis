#!/usr/bin/env python3
"""
SkyGeni Sales Intelligence - Main Execution Script

Run the complete analysis pipeline with command-line arguments.

This system tells leadership what changed, where revenue is leaking, 
and what to focus on this quarter—not just what the win rate is.
"""

import argparse
import sys
import os
import subprocess
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_sales_data, validate_data, add_derived_features
from src.metrics import (
    revenue_weighted_win_rate, deal_friction_index, win_rate,
    win_rate_delta_by_segment, loss_concentration_ratio, sales_rep_win_rate_variance
)
from src.decision_engine import WinRateDriverAnalyzer, generate_actionable_outputs
from src.insights import (
    generate_segment_insight, generate_lead_source_insight, 
    generate_rep_performance_insight, format_insight
)


def run_notebook(notebook_path, output_dir=None):
    """Execute a Jupyter notebook using nbconvert."""
    print(f"\n{'='*80}")
    print(f"Executing notebook: {notebook_path}")
    print(f"{'='*80}\n")
    
    # Ensure we're in the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    notebook_full_path = os.path.join(project_root, notebook_path)
    
    if not os.path.exists(notebook_full_path):
        print(f"[ERROR] Notebook not found: {notebook_full_path}")
        return False
    
    cmd = [
        'jupyter', 'nbconvert',
        '--to', 'notebook',
        '--execute',
        '--inplace',
        '--ExecutePreprocessor.timeout=600',
        notebook_full_path
    ]
    
    if output_dir:
        cmd.extend(['--output-dir', output_dir])
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        print("[OK] Notebook executed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error executing notebook: {e}")
        if e.stderr:
            print(f"STDERR: {e.stderr[-500:]}")
        print("\nNote: Notebook execution failed. The analysis was still run directly via Python modules.")
        return False
    except FileNotFoundError:
        print("[WARN] jupyter nbconvert not found. Trying alternative method...")
        return run_notebook_with_papermill(notebook_path)


def run_notebook_with_papermill(notebook_path):
    """Execute notebook using papermill as fallback."""
    try:
        import papermill as pm
        output_path = notebook_path.replace('.ipynb', '_executed.ipynb')
        pm.execute_notebook(
            notebook_path,
            output_path,
            parameters={}
        )
        print("[OK] Notebook executed successfully with papermill")
        return True
    except ImportError:
        print("[ERROR] papermill not installed. Install with: pip install papermill")
        return False
    except Exception as e:
        print(f"[ERROR] Error executing notebook with papermill: {e}")
        return False


def run_eda_analysis():
    """Run EDA analysis directly using Python modules."""
    print("\n" + "="*80)
    print("Running EDA Analysis")
    print("="*80 + "\n")
    
    try:
        # Load data
        df = load_sales_data('data/skygeni_sales_data.csv')
        is_valid, issues = validate_data(df)
        
        if not is_valid:
            print("[WARN] Data validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
        
        df = add_derived_features(df)
        
        # Calculate all metrics
        print("Calculating Custom Metrics\n")
        
        overall_wr = win_rate(df)
        overall_rwwr = revenue_weighted_win_rate(df)
        overall_dfi = deal_friction_index(df)
        
        print(f"Overall Win Rate: {overall_wr:.1%}")
        print(f"Revenue-Weighted Win Rate (RWWR): {overall_rwwr:.1%}")
        print(f"  → {'RWWR is LOWER - We are losing bigger deals!' if overall_rwwr < overall_wr else 'RWWR is higher - We are winning bigger deals'}")
        
        print(f"\nDeal Friction Index (DFI): {overall_dfi:.2f}")
        if overall_dfi > 1.2:
            print("  → Lost deals take longer - Qualification issues detected")
        elif overall_dfi < 0.8:
            print("  → Lost deals close faster - Good early disqualification")
        else:
            print("  → Similar cycle lengths for won/lost deals")
        
        # Calculate Win Rate Delta by Segment
        if 'acv_bucket' in df.columns:
            wr_delta_acv = win_rate_delta_by_segment(df, segment_col='acv_bucket')
            if len(wr_delta_acv) > 0:
                print(f"\nWin Rate Delta by ACV Bucket (WRΔ):")
                for segment, delta in wr_delta_acv.items():
                    direction = "↓" if delta < 0 else "↑"
                    print(f"  {segment}: {direction} {abs(delta):.1%}")
        
        # Calculate Loss Concentration Ratio
        if 'acv_bucket' in df.columns:
            lcr = loss_concentration_ratio(df, segment_col='acv_bucket', top_n=3)
            if lcr['concentration_ratio'] > 0:
                print(f"\nLoss Concentration Ratio (LCR):")
                print(f"  Top 3 segments account for {lcr['concentration_ratio']:.1%} of all losses")
                print(f"  Top segments: {', '.join(lcr['top_segments'])}")
        
        # Calculate Sales Rep Win Rate Variance
        if 'sales_rep_id' in df.columns:
            srwv = sales_rep_win_rate_variance(df)
            if not pd.isna(srwv):
                print(f"\nSales Rep Win Rate Variance (SRWV): {srwv:.3f}")
                if srwv > 0.15:
                    print("  → High variance - Process problem, not just people")
                elif srwv < 0.10:
                    print("  → Low variance - Consistent process, individual coaching needed")
                else:
                    print("  → Moderate variance - Mix of process and individual factors")
        
        # Generate insights
        print("\n" + "-"*80)
        print("BUSINESS INSIGHTS")
        print("-"*80)
        
        print("\nINSIGHT #1: Segment Analysis")
        insight1 = generate_segment_insight(df, segment_col='acv_bucket', time_period_col='created_quarter')
        print(format_insight(insight1))
        
        print("\nINSIGHT #2: Lead Source Analysis")
        insight2 = generate_lead_source_insight(df)
        print(format_insight(insight2))
        
        print("\nINSIGHT #3: Rep Performance Analysis")
        insight3 = generate_rep_performance_insight(df)
        print(format_insight(insight3))
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error running EDA analysis: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_decision_engine():
    """Run decision engine analysis with enhanced WRDS scoring."""
    print("\n" + "="*80)
    print("Running Decision Engine Analysis")
    print("="*80 + "\n")
    
    try:
        df = load_sales_data('data/skygeni_sales_data.csv')
        df = add_derived_features(df)
        
        # Split into baseline and recent periods
        baseline_cutoff = df['created_date'].max() - pd.DateOffset(months=6)
        baseline_data = df[df['created_date'] < baseline_cutoff].copy()
        recent_data = df[df['created_date'] >= baseline_cutoff].copy()
        
        print(f"Baseline period: {baseline_data['created_date'].min().date()} to {baseline_data['created_date'].max().date()}")
        baseline_wr = (baseline_data['outcome'] == 'Won').sum() / len(baseline_data)
        print(f"Baseline win rate: {baseline_wr:.1%}")
        
        print(f"\nRecent period: {recent_data['created_date'].min().date()} to {recent_data['created_date'].max().date()}")
        recent_wr = (recent_data['outcome'] == 'Won').sum() / len(recent_data)
        print(f"Recent win rate: {recent_wr:.1%}")
        
        wr_change = recent_wr - baseline_wr
        print(f"\nWin Rate Change: {wr_change:+.1%} {'↓' if wr_change < 0 else '↑'}")
        
        # Fit model
        analyzer = WinRateDriverAnalyzer()
        analyzer.fit(recent_data)
        
        # Get drivers with WRDS scoring
        drivers = analyzer.get_drivers(top_n=10, include_wrds=True)
        
        print("\n" + "-"*80)
        print("TOP NEGATIVE DRIVERS (ranked by WRDS)")
        print("-"*80)
        print(f"{'Rank':<6} {'Driver':<30} {'WRDS':<8} {'Impact':<15} {'Revenue Exposure':<18} {'Trend':<15}")
        print("-" * 100)
        
        for i, driver in enumerate(drivers['negative_drivers'][:5], 1):
            print(f"{i:<6} {driver['feature']:<30} {driver['wrds']:<8.3f} "
                  f"{driver['impact']:<15} {driver['revenue_exposure']:<18.1%} "
                  f"{driver['trend_direction']:<15}")
        
        print("\n" + "-"*80)
        print("TOP POSITIVE DRIVERS (ranked by WRDS)")
        print("-"*80)
        print(f"{'Rank':<6} {'Driver':<30} {'WRDS':<8} {'Impact':<15} {'Revenue Exposure':<18} {'Trend':<15}")
        print("-" * 100)
        
        for i, driver in enumerate(drivers['positive_drivers'][:5], 1):
            print(f"{i:<6} {driver['feature']:<30} {driver['wrds']:<8.3f} "
                  f"{driver['impact']:<15} {driver['revenue_exposure']:<18.1%} "
                  f"{driver['trend_direction']:<15}")
        
        # Show detailed action mapping for top negative driver
        if drivers['negative_drivers']:
            top_driver = drivers['negative_drivers'][0]
            print("\n" + "-"*80)
            print(f"DETAILED ANALYSIS: {top_driver['feature']}")
            print("-"*80)
            print(f"WRDS Score: {top_driver['wrds']:.3f}")
            print(f"Impact: {top_driver['interpretation']}")
            print(f"Revenue Exposure: {top_driver['revenue_exposure']:.1%}")
            print(f"Trend: {top_driver['trend_direction']} ({top_driver['trend_delta']:+.1%})")
            
            print("\nLikely Issues:")
            for issue in top_driver.get('likely_issues', []):
                print(f"  • {issue}")
            
            print("\nSuggested Actions:")
            for action in top_driver.get('suggested_actions', []):
                print(f"  • {action}")
        
        # Compare periods
        period_comparison = analyzer.compare_periods(baseline_data, recent_data)
        
        if period_comparison['changed_drivers']:
            print("\n" + "-"*80)
            print("DRIVERS THAT CHANGED OVER TIME")
            print("-"*80)
            changed = sorted(period_comparison['changed_drivers'], 
                           key=lambda x: abs(x['change']), reverse=True)
            print(f"{'Driver':<30} {'Direction':<12} {'Baseline':<12} {'Recent':<12} {'Change':<12}")
            print("-" * 80)
            for driver in changed[:5]:
                print(f"{driver['feature']:<30} {driver['direction']:<12} "
                      f"{driver['baseline_coef']:<12.3f} {driver['recent_coef']:<12.3f} "
                      f"{driver['change']:<12.3f}")
        
        # Generate report
        report = generate_actionable_outputs(analyzer, period_comparison, df=recent_data)
        
        # Save report
        os.makedirs('outputs/reports', exist_ok=True)
        with open('outputs/reports/win_rate_driver_analysis.txt', 'w') as f:
            f.write(report)
        print("\n[OK] Report saved to outputs/reports/win_rate_driver_analysis.txt")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error running decision engine: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_outputs():
    """Verify that expected output files exist."""
    print("\n" + "="*80)
    print("Checking Outputs")
    print("="*80 + "\n")
    
    expected_files = [
        'outputs/insights/win_rate_trend_by_acv.png',
        'outputs/insights/lead_source_analysis.png',
        'outputs/insights/rep_performance.png',
        'outputs/insights/driver_importance.png',
        'outputs/reports/win_rate_driver_analysis.txt'
    ]
    
    all_exist = True
    for file_path in expected_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"[OK] {file_path} ({size:,} bytes)")
        else:
            print(f"[MISSING] {file_path}")
            all_exist = False
    
    return all_exist


def generate_summary():
    """Generate comprehensive summary report."""
    print("\n" + "="*80)
    print("Generating Summary Report")
    print("="*80 + "\n")
    
    try:
        df = load_sales_data('data/skygeni_sales_data.csv')
        df = add_derived_features(df)
        
        # Calculate key metrics
        overall_wr = win_rate(df)
        overall_rwwr = revenue_weighted_win_rate(df)
        overall_dfi = deal_friction_index(df)
        
        # Calculate additional metrics
        wr_delta_acv = win_rate_delta_by_segment(df, segment_col='acv_bucket') if 'acv_bucket' in df.columns else pd.Series()
        lcr = loss_concentration_ratio(df, segment_col='acv_bucket', top_n=3) if 'acv_bucket' in df.columns else {}
        srwv = sales_rep_win_rate_variance(df) if 'sales_rep_id' in df.columns else None
        
        # Generate insights
        insight1 = generate_segment_insight(df, segment_col='acv_bucket', time_period_col='created_quarter')
        insight2 = generate_lead_source_insight(df)
        insight3 = generate_rep_performance_insight(df)
        
        # Decision engine results
        baseline_cutoff = df['created_date'].max() - pd.DateOffset(months=6)
        recent_data = df[df['created_date'] >= baseline_cutoff].copy()
        
        analyzer = WinRateDriverAnalyzer()
        analyzer.fit(recent_data)
        drivers = analyzer.get_drivers(top_n=5, include_wrds=True)
        
        # Create summary report
        summary = f"""# SkyGeni Sales Intelligence - Analysis Summary

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This analysis identifies drivers of win rate decline and provides actionable recommendations for the CRO.

**In one sentence**: *"This system tells leadership what changed, where revenue is leaking, and what to focus on this quarter—not just what the win rate is."*

## Key Metrics

### Standard Metrics
- **Overall Win Rate**: {overall_wr:.1%}
- **Revenue-Weighted Win Rate (RWWR)**: {overall_rwwr:.1%}
- **Deal Friction Index (DFI)**: {overall_dfi:.2f}

### Custom Metrics (Beyond Standard Win Rate)
"""
        
        if len(wr_delta_acv) > 0:
            worst_segment = wr_delta_acv.idxmin()
            worst_delta = wr_delta_acv.min()
            summary += f"- **Win Rate Delta (WRΔ) - Worst Segment**: {worst_segment} declined by {abs(worst_delta):.1%}\n"
        
        if lcr.get('concentration_ratio', 0) > 0:
            summary += f"- **Loss Concentration Ratio (LCR)**: Top 3 segments account for {lcr['concentration_ratio']:.1%} of losses\n"
        
        if srwv is not None and not pd.isna(srwv):
            summary += f"- **Sales Rep Win Rate Variance (SRWV)**: {srwv:.3f}\n"
        
        summary += f"""
### Metric Interpretation

- **RWWR vs Win Rate**: {'RWWR is LOWER - We are losing bigger deals!' if overall_rwwr < overall_wr else 'RWWR is higher - We are winning bigger deals'}
- **DFI**: {'Lost deals take longer - Qualification issues detected' if overall_dfi > 1.2 else 'Lost deals close faster - Good early disqualification' if overall_dfi < 0.8 else 'Similar cycle lengths for won/lost deals'}
"""
        
        summary += "\n## Top 3 Business Insights\n"
        
        summary += "\n### Insight 1: Segment Decline\n"
        summary += f"{format_insight(insight1) if 'what' in insight1 else insight1.get('message', 'N/A')}\n"
        
        summary += "\n### Insight 2: Lead Source Quality\n"
        summary += f"{format_insight(insight2) if 'what' in insight2 else insight2.get('message', 'N/A')}\n"
        
        summary += "\n### Insight 3: Rep Performance\n"
        summary += f"{format_insight(insight3) if 'what' in insight3 else insight3.get('message', 'N/A')}\n"
        
        summary += "\n## Win Rate Drivers (Ranked by WRDS)\n"
        
        summary += "\n### Top Negative Drivers (Hurting Win Rate)\n"
        for i, driver in enumerate(drivers['negative_drivers'][:5], 1):
            summary += f"\n{i}. **{driver['feature']}**\n"
            summary += f"   - WRDS Score: {driver['wrds']:.3f}\n"
            summary += f"   - Impact: {driver['interpretation']}\n"
            summary += f"   - Revenue Exposure: {driver['revenue_exposure']:.1%}\n"
            summary += f"   - Trend: {driver['trend_direction']} ({driver['trend_delta']:+.1%})\n"
            if driver.get('likely_issues'):
                summary += f"   - Likely Issues: {', '.join(driver['likely_issues'][:2])}\n"
            if driver.get('suggested_actions'):
                summary += f"   - Suggested Actions: {driver['suggested_actions'][0]}\n"
        
        summary += "\n### Top Positive Drivers (Improving Win Rate)\n"
        for i, driver in enumerate(drivers['positive_drivers'][:5], 1):
            summary += f"\n{i}. **{driver['feature']}**\n"
            summary += f"   - WRDS Score: {driver['wrds']:.3f}\n"
            summary += f"   - Impact: {driver['interpretation']}\n"
            summary += f"   - Revenue Exposure: {driver['revenue_exposure']:.1%}\n"
        
        summary += f"""

## Recommended Actions

1. **Pipeline Prioritization**: Focus sales efforts on deals with positive drivers
2. **Resource Allocation**: Redirect resources away from segments with negative drivers
3. **Enablement**: Provide targeted coaching on deals with negative driver patterns
4. **Strategic Planning**: Investigate why certain drivers changed over time
5. **Process Improvement**: Address qualification issues identified by DFI and SRWV metrics

## Output Files Generated

- Visualizations: `outputs/insights/*.png`
- Reports: `outputs/reports/win_rate_driver_analysis.txt`
- This summary: `outputs/summary_report.md`

## Next Steps

1. Review visualizations in `outputs/insights/`
2. Read detailed report in `outputs/reports/`
3. Validate insights with sales leadership
4. Implement recommended actions
5. Monitor results over next quarter

## Methodology Notes

**Why Logistic Regression?**
> "Because the goal is not prediction accuracy. The goal is explainable, trusted decisions for sales leaders."

- Model chosen for interpretability, not accuracy
- Every driver is explainable to a non-technical CRO
- Outputs human-readable insights, not raw probabilities
- Defensible without math-heavy explanations
"""
        
        # Save summary
        os.makedirs('outputs', exist_ok=True)
        with open('outputs/summary_report.md', 'w') as f:
            f.write(summary)
        
        print(summary)
        print("\n[OK] Summary saved to outputs/summary_report.md")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error generating summary: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='SkyGeni Sales Intelligence Analysis Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --all                    # Run complete pipeline
  python main.py --part eda               # Run EDA only
  python main.py --part decision_engine   # Run decision engine only
  python main.py --metrics                # Show all custom metrics
  python main.py --notebooks              # Execute notebooks
  python main.py --check-outputs          # Verify outputs
  python main.py --summary                # Generate summary report
        """
    )
    
    parser.add_argument(
        '--part',
        choices=['eda', 'decision_engine', 'all'],
        help='Which part of analysis to run'
    )
    
    parser.add_argument(
        '--metrics',
        action='store_true',
        help='Calculate and display all custom metrics'
    )
    
    parser.add_argument(
        '--notebooks',
        action='store_true',
        help='Execute Jupyter notebooks programmatically'
    )
    
    parser.add_argument(
        '--check-outputs',
        action='store_true',
        help='Verify that expected output files exist'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Generate comprehensive summary report'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run everything: analysis, notebooks, check outputs, and generate summary'
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n" + "="*80)
        print("Quick Start:")
        print("  python main.py --all    # Run complete pipeline")
        print("  python main.py --metrics # See all custom metrics")
        print("="*80)
        return
    
    # Run everything if --all flag
    if args.all:
        print("="*80)
        print("Running Complete Analysis Pipeline")
        print("="*80)
        
        # Run analyses
        run_eda_analysis()
        run_decision_engine()
        
        # Execute notebooks
        print("\n" + "="*80)
        print("Executing Notebooks")
        print("="*80)
        run_notebook('notebooks/02_eda_insights.ipynb')
        run_notebook('notebooks/03_decision_engine.ipynb')
        
        # Check outputs
        check_outputs()
        
        # Generate summary
        generate_summary()
        
        print("\n" + "="*80)
        print("[OK] Analysis Pipeline Complete!")
        print("="*80)
        return
    
    # Run specific parts
    if args.part:
        if args.part == 'eda' or args.part == 'all':
            run_eda_analysis()
        if args.part == 'decision_engine' or args.part == 'all':
            run_decision_engine()
    
    # Show metrics
    if args.metrics:
        run_eda_analysis()
    
    # Execute notebooks
    if args.notebooks:
        run_notebook('notebooks/02_eda_insights.ipynb')
        run_notebook('notebooks/03_decision_engine.ipynb')
    
    # Check outputs
    if args.check_outputs:
        check_outputs()
    
    # Generate summary
    if args.summary:
        generate_summary()


if __name__ == '__main__':
    main()

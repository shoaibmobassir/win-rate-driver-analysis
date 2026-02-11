# SkyGeni Sales Intelligence - Analysis Summary

Generated: 2026-02-11 17:39:32

## Executive Summary

This analysis identifies drivers of win rate decline and provides actionable recommendations for the CRO.

**In one sentence**: *"This system tells leadership what changed, where revenue is leaking, and what to focus on this quarter—not just what the win rate is."*

## Key Metrics

### Standard Metrics
- **Overall Win Rate**: 45.3%
- **Revenue-Weighted Win Rate (RWWR)**: 46.1%
- **Deal Friction Index (DFI)**: 1.02

### Custom Metrics (Beyond Standard Win Rate)
- **Win Rate Delta (WRΔ) - Worst Segment**: Large Enterprise (>$50k) declined by 2.2%
- **Loss Concentration Ratio (LCR)**: Top 3 segments account for 92.2% of losses
- **Sales Rep Win Rate Variance (SRWV)**: 0.025

### Metric Interpretation

- **RWWR vs Win Rate**: RWWR is higher - We are winning bigger deals
- **DFI**: Similar cycle lengths for won/lost deals

## Top 3 Business Insights

### Insight 1: Segment Decline
**What:** Win rate dropped most in acv_bucket='Enterprise ($30k-$50k)' segment

**Why it matters:** Focusing on this segment could have the biggest impact on overall win rate recovery

**Recommended action:** Review pricing, competition, and sales process for Enterprise ($30k-$50k) deals. Consider targeted enablement.

### Insight 2: Lead Source Quality
**What:** Deals from 'Outbound' source have lower win rate (45.5%) and longer cycles (66 days)

**Why it matters:** Marketing spend on Outbound is inflating pipeline volume without quality. This wastes sales time and resources.

**Recommended action:** Rebalance marketing spend toward higher-intent sources. Tighten MQL→SQL qualification criteria for Outbound leads.

### Insight 3: Rep Performance
**What:** Rep rep_2 has normal deal volume (221 deals) but high Deal Friction Index (1.42)

**Why it matters:** Activity looks fine, but effectiveness is not. This rep is spending too much time on deals that won't close, indicating qualification issues.

**Recommended action:** Provide coaching to rep_2 on deal qualification and exit discipline. Review their qualification criteria and early-stage discovery process.

## Win Rate Drivers (Ranked by WRDS)

### Top Negative Drivers (Hurting Win Rate)

1. **cycle_bucket**
   - WRDS Score: 0.076
   - Impact: moderately decreases win probability
   - Revenue Exposure: 27.5%
   - Trend: stable (+0.0%)
   - Likely Issues: Qualification issues, Chasing bad deals too long
   - Suggested Actions: Improve early-stage disqualification

2. **deal_stage**
   - WRDS Score: 0.016
   - Impact: slightly decreases win probability
   - Revenue Exposure: 22.9%
   - Trend: stable (+0.0%)
   - Likely Issues: Process inefficiencies, Resource constraints
   - Suggested Actions: Review sales process

3. **product_type**
   - WRDS Score: 0.001
   - Impact: slightly decreases win probability
   - Revenue Exposure: 35.1%
   - Trend: stable (+0.0%)
   - Likely Issues: Product-market fit, Feature gaps
   - Suggested Actions: Product roadmap alignment

### Top Positive Drivers (Improving Win Rate)

1. **sales_cycle_days**
   - WRDS Score: 0.260
   - Impact: moderately increases win probability
   - Revenue Exposure: 100.0%

2. **deal_amount**
   - WRDS Score: 0.069
   - Impact: slightly increases win probability
   - Revenue Exposure: 100.0%

3. **acv_bucket**
   - WRDS Score: 0.032
   - Impact: slightly increases win probability
   - Revenue Exposure: 61.5%

4. **lead_source**
   - WRDS Score: 0.017
   - Impact: slightly increases win probability
   - Revenue Exposure: 26.5%

5. **region**
   - WRDS Score: 0.011
   - Impact: slightly increases win probability
   - Revenue Exposure: 27.3%


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

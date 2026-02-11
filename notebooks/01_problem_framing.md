# Part 1: Problem Framing

## What is the Real Business Problem?

The CRO's complaint reveals a deeper issue than just declining win rates. The real problem is **lack of diagnostic clarity** into why deals are being lost despite healthy pipeline volume. This creates three critical business challenges:

1. **Unfocused Sales Efforts**: Without understanding root causes, sales teams can't prioritize effectively
2. **Poor Resource Allocation**: Marketing, enablement, and coaching resources are spread without clear direction
3. **Revenue Leakage**: Healthy pipeline volume masks the fact that revenue is leaking through lower conversion rates

**Key Insight**: Pipeline volume ≠ Revenue. A CRO needs to understand not just that win rate dropped, but where, why, and what actions will reverse the trend.

## Key Questions an AI System Should Answer for the CRO

An effective sales intelligence system must answer decision-oriented questions:

1. **Where has win rate dropped?**
   - By segment (Enterprise vs SMB vs Mid-Market)?
   - By region (North America vs APAC vs Europe)?
   - By product type (Enterprise vs Core vs Pro)?
   - By sales rep or team?

2. **Why are deals being lost more often?**
   - Are sales cycles lengthening?
   - Are certain industries or lead sources underperforming?
   - Has deal quality changed?
   - Are we chasing the wrong deals?

3. **What changed compared to previous periods?**
   - Which factors that used to drive wins are now driving losses?
   - Has competitive landscape shifted?
   - Are there new patterns in lost deals?

4. **What should we do next week/quarter to fix it?**
   - Which deals need immediate attention?
   - Where should we redirect sales focus?
   - What enablement or process changes are needed?

## Metrics That Matter Most for Diagnosing Win Rate Issues

Beyond simple win rate, we need metrics that reveal revenue impact and sales behavior:

1. **Revenue-Weighted Win Rate (RWWR)**
   - Formula: `Sum(ACV of won deals) / Sum(ACV of all closed deals)`
   - Why: A flat win rate can hide losing big deals. CROs care about revenue, not deal counts.

2. **Win Rate by Segment Over Time**
   - Track win rate trends by ACV bucket, industry, region
   - Why: Identifies where the problem is concentrated

3. **Deal Velocity (Time-to-Close)**
   - Median days-to-close for won vs lost deals
   - Why: Lengthening cycles often indicate qualification or process issues

4. **Deal Friction Index (DFI)**
   - Formula: `Median days-to-close (lost deals) / Median days-to-close (won deals)`
   - Why: If lost deals take longer, reps are chasing dead deals. Indicates qualification problems.

5. **Loss Concentration**
   - Are losses clustered in specific segments, reps, or sources?
   - Why: Helps prioritize where to focus improvement efforts

6. **Pipeline Quality vs Quantity**
   - Win rate by lead source, deal stage progression rates
   - Why: Healthy pipeline volume can mask quality issues

## Assumptions We're Making

Explicitly stating assumptions shows maturity and helps identify limitations:

1. **Data Quality Assumptions**
   - Deal stages are consistently logged across reps and time
   - Outcome labels (Won/Lost) are accurate and final
   - Deal amounts (ACV) reflect actual contract values
   - Dates are accurate and reflect real deal progression

2. **Business Context Assumptions**
   - Sales motion hasn't fundamentally changed (pricing, ICP, product features)
   - Competitive landscape is relatively stable
   - No major external shocks (pandemic, market crash) affecting all deals uniformly
   - Sales team composition and territories are relatively stable

3. **Temporal Assumptions**
   - Data spans enough time to compare trends (at least 2+ quarters)
   - Seasonal patterns are either minimal or can be accounted for
   - Recent trends are predictive of near-term future

4. **Causal Assumptions**
   - Deal attributes (industry, region, source) are meaningful predictors
   - Historical patterns remain relevant for future decisions
   - Correlation patterns reflect actionable business drivers (not just noise)

## What This Means for the Solution

Our solution must:
- **Segment analysis** to identify where problems are concentrated
- **Time-based comparisons** to understand what changed
- **Revenue-weighted metrics** to prioritize by business impact
- **Interpretable outputs** that connect data patterns to actions
- **Honest limitations** about what we can and cannot determine from data alone

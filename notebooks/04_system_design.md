# Part 4: Mini System Design

## Sales Insight & Alert System Architecture

This document designs a lightweight Sales Insight & Alert System that SkyGeni could productize to help CROs monitor win rate and take action.

## High-Level Architecture

```
┌─────────────┐
│   CRM Data  │ (Salesforce, HubSpot, etc.)
│   Sources   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         ETL Pipeline                │
│  - Data extraction                  │
│  - Validation & cleaning            │
│  - Feature engineering              │
│  - Load to feature store            │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│      Feature Store                  │
│  - Deal attributes                  │
│  - Historical metrics               │
│  - Time-series data                 │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    Insight Engine                   │
│  - Win rate calculations            │
│  - Custom metrics (RWWR, DFI)       │
│  - Driver analysis                  │
│  - Trend detection                  │
└──────┬──────────────────────────────┘
       │
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Alerts     │   │ Dashboards  │   │  Reports    │
│  (Real-time)│   │ (Interactive)│   │ (Scheduled) │
└─────────────┘   └─────────────┘   └─────────────┘
```

## Data Flow

### 1. Data Ingestion (Daily)
- **Source**: CRM APIs (Salesforce, HubSpot, etc.)
- **Frequency**: Daily sync at 2 AM
- **Process**:
  - Extract new/updated deals since last sync
  - Validate data quality (missing fields, invalid values)
  - Transform to standard schema
  - Load into feature store

### 2. Feature Engineering (Daily)
- **Input**: Raw deal data
- **Output**: Enriched features
- **Features Created**:
  - ACV buckets
  - Sales cycle buckets
  - Time-based features (quarter, month)
  - Derived metrics (days since creation, stage progression)

### 3. Insight Generation (Daily/Weekly/Monthly)

#### Daily (Pipeline Metrics)
- Current pipeline health
- Deal stage progression rates
- High-risk deal identification
- **Run Time**: 6 AM (after data sync)

#### Weekly (Trend Analysis)
- Win rate trends by segment
- Lead source performance
- Rep performance patterns
- **Run Time**: Monday 8 AM

#### Monthly (Strategic Insights)
- Win rate driver analysis
- Period-over-period comparisons
- Strategic recommendations
- **Run Time**: First Monday of month, 9 AM

### 4. Alert Generation (Real-time)
- **Trigger**: Significant metric changes detected
- **Examples**:
  - Win rate drops >5% in any segment
  - DFI increases >20% for any rep
  - Pipeline quality score drops below threshold

## Example Alerts

### Alert 1: Enterprise Win Rate Drop
```
🚨 ALERT: Enterprise Win Rate Decline
─────────────────────────────────────
Segment: Enterprise (>$50k ACV)
Win Rate: 42% (down from 58% last quarter)
Impact: $2.3M revenue at risk
Action: Review pricing and competitive positioning
```

### Alert 2: Lead Source Quality Issue
```
⚠️  WARNING: Lead Source Performance
─────────────────────────────────────
Source: Paid Ads
Win Rate: 28% (below threshold of 35%)
Sales Cycle: 95 days (20% longer than average)
Impact: Wasting sales time on low-quality leads
Action: Tighten MQL→SQL qualification criteria
```

### Alert 3: High-Risk Deals
```
🔍 INSIGHT: High-Risk Deals Identified
─────────────────────────────────────
10 deals showing loss-risk patterns:
- Enterprise deals >90 days in cycle
- Outbound source + Low engagement
Total ACV at risk: $450k
Action: Review these deals in next pipeline review
```

## Run Frequency Summary

| Component | Frequency | Time | Purpose |
|-----------|-----------|------|---------|
| Data Sync | Daily | 2 AM | Get latest deal data |
| Pipeline Metrics | Daily | 6 AM | Monitor current pipeline health |
| Trend Analysis | Weekly | Monday 8 AM | Track win rate trends |
| Strategic Analysis | Monthly | 1st Monday 9 AM | Deep dive insights |
| Alerts | Real-time | On-demand | Immediate notifications |

## Failure Cases & Limitations

### 1. Data Quality Issues
**Problem**: Missing or inconsistent CRM data
- **Impact**: Incorrect metrics, false alerts
- **Mitigation**: 
  - Data validation layer with quality scores
  - Alert on data quality degradation
  - Fallback to last known good state

### 2. Small Sample Sizes
**Problem**: Insufficient deals in a segment for reliable metrics
- **Impact**: Noisy or misleading insights
- **Mitigation**:
  - Minimum sample size thresholds (e.g., 10 deals)
  - Confidence intervals on metrics
  - Aggregate to higher levels when needed

### 3. Correlation vs Causation
**Problem**: Model identifies associations, not causes
- **Impact**: Wrong actions taken
- **Mitigation**:
  - Label insights as "associations" not "causes"
  - Require qualitative validation with sales leaders
  - Track intervention outcomes

### 4. Seasonality & External Factors
**Problem**: Win rate changes due to market conditions, not sales issues
- **Impact**: False alarms, wasted effort
- **Mitigation**:
  - Compare to year-over-year baselines
  - Include external indicators (market data)
  - Contextualize alerts with market conditions

### 5. Model Drift
**Problem**: Drivers change over time, model becomes stale
- **Impact**: Decreasing accuracy
- **Mitigation**:
  - Retrain models quarterly
  - Monitor prediction accuracy
  - A/B test model updates

### 6. CRM Integration Failures
**Problem**: API downtime or rate limits
- **Impact**: Missing data, delayed insights
- **Mitigation**:
  - Retry logic with exponential backoff
  - Cache last successful sync
  - Alert on sync failures

## Technical Considerations

### Scalability
- **Current**: Handles ~5,000 deals
- **Future**: Design for 100k+ deals with partitioning
- **Approach**: Batch processing with Spark/Dask for large datasets

### Performance
- **Target**: <5 minutes for daily pipeline metrics
- **Optimization**: 
  - Incremental processing (only new/updated deals)
  - Cached aggregations
  - Parallel processing by segment

### Reliability
- **Uptime Target**: 99.5%
- **Monitoring**: 
  - Health checks on all components
  - Alert on processing failures
  - Automatic retries with circuit breakers

### Security & Privacy
- **Data**: Encrypted at rest and in transit
- **Access**: Role-based access control (CRO, Sales Ops, Reps)
- **Compliance**: GDPR, SOC 2 considerations

## Productization Roadmap

### Phase 1: MVP (Current)
- Daily pipeline metrics
- Weekly trend reports
- Basic alerts

### Phase 2: Enhanced Insights
- Predictive deal risk scoring
- Rep coaching recommendations
- Automated action suggestions

### Phase 3: Advanced Features
- Natural language insights ("Win rate dropped because...")
- Integration with sales tools (Slack, email)
- Custom alert rules per customer

## Success Metrics

- **Adoption**: % of customers using alerts weekly
- **Action Rate**: % of alerts that lead to actions
- **Impact**: Win rate improvement after using insights
- **Satisfaction**: NPS score from CROs

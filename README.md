# SkyGeni – Sales Intelligence Challenge

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run complete analysis pipeline
python main.py --all

# Or run specific parts:
python main.py --part eda              # EDA analysis only
python main.py --part decision_engine  # Decision engine only
python main.py --metrics               # Show all custom metrics
python main.py --summary               # Generate summary report
```

**Output**: Reports saved to `outputs/reports/`, visualizations to `outputs/insights/`

## Overview

This repository contains a complete sales intelligence solution designed to help CROs understand why win rates are declining and what actions to take. The solution focuses on **business clarity and actionable insights** over complex ML models.

**Problem**: A B2B SaaS company's win rate has dropped over the last two quarters, but pipeline volume looks healthy. The CRO needs to understand what's going wrong and what to focus on.

**Solution**: A data-driven insight system that identifies win rate drivers, custom metrics, and actionable recommendations.

**In one sentence**: *"This system tells leadership what changed, where revenue is leaking, and what to focus on this quarter—not just what the win rate is."*

## Project Structure

```
SkyGeni1234/
├── README.md                          # This file
├── main.py                            # Main execution script (run with --all)
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
├── .cursorrules                       # Development rules for SkyGeni assignment
├── data/
│   └── skygeni_sales_data.csv         # Sales dataset
├── notebooks/
│   ├── 01_problem_framing.md          # Part 1: Problem Framing
│   ├── 02_eda_insights.ipynb          # Part 2: EDA & Insights
│   ├── 03_decision_engine.ipynb       # Part 3: Win Rate Driver Analysis
│   └── 04_system_design.md            # Part 4: System Design
├── src/
│   ├── __init__.py
│   ├── data_loader.py                 # Data loading and validation
│   ├── metrics.py                     # Custom metrics (RWWR, DFI, WRΔ, LCR, SRWV)
│   ├── insights.py                    # Business insight generators
│   ├── decision_engine.py            # Win rate driver analysis with WRDS
│   └── utils.py                      # Visualization utilities
├── outputs/
│   ├── insights/                     # Generated visualizations
│   ├── models/                        # Saved models
│   └── reports/                       # Business reports
└── reflection.md                      # Part 5: Reflection
```

## Key Components

### Part 1: Problem Framing
**File**: `notebooks/01_problem_framing.md`

Frames the business problem, identifies key questions, defines important metrics, and states assumptions.

**Key Questions Answered**:
- What is the real business problem?
- What questions should an AI system answer?
- What metrics matter most?
- What assumptions are we making?

### Part 2: Data Exploration & Insights
**File**: `notebooks/02_eda_insights.ipynb`

Performs exploratory data analysis and generates business insights.

**Custom Metrics**:
1. **Revenue-Weighted Win Rate (RWWR)**: `Sum(ACV won) / Sum(ACV all closed)`
   - Reveals revenue impact, not just deal count impact
   - A flat win rate can hide losing big deals
   - **Why it's powerful**: CROs care about revenue leakage, not deal count

2. **Deal Friction Index (DFI)**: `Median days-to-close (lost) / Median days-to-close (won)`
   - Identifies qualification issues
   - DFI > 1.2 indicates reps are chasing dead deals too long
   - **Action**: Improve early-stage disqualification, tighten MEDDICC/ICP enforcement

3. **Win Rate Delta by Segment (WRΔ)**: `Win Rate (Last 2Q) - Win Rate (Previous 2Q)`
   - Answers "what changed?" - CROs don't ask "what is the win rate", they ask "what changed?"
   - Shows where decline is localized (industry, region, product)
   - **Action**: Targeted fixes instead of blanket panic

4. **Loss Concentration Ratio (LCR)**: `% of all losses from top N segments`
   - Example: "42% of losses come from Enterprise + Paid Leads"
   - Shows whether problem is systemic or localized
   - **Action**: Fix the few things causing most losses (80/20 principle)

5. **Sales Rep Win Rate Variance (SRWV)**: `Std Dev of win rates across reps`
   - High variance (>0.15) = process problem, not just people
   - Low variance (<0.10) = consistent process, individual coaching needed
   - **Action**: Helps decide coaching vs process fixes

**Business Insights**:
1. Win rate decline by segment (Enterprise vs SMB)
2. Lead source quality impact on win rate
3. Rep-level performance patterns (volume vs effectiveness)

### Part 3: Decision Engine (Win Rate Driver Analysis)
**File**: `notebooks/03_decision_engine.ipynb`

Builds an interpretable model to identify which deal attributes drive wins vs losses and converts them into ranked, actionable decisions.

**Model**: Logistic Regression (chosen for interpretability and explainability)

**Why Logistic Regression?**
> "Because the goal is not prediction accuracy. The goal is explainable, trusted decisions for sales leaders."

**Win Rate Driver Score (WRDS)**:
The decision engine calculates WRDS for each driver:
```
WRDS = Impact Strength × Revenue Exposure × Recent Trend Multiplier
```

Where:
- **Impact Strength**: Coefficient magnitude from logistic regression
- **Revenue Exposure**: % of total pipeline ACV affected by this driver
- **Recent Trend**: Whether the driver is worsening or improving (multiplier)

**Enhanced Outputs**:
- **Top Negative Drivers** (ranked by WRDS):
  - Driver name
  - Impact strength
  - Revenue at risk
  - What changed (trend delta)
  - Likely issues
  - Suggested actions

- **Top Positive Drivers** (ranked by WRDS):
  - Driver name
  - Impact strength
  - Revenue upside
  - Trend direction

- **Period-over-period comparisons**: Shows which drivers changed over time

- **Action Mapping**: Each driver includes:
  - Likely issues (e.g., "Pricing objections", "Competitive pressure")
  - Suggested actions (e.g., "Exec sponsorship on top 20 deals", "Pricing review")

**Example Output**:
```
🔻 Top Negative Drivers
Driver: Enterprise ACV > $50k
Impact: ↓ High
Revenue at Risk: $3.2M
What Changed: Win rate -18% QoQ
Likely Issues:
- Pricing objections
- Competitive pressure
- Longer procurement cycles
Suggested Actions:
- Exec sponsorship on top 20 deals
- Pricing review
- Deal desk involvement earlier
```

**In one sentence**: *"This system tells leadership what changed, where revenue is leaking, and what to focus on this quarter—not just what the win rate is."*

### Part 4: System Design
**File**: `notebooks/04_system_design.md`

Designs a lightweight Sales Insight & Alert System for productization.

**Components**:
- Data flow architecture
- Alert examples
- Run frequency (daily/weekly/monthly)
- Failure cases and limitations

### Part 5: Reflection
**File**: `reflection.md`

Honest assessment of assumptions, limitations, and future directions.

**Topics**:
- Weakest assumptions
- What would break in production
- What to build next (1 month roadmap)
- Least confident areas

## How to Run

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd SkyGeni1234
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Ensure data file exists**:
   - Place `skygeni_sales_data.csv` in the `data/` directory
   - The dataset should have columns: `deal_id`, `created_date`, `closed_date`, `deal_stage`, `deal_amount`, `sales_rep_id`, `industry`, `region`, `product_type`, `lead_source`, `outcome`, `sales_cycle_days`

### Running the Analysis

#### Option 1: Run Complete Pipeline (Recommended)

Use the `main.py` script to run the entire analysis pipeline:

```bash
# Run everything (EDA + Decision Engine + Notebooks + Summary)
python main.py --all

# Or run specific parts:
python main.py --part eda              # EDA analysis only
python main.py --part decision_engine  # Decision engine only
python main.py --metrics               # Show all custom metrics
python main.py --summary               # Generate summary report
python main.py --check-outputs         # Verify output files
```

**What `--all` does:**
1. Runs EDA analysis with all custom metrics
2. Runs decision engine with WRDS scoring
3. Executes Jupyter notebooks
4. Checks output files
5. Generates comprehensive summary report

**Quick Start:**
```bash
python main.py --all
```

#### Option 2: Run Jupyter Notebooks

1. **Start Jupyter**:
```bash
jupyter notebook
```

2. **Run notebooks in order**:
   - `notebooks/02_eda_insights.ipynb` - EDA and insights
   - `notebooks/03_decision_engine.ipynb` - Win rate driver analysis

3. **View outputs**:
   - Visualizations saved to `outputs/insights/`
   - Reports saved to `outputs/reports/`

#### Option 3: Run Python Scripts Directly

```bash
# From project root - Quick metric check
python -c "from src.data_loader import load_sales_data, add_derived_features; from src.metrics import revenue_weighted_win_rate; df = load_sales_data('data/skygeni_sales_data.csv'); df = add_derived_features(df); print(f'RWWR: {revenue_weighted_win_rate(df):.1%}')"
```

### Expected Outputs

After running `python main.py --all` or the notebooks, you should see:

1. **Console Output**:
   - All 5 custom metrics (RWWR, DFI, WRΔ, LCR, SRWV)
   - Business insights with recommendations
   - Top negative/positive drivers ranked by WRDS
   - Revenue exposure and trend analysis
   - Action mappings for each driver

2. **Visualizations** (`outputs/insights/`):
   - `win_rate_trend_by_acv.png` - Win rate trends by ACV bucket
   - `lead_source_analysis.png` - Lead source performance
   - `rep_performance.png` - Rep volume vs effectiveness
   - `driver_importance.png` - Win rate driver coefficients

3. **Reports** (`outputs/reports/`):
   - `win_rate_driver_analysis.txt` - Actionable business report with:
     - Top negative drivers with revenue at risk
     - Top positive drivers with revenue upside
     - Likely issues and suggested actions for each driver
     - Period-over-period comparisons
   - `summary_report.md` - Executive summary with all key findings

4. **Saved Models** (`outputs/models/`):
   - `recent_period_model.joblib` - Trained model for recent period
   - `baseline_period_model.joblib` - Trained model for baseline period
   - Models include: trained logistic regression, scalers, encoders, metadata

### Example Console Output

When you run `python main.py --all`, you'll see:

```
📊 Calculating Custom Metrics

Overall Win Rate: 45.3%
Revenue-Weighted Win Rate (RWWR): 46.1%
  → RWWR is higher - We are winning bigger deals

Deal Friction Index (DFI): 1.02
  → Similar cycle lengths for won/lost deals

Win Rate Delta by ACV Bucket (WRΔ):
  SMB (<$10k): ↓ 1.3%
  Mid-Market ($10k-$30k): ↑ 4.2%
  Enterprise ($30k-$50k): ↓ 0.9%
  Large Enterprise (>$50k): ↓ 2.2%

Loss Concentration Ratio (LCR):
  Top 3 segments account for 92.2% of all losses
  Top segments: SMB (<$10k), Mid-Market ($10k-$30k), Large Enterprise (>$50k)

Sales Rep Win Rate Variance (SRWV): 0.025
  → Low variance - Consistent process, individual coaching needed

🔻 TOP NEGATIVE DRIVERS (ranked by WRDS)
Rank   Driver                         WRDS     Impact          Revenue Exposure   Trend          
----------------------------------------------------------------------------------------------------
1      cycle_bucket                   0.076    ↓               27.5%              stable         
2      deal_stage                     0.016    ↓               22.9%              stable         
3      product_type                   0.001    ↓               35.1%              stable         

🔺 TOP POSITIVE DRIVERS (ranked by WRDS)
Rank   Driver                         WRDS     Impact          Revenue Exposure   Trend          
----------------------------------------------------------------------------------------------------
1      sales_cycle_days               0.260    ↑               100.0%             stable         
2      deal_amount                    0.069    ↑               100.0%             stable         
3      acv_bucket                     0.032    ↑               61.5%              stable         
...
```

## Key Decisions & Rationale

### 1. Why Logistic Regression?

**Decision**: Use logistic regression instead of complex ML models (XGBoost, neural networks).

**Rationale**:
- **Interpretability**: Coefficients directly show feature impact on win probability
- **Speed**: Fast to train and iterate
- **Business-First**: CROs need to understand WHY, not just predictions
- **Sufficient**: For this problem, interpretability > accuracy

### 2. Why Custom Metrics?

**Decision**: Invent Revenue-Weighted Win Rate (RWWR) and Deal Friction Index (DFI).

**Rationale**:
- **RWWR**: Standard win rate hides revenue impact. Losing one $100k deal hurts more than losing ten $5k deals.
- **DFI**: Identifies qualification issues. If lost deals take longer, reps are wasting time on dead deals.

### 3. Why Option B (Win Rate Driver Analysis)?

**Decision**: Choose Win Rate Driver Analysis over Risk Scoring, Forecast, or Anomaly Detection.

**Rationale**:
- **Directly addresses CRO complaint**: "Why did win rate drop?"
- **Actionable**: Identifies what to focus on
- **Interpretable**: Easy to explain to non-technical stakeholders
- **Natural fit**: Complements EDA insights

### 4. Why Simple System Design?

**Decision**: Design lightweight system, not enterprise-scale architecture.

**Rationale**:
- **MVP mindset**: Start simple, iterate based on feedback
- **Practical**: Most customers don't need complex infrastructure
- **Fast to build**: Can ship in weeks, not months
- **Easier to maintain**: Less moving parts = fewer failure modes

## Business Value

### For CROs

1. **Diagnostic Clarity**: Understand WHERE and WHY win rate dropped
2. **Prioritization**: Know which deals/segments to focus on
3. **Actionable Insights**: Each finding includes recommended actions
4. **Time Savings**: Automated analysis vs manual spreadsheet work

### Example Use Cases

1. **Pipeline Prioritization**: "Focus on Referral and Partner deals in Mid-Market ACV range"
2. **Resource Allocation**: "Reduce investment in Outbound Enterprise leads"
3. **Enablement**: "Train reps on Enterprise deal qualification"
4. **Strategic Planning**: "Enterprise deals became negative drivers - investigate pricing"

## Limitations & Assumptions

### Key Limitations

1. **Correlation ≠ Causation**: Model shows associations, not proven causes
2. **Data Quality**: Assumes CRM data is accurate and complete
3. **Sample Sizes**: Some segments may have insufficient data for reliable metrics
4. **Temporal Stability**: Assumes historical patterns remain relevant

### Assumptions

1. Deal stages are consistently logged
2. Outcome labels (Won/Lost) are accurate
3. Sales motion hasn't fundamentally changed
4. Data spans enough time for trend analysis

See `reflection.md` for detailed discussion of limitations and how to address them.

## Evaluation Criteria Alignment

| Criterion | Weight | How Addressed |
|-----------|--------|---------------|
| Problem framing & business thinking | 25% | Part 1: Clear problem framing, business-first approach |
| Insight quality & metric design | 20% | Part 2: Custom metrics (RWWR, DFI), 3+ business insights |
| Decision engine quality | 20% | Part 3: Interpretable model, actionable outputs |
| Engineering & code quality | 15% | Clean code structure, reusable modules, documentation |
| Out-of-box thinking | 10% | Custom metrics, business-first approach, honest reflection |
| Communication & clarity | 10% | Plain business language, clear explanations, visualizations |

## Next Steps

If given 1 month to extend this solution:

1. **Week 1-2**: Enhanced features (deal risk scoring, rep coaching insights)
2. **Week 3**: Integration & automation (CRM sync, alert system)
3. **Week 4**: Validation & refinement (A/B testing, user feedback)

See `reflection.md` for detailed roadmap.

## What's Included

### Enhanced Metrics (Beyond Standard Win Rate)

1. **Revenue-Weighted Win Rate (RWWR)** - Reveals revenue impact, not just deal count
2. **Deal Friction Index (DFI)** - Identifies qualification issues
3. **Win Rate Delta by Segment (WRΔ)** - Shows what changed over time
4. **Loss Concentration Ratio (LCR)** - Identifies 80/20 problem areas
5. **Sales Rep Win Rate Variance (SRWV)** - Distinguishes process vs people problems

### Enhanced Decision Engine

- **Win Rate Driver Score (WRDS)**: Ranks drivers by impact, revenue exposure, and recent trends
- **Revenue Exposure**: Calculates % of pipeline ACV affected by each driver
- **Recent Trend Analysis**: Identifies worsening vs improving drivers
- **Action Mapping**: Maps each driver to likely issues and suggested actions
- **Ranked Outputs**: Top negative/positive drivers with business context

### Main Execution Script (`main.py`)

Run the complete pipeline with a single command:
```bash
python main.py --all
```

Features:
- Calculates all 5 custom metrics
- Runs decision engine with WRDS scoring
- Generates actionable reports
- Executes notebooks programmatically
- Creates comprehensive summary

### Development Rules (`.cursorrules`)

Guidelines for maintaining business-first approach:
- Optimize for clarity over complexity
- Every insight must drive action
- Explainable models over black boxes
- Plain business language

## Contact & Questions

For questions about this solution:
- Review the notebooks for detailed analysis
- Check `reflection.md` for limitations and assumptions
- See `notebooks/04_system_design.md` for architecture details
- Run `python main.py --help` for usage instructions

## License

This project is part of a take-home assignment for SkyGeni.

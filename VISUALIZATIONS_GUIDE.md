# Visualizations and Analysis Guide

## Where Are the Visualizations?

### Saved Image Files

All visualizations are saved to: **`outputs/insights/`**

1. **`win_rate_trend_by_acv.png`** (179 KB)
   - Shows win rate trends over time by ACV bucket
   - Generated in: `notebooks/02_eda_insights.ipynb` (Cell 8)

2. **`lead_source_analysis.png`** (115 KB)
   - Shows win rate and sales cycle by lead source
   - Generated in: `notebooks/02_eda_insights.ipynb` (Cell 14)

3. **`rep_performance.png`** (243 KB)
   - Shows rep performance: volume vs effectiveness (DFI)
   - Generated in: `notebooks/02_eda_insights.ipynb` (Cell 17)

4. **`driver_importance.png`** (135 KB)
   - Shows win rate driver coefficients from logistic regression
   - Generated in: `notebooks/03_decision_engine.ipynb` (Cell 9)

### How to View Visualizations

#### Option 1: View Saved Images Directly

```bash
# View images in outputs/insights/
open outputs/insights/win_rate_trend_by_acv.png
open outputs/insights/lead_source_analysis.png
open outputs/insights/rep_performance.png
open outputs/insights/driver_importance.png
```

#### Option 2: Open Notebooks in Jupyter

When you open the notebooks in Jupyter, the visualizations will display inline:

1. **Start Jupyter**:
```bash
jupyter notebook
```

2. **Open notebooks**:
   - `notebooks/02_eda_insights.ipynb`
   - `notebooks/03_decision_engine.ipynb`

3. **Run all cells** - visualizations will appear inline after each plotting cell

#### Option 3: View in Generated Reports

The visualizations are referenced in:
- `outputs/reports/win_rate_driver_analysis.txt`
- `outputs/summary_report.md`

## Notebook Structure

### `02_eda_insights.ipynb`

**Visualization Cells:**

1. **Cell 8**: Win Rate Trend by ACV Bucket
   - Code: `plot_win_rate_trend(df, segment_col='acv_bucket', time_col='created_quarter')`
   - Saves to: `outputs/insights/win_rate_trend_by_acv.png`
   - Shows: Win rate trends over quarters by segment

2. **Cell 14**: Lead Source Analysis
   - Code: Creates bar charts for win rate and sales cycle by source
   - Saves to: `outputs/insights/lead_source_analysis.png`
   - Shows: Lead source performance comparison

3. **Cell 17**: Rep Performance Analysis
   - Code: Creates scatter plot of deal count vs DFI
   - Saves to: `outputs/insights/rep_performance.png`
   - Shows: Rep volume vs effectiveness

### `03_decision_engine.ipynb`

**Visualization Cells:**

1. **Cell 9**: Driver Importance
   - Code: `plot_driver_importance(drivers)`
   - Saves to: `outputs/insights/driver_importance.png`
   - Shows: Logistic regression coefficients for win rate drivers

## Analysis Outputs

### Console Output

When you run `python main.py --all`, you'll see:

- All 5 custom metrics (RWWR, DFI, WRΔ, LCR, SRWV)
- Business insights with recommendations
- Top negative/positive drivers ranked by WRDS
- Revenue exposure and trend analysis

### Reports

- **`outputs/reports/win_rate_driver_analysis.txt`**: Detailed driver analysis with actions
- **`outputs/summary_report.md`**: Executive summary with all findings

### Data Tables

The notebooks also display:
- Detailed metrics by segment (ACV bucket, lead source, rep)
- Period-over-period comparisons
- Win rate deltas and trends

## Quick Access

```bash
# View all visualizations
ls -lh outputs/insights/*.png

# Open a specific visualization
open outputs/insights/win_rate_trend_by_acv.png

# View reports
cat outputs/reports/win_rate_driver_analysis.txt
cat outputs/summary_report.md
```

## Note on Notebook Display

The notebooks are configured to:
1. **Save images** to `outputs/insights/` (for reports and sharing)
2. **Display inline** when opened in Jupyter (using `plt.show()`)

If images don't display inline in Jupyter:
- Make sure you're running cells in order
- Check that `%matplotlib inline` is executed
- Images are always saved to `outputs/insights/` regardless

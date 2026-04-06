---
name: cuXfilter
description: Generate GPU-accelerated cross-filtering dashboards using cuDF. Use when the user asks for a cross-filtering dashboard, interactive filter on a large dataset, linked charts, or a GPU dashboard. Also triggered by /cuXfilter.
triggers:
  - cross-filtering dashboard
  - interactive filter on my dataset
  - linked charts on my data
  - GPU dashboard
  - /cuXfilter
---

# cuXfilter — GPU-Accelerated Cross-Filtering Dashboards

Generate complete, runnable cross-filtering dashboard code for large datasets using cuDF as the GPU data layer.

## Step 1: Detect Existing cuxfilter Code

Scan the user's files and conversation for `import cuxfilter` or `cux_df`.

**If found:** Load `references/migration.md`. Tell the user:
> "The cuxfilter library has been sunset. I'll help you migrate this to a modern equivalent that doesn't require the cuxfilter package."
Then proceed through the steps below, using the migration reference to map their existing charts to the new library.

**If not found:** Proceed fresh. Do not mention cuxfilter.

## Step 2: Gather Requirements

Infer from context first. Ask only what you cannot determine:

1. **Data source** — What cuDF DataFrame or file will be used? (Parquet, Arrow, CSV)
2. **Viz library** — Check for existing imports (`import panel`, `import dash`, `import streamlit`). If none found, ask:
   > "Which visualization library do you have installed — Panel/HoloViews, Plotly Dash, or Streamlit?"
3. **Output format** — Is this for a Jupyter notebook or a standalone `.py` script?

## Step 3: Generate the Dashboard

Load the appropriate reference file before generating:
- Panel/HoloViews → `references/panel-holoviews.md`
- Plotly Dash → `references/plotly-dash.md`
- Streamlit → `references/streamlit.md`

Produce a complete, runnable file containing:
- cuDF data loading (required — no pandas fallback at the data layer)
- At least two linked charts with cross-filtering wired up
- A sensible default layout
- Comments on the three most commonly customized sections:
  ```
  # CHART TYPES: swap chart types here (e.g. hv.Points → hv.Bars)
  # FILTER COLUMNS: change the column names used for filtering here
  # LAYOUT: rearrange or add rows/columns here
  ```

## Step 4: Offer Next Steps

After delivering the generated file, suggest:
- Add more chart types
- Connect to a live or streaming data source
- Deploy to a server (`panel serve app.py`, `gunicorn app:server`, `streamlit run app.py`)

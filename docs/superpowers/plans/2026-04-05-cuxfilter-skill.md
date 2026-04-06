# cuXfilter Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a portable AI agent skill that generates GPU-accelerated cross-filtering dashboards using cuDF, replacing the sunset cuxfilter Python library.

**Architecture:** A lean main skill file (`cuXfilter.md`) encodes process and judgment; four reference files ground the agent in library-specific GPU patterns. The main skill is the only required install — reference files are loaded on demand. No code templates are embedded in the skill; the agent's native code generation handles all output.

**Tech Stack:** Markdown skill files (platform-agnostic); cuDF as GPU data layer; Panel/HoloViews/DataShader, Plotly Dash, and Streamlit as supported viz libraries.

---

## File Map

| Action | Path | Purpose |
|--------|------|---------|
| Create | `skill/skills/cuXfilter.md` | Main skill — triggers, process, judgment |
| Create | `skill/references/panel-holoviews.md` | GPU patterns for Panel + DataShader |
| Create | `skill/references/plotly-dash.md` | GPU patterns for Plotly Dash |
| Create | `skill/references/streamlit.md` | GPU patterns for Streamlit |
| Create | `skill/references/migration.md` | cuxfilter → modern equivalents mapping |
| Create | `skill/README.md` | Installation and usage instructions |

---

## Task 1: Scaffold directory structure

**Files:**
- Create: `skill/skills/` (directory)
- Create: `skill/references/` (directory)

- [ ] **Step 1: Create directories**

```bash
mkdir -p skill/skills skill/references
```

Expected: no output, directories exist.

- [ ] **Step 2: Verify**

```bash
ls skill/
```

Expected output:
```
references/
skills/
```

- [ ] **Step 3: Commit**

```bash
git add skill/
git commit -m "chore: scaffold cuXfilter skill directory structure"
```

---

## Task 2: Write the main skill file `cuXfilter.md`

**Files:**
- Create: `skill/skills/cuXfilter.md`

- [ ] **Step 1: Write the file**

Create `skill/skills/cuXfilter.md` with this exact content:

```markdown
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
```

- [ ] **Step 2: Verify the file exists and has the required sections**

```bash
grep -c "Step [1-4]" skill/skills/cuXfilter.md
```

Expected output: `4`

- [ ] **Step 3: Commit**

```bash
git add skill/skills/cuXfilter.md
git commit -m "feat: add cuXfilter main skill file"
```

---

## Task 3: Write `panel-holoviews.md` reference

**Files:**
- Create: `skill/references/panel-holoviews.md`

- [ ] **Step 1: Write the file**

Create `skill/references/panel-holoviews.md` with this exact content:

```markdown
# Panel + HoloViews/DataShader Reference

**When to use:** Best for 10M+ rows — DataShader renders server-side so only pixel data crosses the network.

## Key Imports and Setup

```python
import cudf
import numpy as np
import holoviews as hv
import holoviews.operation.datashader as hd
import datashader as ds
import panel as pn

hv.extension('bokeh')
pn.extension()
```

## Cross-Filtering Pattern

Panel uses `hv.streams.BoundsXY` to pass the user's selection box to dependent plots. The key principle: filter in cuDF, convert to pandas only at the moment of rendering non-DataShader elements.

```python
# Load data — stay in cuDF as long as possible
gdf = cudf.read_parquet("data.parquet")

# DataShader renders cuDF directly — do not convert before datashade()
points = hv.Points(gdf, kdims=['x', 'y'])
shaded = hd.datashade(points)

# BoundsXY stream carries the user's drag-select box coordinates
selection = hv.streams.BoundsXY(source=points, bounds=(0, 0, 0, 0))

@pn.depends(selection.param.bounds)
def filtered_hist(bounds):
    x0, y0, x1, y1 = bounds
    if x0 == x1 == y0 == y1 == 0:
        filtered = gdf
    else:
        filtered = gdf[
            (gdf['x'] >= x0) & (gdf['x'] <= x1) &
            (gdf['y'] >= y0) & (gdf['y'] <= y1)
        ]
    # Convert to pandas only at render time, on the filtered slice
    counts, edges = np.histogram(filtered['value'].to_pandas(), bins=30)
    return hv.Histogram((edges, counts)).opts(width=400, height=300)

# LAYOUT: rearrange or add elements here
layout = pn.Row(shaded, filtered_hist)
layout.servable()
```

## Known GPU Gotchas

- `hd.datashade()` and `hd.rasterize()` accept cuDF DataFrames directly — **do not** call `.to_pandas()` before passing to these functions. Converting defeats the purpose.
- Most other HoloViews elements (`hv.Histogram`, `hv.Bars`, `hv.Curve`) require pandas/numpy. Always filter in cuDF first, then call `.to_pandas()` on the smaller result.
- `cudf.DataFrame` does not support `.plot()` — route all rendering through HoloViews or hvplot.
- For hvplot on cuDF, use `import hvplot.cudf` (requires hvplot >= 0.9). For hvplot on pandas, use `import hvplot.pandas`.
- `BoundsXY` initial value `(0, 0, 0, 0)` means "no selection" — always check for this and return the full dataset.
```

- [ ] **Step 2: Verify the four required sections are present**

```bash
grep -E "^## (When to use|Key Imports|Cross-Filtering Pattern|Known GPU Gotchas)" skill/references/panel-holoviews.md
```

Expected output (4 lines):
```
## When to use:
## Key Imports and Setup
## Cross-Filtering Pattern
## Known GPU Gotchas
```

- [ ] **Step 3: Commit**

```bash
git add skill/references/panel-holoviews.md
git commit -m "feat: add Panel+HoloViews GPU reference for cuXfilter skill"
```

---

## Task 4: Write `plotly-dash.md` reference

**Files:**
- Create: `skill/references/plotly-dash.md`

- [ ] **Step 1: Write the file**

Create `skill/references/plotly-dash.md` with this exact content:

```markdown
# Plotly Dash + cuDF Reference

**When to use:** Best when users need rich interactive chart types (3D, maps, financial) or are deploying a multi-user web app.

## Key Imports and Setup

```python
import cudf
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

app = Dash(__name__)
```

## Cross-Filtering Pattern

Dash uses `@app.callback` decorators. Each chart's `selectedData` property is an `Input` to other charts. The cuDF DataFrame lives at module level; filtering happens in the callback; `.to_pandas()` happens last, on the filtered result.

```python
# Load at module level — callbacks run in the server process, not the browser
gdf = cudf.read_parquet("data.parquet")

# LAYOUT: rearrange or add dcc.Graph elements here
app.layout = html.Div([
    dcc.Graph(id='scatter', style={'width': '50%', 'display': 'inline-block'}),
    dcc.Graph(id='histogram', style={'width': '50%', 'display': 'inline-block'}),
])

@app.callback(
    Output('histogram', 'figure'),
    Input('scatter', 'selectedData')
)
def update_histogram(selected):
    if selected and selected.get('points'):
        # FILTER COLUMNS: change 'x' and 'y' to your column names
        indices = [p['pointIndex'] for p in selected['points']]
        # Boolean mask is faster than iloc for large cuDF DataFrames
        mask = cudf.Series(False, index=range(len(gdf)))
        mask.iloc[indices] = True
        filtered = gdf[mask]
    else:
        filtered = gdf
    # CHART TYPES: swap px.histogram for another chart type here
    return px.histogram(filtered.to_pandas(), x='value', nbins=30)

@app.callback(
    Output('scatter', 'figure'),
    Input('histogram', 'selectedData')
)
def update_scatter(selected):
    if selected and selected.get('points'):
        # Extract bin range from histogram selection
        x0 = selected['points'][0].get('x', None)
        x1 = selected['points'][-1].get('x', None)
        if x0 is not None and x1 is not None:
            filtered = gdf[(gdf['value'] >= x0) & (gdf['value'] <= x1)]
        else:
            filtered = gdf
    else:
        filtered = gdf
    return px.scatter(filtered.to_pandas(), x='x', y='y')

if __name__ == '__main__':
    app.run(debug=True)
```

## Known GPU Gotchas

- Plotly accepts pandas DataFrames only — always call `.to_pandas()` before passing to `px.*`. Filter in cuDF first, convert last.
- For datasets >1M rows, aggregate in cuDF before converting — never pass millions of rows to Plotly. Use `gdf.groupby('col').agg({'val': 'mean'}).to_pandas()` before plotting.
- The cuDF DataFrame must be loaded at module level or stored in a server-side cache (e.g., `flask_caching`). Do not store it in `dcc.Store` — that serializes to the browser.
- `gdf.iloc[list_of_indices]` works but is slower than boolean mask filtering on large DataFrames. Prefer mask-based filtering when the selection can be expressed as a condition.
- Dash callbacks are stateless by default — each callback receives the full current widget state, not a delta. Design filters to be re-applied from scratch on each callback.
```

- [ ] **Step 2: Verify the four required sections are present**

```bash
grep -E "^## (When to use|Key Imports|Cross-Filtering Pattern|Known GPU Gotchas)" skill/references/plotly-dash.md
```

Expected: 4 lines matching the section headers.

- [ ] **Step 3: Commit**

```bash
git add skill/references/plotly-dash.md
git commit -m "feat: add Plotly Dash GPU reference for cuXfilter skill"
```

---

## Task 5: Write `streamlit.md` reference

**Files:**
- Create: `skill/references/streamlit.md`

- [ ] **Step 1: Write the file**

Create `skill/references/streamlit.md` with this exact content:

```markdown
# Streamlit + cuDF Reference

**When to use:** Best for rapid prototyping and internal tools — simplest to write, but reruns the full script on every interaction, which limits scalability for very large datasets.

## Key Imports and Setup

```python
import cudf
import streamlit as st
import plotly.express as px
import numpy as np
```

## Cross-Filtering Pattern

Streamlit reruns the entire script on every widget interaction. Use `st.cache_resource` to hold the cuDF DataFrame across reruns (not `st.cache_data` — cuDF objects are not serializable). Filter state comes from widget return values read during each rerun.

```python
@st.cache_resource
def load_data():
    # cache_resource keeps the cuDF object alive across reruns
    return cudf.read_parquet("data.parquet")

gdf = load_data()

# FILTER COLUMNS: change 'value' to the column you want to filter on
col = st.selectbox("Filter column", gdf.columns.to_arrow().to_pylist())
col_min = float(gdf[col].min())
col_max = float(gdf[col].max())
selected_range = st.slider(
    f"{col} range",
    min_value=col_min,
    max_value=col_max,
    value=(col_min, col_max)
)

# Filter in cuDF — vectorized, no Python loops
filtered = gdf[(gdf[col] >= selected_range[0]) & (gdf[col] <= selected_range[1])]

# Convert to pandas only after filtering, for Plotly rendering
pdf = filtered.to_pandas()

# LAYOUT: add or rearrange st.columns here
col1, col2 = st.columns(2)
with col1:
    # CHART TYPES: swap px.scatter for another chart type here
    st.plotly_chart(px.scatter(pdf, x=pdf.columns[0], y=pdf.columns[1]), use_container_width=True)
with col2:
    st.plotly_chart(px.histogram(pdf, x=col, nbins=30), use_container_width=True)

st.caption(f"Showing {len(filtered):,} of {len(gdf):,} rows")
```

## Known GPU Gotchas

- Use `st.cache_resource` (not `st.cache_data`) for cuDF DataFrames. `cache_data` tries to serialize the return value to pickle, which fails for cuDF objects.
- `gdf.columns.to_pandas()` does not exist — use `gdf.columns.to_arrow().to_pylist()` or `list(gdf.columns)` to get column names as Python strings.
- Keep all filtering vectorized in cuDF — never iterate over rows with a Python loop. Streamlit reruns mean every slider movement re-executes the filter.
- Do not call `.to_pandas()` on a 100M+ row DataFrame before filtering — this will OOM. Always filter first, convert the smaller result.
- `st.dataframe()` and `st.table()` do not accept cuDF — always `.to_pandas()` before passing to these functions.
- Streamlit has no built-in cross-chart selection (no equivalent to Bokeh's lasso select feeding another chart). Use `st.session_state` if you need to carry a selection across widget groups, or use Plotly's `selectedData` via `st.plotly_chart(on_select=...)` (Streamlit >= 1.33).
```

- [ ] **Step 2: Verify the four required sections are present**

```bash
grep -E "^## (When to use|Key Imports|Cross-Filtering Pattern|Known GPU Gotchas)" skill/references/streamlit.md
```

Expected: 4 lines matching the section headers.

- [ ] **Step 3: Commit**

```bash
git add skill/references/streamlit.md
git commit -m "feat: add Streamlit GPU reference for cuXfilter skill"
```

---

## Task 6: Write `migration.md` reference

**Files:**
- Create: `skill/references/migration.md`

- [ ] **Step 1: Write the file**

Create `skill/references/migration.md` with this exact content:

```markdown
# cuxfilter Migration Reference

The cuxfilter Python library has been sunset. This reference maps cuxfilter concepts to their modern equivalents so an agent can understand what existing cuxfilter code was doing and reproduce it correctly — without the cuxfilter package.

## How to Use This Reference

When you detect `import cuxfilter` or `cux_df` in the user's code:
1. Identify which cuxfilter constructs are present (use the table below)
2. Ask the user which viz library they want to move to (Panel, Dash, or Streamlit) if not obvious from context
3. Reproduce the dashboard's behavior using the modern equivalent — do not attempt a line-by-line translation

## Concept Mapping

| cuxfilter construct | Modern equivalent |
|---|---|
| `import cuxfilter` | `import cudf` + viz library of choice |
| `cuxfilter.DataFrame.from_dataframe(df)` | `df` is already a cuDF DataFrame — use it directly |
| `cuxfilter.DataFrame.from_arrow(table)` | `cudf.DataFrame.from_arrow(table)` |
| `cuxfilter.load_graph(nodes, edges)` | `cudf.read_csv()` for each, then use `cugraph` or `networkx` |
| `cuxfilter.charts.bokeh.bar()` | `hvplot.bar()` (Panel) or `px.bar` in `dcc.Graph` (Dash) |
| `cuxfilter.charts.datashader.scatter()` | `hd.datashade(hv.Points(gdf, kdims=['x','y']))` (Panel) |
| `cuxfilter.charts.datashader.line()` | `hd.datashade(hv.Curve(gdf, kdims=['x'], vdims=['y']))` (Panel) |
| `cuxfilter.charts.datashader.heatmap()` | `hd.datashade(hv.Points(gdf), aggregator=ds.mean('value'))` (Panel) |
| `cuxfilter.charts.panel_widgets.range_slider()` | `pn.widgets.RangeSlider` (Panel) or `dcc.RangeSlider` (Dash) |
| `cuxfilter.charts.panel_widgets.drop_down()` | `pn.widgets.Select` (Panel) or `dcc.Dropdown` (Dash) |
| `cuxfilter.charts.panel_widgets.multi_select()` | `pn.widgets.MultiSelect` (Panel) or `dcc.Dropdown(multi=True)` (Dash) |
| `cuxfilter.charts.panel_widgets.card()` | `pn.pane.Markdown` or `pn.pane.HTML` (Panel) |
| `cuxfilter.charts.panel_widgets.number()` | `pn.indicators.Number` (Panel) |
| `cux_df.dashboard(charts=[...])` | `pn.Row(*charts).servable()` (Panel) or `app.layout = html.Div([...])` (Dash) |
| `dashboard.show()` | `panel serve app.py` (Panel) or `app.run()` (Dash) |
| `dashboard.app()` | Returns a Panel or Dash app object — same pattern |
| Implicit callback wiring | Explicit `hv.streams.BoundsXY` (Panel) or `@app.callback` (Dash) |

## Key Conceptual Difference

cuxfilter wired cross-filtering callbacks automatically when charts shared the same DataFrame. Modern libraries require explicit wiring:

- **Panel**: bind `hv.streams.BoundsXY` or `hv.streams.Selection1D` to a source element; use `@pn.depends` on derived elements
- **Dash**: use `@app.callback(Output(...), Input('chart-id', 'selectedData'))`
- **Streamlit**: no explicit wiring — widget state drives a full script rerun; use `st.session_state` for persistent selections across widget groups

## What Not to Port

`cuxfilter.charts.deckgl.*` (choropleth 2D and 3D) has no direct drop-in replacement in Panel or Dash. Recommend:
- `pydeck` for standalone Deck.GL rendering
- `dash-deck` for Deck.GL inside a Dash app

Do not attempt to replicate Deck.GL charts using the Panel or Dash DataShader patterns — they are fundamentally different rendering pipelines.
```

- [ ] **Step 2: Verify the mapping table covers all key cuxfilter constructs**

```bash
grep -c "cuxfilter\." skill/references/migration.md
```

Expected: at least `15` (one per table row that references a cuxfilter construct).

- [ ] **Step 3: Commit**

```bash
git add skill/references/migration.md
git commit -m "feat: add cuxfilter migration reference for cuXfilter skill"
```

---

## Task 7: Write `README.md` for distribution

**Files:**
- Create: `skill/README.md`

- [ ] **Step 1: Write the file**

Create `skill/README.md` with this exact content:

```markdown
# cuXfilter Skill

A portable AI agent skill that generates GPU-accelerated cross-filtering dashboards using cuDF. Works with Claude Code, Codex, Cursor, and any agent platform that supports the superpowers skill format.

## What It Does

When you ask your agent for a cross-filtering dashboard on a large dataset, this skill instructs the agent to:

1. Detect whether you have existing cuxfilter code and offer to migrate it
2. Ask which visualization library you have (Panel/HoloViews, Plotly Dash, or Streamlit)
3. Generate a complete, runnable dashboard file with cuDF data loading and at least two linked charts

The generated code runs on any CUDA-capable machine. No cuxfilter package required.

## Installation

### Claude Code

```bash
claude plugins install /path/to/skill/
```

Or copy `skills/cuXfilter.md` and `references/` into your active plugin directory.

### Cursor / Copilot

Copy `skills/cuXfilter.md` into your `.cursor/rules/` or `.github/copilot-instructions.md` and include the references directory alongside it.

## Usage

**Slash command:**
```
/cuXfilter
```

**Natural language:**
```
Build me a cross-filtering dashboard on my accidents.parquet file
```
```
I have a linked charts setup I built with cuxfilter — can you help me migrate it?
```

## Requirements (for generated code)

- CUDA 12.2+, Volta GPU (Compute Capability ≥ 7.0)
- cuDF (install via RAPIDS conda or pip)
- One of: Panel + HoloViews + DataShader, Plotly Dash, or Streamlit

## File Structure

```
skill/
  skills/
    cuXfilter.md         # main skill — install this
  references/
    panel-holoviews.md   # loaded on demand for Panel output
    plotly-dash.md       # loaded on demand for Dash output
    streamlit.md         # loaded on demand for Streamlit output
    migration.md         # loaded on demand when cuxfilter code is detected
  README.md
```
```

- [ ] **Step 2: Verify README has installation and usage sections**

```bash
grep -E "^## (What It Does|Installation|Usage|Requirements|File Structure)" skill/README.md
```

Expected: 5 matching lines.

- [ ] **Step 3: Commit**

```bash
git add skill/README.md
git commit -m "docs: add cuXfilter skill README with installation and usage"
```

---

## Task 8: Validate skill coverage against spec

This task runs manually — no code to write.

- [ ] **Step 1: Check trigger coverage**

Open `skill/skills/cuXfilter.md`. Verify the `triggers:` frontmatter contains:
- At least 4 natural language phrases
- The `/cuXfilter` slash command

- [ ] **Step 2: Check migration detection**

In `cuXfilter.md`, verify Step 1 instructs the agent to scan for both `import cuxfilter` and `cux_df` (not just one).

- [ ] **Step 3: Check output format coverage**

In `cuXfilter.md`, verify Step 2 asks for both notebook and standalone script output.

- [ ] **Step 4: Check reference file completeness**

Run:
```bash
for f in skill/references/*.md; do
  echo "=== $f ==="
  grep -E "^## (When to use|Key Imports|Cross-Filtering Pattern|Known GPU Gotchas)" "$f"
done
```

Expected: each of the three library reference files (panel-holoviews, plotly-dash, streamlit) prints all 4 section headers. `migration.md` will not — that is expected.

- [ ] **Step 5: Check migration table completeness**

```bash
grep -c "cuxfilter\." skill/references/migration.md
```

Expected: ≥ 15 rows covering the constructs listed in the spec.

- [ ] **Step 6: Commit validation evidence**

No code changes — this step produces no files. If any gaps are found in steps 1–5, fix the relevant file and amend the commit for that file before marking this task done.

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Covered by |
|---|---|
| Agent generates complete runnable dashboard | Task 2 (cuXfilter.md Step 3) |
| GPU-first: cuDF required | Task 2 (Step 3), Tasks 3–5 (gotchas) |
| Library-agnostic: Panel, Dash, Streamlit | Tasks 3, 4, 5 |
| Notebook and script output | Task 2 (Step 2, item 3) |
| Fresh start — no mention of cuxfilter by default | Task 2 (Step 1, "If not found") |
| Migration path when cuxfilter detected | Task 2 (Step 1) + Task 6 |
| Natural language + slash command triggers | Task 2 (frontmatter) |
| Reference files: 4 sections each | Tasks 3, 4, 5 |
| Migration table: all key constructs | Task 6 |

**Placeholder scan:** No TBDs, TODOs, or "similar to above" references. All code blocks are complete.

**Type consistency:** No function names or types are defined in one task and used differently in another — these are independent markdown files.

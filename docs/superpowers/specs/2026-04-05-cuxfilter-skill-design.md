# cuXfilter Skill Design

**Date:** 2026-04-05
**Status:** Approved
**Author:** Ajay Thorve

## Overview

Sunset the cuxfilter Python library and replace it with a portable AI agent skill (`cuXfilter`) that any omni agent (Claude Code, Codex, Cursor, etc.) can use to generate GPU-accelerated cross-filtering dashboards on behalf of the user. The user gets a complete, runnable dashboard without needing to install or maintain the cuxfilter library.

## Goals

- Agent generates a complete working cross-filtering dashboard app (notebook or standalone script) tailored to the user's data and library choices
- GPU-first: cuDF is the default data layer; GPU acceleration is not optional
- Visualization layer is library-agnostic: agent detects or asks which library the user has (Panel/HoloViews, Plotly Dash, Streamlit) and generates accordingly
- Works in both Jupyter notebooks and standalone Python scripts
- If user has existing cuxfilter code, agent offers to migrate it — no reference to cuxfilter otherwise

## Non-Goals

- The skill does not wrap or depend on the cuxfilter Python library
- The skill does not support CPU-only / pandas-only workflows as a primary path
- No GUI wizard — agent asks questions conversationally

## File Structure

```
cuxfilter/
  skills/
    cuXfilter.md            # main skill — triggers, process, judgment rules
  references/
    panel-holoviews.md      # GPU-friendly patterns for Panel + DataShader
    plotly-dash.md          # patterns for Dash + cuDF
    streamlit.md            # patterns for Streamlit + cuDF
    migration.md            # conceptual mapping from cuxfilter to modern equivalents
```

`cuXfilter.md` is the only required file. Reference files are loaded by the agent on demand and do not bloat the main skill's context footprint.

## Triggers

The skill registers two trigger types:

1. **Natural language** — phrases like "cross-filtering dashboard", "interactive filter on my dataset", "linked charts", "GPU dashboard"
2. **Slash command** — `/cuXfilter`

## Main Skill: `cuXfilter.md`

The skill encodes process and judgment, not code templates. It instructs the agent to:

### Step 1 — Detect context
- Look for `import cuxfilter` or `cux_df` in the user's files/conversation
- If found: load `migration.md`, explain that cuxfilter is sunset, offer to convert the existing code to a modern equivalent before proceeding
- If not found: proceed fresh with no mention of cuxfilter

### Step 2 — Gather requirements
Ask (or infer from context):
1. What is the data source? (cuDF DataFrame, Arrow, Parquet, CSV, etc.)
2. Which viz library is available? (detect from environment/imports if possible; otherwise ask — choices: Panel+HoloViews, Plotly Dash, Streamlit)
3. What output format? (Jupyter notebook or standalone `.py` script)

### Step 3 — Generate the dashboard
Produce a complete, runnable output file containing:
- GPU-accelerated data loading via cuDF (required)
- At least two linked charts with cross-filtering wired up
- A sensible default layout
- Comments marking the sections users most commonly customize (chart types, filter columns, layout)

Load the appropriate reference file (`panel-holoviews.md`, `plotly-dash.md`, or `streamlit.md`) to ground the generated code in correct GPU-friendly patterns.

### Step 4 — Offer next steps
After generating, suggest: add more chart types, connect to a live/streaming data source, deploy to a server.

## Reference Files

Each reference file grounds the agent in library-specific GPU patterns. Structure per file:

- **When to use** — one-sentence fit statement (e.g., "Panel + DataShader: best for 10M+ rows, server-side rendering")
- **Key imports and setup** — the cuDF + library wiring
- **Cross-filtering pattern** — how linked selection/filtering works in this library (non-obvious, differs across libraries)
- **Known GPU gotchas** — e.g., DataShader requires `.to_pandas()` at render time; cuDF doesn't support all pandas ops

## Migration Reference: `migration.md`

A conceptual lookup table mapping cuxfilter constructs to modern equivalents. Gives the agent the mapping needed to reason about what existing code was doing and reproduce it correctly — not an automated converter.

| cuxfilter concept | Replacement |
|---|---|
| `cuxfilter.DataFrame` | `cudf.read_parquet()` / `cudf.DataFrame` |
| `cuxfilter.charts.bokeh.bar()` | Panel `hvplot.bar()` or Dash `dcc.Graph` |
| `cuxfilter.charts.datashader.scatter()` | Panel `hv.Points` + DataShader pipeline |
| `cuxfilter.charts.panel_widgets.range_slider()` | Panel `pn.widgets.RangeSlider` or Dash `dcc.RangeSlider` |
| `cux_df.dashboard(charts=[...])` | Panel `pn.Row()` / Dash `app.layout` |
| Callback wiring (implicit in cuxfilter) | Explicit library-specific selection callbacks |

## Success Criteria

- An agent with this skill installed can take a user from "I have a cuDF DataFrame" to a running cross-filtering dashboard in one conversation turn
- The generated code runs without modification on a CUDA-capable machine
- Existing cuxfilter users can migrate their code with agent assistance, not manual effort
- The skill file itself requires no maintenance as underlying libraries evolve — the agent's own knowledge handles library updates

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

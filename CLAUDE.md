# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is this repo

This repo contains the **cuXfilter agent skill** — a portable AI agent skill that generates GPU-accelerated cross-filtering dashboards using cuDF. The Python library has been sunset.

## Structure

```
skill/
  skills/cuXfilter.md       # main skill file (triggers + 4-step process)
  references/
    panel-holoviews.md      # GPU patterns for Panel + HoloViews/DataShader
    plotly-dash.md          # GPU patterns for Plotly Dash
    streamlit.md            # GPU patterns for Streamlit
    migration.md            # cuxfilter → modern equivalents mapping
  README.md                 # installation and usage
```

## Editing the skill

- `skill/skills/cuXfilter.md` — edit triggers or the agent process here
- `skill/references/*.md` — edit library-specific GPU patterns here
- Keep code examples in reference files technically accurate — agents copy them verbatim
- The skill encodes process and judgment, not code templates

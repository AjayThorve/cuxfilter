# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is cuxfilter

cuxfilter is a RAPIDS framework for GPU-accelerated cross-filtering of large tabular datasets (100M+ rows). It connects web visualizations (Bokeh, DataShader, Deck.GL) to GPU-accelerated filtering via cuDF. Requires CUDA 12.2+ and Volta architecture (Compute Capability ≥7.0).

## Commands

All commands run from the `python/` directory unless noted.

**Install for development:**
```bash
cd python && pip install .
```

**Run all tests:**
```bash
cd python && pytest
```

**Run a single test file:**
```bash
cd python && pytest cuxfilter/tests/test_dashboard.py -v
```

**Run tests with coverage (matches CI):**
```bash
cd python && pytest --numprocesses=8 --dist=worksteal --cov=cuxfilter --cov-report=term
```

**Lint/format:**
```bash
black python/cuxfilter
flake8 python/cuxfilter
```

**Pre-commit (runs black, flake8, and other hooks):**
```bash
pre-commit run --hook-stage manual --all-files --show-diff-on-failure
```

## Architecture

The main entry point for users is `cuxfilter.DataFrame`, which wraps cuDF/dask_cudf DataFrames and creates `DashBoard` objects.

**Data flow:**
1. `DataFrame.from_arrow()` / `from_dataframe()` / `load_graph()` — load data
2. Create chart objects from `cuxfilter.charts.*` (e.g., `bokeh.bar`, `datashader.scatter`)
3. `cux_df.dashboard(charts=[], sidebar=[])` — assemble the dashboard
4. Dashboard runs as a Panel/Bokeh server; charts communicate cross-filtering via the dashboard

**Key source files:**
- `python/cuxfilter/dataframe.py` — main user-facing API
- `python/cuxfilter/dashboard.py` — orchestrates chart communication and filtering state
- `python/cuxfilter/charts/` — chart implementations grouped by library (bokeh, datashader, deckgl, panel_widgets)
- `python/cuxfilter/charts/core/` — `BaseChart`, `BaseWidget`, `ViewDataFrame` base classes that all chart types extend
- `python/cuxfilter/layouts/` — dashboard layout templates
- `python/cuxfilter/themes/` — dashboard styling
- `python/cuxfilter/assets/` — UI resources and notebook integration utilities

**Chart libraries supported:** Bokeh, DataShader, Deck.GL, Panel Widgets (sliders, dropdowns, etc.), and a custom `view_dataframe` chart.

**Tests:** `python/cuxfilter/tests/` with ~20 files. Core chart tests are in `tests/charts/core/`.

## Dependencies

Managed via `dependencies.yaml` (RAPIDS dependency file generator). Core runtime deps: cudf, dask-cudf, cupy, datashader, bokeh, panel, geopandas, jupyter-server-proxy. Build backend: `rapids-build-backend`.

FutureWarning and DeprecationWarning are treated as errors in tests (configured in `python/pyproject.toml`).

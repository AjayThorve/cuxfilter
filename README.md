# cuXfilter

> The cuXfilter Python library has been sunset. This repo now contains a portable AI agent skill that generates GPU-accelerated cross-filtering dashboards — no library installation required.

## What is cuXfilter (the skill)?

An AI agent skill that instructs any omni agent (Claude Code, Codex, Cursor, etc.) to generate complete, runnable cross-filtering dashboard code for large datasets using cuDF as the GPU data layer.

See [`skill/README.md`](skill/README.md) for installation and usage instructions.

## Quick Start

Install the skill in your agent, then ask:

```
Build me a cross-filtering dashboard on my data.parquet file
```

or use the slash command:

```
/cuXfilter
```

## Requirements (for generated dashboards)

- CUDA 12.2+, Volta GPU (Compute Capability ≥ 7.0)
- [cuDF](https://docs.rapids.ai/api/cudf/stable/) via RAPIDS
- One of: Panel + HoloViews + DataShader, Plotly Dash, or Streamlit

## License

Apache 2.0 — see [LICENSE](LICENSE)

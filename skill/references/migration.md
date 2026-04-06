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
| `cuxfilter.DataFrame` | `cudf.DataFrame` |
| `cuxfilter.DataFrame.from_dataframe(df)` | `df` is already a cuDF DataFrame — use it directly |
| `cuxfilter.DataFrame.from_arrow(table)` | `cudf.DataFrame.from_arrow(table)` |
| `cuxfilter.load_graph(nodes, edges)` | `cudf.read_csv()` for each, then use `cugraph` or `networkx` |
| `cuxfilter.charts.bokeh.bar()` | `hvplot.bar()` (Panel) or `px.bar` in `dcc.Graph` (Dash) |
| `cuxfilter.charts.bokeh.scatter()` | `hvplot.scatter()` (Panel) or `px.scatter` in `dcc.Graph` (Dash) |
| `cuxfilter.charts.datashader.scatter()` | `hd.datashade(hv.Points(gdf, kdims=['x','y']))` (Panel) |
| `cuxfilter.charts.datashader.line()` | `hd.datashade(hv.Curve(gdf, kdims=['x'], vdims=['y']))` (Panel) |
| `cuxfilter.charts.datashader.heatmap()` | `hd.datashade(hv.Points(gdf, kdims=['x','y']), aggregator=ds.count())` (Panel) — use `ds.mean('col')` for value-weighted heatmaps |
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

`cuxfilter.charts.deckgl.*` (choropleth 2D and 3D) has no direct drop-in replacement in Panel, Dash, or Streamlit via DataShader. Recommend:
- `pydeck` for standalone Deck.GL rendering
- `dash-deck` for Deck.GL inside a Dash app
- `st.pydeck_chart()` for Deck.GL inside a Streamlit app

Do not attempt to replicate Deck.GL charts using DataShader patterns — they are fundamentally different rendering pipelines.

# Plotly Dash + cuDF Reference

## When to use

Best when users need rich interactive chart types (3D, maps, financial) or are deploying a multi-user web app.

## Key Imports and Setup

```python
import cudf  # pandas not imported — cuDF handles all data; only .to_pandas() at render time
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
        # Use iloc for index-based point selection (direct gather — efficient for small k)
        # Use boolean mask only when filtering by a column condition (e.g., value range)
        filtered = gdf.iloc[indices]
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
        # Plotly histogram selectedData gives bin centers, not edges.
        # Extend x1 by half a bin width to capture the full rightmost bin.
        x0 = selected['points'][0].get('x', None)
        x1 = selected['points'][-1].get('x', None)
        if x0 is not None and x1 is not None:
            n_bins = len(selected['points'])
            half_bin = (x1 - x0) / (2 * max(n_bins - 1, 1)) if n_bins > 1 else 0
            filtered = gdf[(gdf['value'] >= x0) & (gdf['value'] <= x1 + half_bin)]
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
- `gdf.iloc[indices]` is the right tool for point-index based selection (direct gather). Boolean mask filtering is more efficient when you can express the filter as a column condition (e.g., `gdf[gdf['col'] > val]`). Do not construct a mask just to apply point indices.
- Dash callbacks are stateless by default — each callback receives the full current widget state, not a delta. Design filters to be re-applied from scratch on each callback.

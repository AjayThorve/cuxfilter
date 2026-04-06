# Panel + HoloViews/DataShader Reference

## When to use

Best for 10M+ rows — DataShader renders server-side so only pixel data crosses the network.

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
    return hv.Histogram((counts, edges)).opts(width=400, height=300)

# LAYOUT: rearrange or add elements here
layout = pn.Row(shaded, filtered_hist)
layout.servable()
```

## Known GPU Gotchas

- `hd.datashade()` and `hd.rasterize()` accept cuDF DataFrames directly — **do not** call `.to_pandas()` before passing to these functions. Converting defeats the purpose.
- Most other HoloViews elements (`hv.Histogram`, `hv.Bars`, `hv.Curve`) require pandas/numpy. Always filter in cuDF first, then call `.to_pandas()` on the smaller result.
- `cudf.DataFrame` does not support `.plot()` — route all rendering through HoloViews or hvplot.
- For hvplot on cuDF, use `import hvplot.cudf` (requires hvplot >= 0.7). For hvplot on pandas, use `import hvplot.pandas`.
- `BoundsXY` initial value `(0, 0, 0, 0)` means "no selection" — always check for this and return the full dataset. Note: if your data contains the exact point `(0, 0)`, a single-point click there is indistinguishable from no-selection; warn users accordingly.
- `hv.Points(gdf)` may silently convert cuDF to pandas before passing to DataShader. Verify with `type(points.data)` — if it shows `pandas.DataFrame`, HoloViews converted it. Pass the cuDF DataFrame directly to `hd.datashade()` to avoid this: `hd.datashade(hv.Points(gdf, kdims=['x','y']))`.

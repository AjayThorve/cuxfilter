# Streamlit + cuDF Reference

## When to use

Best for rapid prototyping and internal tools — simplest to write, but reruns the full script on every interaction, which limits scalability for very large datasets.

## Key Imports and Setup

```python
import cudf
import streamlit as st
import plotly.express as px
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
col = st.selectbox("Filter column", list(gdf.columns))
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

- Use `st.cache_resource` (not `st.cache_data`) for cuDF DataFrames. `cache_data` tries to serialize the return value, which fails for cuDF objects.
- `list(gdf.columns)` is the correct way to get column names as Python strings for Streamlit widgets. `gdf.columns.to_pandas()` does not exist on cuDF Index objects.
- Keep all filtering vectorized in cuDF — never iterate over rows with a Python loop. Streamlit reruns mean every slider movement re-executes the filter.
- Do not call `.to_pandas()` on a large DataFrame before filtering — always filter in cuDF first, then convert the smaller result.
- `st.dataframe()` and `st.table()` do not accept cuDF — always `.to_pandas()` before passing to these functions.
- Streamlit has no built-in cross-chart selection. For chart-to-chart filtering, use `st.plotly_chart(on_select="rerun")` (Streamlit >= 1.33) and read `st.session_state` for the selection, or use `st.session_state` with widget keys to carry selections across widget groups.

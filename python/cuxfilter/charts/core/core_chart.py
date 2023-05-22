import cudf
import dask_cudf
import logging
import panel as pn
from bokeh.models import ColumnDataSource
from panel.config import panel_extension
from typing import Dict, Literal

from ...assets import cudf_utils, datetime as dt


class BaseChart:
    chart_type: str = None
    x: str = None
    y: str = None
    aggregate_fn: str = "count"
    color: str = None
    _height: int = 0
    _width: int = 0
    add_interaction: bool = True
    chart = None
    source = None
    source_backup = None
    data_points: int = 0
    filter_widget = None
    _library_specific_params: Dict[str, str] = {}
    stride = None
    stride_type = int
    min_value: float = 0.0
    max_value: float = 0.0
    x_label_map = {}
    y_label_map = {}
    _initialized = False
    # widget=False can only be rendered the main layout
    is_widget = False
    title = ""
    _renderer_mode: Literal["web-app", "notebook"] = "web-app"

    @property
    def renderer_mode(self):
        return self._renderer_mode

    @renderer_mode.setter
    def renderer_mode(self, value):
        valid_values = ["web-app", "notebook"]
        if value not in valid_values:
            raise ValueError(
                f"""Invalid value '{value}'. Value must be one of
                {valid_values}."""
            )
        self._renderer_mode = value

    @property
    def name(self):
        chart_type = self.chart_type if self.chart_type else "chart"
        return f"{self.x}_{chart_type}_{self.title}"

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        if self.chart is not None:
            self.update_dimensions(width=value)
        if self.filter_widget is not None:
            self.filter_widget.width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        if self.chart is not None:
            self.update_dimensions(height=value)

    @property
    def library_specific_params(self):
        return self._library_specific_params

    @property
    def x_dtype(self):
        if isinstance(self.source, ColumnDataSource):
            return self.source.data[self.data_x_axis].dtype
        elif isinstance(self.source, (cudf.DataFrame, dask_cudf.DataFrame)):
            return self.source[self.x].dtype
        return None

    @property
    def y_dtype(self):
        if isinstance(self.source, ColumnDataSource):
            return self.source.data[self.data_x_axis].dtype
        elif isinstance(self.source, (cudf.DataFrame, dask_cudf.DataFrame)):
            return self.source[self.y].dtype
        return None

    @library_specific_params.setter
    def library_specific_params(self, value):
        self._library_specific_params = value
        self.extract_mappers()
        self.set_color()

    def set_color(self):
        if "color" in self.library_specific_params:
            self.color = self.library_specific_params["color"]

    def extract_mappers(self):
        if "x_label_map" in self.library_specific_params:
            self.x_label_map = self.library_specific_params["x_label_map"]
            self.library_specific_params.pop("x_label_map")
        if "y_label_map" in self.library_specific_params:
            self.y_label_map = self.library_specific_params["y_label_map"]
            self.library_specific_params.pop("y_label_map")

    def _repr_mimebundle_(self, include=None, exclude=None):
        view = self.view()
        if self._initialized and panel_extension._loaded:
            return view._repr_mimebundle_(include, exclude)

        if self._initialized is False:
            logging.warning(
                "dashboard has not been initialized."
                "Please run cuxfilter.dashboard.Dashboard([...charts])"
                " to view this object in notebook"
            )

        if panel_extension._loaded is False:
            logging.warning(
                "notebooks assets not loaded."
                "Please run cuxfilter.load_notebooks_assets()"
                " to view this object in notebook"
            )
            if isinstance(view, pn.Column):
                return view.pprint()
        return None

    def _to_xaxis_type(self, dates):
        """
        Description: convert to int64 if self.x_dtype is of type datetime
        -----------------------------------------------------------------
        Input:
            dates: cudf.Series | list | tuple
        """
        return dt.to_int64_if_datetime(dates, self.x_dtype)

    def _to_yaxis_type(self, dates):
        """
        Description: convert to int64 if self.y_dtype is of type datetime
        -----------------------------------------------------------------
        Input:
            dates: cudf.Series | list | tuple
        """
        return dt.to_int64_if_datetime(dates, self.y_dtype)

    def _xaxis_dt_transform(self, dates):
        """
        Description: convert to datetime64 if self.x_dtype is of type datetime
        -----------------------------------------------------------------
        Input:
            dates: list | tuple of integer timestamps objects
        """
        return dt.to_dt_if_datetime(dates, self.x_dtype)

    def _yaxis_dt_transform(self, dates):
        """
        Description: convert to datetime64 if self.y_dtype is of type datetime
        -----------------------------------------------------------------
        Input:
            dates: list | tuple of integer timestamps objects
        """
        return dt.to_dt_if_datetime(dates, self.y_dtype)

    def _xaxis_np_dt64_transform(self, dates):
        """
        Description: convert to datetime64 if self.x_dtype is of type datetime
        -----------------------------------------------------------------
        Input:
            dates: list | tuple of datetime.datetime objects
        """
        return dt.to_np_dt64_if_datetime(dates, self.x_dtype)

    def _yaxis_np_dt64_transform(self, dates):
        """
        Description: convert to datetime64 if self.y_dtype is of type datetime
        -----------------------------------------------------------------
        Input:
            dates: list | tuple of datetime.datetime objects
        """
        return dt.to_np_dt64_if_datetime(dates, self.y_dtype)

    def _xaxis_stride_type_transform(self, stride_type):
        """
        Description: return stride_type=CUDF_TIMEDELTA_TYPE if self.x_dtype is
                of type datetime, else return stride_type
        """
        return dt.transform_stride_type(stride_type, self.x_dtype)

    def _yaxis_stride_type_transform(self, stride_type):
        """
        Description: return stride_type=CUDF_TIMEDELTA_TYPE if self.y_dtype is
                of type datetime else return stride_type
        """
        return dt.transform_stride_type(stride_type, self.y_dtype)

    def view(self):
        return self.chart

    def update_dimensions(self, width=None, height=None):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def calculate_source(self, data):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def generate_chart(self):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def add_reset_event(self, callback=None):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def compute_query_dict(self, query_dict):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def reset_chart(self, data: list = []):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def reload_chart(self, data, patch_update: bool):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def format_source_data(self, source_dict, patch_update=False):
        """"""
        # print('function to be overridden by library specific extensions')
        return -1

    def get_source_y_axis(self):
        # print('function to be overridden by library specific extensions')
        return []

    def apply_mappers(self):
        """"""
        # print('function to be overridden by library specific extensions')
        return -1

    def query_chart_by_range(
        self,
        active_chart,
        query_tuple,
        datatile,
        query="",
        local_dict={},
        indices=None,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: None in case of Gpu Geo Scatter charts
            4. query: query string representing the current filtered state of
                    the dashboard
            5. local_dict: dictionary containing the variable:value mapping
                    local to the query_string.
                    Passed as a parameter to cudf.query() api
            6. indices: cudf.Series representing the current filtered state
                    of the dashboard, apart from the query_string,
                    since the lasso_select callback results in a boolean mask
        -------------------------------------------

        Ouput:
        """
        if datatile is not None:
            self._query_by_range_datatile(active_chart, query_tuple, datatile)
        else:
            min_val, max_val = query_tuple
            final_query = "@min_val<=" + active_chart.x + "<=@max_val"
            local_dict.update({"min_val": min_val, "max_val": max_val})
            if len(query) > 0:
                final_query += " and " + query
            self.reload_chart(
                self._compute_source(final_query, local_dict, indices),
                False,
            )

    def _compute_source(self, query, local_dict, indices):
        return cudf_utils.query_df(self.source, query, local_dict, indices)

    # def query_chart_by_indices(
    #     self,
    #     active_chart: BaseChart,
    #     old_indices,
    #     new_indices,
    #     datatile=None,
    #     query="",
    #     local_dict={},
    #     indices=None,
    # ):
    #     """
    #     Description:

    #     -------------------------------------------
    #     Input:
    #         1. active_chart: chart object of active_chart
    #         2. old_indices: list of indices selected in previous callback
    #         3. new_indices: list of indices selected in currently
    #         4. datatile: None in case of Geo scatter charts
    #         5. query: query string representing the current filtered state of
    #                 the dashboard
    #         6. local_dict: dictionary containing the variable:value mapping
    #                 local to the query_string.
    #                 Passed as a parameter to cudf.query() api
    #         7. indices: cudf.Series representing the current filtered state
    #                 of the dashboard, apart from the query_string,
    #                 since the lasso_select callback results in a boolean mask
    #     -------------------------------------------

    #     Ouput:
    #     """
    #     if "" in new_indices:
    #         new_indices.remove("")
    #     if len(new_indices) == 0:
    #         # case: all selected indices were reset
    #         # reset the chart
    #         final_query = query
    #     elif len(new_indices) == 1:
    #         final_query = f"{active_chart.x}=={str(float(new_indices[0]))}"
    #         if len(query) > 0:
    #             final_query += f" and {query}"
    #     else:
    #         new_indices_str = ",".join(map(str, new_indices))
    #         final_query = f"{active_chart.x} in ({new_indices_str})"
    #         if len(query) > 0:
    #             final_query += f" and {query}"

    #     self.reload_chart(
    #         self._compute_source(final_query, local_dict, indices),
    #         False,
    #     )

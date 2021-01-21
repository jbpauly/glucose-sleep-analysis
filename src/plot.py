import pathlib
from os.path import abspath, dirname

import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

SRC_PATH = pathlib.Path(dirname(abspath(__file__)))


def altair_heatmap(corr_matrix: pd.DataFrame, x_selection: str = None, y_selection: str = None) -> alt.Chart:
    """
    Create an interactive Altair heatmap of parameter correlations with user defined x and y parameters.
    The x-y selection will be highlighted in pink.
    Args:
        corr_matrix: DataFrame of parameter correlations.
        x_selection: Selected parameter to highlight on x axis.
        y_selection:Selected parameter to highlight on y axis.

    Returns: The altair plot.

    """
    pair = alt.selection_single(fields=["x", "y"], clear=False, name="pair")
    chart = alt.Chart(corr_matrix.round(2)).mark_rect(tooltip=True).encode(
        x=alt.X('x', title=None),
        y=alt.Y('y', title=None),
        color=alt.condition(((alt.datum.x == x_selection) &
                             (alt.datum.y == y_selection)),
                            alt.value('pink'),
                            'correlation:Q',
                            ),
    ).add_selection(pair)
    return chart


def altair_scatter(dataset: pd.DataFrame, x_selection: str, y_selection: str, color_selection: str) -> alt.Chart:
    """
    Create an interactive Altair scatter plot with user defined x and y parameters as well as an optional third
    parameter used for marker color gradient.
    Args:
        dataset: DataFrame containing selected parameters.
        x_selection: Parameter to plot along the x-axis.
        y_selection: Parameter to plot along the y-axis.
        color_selection: Parameter to use for scatter marker color gradient (parameter options are numeric intervals).

    Returns: The altair plot.

    """

    # use set to handle edge case of duplicated axes or 'Date' selection
    tooltip = list(set(['Date', x_selection, y_selection, color_selection]))
    if color_selection == '<select>':
        tooltip.remove(color_selection)
        color = alt.value('blue')
    else:
        color = color_selection  # color will have grade with range of parameter's values

    plot = alt.Chart(dataset) \
        .mark_circle() \
        .encode(x=x_selection,
                y=y_selection,
                tooltip=tooltip,
                color=color) \
        .interactive()

    return plot


def plotly_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    """
     Create a Plotly heatmap of parameter correlations.
    Args:
        corr_matrix: DataFrame of correlations, should be square (columns and indexes are the same).

    Returns: The Plotly graph object figure.

    """
    title = "Metrics Summary: Pearson's Correlation"
    data = [go.Heatmap(x=corr_matrix.columns,
                       y=corr_matrix.index,
                       z=corr_matrix,
                       colorscale='Blues',
                       colorbar=dict(title='Correlation'),
                       zmin=-1,
                       zmax=1,
                       )]
    layout = go.Layout(autosize=False,
                       xaxis=dict(showticklabels=True, tickfont=dict(size=8)),
                       yaxis=dict(showticklabels=True, tickfont=dict(size=8)), )
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5
        ),
        xaxis=dict(
            automargin=True
        ),
        yaxis=dict(
            automargin=True
        )
    )
    return fig


def plotly_scatter(dataset: pd.DataFrame,
                   x_selection: str,
                   y_selection: str,
                   color_selection: str,
                   hover: [str] = None) -> go.Figure:
    """
    Create an interactive Plotly scatter plot with user defined x and y parameters as well as an optional third
    parameter used for point color gradient.
    Args:
        dataset: DataFrame containing selected parameters.
        x_selection: Parameter to plot along the x-axis.
        y_selection: Parameter to plot along the y-axis.
        color_selection: Parameter to use for scatter marker color gradient (parameter options are numeric intervals).
        hover: Additional parameters to include in the tool tip.

    Returns: The Plotly graph object figure.

    """
    title = f"Scatter Analysis: {x_selection} vs. {y_selection}"
    if color_selection == '<select>':
        color = None
    else:
        color = color_selection
    fig = px.scatter(dataset,
                     x=x_selection,
                     y=y_selection,
                     color_continuous_scale='Blues',
                     color=color,
                     trendline="ols",
                     hover_data=hover)
    fig.update_traces(
        marker=dict(
            line=dict(width=1,
                      color='DarkSlateGrey')),
        )
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5
        )
    )
    return fig


def plotly_line(dataset: pd.DataFrame, x_selection: str, y_selection: str, date_col: str = 'Date') -> go.Figure:
    """
    Create a multi-line timeseries Plotly plot. Plot both the x and y selection variables.
    Args:
        dataset: Dataset of parameters.
        x_selection: Sub-line 1 for the plot.
        y_selection: Sub-line 2 for the plot.
        date_col: Dates to plot on the x axis.

    Returns: The Plotly graph object figure.

    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=dataset.loc[:, date_col],
                   y=dataset.loc[:, x_selection],
                   mode='lines+markers',
                   name=x_selection),
        secondary_y=False, )
    fig.add_trace(
        go.Scatter(x=dataset.loc[:, date_col],
                   y=dataset.loc[:, y_selection],
                   mode='lines+markers',
                   name=y_selection),
        secondary_y=True, )
    fig.update_layout(
        xaxis=dict(
            title='Date',
            showgrid=True,
            showspikes=True,
            spikemode='across + toaxis',
            spikesnap='cursor',
            showline=True,
            spikedash='solid',
            rangeselector=dict(
                buttons=list([
                    dict(count=7,
                         label="1w",
                         step="day",
                         stepmode="backward"),
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        ),
        yaxis=dict(
            showgrid=True,
            title=x_selection
        ),
        yaxis2=dict(
            showgrid=False,
            title=y_selection
        ),
        title=dict(
            text='Metrics Trends',
            x=0.5
        ),
        legend=dict(
            orientation="h",
        )
    )
    return fig

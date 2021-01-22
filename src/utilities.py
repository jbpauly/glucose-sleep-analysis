import pandas as pd
import streamlit as st
import pathlib
import datetime as dt
from os.path import abspath, dirname
from pandas_profiling import ProfileReport
import glucose as gc

SRC_PATH = pathlib.Path(dirname(abspath(__file__)))


@st.cache(suppress_st_warning=True)
def read_markdown_file(file: str) -> str:
    """
    Read a markdown file and return as text.
    Args:
        file: name of file, which should be located in src/content/

    Returns:
    File text as a a string.
    """
    return (SRC_PATH / 'content' / file).read_text()


@st.cache(suppress_st_warning=True)
def create_metrics_dataset(sleep_scores: pd.DataFrame,
                           metabolic_scores: pd.DataFrame,
                           fasting_scores: pd.DataFrame) -> pd.DataFrame:
    """
    Inner join the fitness, metabolic, and fasting scores on date and create a date column.
    Args:
        sleep_scores: Daily sleep scores from Whoop.
        metabolic_scores: Daily metabolic scores from Levels.
        fasting_scores: Daily fasting scores from Zero Fasting.

    Returns: A pandas DataFrame of the joined metrics.

    """
    metrics = pd.concat([metabolic_scores, sleep_scores, fasting_scores], axis=1, sort=True, join='inner')\
        .round(2).reset_index()
    metrics.rename(columns={'index': 'Date'}, inplace=True)
    return metrics


@st.cache(suppress_st_warning=True)
def create_raw_analysis_dataset(sleep: pd.DataFrame, glucose: pd.Series) -> pd.DataFrame:
    """
    Create the full dataset for use in scatter plot analysis.
    First create subsets of glucose statistics by various grouping created:
        - glucose statistics (day)
        - glucose statistics (previous day)
        - glucose statistics (sleep)
    Outer join the glucose statistics dataFrames.
    Inner join with daily sleep data.

    Args:
        sleep: Sleep data uploaded to the app.
        glucose: Glucose data uploaded to the app.

    Returns: A wide pandas dataFrame of sleep and glucose statistics.
             Index values will be unique dates.
             Columns will be unique statistics (sleep or glucose related).

    """
    sleep_groups = gc.create_glucose_sleep_groups(glucose=glucose, sleep=sleep)
    day_groups = gc.create_glucose_day_groups(glucose=glucose)
    glucose_sleep_stats = gc.grouped_glucose_stats(groups=sleep_groups, time_label='Sleep')
    glucose_day_stats = gc.grouped_glucose_stats(groups=day_groups, time_label='Day')
    all_glucose_data = pd.concat([glucose_sleep_stats, glucose_day_stats], axis=1)
    sleep_numeric = sleep.copy().drop(columns=['Sleep Start', 'Sleep End'])
    all_data = all_glucose_data.merge(sleep_numeric, left_index=True, right_index=True).round(2).reset_index()
    all_data.rename(columns={'index': 'Date'}, inplace=True)

    return all_data


@st.cache(suppress_st_warning=True)
def corr_matrix_long(parameters: pd.DataFrame, date_column: str = None) -> pd.DataFrame:
    """
    Create a long format correlation 'matrix'. Columns include 'x', 'y', and 'correlation'.
    Args:
        parameters: A pandas DataFrame of measurements.
        date_column: Date column, if it exists, in the parameters DataFrame.

    Returns: The correlations of each parameter pair (x-y) in long format.

    """
    if date_column:
        parameters = parameters.copy().drop(columns=[date_column])
    correlations = parameters.corr().reset_index().melt('index')
    correlations.columns = ['x', 'y', 'correlation']
    return correlations


@st.cache(suppress_st_warning=True)
def corr_matrix(parameters: pd.DataFrame, date_column: str = None) -> pd.DataFrame:
    """
    Create a square format correlation 'matrix'. Indexes and columns will match.
    Args:
        parameters: A pandas DataFrame of measurements.
        date_column: Date column, if it exists, in the parameters DataFrame.

    Returns: The correlations as a matrix.

    """
    if date_column:
        parameters = parameters.copy().drop(columns=[date_column])
    matrix = parameters.corr()
    return matrix


@st.cache(suppress_st_warning=True)
def create_dates(dates: [str]) -> [dt.date]:
    """
    Create a list of dates as datetime.date objects.
    Args:
        dates: A list of dates in string format: '%Y-%m-%d'.

    Returns: The list of dates.

    """
    dates_list = [dt.datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
    return dates_list


@st.cache()
def profile_report(summary_data: pd.DataFrame) -> ProfileReport:
    """
    Create a pandas_profiling profile report to embed in the Streamlit app or Jupyter Notebook
    Args:
        summary_data: Dataset to be analyzed.

    Returns: The profile report.

    """
    pr = ProfileReport(summary_data, explorative=True)
    return pr


def variables_for_plot(dataset: pd.DataFrame,
                       date_col: str = 'Date',
                       default_x: str = None,
                       default_y: str = None,
                       default_c: str = None,
                       app_section: str = 'user') -> (str, str, str):
    """
    Get user selected parameters for plot x-axis, y-axis, and optionally, the marker color gradient.
    Args:
        app_section: section of app where function is called from. String used to set streamlit widget keys.
        dataset: pandas dataFrame used for plotting. Expect a 'Date' column and a unique statistics for all other
        columns.
        default_x: default parameter desired for x axis of scatter plot.
        default_y: default parameter desired for y axis of scatter plot.
        default_c: default parameter desired for color scheme of scatter plot.
        date_col: Name of date column to be removed from selection options.

    Returns: parameter selections for the x-axis, y-axis, and the marker color gradient as strings.

    """

    all_cols = sorted(dataset)
    all_cols.insert(0, '<select>')
    all_cols_no_date = all_cols.copy()
    all_cols_no_date.remove(date_col)

    x_default, y_default, c_default = 0, 0, 0

    if default_x:
        x_default = all_cols_no_date.index(default_x)
    if default_y:
        y_default = all_cols_no_date.index(default_y)
    if default_c:
        c_default = all_cols_no_date.index(default_c)

    x_key = app_section + '_x'
    y_key = app_section + '_y'
    c_key = app_section + '_c'
    x_axis_col, y_axis_col, color_col = st.beta_columns(3)
    x = x_axis_col.selectbox(label='X-Axis', options=all_cols_no_date, index=x_default, key=x_key)
    y = y_axis_col.selectbox(label='Y-Axis', options=all_cols_no_date, index=y_default, key=y_key)
    color = color_col.selectbox(label='OPTIONAL: Color Gradient',
                                options=all_cols_no_date,
                                index=c_default,
                                key=c_key)

    return x, y, color

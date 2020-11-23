import pandas as pd
import streamlit as st
import numpy as np
import altair as alt
import pathlib
from os.path import abspath, dirname

SRC_PATH = pathlib.Path(dirname(abspath(__file__)))


@st.cache(suppress_st_warning=True)
def read_markdown_file(file:str) -> str:
    """
    Read a markdown file and return as text.
    Args:
        file: name of file, which should be located in src/content/

    Returns:
    File text as a a string.
    """
    return (SRC_PATH / 'content' / file).read_text()


@st.cache(suppress_st_warning=True)
def read_markdown_file(file:str) -> str:
    """
    Read a markdown file and return as text.
    Args:
        file: name of file, which should be located in src/content/

    Returns:
    File text as a a string.
    """
    return (SRC_PATH / 'content' / file).read_text()


@st.cache(suppress_st_warning=True)
def load_sleep_data(sleep_file) -> pd.DataFrame:
    """
    Load a Whoop sleep summary CSV file and return a pandas DataFrame version of the file
    Args:
        sleep_file: file to be converted to a DataFrame

    Returns: pandas DataFrame of sleep data
    """

    # TODO: split into 'read' and 'load' functions

    expected_cols = ['Date',
                     'Strain',
                     'Recovery',
                     'Sleep Score',
                     'RHR',
                     'Average HR',
                     'Max HR',
                     'Respiratory Rate',
                     'HRV (ms)',
                     'Sleep (hr)',
                     'Sleep Start',
                     'Sleep End']
    try:
        raw_sleep = pd.read_csv(sleep_file,
                                header=0,
                                parse_dates=['Date'],
                                index_col='Date',
                                usecols=expected_cols
                                )
    except ValueError:
        st.error(f"""
        Incorrect format of sleep data CSV. Please make sure you uploaded the correct file.
        \nThe following columns must be present in the first row:
        \n {expected_cols}
        """)
        raise
    raw_sleep['Sleep Start'] = raw_sleep['Sleep Start'].astype('datetime64[ms]')
    raw_sleep['Sleep End'] = raw_sleep['Sleep End'].astype('datetime64[ms]')
    return raw_sleep


@st.cache(suppress_st_warning=True)
def load_glucose_data(glucose_file, timezone: str) -> pd.DataFrame:
    """
    Load a FreeStyle LibreLink CSV file and return a pandas DataFrame version of the file
    Args:
        timezone: Expected timezone of the glucose data
        glucose_file: file to be converted to a DataFrame

    Returns: pandas DataFrame of glucose data
    """

    # TODO: split into 'read' and 'load' functions

    expected_cols = ['Device Timestamp',
                     'Record Type',
                     'Historic Glucose mg/dL']

    try:
        raw_glucose = pd.read_csv(glucose_file,
                                  header=1,
                                  usecols=expected_cols,
                                  parse_dates=['Device Timestamp'],
                                  index_col='Device Timestamp'
                                  )
    except ValueError:
        st.error(f"""
        Incorrect format of glucose data CSV. Please make sure you uploaded the correct file.
        \ntThe following columns must be present in the second row:
        \n {expected_cols}
        """)
        raise

    glucose_utc_time = raw_glucose.tz_localize(timezone, ambiguous='NaT').tz_convert(None)
    clean_glucose = glucose_utc_time.loc[(glucose_utc_time['Record Type'] == 0)
                                         & (glucose_utc_time.index.notnull()),
                                         'Historic Glucose mg/dL'].rename('Glucose (mg/dL)')
    clean_glucose.index.rename('Timestamp', inplace=True)
    return clean_glucose


# Other option for aggregating statistics: aggregate over pandas.groupBy() groups.
# This would require creating temporary labels for every glucose sample.
# For example, label glucose samples by date, if sample timestamp is within date's sleep period.
# Then groupBy(label) and aggregate.
# For now, keep the single series and dict iterating method for flexibility.
# In the future, pass in statistics to be calculated (out of box or custom).
def glucose_stats(glucose: pd.Series, time_label: str = None) -> pd.Series:
    """
    Aggregate statistics over a series of glucose data and return the statistics as a series.
    Optionally, add an additional time label associated with the series (i.e. 'Day', 'Previous Day', 'Sleep').
    Args:
        time_label: Optional label.
        glucose: pandas Series to aggregate over.

    Returns: Aggregated statistics as a pandas Series.

    """

    if time_label:
        time_unit = f" ({time_label})"
    else:
        time_unit = ""
    stats = glucose.agg(gc_mean='mean', gc_std='std', gc_min='min', gc_max='max')
    stats.rename(index={"gc_mean": "Glucose Mean" + time_unit,
                        "gc_std": "Glucose Volatility" + time_unit,
                        "gc_min": "Glucose Minimum" + time_unit,
                        "gc_max": "Glucose Maximum" + time_unit},
                 inplace=True)
    return stats


@st.cache(suppress_st_warning=True)
def grouped_glucose_stats(groups: dict, time_label: str = None) -> pd.Series:
    """
    Aggregate statistics over multiple series of glucose data. Each series will be passed to glucose_stats(), and
    combined into a single dataFrame. Optionally, add an additional time label associated with the series
    (i.e. 'Day', 'Previous Day', 'Sleep'). Example use would be a collection of series, one for every day,
    or sleep period.
    Args:
        time_label: Optional label.
        groups: Dictionary of groups, keys can be anything, but values should be a subseries of glucose data associated
                with the key. Keys will then be the index values of the returned dataFrame. Most common practice is to
                store a date as the key.

    Returns: A pandas dataFrame of aggregated statistics for a group of glucose subseries.
             dataFrame index values from groups dictionary keys.
             dataFrame columns will be statistics calculated in glucose_stats().

    """
    all_stats = {}
    for key, glucose in groups.items():
        stats = glucose_stats(glucose=glucose, time_label=time_label)
        all_stats[key] = stats
    all_stats_grouped = pd.DataFrame.from_dict(all_stats, orient='index')

    return all_stats_grouped


@st.cache(suppress_st_warning=True)
def create_glucose_day_groups(glucose: pd.Series) -> dict:
    """
    Create a dictionary of glucose series, unique to each day in the parent glucose series.
    Keys will be unique dates in the parent series.
    Values will be the subseries with timestamp dates matching the key.

    Args:
        glucose: A pandas Series of glucose measurements.

    Returns: The dictionary of subsamples.

    """
    day_groups = dict(list(glucose.groupby(glucose.index.date)))
    return day_groups


# Other option is take a day_stats dataFrame and shift index by 1 day,
# but, would have to adjust column names for correct time label (day) -> (previous day)
@st.cache(suppress_st_warning=True)
def create_glucose_previous_day_groups(day_groups: dict) -> dict:
    """
    Create a dictionary of glucose subseries, unique to each day in the parent glucose series.
    Subseries data of each dictionary item will lag item key (date) by 1 day.
    Keys will be (unique dates in the parent series) + 1 day.
    Values will be the subseries with timestamp dates matching 1 day prior to the key.

    Args:
        day_groups: A dictionary of daily glucose series.
                    Keys individual dates with glucose data.
                    Values will be the glucose subseries with timestamp dates matching the key.

    Returns: The dictionary of glucose subsamples.
             Keys will be (unique dates in the parent series) + 1 day.
             Values will be the subseries with timestamp dates matching 1 day prior to the key.
    """
    previous_day_groups = {}
    for previous_day, previous_glucose in day_groups.items():
        today = previous_day + pd.Timedelta('1D')
        previous_day_groups[today] = previous_glucose
    return previous_day_groups


@st.cache(suppress_st_warning=True)
def create_glucose_sleep_groups(glucose: pd.Series, sleep: pd.DataFrame) -> dict:
    """
    Create a dictionary of glucose series, unique to each day where both sleep and glucose data are available.
    Keys will be unique dates.
    Values will be the subseries with timestamp dates matching the key.
    Args:
        sleep: pandas DataFrame containing sleep data. Required date index, and 'Sleep Start' and 'Sleep End' columns.
        glucose: pandas Series of glucose data.

    Returns: Dictionary of glucose subseries.
             Keys are unique dates of sleep.
             Values are the subseries of glucose measurements during the sleep period for key date.

    """
    glucose_days = np.unique(glucose.index.date)
    sleep_days = sleep.index
    glucose_sleep_days = sleep_days[sleep_days.isin(glucose_days)]

    groups = {}
    for day in glucose_sleep_days:
        period = (glucose.index >= sleep.loc[day]['Sleep Start']) \
                 & (glucose.index <= sleep.loc[day]['Sleep End'])
        sleeping_glucose = glucose[period]
        if sleeping_glucose.empty:  # handle edge case: dates match, but no glucose data in sleep time period
            continue
        groups[day] = sleeping_glucose

    return groups


@st.cache(suppress_st_warning=True)
def create_analysis_dataset(sleep: pd.DataFrame, glucose: pd.Series) -> pd.DataFrame:
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
    sleep_groups = create_glucose_sleep_groups(glucose=glucose, sleep=sleep)
    day_groups = create_glucose_day_groups(glucose=glucose)
    previous_day_groups = create_glucose_previous_day_groups(day_groups=day_groups)
    glucose_sleep_stats = grouped_glucose_stats(groups=sleep_groups, time_label='Sleep')
    glucose_day_stats = grouped_glucose_stats(groups=day_groups, time_label='Day')
    glucose_previous_day_stats = grouped_glucose_stats(groups=previous_day_groups,
                                                       time_label='Previous Day')
    all_glucose_data = pd.concat([glucose_sleep_stats, glucose_day_stats, glucose_previous_day_stats], axis=1)
    sleep_numeric = sleep.copy().drop(columns=['Sleep Start', 'Sleep End'])
    all_data = all_glucose_data.merge(sleep_numeric, left_index=True, right_index=True).round(2).reset_index()
    all_data.rename(columns={'index': 'Date'}, inplace=True)

    return all_data


def create_scatter(dataset: pd.DataFrame, x_selection: str, y_selection: str, color_selection: str) -> alt.Chart:
    """
    Create an interactive altair scatter plot with user defined x and y parameters as well as an optional third
    parameter used for marker color gradient.
    Args:
        dataset: dataFrame containing selected parameters.
        x_selection: Parameter to plot along the x-axis.
        y_selection: Parameter to plot along the y-axis.
        color_selection: Parameter to use for scatter marker color gradient (parameter options are numeric intervals)

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


def variables_for_plot(dataset: pd.DataFrame, app_section: str = 'user') -> (str, str, str):
    """
    Get user selected parameters for plot x-axis, y-axis, and optionally, the marker color gradient.
    Args:
        app_section: section of app where function is called from. String used to set streamlit widget keys.
        dataset: pandas dataFrame used for plotting. Expect a 'Date' column and a unique statistics for all other
        columns.

    Returns: parameter selections for the x-axis, y-axis, and the marker color gradient as strings.

    """

    all_cols = sorted(dataset)
    all_cols.insert(0, '<select>')
    all_cols_no_date = all_cols.copy()
    all_cols_no_date.remove('Date')
    x_default = all_cols.index('Sleep Score')
    y_default = all_cols.index('Glucose Volatility (Previous Day)')
    c_default = all_cols_no_date.index('Recovery')

    x_key = app_section + '_x'
    y_key = app_section + '_y'
    c_key = app_section + '_c'
    x_axis_col, y_axis_col, color_col = st.beta_columns(3)
    x = x_axis_col.selectbox(label='X-Axis', options=all_cols, index=x_default, key=x_key)
    y = y_axis_col.selectbox(label='Y-Axis', options=all_cols, index=y_default, key=y_key)
    color = color_col.selectbox(label='OPTIONAL: Color Gradient',
                                options=all_cols_no_date,
                                index=c_default,
                                key=c_key)

    return x, y, color

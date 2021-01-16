import pandas as pd
import streamlit as st
import numpy as np
import pathlib
from os.path import abspath, dirname
import datetime

SRC_PATH = pathlib.Path(dirname(abspath(__file__)))


# @st.cache(suppress_st_warning=True)
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


# @st.cache(suppress_st_warning=True)
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


# @st.cache(suppress_st_warning=True)
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
# @st.cache(suppress_st_warning=True)
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


# @st.cache(suppress_st_warning=True)
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


# def set_duration_start_end(start: pd.Series, duration_minutes: int) -> dict:
#     duration_delta = pd.timedelta(duration_minutes, 'minutes')
#     end = start.copy + duration_delta
#     all_start_end = # MERGE START AND END TOGETHER
#     return all_start_end


def sub_period_glucose(glucose: pd.Series, start: datetime, end: datetime) -> pd.Series:
    period = (glucose.index >= start) & (glucose.index <= end)
    sub_glucose = glucose[period]
    if sub_glucose.empty:  # handle edge case: no glucose data in period
        return None
    else:
        return sub_glucose


def period_group_glucose(glucose: pd.Series, all_start_end: pd.DataFrame):
    all_period_glucose = {}
    for period in all_start_end:
        period_glucose = sub_period_glucose(glucose=glucose, start=period.start, end=period.end)
        if period_glucose:  # NEED TO CHECK IF NOT NONE
            key = period.index
            all_period_glucose[key] = period_glucose
    return all_period_glucose

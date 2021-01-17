import pandas as pd
import streamlit as st


@st.cache(suppress_st_warning=True)
def load_zero_data(fast_file) -> pd.DataFrame:
    """
    Load a Zero Fasting data export CSV file and return a pandas DataFrame version of the file.
    DataFrame is reindexed chronologically, oldest to newest, before returned.
    Args:
        fast_file: file to be converted to a DataFrame.

    Returns: pandas DataFrame of sleep data.
    """
    expected_cols = ['Date', 'Start', 'End', 'Hours', 'Night Eating']
    try:
        fasts = pd.read_csv(fast_file,
                            header=0,
                            parse_dates=['Date'],
                            usecols=expected_cols)
    except ValueError:
        st.error(f"""
        Incorrect format of fast data CSV. Please make sure you uploaded the correct file.
        \nThe following columns must be present in the first row:
        \n {expected_cols}
        """)
        raise
    fasts = fasts.iloc[::-1].reset_index(drop=True)  # order by oldest to newest
    return fasts


@st.cache(suppress_st_warning=True)
def fasts_start_end(fasts: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the start and end datetimes of each logged fast from a file exported from Zero Fasting.
    Args:
        fasts: The Zero Fasting file export as a pandas DataFrame.

    Returns: A DataFrame with the start and end datetimes as individuals columns.

    """
    start_times = pd.to_datetime(fasts['Start']).dt.strftime('%H:%M:%S')
    start_times_duration = pd.to_timedelta(start_times)
    end_times = pd.to_datetime(fasts['End']).dt.strftime('%H:%M:%S')
    end_times_duration = pd.to_timedelta(end_times)
    start_dates = fasts.Date
    start_dt = (start_dates + start_times_duration).rename('start_dt')
    end_dates = (start_dt + pd.to_timedelta(fasts.Hours, 'H')).dt.date
    end_dt = (pd.to_datetime(end_dates) + end_times_duration).rename('end_dt')
    start_end = pd.concat([start_dt, end_dt], axis=1)
    return start_end


@st.cache(suppress_st_warning=True)
def date_durations(start_end: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the durations of each fast, broken down by day (start and end days).

    Args:
        start_end: A pandas DataFrame of fasts with the start and end datetimes as columns
                   (output from zero.fasts_start_end()).

    Returns: A pandas DataFrame of fasts durations: start date duration, end date duration, total duration.

    """

    # TODO calculate for fasts longer than 24 hours

    start_duration = pd.Timedelta(24, 'h') - pd.to_timedelta(start_end.start_dt.dt.strftime('%H:%M:%S'))
    end_duration = pd.to_timedelta(start_end.end_dt.dt.strftime('%H:%M:%S'))
    start_hours = (start_duration / pd.Timedelta(1, 'h')).rename('start_hours')
    end_hours = (end_duration / pd.Timedelta(1, 'h')).rename('end_hours')
    total_hours = ((start_end.end_dt - start_end.start_dt) / pd.Timedelta('1H')).rename('total_hours')
    durations = pd.concat([start_hours, end_hours, total_hours], axis=1)
    return durations


def fasts_details(fasts: pd.DataFrame) -> pd.DataFrame:
    """
    Combine outputs from zero.fasts_start_end() and zero.date_durations() for a detailed dataset on the fasts.
    Args:
        fasts: The Zero Fasting file export as a pandas DataFrame.

    Returns: The combined pandas DataFrame.

    """
    start_end = fasts_start_end(fasts)
    durations = date_durations(start_end)
    details = pd.concat([start_end, durations], axis=1)
    return details


@st.cache(suppress_st_warning=True)
def fast_cumulative_consecutive(details: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate cumulative and consecutive hours of fasts for each day in a fast_details dataset.
    Args:
        details: DataFrame containing the durations for the start and end day of fasts, output from zero.fast_details().

    Returns: A pandas DataFrame with the cumulative and consecutive hours of fasts for each day.
             There are potentially 2 fasts occurring in a single day (one ends and another starts).
                - Cumulative fast hours is the sum of hours fasted throughout the day.
                - Consecutive fast hours is the maximum consecutive hours fasted up until the end of the day.
                    - This can include hours from previous day if it carries over to current day.

    """
    first_date = details.start_dt[0].date()
    last_date = details.end_dt.iat[-1].date()
    all_fast_dates = pd.date_range(start=first_date, end=last_date, freq='1D').date  # create dates not datetime
    stats = pd.DataFrame({'Fast (cumulative hours)': 0, 'Fast (consecutive hours)': 0}, index=all_fast_dates,
                         dtype=float)
    for index, fast in details.iterrows():
        start_date = fast["start_dt"].date()
        end_date = fast["end_dt"].date()
        stats.at[start_date, 'Fast (cumulative hours)'] += fast['start_hours']
        stats.at[start_date, 'Fast (consecutive hours)'] = max(fast['start_hours'],
                                                               stats.at[start_date, 'Fast (consecutive hours)'])
        stats.at[end_date, 'Fast (cumulative hours)'] += fast['end_hours']
        stats.at[end_date, 'Fast (consecutive hours)'] = max(fast['total_hours'],
                                                             stats.at[end_date, 'Fast (consecutive hours)'])
    return stats


@st.cache(suppress_st_warning=True)
def fasts_binned(cumulative_consecutive: pd.DataFrame) -> pd.DataFrame:
    """
    Bin consecutive and cumulative fasting hours stats from 0-12, 13-15, 16-18, 18+ hours, 
    as well as a fasting benchmark (fasts? yes/no) cumulative hours by binning from 0-12, and 13+ hours.
    Args:
        cumulative_consecutive: Output from zero.fast_day_stats().

    Returns: Binnings as a pandas DataFrame with columns: Fast (consecutive hours), Fast (cumulative hours), fasts.

    """
    consecutive_binned = pd.cut(x=cumulative_consecutive['Fast (consecutive hours)'],
                                bins=[-1, 12, 15, 18, 24],
                                labels=['0-12 hrs', '13-15 hrs', '16-18 hrs', '18+ hrs']).\
        rename('Fast Binned (consecutive hrs)')
    cumulative_binned = pd.cut(x=cumulative_consecutive['Fast (cumulative hours)'],
                               bins=[-1, 12, 15, 18, 24],
                               labels=['0-12 hrs', '13-15 hrs', '16-18 hrs', '18+ hrs']).\
        rename('Fast Binned (cumulative hrs)')
    fast = pd.cut(x=cumulative_consecutive['Fast (cumulative hours)'],
                  bins=[-1, 12, 24],
                  labels=['No', 'Yes']).rename('Fast')

    binned_fasts = pd.concat([consecutive_binned, cumulative_binned, fast], axis=1)
    return binned_fasts


@st.cache(suppress_st_warning=True)
def all_fasts_stats(fasts: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the daily cumulative and consecutive fasts durations and bin the fasts.
    Args:
        fasts: The Zero Fasting file export as a pandas DataFrame.

    Returns: The calculations and binned data indexed on date.

    """
    details = fasts_details(fasts)
    cumulative_consecutive = fast_cumulative_consecutive(details)
    binned = fasts_binned(cumulative_consecutive)
    all_stats = pd.concat([cumulative_consecutive, binned], axis=1)
    return all_stats

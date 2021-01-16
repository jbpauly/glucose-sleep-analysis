import pandas as pd
import streamlit as st


# @st.cache(suppress_st_warning=True)
def load_whoop_data(sleep_file) -> pd.DataFrame:
    """
    Load a Whoop daily summary CSV file and return a pandas DataFrame version of the file.
    Only read in a subset of columns defined by the expected_cols parameter.
    Args:
        sleep_file: file to be converted to a DataFrame.

    Returns: pandas DataFrame of daily Whoop summary data.
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
    raw_sleep.index = raw_sleep.index.date # change index from datetime to date
    return raw_sleep



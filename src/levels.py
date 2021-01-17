import pandas as pd
import streamlit as st


@st.cache(suppress_st_warning=True)
def load_levels_data(levels_file) -> pd.DataFrame:
    """
    Load a CSV file of Levels daily scores as a DataFrame.
    Args:
        levels_file: file to be converted to a DataFrame.

    Returns: pandas DataFrame of Levels daily scores.
    """
    expected_cols = ['Date', 'Levels Score (day)']

    try:
        levels = pd.read_csv(levels_file,
                             header=0, parse_dates=['Date'],
                             index_col='Date',
                             usecols=expected_cols)
    except ValueError:
        st.error(f"""
        Incorrect format of Levels data CSV. Please make sure you uploaded the correct file.
        \nThe following columns must be present in the first row:
        \n {expected_cols}
        """)
        raise
    levels.index = levels.index.date # change index from datetime to date
    return levels

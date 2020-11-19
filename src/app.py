import streamlit as st
import utilities as util
from pytz import all_timezones
import pandas as pd

st.sidebar.header("Cross Analyze Your Sleep and Glucose Data")
st.sidebar.subheader("Chose a section:")
example_analysis_sb = st.sidebar.checkbox(
    "Run Example", value=True)

analyze_data_sb = st.sidebar.checkbox(
    "Analyze Your Data", value=False
)
default_tz_index = all_timezones.index('America/Chicago')


if example_analysis_sb:
    sample_dataset = pd.read_csv('src/sample.csv', parse_dates=['Date'], index_col=0)
    x_selection_sample, y_selection_sample, color_selection_sample = util.variables_for_plot(sample_dataset,
                                                                                             app_section='example')
    if x_selection_sample != '<select>' and y_selection_sample != '<select>':
        sample_plot = util.create_scatter(sample_dataset, x_selection_sample, y_selection_sample,
                                          color_selection_sample)
        st.altair_chart(sample_plot, use_container_width=True)


sleep_df = None
glucose_df = None
if analyze_data_sb:
    with st.beta_expander("Upload Data", expanded=False):
        tz_select_col, tz_verify_col = st.beta_columns((2, 1))
        time_zone = tz_select_col.selectbox("Select your timezone associated with your glucose data",
                                            options=all_timezones,
                                            index=default_tz_index
                                            )
        tz_verify_col.text("")
        tz_verify_col.text("")
        verified_tz = tz_verify_col.checkbox('Verify selected timezone', value=False)
        sleep_col, glucose_col = st.beta_columns(2)
        sleep_file = sleep_col.file_uploader("Upload Sleep Data", type=['csv'])
        glucose_file = glucose_col.file_uploader("Upload Glucose Data", type=['csv'])

        if sleep_file is not None and glucose_file is not None:
            sleep_df = util.load_sleep_data(sleep_file)
            if not verified_tz:
                st.error('Please verify the selected timezone for your glucose data for accurate pairing with your '
                         'sleep data.')
            else:
                glucose_df = util.load_glucose_data(glucose_file, time_zone)

    with st.beta_expander("Analyze Data", expanded=False):
        if sleep_df is not None and glucose_df is not None:
            all_data = util.create_analysis_dataset(sleep=sleep_df, glucose=glucose_df)

            x_selection, y_selection, color_selection = util.variables_for_plot(all_data,)
            if x_selection != '<select>' and y_selection != '<select>':
                plot = util.create_scatter(all_data, x_selection, y_selection, color_selection)
                st.altair_chart(plot, use_container_width=True)

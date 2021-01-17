import streamlit as st
import streamlit.components.v1 as components
import utilities as util
import plot
import pandas as pd
from PIL import Image
import levels as lv
import whoop as wp
import zero as zo


sample_file_path = util.SRC_PATH / 'sample.csv'
st.sidebar.subheader("Application Pages:")
st.markdown("""
# Metabolic Health and Sleep Analyzer
An application to cross analyze your sleep and metabolic health metrics.
""")
welcome_sb = st.sidebar.checkbox(
    "User Guide", value=True)
example_analysis_sb = st.sidebar.checkbox(
    "Run Example", value=False)
analyze_data_sb = st.sidebar.checkbox(
    "Analyze Your Data", value=False
)

st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
with st.sidebar.beta_expander("Meet the Developer"):
    me = Image.open(util.SRC_PATH /'content/me.jpeg')
    st.image(me, use_column_width=True,
    )
    meet_developer_file = util.read_markdown_file("meet_developer.md")
    st.markdown(meet_developer_file, unsafe_allow_html=True)

if welcome_sb:
    with st.beta_expander("Welcome!", expanded=True):
        welcome_file = util.read_markdown_file("welcome.md")
        st.markdown(welcome_file, unsafe_allow_html=True)

    with st.beta_expander("Get Started", expanded=True):
        get_started_file = util.read_markdown_file("get_started.md")
        st.markdown(get_started_file, unsafe_allow_html=True)
        components.iframe("https://www.loom.com/embed/62467100449b4c45bca5b603cfd573ac", height=430)


if example_analysis_sb:
    sample_dataset = pd.read_csv(sample_file_path, parse_dates=['Date'], index_col=0).round(2)
    corr_matrix = util.corr_matrix(sample_dataset, 'Date').round(2)
    corr_heatmap = plot.plotly_heatmap(corr_matrix)
    st.plotly_chart(corr_heatmap, use_container_width=True)
    x_selection_sample, y_selection_sample, color_selection_sample = util.variables_for_plot(sample_dataset,
                                                                                             app_section='example')
    if x_selection_sample != '<select>' and y_selection_sample != '<select>':
        scatter = plot.plotly_scatter(sample_dataset, x_selection_sample, y_selection_sample, color_selection_sample)
        line = plot.plotly_line(sample_dataset, x_selection_sample, y_selection_sample, 'Date')
        st.plotly_chart(scatter, use_container_width=True)
        st.plotly_chart(line, use_container_width=True)
        # sample_scatter = util.create_scatter(sample_dataset,
        #                                      x_selection_sample,
        #                                      y_selection_sample,
        #                                      color_selection_sample)
        # corr_matrix = util.create_correlation_matrix(sample_dataset, date_column='Date')
        # sample_corr = util.create_matrix_heatmap(corr_matrix,
        #                                          x_selection_sample,
        #                                          y_selection_sample)
        # st.altair_chart(sample_corr, use_container_width=True)
        # st.altair_chart(sample_scatter, use_container_width=True)

    # pr = util.profile_report(sample_dataset)
    # st_profile_report(pr)

fitness_scores = None
metabolic_scores = None
fasting_scores = None
if analyze_data_sb:
    with st.beta_expander("Upload Data", expanded=False):
        whoop_col, levels_col, zero_col = st.beta_columns(3)
        whoop_file = whoop_col.file_uploader("Upload Whoop Data", type=['csv'])
        levels_file = levels_col.file_uploader("Upload Levels Data", type=['csv'])
        zero_file = zero_col.file_uploader("Upload Zero Fasting Data", type=['csv'])
        if whoop_file is not None and levels_file is not None and zero_file is not None:
            fitness_scores = wp.load_whoop_data(whoop_file)
            metabolic_scores = lv.load_levels_data(levels_file)
            fasting = zo.load_zero_data(zero_file)
            fasting_scores = zo.all_fasts_stats(fasting)

    with st.beta_expander("Analyze Data", expanded=False):
        if fitness_scores is not None and metabolic_scores is not None and fasting_scores is not None:
            all_metrics = util.create_metrics_dataset(fitness_scores=fitness_scores,
                                                      metabolic_scores=metabolic_scores,
                                                      fasting_scores=fasting_scores,)

            x_selection, y_selection, color_selection = util.variables_for_plot(all_metrics, )
            if x_selection != '<select>' and y_selection != '<select>':
                scatter = plot.plotly_scatter(all_metrics, x_selection, y_selection,
                                              color_selection)
                line = plot.plotly_line(all_metrics, x_selection, y_selection, 'Date')
                st.plotly_chart(scatter, use_container_width=True)
                st.plotly_chart(line, use_container_width=True)

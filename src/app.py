import streamlit as st
import streamlit.components.v1 as components
from streamlit_pandas_profiling import st_profile_report
import utilities as util
import plot
import pandas as pd
from PIL import Image
import levels as lv
import whoop as wp
import zero as zo

sample_file_path = util.SRC_PATH / 'sample.csv'
data_dictionary_path = util.SRC_PATH / 'content' / 'metrics_data_dictionary.csv'
data_dictionary = pd.read_csv(data_dictionary_path, index_col='Label')
sample = pd.read_csv(sample_file_path, parse_dates=['Date'], index_col=0).round(2)

st.set_page_config(page_title='Metabolic Health',
                   page_icon='🔎',
                   layout='centered',
                   initial_sidebar_state='expanded')
st.sidebar.subheader("Application Pages:")
st.markdown("""
# Metabolic Health Analysis 
An application to cross analyze your metabolic health and lifestyle metrics.
""")
welcome_sb = st.sidebar.checkbox(
    "Welcome", value=True)
data_sb = st.sidebar.checkbox(
    "Data", value=False)
example_analysis_sb = st.sidebar.checkbox(
    "Analysis", value=False)
analyze_data_sb = st.sidebar.checkbox(
    "Analyze Your Data", value=False
)
more_info_sb = st.sidebar.checkbox(
    "Additional Information", value=False
)

st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")

with st.sidebar.beta_expander("Meet the Developer"):
    me = Image.open(util.SRC_PATH / 'content/me.jpeg')
    st.image(me, use_column_width=True,
             )
    meet_developer_file = util.read_markdown_file("meet_developer.md")
    st.markdown(meet_developer_file, unsafe_allow_html=True)

if welcome_sb:
    st.write("")
    with st.beta_expander("Welcome!", expanded=True):
        welcome_file = util.read_markdown_file("welcome.md")
        st.markdown(welcome_file, unsafe_allow_html=True)

if data_sb:
    st.write("")
    st.markdown("## Data")
    with st.beta_expander("Data Overview", expanded=True):
        data_overview_file = util.read_markdown_file("data/data_overview.md")
        st.markdown(data_overview_file, unsafe_allow_html=True)
        st.write(sample[0:4])
    with st.beta_expander("Metabolic Score", expanded=False):
        ms_file = util.read_markdown_file("data/metabolic_score.md")
        st.markdown(ms_file, unsafe_allow_html=True)
    with st.beta_expander("Fast (cumulative and consecutive hours)", expanded=False):
        fast_cc_file = util.read_markdown_file("data/fast_cc.md")
        st.markdown(fast_cc_file, unsafe_allow_html=True)
        fast_example = Image.open(util.SRC_PATH / 'content/data/fast_breakdown.jpg')
        st.image(fast_example, use_column_width=True, )
    with st.beta_expander("Fast Binned (cumulative and consecutive hours)", expanded=False):
        fast_binned_file = util.read_markdown_file("data/fast_binned.md")
        st.markdown(fast_binned_file, unsafe_allow_html=True)
    with st.beta_expander("Fast", expanded=False):
        fast_file = util.read_markdown_file("data/fast.md")
        st.markdown(fast_file, unsafe_allow_html=True)
    with st.beta_expander("Strain", expanded=False):
        strain_file = util.read_markdown_file("data/strain.md")
        st.markdown(strain_file, unsafe_allow_html=True)
    with st.beta_expander("Recovery", expanded=False):
        recovery_file = util.read_markdown_file("data/recovery.md")
        st.markdown(recovery_file, unsafe_allow_html=True)
    with st.beta_expander("Sleep Score", expanded=False):
        sleep_score_file = util.read_markdown_file("data/sleep_score.md")
        st.markdown(sleep_score_file, unsafe_allow_html=True)
    with st.beta_expander("Strain", expanded=False):
        sleep_file = util.read_markdown_file("data/sleep.md")
        st.markdown(sleep_file, unsafe_allow_html=True)

if example_analysis_sb:
    st.write("")
    st.markdown("## Analysis")
    st.write("")

    sample_dataset = sample
    sample_corr = util.corr_matrix(sample_dataset, 'Date').round(2)
    sample_heatmap = plot.plotly_heatmap(sample_corr)
    st.plotly_chart(sample_heatmap, use_container_width=True)

    with st.beta_expander("View Information on Pearson's Correlation Coefficient"):
        sample_pc = util.read_markdown_file("pearson_corr.md")
        st.markdown(sample_pc, unsafe_allow_html=True)
    with st.beta_expander("View Information on Ordinary Least Squares (OLS) Regression"):
        sample_ols = util.read_markdown_file("ols.md")
        st.markdown(sample_ols, unsafe_allow_html=True)

    with st.beta_expander("View Data Dictionary"):
        st.table(data_dictionary)

    x_selection_sample, y_selection_sample, color_selection_sample = util.variables_for_plot(sample_dataset,
                                                                                             date_col='Date',
                                                                                             default_x='Sleep Score',
                                                                                             default_y='Metabolic Score',
                                                                                             default_c='Fast',
                                                                                             app_section='sample')
    if x_selection_sample != '<select>' and y_selection_sample != '<select>':
        sample_scatter = plot.plotly_scatter(sample_dataset, x_selection_sample, y_selection_sample,
                                          color_selection_sample)
        sample_line = plot.plotly_line(sample_dataset, x_selection_sample, y_selection_sample, 'Date')
        st.plotly_chart(sample_scatter, use_container_width=True)
        st.plotly_chart(sample_line, use_container_width=True)

    # sample_report = st.checkbox("Generate Pandas Profile Report", key='sample')
    # if sample_report:
    #     sample_pr = util.profile_report(sample_dataset)
    #     st_profile_report(sample_pr)

fitness_scores = None
metabolic_scores = None
fasting_scores = None
if analyze_data_sb:
    st.write("")
    st.markdown("## Analyze Your Data")
    with st.beta_expander("Gather Data", expanded=True):
        get_started_file = util.read_markdown_file("instructions/get_started.md")
        st.markdown(get_started_file, unsafe_allow_html=True)

        levels_instruction_file = util.read_markdown_file("instructions/levels_instruction.md")
        levels_instruction_img = Image.open(util.SRC_PATH / 'content/instructions/levels_log.jpg')
        st.markdown(levels_instruction_file, unsafe_allow_html=True)
        st.image(levels_instruction_img, use_column_width=True, )

        zero_instruction_file = util.read_markdown_file("instructions/zero_instruction.md")
        zero_instruction_img = Image.open(util.SRC_PATH / 'content/instructions/zero_export.jpg')
        st.markdown(zero_instruction_file, unsafe_allow_html=True)
        st.image(zero_instruction_img, use_column_width=True, )

        whoop_instruction_file = util.read_markdown_file("instructions/whoop_instruction.md")
        st.markdown(whoop_instruction_file, unsafe_allow_html=True)
        components.iframe("https://www.loom.com/embed/0146ce68e8b14e408ae05c40d1bd1484", height=430)

        upload_instruction_file = util.read_markdown_file("instructions/upload.md")
        st.markdown(upload_instruction_file, unsafe_allow_html=True)

    with st.beta_expander("Upload Data", expanded=False):
        whoop_col, levels_col, zero_col = st.beta_columns(3)
        whoop_file = whoop_col.file_uploader("Upload Whoop Data", type=['csv'])
        levels_file = levels_col.file_uploader("Upload Levels Data", type=['csv'])
        zero_file = zero_col.file_uploader("Upload Zero Fasting Data", type=['csv'])
        if whoop_file is not None and levels_file is not None and zero_file is not None:
            fitness_scores = wp.load_whoop_data(whoop_file)
            sleep_scores = wp.sleep_metrics(fitness_scores)
            metabolic_scores = lv.load_levels_data(levels_file)
            fasting = zo.load_zero_data(zero_file)
            fasting_scores = zo.all_fasts_stats(fasting)

    with st.beta_expander("Analyze Data", expanded=False):
        st.write("")
        if sleep_scores is not None and metabolic_scores is not None and fasting_scores is not None:
            dd_column, pc_column, ols_column = st.beta_columns(3)

            view_dd = dd_column.checkbox("Data Dictionary")
            view_pc = pc_column.checkbox("Pearson's Correlation Coefficient")
            view_ols = ols_column.checkbox("Ordinary Least Squares Regression")
            if view_dd:
                st.table(data_dictionary)
            if view_pc:
                pc_file = util.read_markdown_file("pearson_corr.md")
                st.markdown(pc_file, unsafe_allow_html=True)
            if view_ols:
                ols_file = util.read_markdown_file("ols.md")

                st.markdown(ols_file, unsafe_allow_html=True)

            st.write("")

            all_metrics = util.create_metrics_dataset(sleep_scores=sleep_scores,
                                                      metabolic_scores=metabolic_scores,
                                                      fasting_scores=fasting_scores, )
            corr_matrix = util.corr_matrix(all_metrics, 'Date').round(2)
            corr_heatmap = plot.plotly_heatmap(corr_matrix)
            st.plotly_chart(corr_heatmap, use_container_width=True)

            x_selection, y_selection, color_selection = util.variables_for_plot(all_metrics,
                                                                                date_col='Date',
                                                                                default_x='Sleep Score',
                                                                                default_y='Metabolic Score',
                                                                                default_c='Fast',
                                                                                app_section='user')
            if x_selection != '<select>' and y_selection != '<select>':
                scatter = plot.plotly_scatter(all_metrics, x_selection, y_selection, color_selection)
                line = plot.plotly_line(all_metrics, x_selection, y_selection, 'Date')
                st.write("")
                st.plotly_chart(scatter, use_container_width=True)
                st.plotly_chart(line, use_container_width=True)

            # get_report = st.checkbox("Generate Pandas Profile Report", key = 'user')
            # if get_report:
            #     pr = util.profile_report(all_metrics)
            #     st_profile_report(pr)

if more_info_sb:
    st.markdown("## Additional Information")
    more_info_file = util.read_markdown_file("more_info/odds_ends.md")
    st.markdown(more_info_file, unsafe_allow_html=True)
    with st.beta_expander("Levels Health", expanded=False):
        levels_file = util.read_markdown_file("more_info/levels.md")
        st.markdown(levels_file, unsafe_allow_html=True)
        levels = Image.open(util.SRC_PATH / 'content/more_info/levels.jpg')
        st.image(levels, use_column_width=True, )
    with st.beta_expander("Zero Fasting", expanded=False):
        zero_file = util.read_markdown_file("more_info/zero.md")
        st.markdown(zero_file, unsafe_allow_html=True)
        zero = Image.open(util.SRC_PATH / 'content/more_info/zero.png')
        st.image(zero, use_column_width=True, )
    with st.beta_expander("Whoop", expanded=False):
        whoop_file = util.read_markdown_file("more_info/whoop.md")
        st.markdown(whoop_file, unsafe_allow_html=True)
        whoop = Image.open(util.SRC_PATH / 'content/more_info/whoop.jpg')
        st.image(whoop, use_column_width=True, )

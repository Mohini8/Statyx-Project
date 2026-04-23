import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from services.statistics_service import (
    descriptive_statistics,
    build_overall_categorical_table
)

from services.report_service import generate_statistics_report
import os


@st.cache_data
def cached_descriptive_stats(df_key):
    """Cache descriptive statistics calculation to avoid recalculation on every rerun."""
    df = st.session_state.get("df")
    if df is None:
        return None
    return descriptive_statistics(df)


@st.cache_data
def cached_categorical_table(df_key):
    """Cache categorical summary table to avoid recalculation on every rerun."""
    df = st.session_state.get("df")
    if df is None:
        return None
    return build_overall_categorical_table(df)


@st.cache_data
def get_cached_column_counts(col_name, df_key):
    """Cache value counts for each column to avoid recalculation."""
    df = st.session_state.get("df")
    if df is None or col_name not in df.columns:
        return None, None
    counts = df[col_name].value_counts(dropna=False)
    perc = (counts / counts.sum()) * 100
    return counts, perc


def build_categorical_chart(summary_df, col, chart_type, sort, labels, color, 
                            title, title_size, axis_size, width, height, bg, grid, legend):
    """Build a single categorical chart with given parameters."""
    plot_df = summary_df.copy()
    
    if sort == "Descending":
        plot_df = plot_df.sort_values("Count", ascending=False)
    elif sort == "Ascending":
        plot_df = plot_df.sort_values("Count", ascending=True)

    if chart_type == "Column":
        fig = px.bar(plot_df, x=plot_df.index, y="Count",
                     text="Count" if labels else None)
    else:
        fig = px.bar(plot_df, y=plot_df.index, x="Count",
                     orientation="h",
                     text="Count" if labels else None)

    fig.update_traces(marker_color=color, width=width)

    fig.update_layout(
        title=dict(text=title, font=dict(size=title_size)),
        height=height,
        plot_bgcolor=bg,
        paper_bgcolor=bg,
        showlegend=legend,
        xaxis=dict(showgrid=grid, tickfont=dict(size=axis_size)),
        yaxis=dict(showgrid=grid, tickfont=dict(size=axis_size))
    )
    
    return fig


def render():

    # =====================================================
    # 🎨 SAAS UI (CLEAN + MODERN)
    # =====================================================
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #edf5ff, #f8fbff);
        font-family: 'Inter', sans-serif;
    }

    .card {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 15px;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.06);
    }

    .section-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .stButton>button {
        background: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 0.4rem 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="section-title">📊 Statistical Analysis</div>
        <div>Automated insights • Interactive charts • Research-grade reporting</div>
    </div>
    """, unsafe_allow_html=True)

    df = st.session_state.get("df", None)

    if df is None:
        st.warning("Upload data first")
        return

    report_data = []
    
    # Create a cache key based on dataframe shape/content
    df_key = (df.shape[0], df.shape[1], tuple(df.columns), id(df))

    # =====================================================
    # 📊 NUMERICAL SUMMARY
    # =====================================================
    desc = cached_descriptive_stats(df_key)

    if desc is not None:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("### 📈 Numerical Summary")
        st.dataframe(desc, use_container_width=True)

        st.markdown("### 🧠 Insights")

        for col in desc.index:

            mean = df[col].mean()
            std = df[col].std()

            insight = f"""
            **{col}** → Mean: **{mean:.2f}**, Std: **{std:.2f}**.
            Distribution appears {"highly variable" if std > mean else "stable"}.
            """

            st.write(insight)

        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # 📊 CATEGORICAL SUMMARY
    # =====================================================
    cat_cols = list(df.select_dtypes(include="object").columns)

    if len(cat_cols) > 0:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("### 🧩 Categorical Overview")

        overall_cat = cached_categorical_table(df_key)
        if overall_cat is not None:
            st.dataframe(overall_cat, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # 📊 ADVANCED CATEGORY ANALYSIS
    # =====================================================
    for col in cat_cols:

        counts, perc = get_cached_column_counts(col, df_key)
        if counts is None:
            continue

        summary_df = pd.DataFrame({
            "Count": counts,
            "Percentage (%)": perc.round(2)
        })

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown(f"### 🔹 {col}")
        st.dataframe(summary_df, use_container_width=True)

        # ----------------------------
        # 🎛️ CONTROL PANEL
        # ----------------------------
        with st.expander("⚙️ Customize Chart", expanded=False):

            col1, col2, col3, col4 = st.columns(4)

            chart_type = col1.selectbox("Type", ["Column", "Bar"], key=f"{col}_type")
            sort = col2.selectbox("Sort", ["None", "Descending", "Ascending"], key=f"{col}_sort")
            labels = col3.checkbox("Labels", True, key=f"{col}_labels")
            legend = col4.checkbox("Legend", True, key=f"{col}_legend")

            color = st.color_picker("Color", "#d97706", key=f"{col}_color")

            # Advanced
            t1, t2, t3 = st.columns(3)
            title = t1.text_input("Title", f"Distribution of {col}", key=f"{col}_title")
            title_size = t2.slider("Title Size", 10, 40, 18, key=f"{col}_ts")
            axis_size = t3.slider("Axis Size", 8, 25, 12, key=f"{col}_as")

            a1, a2, a3 = st.columns(3)
            width = a1.slider("Bar Width", 0.1, 1.0, 0.4, key=f"{col}_bw")
            height = a2.slider("Height", 300, 800, 420, key=f"{col}_h")
            bg = a3.color_picker("Background", "#ffffff", key=f"{col}_bg")

            grid = st.checkbox("Grid", True, key=f"{col}_grid")

        # ----------------------------
        # 📊 BUILD CHART (ONLY WHEN SETTINGS CHANGE)
        # ----------------------------
        # Create unique hash of current settings to detect changes
        chart_settings = (chart_type, sort, labels, legend, color, title, title_size, 
                         axis_size, width, height, bg, grid)
        settings_key = f"{col}_settings_hash"
        
        # Only rebuild chart if settings have changed
        current_hash = hash(chart_settings)
        last_hash = st.session_state.get(settings_key)
        
        if current_hash != last_hash or f"{col}_fig" not in st.session_state:
            # Settings changed, rebuild chart
            fig = build_categorical_chart(summary_df, col, chart_type, sort, labels, 
                                         color, title, title_size, axis_size, width, height, bg, grid, legend)
            st.session_state[f"{col}_fig"] = fig
            st.session_state[settings_key] = current_hash
        else:
            # Settings unchanged, use cached chart
            fig = st.session_state.get(f"{col}_fig")

        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # ----------------------------
        # 🧠 INTERPRETATION
        # ----------------------------
        dominant = counts.idxmax()
        pct = perc.loc[dominant]

        st.markdown(
            f"**Insight:** {dominant} dominates with **{pct:.1f}%** share."
        )

        report_data.append({
            "column": col,
            "table": summary_df,
            "interpretation": f"{dominant} dominates ({pct:.1f}%)"
        })

        st.markdown('</div>', unsafe_allow_html=True)

    # =====================================================
    # 📥 REPORT ENGINE (CACHED)
    # =====================================================
    if report_data:

        st.markdown("### 📥 Export Reports")

        try:
            if "word_report" not in st.session_state or st.session_state.word_report is None:
                path = generate_statistics_report(df, report_data, "docx")

                if path and os.path.exists(path):
                    with open(path, "rb") as f:
                        st.session_state.word_report = f.read()
                else:
                    st.error("Word report generation failed")
                    st.session_state.word_report = None

        except Exception as e:
            st.error(f"Error generating Word report: {e}")
            st.session_state.word_report = None

        try:
            if "pdf_report" not in st.session_state or st.session_state.pdf_report is None:
                path = generate_statistics_report(df, report_data, "pdf")

                if path and os.path.exists(path):
                    with open(path, "rb") as f:
                        st.session_state.pdf_report = f.read()
                else:
                    st.error("PDF report generation failed")
                    st.session_state.pdf_report = None

        except Exception as e:
            st.error(f"Error generating PDF report: {e}")
            st.session_state.pdf_report = None

        c1, c2 = st.columns(2)

        with c1:
            if st.session_state.get("word_report"):
                st.download_button("Download Word", st.session_state.word_report, "report.docx")
            else:
                st.warning("Word report not available")

        with c2:
            if st.session_state.get("pdf_report"):
                st.download_button("Download PDF", st.session_state.pdf_report, "report.pdf")
            else:
                st.warning("PDF report not available")
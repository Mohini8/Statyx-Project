import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from services.Dataset_Service import get_session_df
from utils.Column_Utils import get_numeric_columns, get_categorical_columns, get_all_columns

COLOR_PALETTES = {
    "Blue": px.colors.sequential.Blues,
    "Viridis": px.colors.sequential.Viridis,
    "Plasma": px.colors.sequential.Plasma,
    "Turbo": px.colors.sequential.Turbo,
    "Pastel": px.colors.qualitative.Pastel,
    "Set2": px.colors.qualitative.Set2,
    "Bold": px.colors.qualitative.Bold,
}

COLOR_SEQUENCES = {
    "Blue": "#3b82f6",
    "Indigo": "#6366f1",
    "Teal": "#14b8a6",
    "Rose": "#f43f5e",
    "Amber": "#f59e0b",
    "Emerald": "#10b981",
}


def render():
    st.markdown("## Visualization Module")

    df = get_session_df()
    if df is None:
        st.warning("No dataset loaded. Please upload a file in the Upload module first.")
        return

    numeric_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)
    all_cols = get_all_columns(df)

    chart_type = st.selectbox(
        "Chart Type",
        ["Histogram", "Bar Chart", "Line Chart", "Scatter Plot", "Box Plot",
         "Violin Plot", "Pie Chart", "Heatmap", "Scatter Matrix"],
    )

    # Common settings
    with st.expander("Chart Settings", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            chart_width = st.slider("Width (px)", 400, 1400, 900, key="chart_w")
        with col2:
            chart_height = st.slider("Height (px)", 300, 900, 500, key="chart_h")
        with col3:
            color_name = st.selectbox("Color", list(COLOR_SEQUENCES.keys()), key="chart_color")

    base_color = COLOR_SEQUENCES[color_name]
    template = "plotly_white"

    fig = None

    if chart_type == "Histogram":
        if not numeric_cols:
            st.info("No numeric columns available.")
            return
        col = st.selectbox("Column", numeric_cols, key="hist_col")
        bins = st.slider("Number of bins", 5, 100, 30, key="hist_bins")
        color_by = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="hist_color")
        
        fig = px.histogram(
            df, x=col,
            nbins=bins,
            color=color_by if color_by != "None" else None,
            title=f"Histogram: {col}",
            template=template,
            color_discrete_sequence=[base_color],
        )
        fig.update_layout(bargap=0.05)

    elif chart_type == "Bar Chart":
        col = st.selectbox("X-axis (categorical)", all_cols, key="bar_x")
        if numeric_cols:
            y_col = st.selectbox("Y-axis (numeric)", ["Count"] + numeric_cols, key="bar_y")
        else:
            y_col = "Count"
        color_by = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="bar_color")
        orientation = st.radio("Orientation", ["Vertical", "Horizontal"], key="bar_orient")

        if y_col == "Count":
            data = df[col].value_counts().reset_index()
            data.columns = [col, "Count"]
            if orientation == "Vertical":
                fig = px.bar(data, x=col, y="Count", title=f"Count of {col}",
                             template=template, color_discrete_sequence=[base_color])
            else:
                fig = px.bar(data, x="Count", y=col, orientation="h",
                             title=f"Count of {col}", template=template,
                             color_discrete_sequence=[base_color])
        else:
            fig = px.bar(
                df, x=col, y=y_col,
                color=color_by if color_by != "None" else None,
                title=f"{y_col} by {col}",
                template=template,
                color_discrete_sequence=[base_color],
            )

    elif chart_type == "Line Chart":
        if not numeric_cols:
            st.info("No numeric columns available.")
            return
        x_col = st.selectbox("X-axis", all_cols, key="line_x")
        y_cols = st.multiselect("Y-axis (select 1 or more)", numeric_cols, default=numeric_cols[:1], key="line_y")
        if not y_cols:
            st.info("Select at least one Y-axis column.")
            return
        fig = px.line(df, x=x_col, y=y_cols, title=f"Line Chart", template=template)

    elif chart_type == "Scatter Plot":
        if len(numeric_cols) < 2:
            st.info("Need at least 2 numeric columns.")
            return
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
        with col2:
            y_col = st.selectbox("Y-axis", [c for c in numeric_cols if c != x_col], key="scatter_y")
        color_by = st.selectbox("Color by (optional)", ["None"] + cat_cols + numeric_cols, key="scatter_color")
        size_by = st.selectbox("Size by (optional)", ["None"] + numeric_cols, key="scatter_size")
        trendline = st.checkbox("Show trendline", value=False, key="scatter_trend")

        fig = px.scatter(
            df, x=x_col, y=y_col,
            color=color_by if color_by != "None" else None,
            size=size_by if size_by != "None" else None,
            trendline="ols" if trendline else None,
            title=f"Scatter: {x_col} vs {y_col}",
            template=template,
            color_discrete_sequence=[base_color],
            opacity=0.7,
        )

    elif chart_type == "Box Plot":
        if not numeric_cols:
            st.info("No numeric columns available.")
            return
        y_col = st.selectbox("Value column", numeric_cols, key="box_y")
        x_col = st.selectbox("Group by (optional)", ["None"] + cat_cols, key="box_x")
        fig = px.box(
            df, x=x_col if x_col != "None" else None, y=y_col,
            title=f"Box Plot: {y_col}",
            template=template,
            color_discrete_sequence=[base_color],
            notched=True,
        )

    elif chart_type == "Violin Plot":
        if not numeric_cols:
            st.info("No numeric columns available.")
            return
        y_col = st.selectbox("Value column", numeric_cols, key="violin_y")
        x_col = st.selectbox("Group by (optional)", ["None"] + cat_cols, key="violin_x")
        fig = px.violin(
            df, x=x_col if x_col != "None" else None, y=y_col,
            title=f"Violin Plot: {y_col}",
            template=template,
            color_discrete_sequence=[base_color],
            box=True, points="outliers",
        )

    elif chart_type == "Pie Chart":
        if not cat_cols:
            st.info("No categorical columns available.")
            return
        col = st.selectbox("Column", cat_cols, key="pie_col")
        top_n = st.slider("Show top N categories", 3, 20, 8, key="pie_n")
        data = df[col].value_counts().head(top_n).reset_index()
        data.columns = [col, "Count"]
        fig = px.pie(data, values="Count", names=col,
                     title=f"Distribution: {col}", template=template)

    elif chart_type == "Heatmap":
        if len(numeric_cols) < 2:
            st.info("Need at least 2 numeric columns.")
            return
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                        title="Correlation Heatmap", zmin=-1, zmax=1)

    elif chart_type == "Scatter Matrix":
        if len(numeric_cols) < 2:
            st.info("Need at least 2 numeric columns.")
            return
        cols_to_plot = st.multiselect("Select columns", numeric_cols, default=numeric_cols[:4], key="splom_cols")
        color_by = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="splom_color")
        if len(cols_to_plot) >= 2:
            fig = px.scatter_matrix(
                df, dimensions=cols_to_plot,
                color=color_by if color_by != "None" else None,
                title="Scatter Matrix",
                template=template,
                opacity=0.6,
            )

    if fig is not None:
        fig.update_layout(width=chart_width, height=chart_height)
        st.plotly_chart(fig, use_container_width=True)

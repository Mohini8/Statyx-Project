import streamlit as st
import pandas as pd
import plotly.express as px
from services.Dataset_Service import get_session_df
from services.AI_Service import generate_auto_insights
from utils.Column_Utils import get_numeric_columns, get_categorical_columns


def render():
    st.markdown("## AI Analysis")
    st.markdown("Automatic insights and patterns detected from your dataset.")

    df = get_session_df()
    if df is None:
        st.warning("No dataset loaded. Please upload a file in the Upload module first.")
        return

    with st.spinner("Generating AI insights..."):
        insights = generate_auto_insights(df)

    # Insight cards
    severity_colors = {
        "info": "#dbeafe",
        "warning": "#fef3c7",
        "success": "#d1fae5",
        "alert": "#fee2e2",
    }
    severity_icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "success": "✅",
        "alert": "🚨",
    }

    st.markdown("### Insights Summary")
    
    info_count = sum(1 for i in insights if i["severity"] == "info")
    warn_count = sum(1 for i in insights if i["severity"] == "warning")
    ok_count = sum(1 for i in insights if i["severity"] == "success")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Insights", len(insights))
    with col2:
        st.metric("Informational", info_count)
    with col3:
        st.metric("Warnings", warn_count)
    with col4:
        st.metric("All Clear", ok_count)

    st.markdown("---")

    for ins in insights:
        color = severity_colors.get(ins["severity"], "#f1f5f9")
        icon = severity_icons.get(ins["severity"], "📊")
        st.markdown(
            f"""
            <div style="background:{color}; padding:16px 20px; border-radius:10px; margin-bottom:12px;">
                <div style="font-weight:600; font-size:15px; margin-bottom:4px;">{icon} {ins['title']}</div>
                <div style="color:#374151; font-size:14px;">{ins['description']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Additional visual analysis
    st.markdown("---")
    st.markdown("### Quick Visual Analysis")

    numeric_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)

    tab1, tab2 = st.tabs(["Distributions Overview", "Categorical Breakdown"])

    with tab1:
        if numeric_cols:
            cols_to_show = numeric_cols[:6]
            for i in range(0, len(cols_to_show), 2):
                c1, c2 = st.columns(2)
                for j, col_idx in enumerate(range(i, min(i + 2, len(cols_to_show)))):
                    col = cols_to_show[col_idx]
                    fig = px.histogram(df, x=col, nbins=25, title=col,
                                       template="plotly_white", color_discrete_sequence=["#3b82f6"])
                    fig.update_layout(showlegend=False, height=250, margin=dict(t=30, b=20))
                    (c1 if j == 0 else c2).plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns available for distribution analysis.")

    with tab2:
        if cat_cols:
            for col in cat_cols[:4]:
                n_unique = df[col].nunique()
                if n_unique <= 20:
                    counts = df[col].value_counts().reset_index()
                    counts.columns = [col, "Count"]
                    fig = px.bar(counts, x=col, y="Count", title=f"Distribution: {col}",
                                 template="plotly_white", color_discrete_sequence=["#6366f1"])
                    fig.update_layout(height=280)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categorical columns available for breakdown analysis.")

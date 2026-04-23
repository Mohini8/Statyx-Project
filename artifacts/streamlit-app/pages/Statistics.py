import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from services.Dataset_Service import get_session_df
from services.Statistics_Service import (
    get_descriptive_stats, get_correlation_matrix, normality_test,
    t_test, chi_square_test, anova_test, get_frequency_table,
)
from utils.Column_Utils import get_numeric_columns, get_categorical_columns


def render():
    st.markdown("## Statistics Module")

    df = get_session_df()
    if df is None:
        st.warning("No dataset loaded. Please upload a file in the Upload module first.")
        return

    numeric_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)

    tab1, tab2, tab3, tab4 = st.tabs(["Descriptive Stats", "Correlation", "Statistical Tests", "Frequency Tables"])

    with tab1:
        st.markdown("### Descriptive Statistics")
        selected = st.multiselect("Select columns (leave empty for all numeric)", numeric_cols, key="desc_cols")
        desc = get_descriptive_stats(df, selected if selected else None)
        
        if desc.empty:
            st.info("No numeric columns found.")
        else:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Numeric Columns", len(numeric_cols))
            with col2:
                st.metric("Categorical Columns", len(cat_cols))
            with col3:
                st.metric("Total Observations", f"{len(df):,}")

            st.dataframe(desc.style.background_gradient(cmap="Blues", subset=["mean", "std"]), use_container_width=True)

            # Box plots
            if st.checkbox("Show distribution box plots", value=True):
                cols_to_plot = selected if selected else numeric_cols[:8]
                if cols_to_plot:
                    fig = px.box(df[cols_to_plot], title="Distribution of Numeric Variables",
                                 template="plotly_white", color_discrete_sequence=["#3b82f6"])
                    st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("### Correlation Matrix")
        if len(numeric_cols) < 2:
            st.info("Need at least 2 numeric columns for correlation analysis.")
        else:
            method = st.selectbox("Correlation method", ["pearson", "spearman", "kendall"], key="corr_method")
            corr = get_correlation_matrix(df, method)
            
            if corr.empty:
                st.info("Not enough numeric data for correlation.")
            else:
                # Heatmap
                fig = px.imshow(
                    corr,
                    text_auto=True,
                    color_continuous_scale="RdBu_r",
                    title=f"{method.capitalize()} Correlation Matrix",
                    zmin=-1, zmax=1,
                )
                fig.update_layout(template="plotly_white", height=500)
                st.plotly_chart(fig, use_container_width=True)

                # Strong correlations
                with st.expander("Strong Correlations (|r| > 0.7)"):
                    strong = []
                    for i in range(len(corr)):
                        for j in range(i + 1, len(corr)):
                            val = corr.iloc[i, j]
                            if abs(val) > 0.7:
                                strong.append({
                                    "Variable 1": corr.columns[i],
                                    "Variable 2": corr.columns[j],
                                    "Correlation": round(val, 4),
                                    "Strength": "Strong Positive" if val > 0 else "Strong Negative",
                                })
                    if strong:
                        st.dataframe(pd.DataFrame(strong), use_container_width=True)
                    else:
                        st.info("No strong correlations found (|r| > 0.7).")

                st.dataframe(corr.style.background_gradient(cmap="RdBu_r", vmin=-1, vmax=1), use_container_width=True)

    with tab3:
        st.markdown("### Statistical Tests")
        test_type = st.selectbox("Select test", [
            "Normality Test (Shapiro-Wilk)",
            "Independent T-Test",
            "Paired T-Test",
            "Chi-Square Test",
            "One-Way ANOVA",
        ])

        if test_type == "Normality Test (Shapiro-Wilk)":
            if not numeric_cols:
                st.info("No numeric columns available.")
            else:
                col = st.selectbox("Select column", numeric_cols, key="norm_col")
                if st.button("Run Test", key="run_norm"):
                    result = normality_test(df, col)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("Test Statistic", result["statistic"])
                        with c2:
                            st.metric("P-Value", result["p_value"])
                        with c3:
                            st.metric("Normal?", "Yes" if result["normal"] else "No")
                        
                        if result["normal"]:
                            st.success("The distribution appears to be normal (p > 0.05).")
                        else:
                            st.warning("The distribution is NOT normal (p ≤ 0.05). Consider non-parametric tests.")

                        # Distribution plot
                        fig = px.histogram(df[col].dropna(), nbins=30, title=f"Distribution of {col}",
                                           template="plotly_white", color_discrete_sequence=["#3b82f6"])
                        st.plotly_chart(fig, use_container_width=True)

        elif test_type in ("Independent T-Test", "Paired T-Test"):
            if len(numeric_cols) < 2:
                st.info("Need at least 2 numeric columns.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    col1 = st.selectbox("Column 1", numeric_cols, key="ttest_col1")
                with c2:
                    col2 = st.selectbox("Column 2", [c for c in numeric_cols if c != col1], key="ttest_col2")
                if st.button("Run T-Test", key="run_ttest"):
                    result = t_test(df, col1, col2, paired=(test_type == "Paired T-Test"))
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Test", result["test"])
                    with c2:
                        st.metric("Statistic", result["statistic"])
                    with c3:
                        st.metric("P-Value", result["p_value"])
                    if result["significant"]:
                        st.success("Significant difference found (p ≤ 0.05).")
                    else:
                        st.info("No significant difference found (p > 0.05).")

        elif test_type == "Chi-Square Test":
            if len(cat_cols) < 2:
                st.info("Need at least 2 categorical columns.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    col1 = st.selectbox("Column 1", cat_cols, key="chi_col1")
                with c2:
                    col2 = st.selectbox("Column 2", [c for c in cat_cols if c != col1], key="chi_col2")
                if st.button("Run Chi-Square Test", key="run_chi"):
                    result = chi_square_test(df, col1, col2)
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Chi-Square Statistic", result["statistic"])
                    with c2:
                        st.metric("P-Value", result["p_value"])
                    with c3:
                        st.metric("Degrees of Freedom", result["degrees_of_freedom"])
                    if result["significant"]:
                        st.success("Significant association found between the variables (p ≤ 0.05).")
                    else:
                        st.info("No significant association found (p > 0.05).")
                    # Contingency table
                    with st.expander("Contingency Table"):
                        ct = pd.crosstab(df[col1], df[col2])
                        st.dataframe(ct, use_container_width=True)

        elif test_type == "One-Way ANOVA":
            if not numeric_cols or not cat_cols:
                st.info("Need at least 1 numeric and 1 categorical column.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    value_col = st.selectbox("Numeric variable", numeric_cols, key="anova_val")
                with c2:
                    group_col = st.selectbox("Grouping variable", cat_cols, key="anova_grp")
                if st.button("Run ANOVA", key="run_anova"):
                    result = anova_test(df, value_col, group_col)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("F-Statistic", result["statistic"])
                        with c2:
                            st.metric("P-Value", result["p_value"])
                        if result["significant"]:
                            st.success("Significant differences between groups (p ≤ 0.05).")
                        else:
                            st.info("No significant difference between groups (p > 0.05).")

    with tab4:
        st.markdown("### Frequency Tables")
        if not cat_cols:
            st.info("No categorical columns found.")
        else:
            col = st.selectbox("Select column", cat_cols, key="freq_col")
            top_n = st.slider("Show top N values", 5, 50, 20, key="freq_n")
            freq = get_frequency_table(df, col, top_n)
            st.dataframe(freq, use_container_width=True)

            fig = px.bar(freq, x="Value", y="Count", title=f"Frequency Distribution: {col}",
                         template="plotly_white", color_discrete_sequence=["#3b82f6"])
            st.plotly_chart(fig, use_container_width=True)

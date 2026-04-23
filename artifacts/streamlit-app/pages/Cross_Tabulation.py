import streamlit as st
import pandas as pd
import plotly.express as px
from services.Dataset_Service import get_session_df
from utils.Column_Utils import get_categorical_columns, get_numeric_columns


def render():
    st.markdown("## Cross Tabulation")
    st.markdown("Analyze relationships between categorical variables and compute pivot tables.")

    df = get_session_df()
    if df is None:
        st.warning("No dataset loaded. Please upload a file in the Upload module first.")
        return

    cat_cols = get_categorical_columns(df)
    numeric_cols = get_numeric_columns(df)

    if len(cat_cols) < 2:
        st.info("Cross tabulation requires at least 2 categorical columns in your dataset.")
        return

    tab1, tab2 = st.tabs(["Cross Tabulation", "Pivot Table"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            row_var = st.selectbox("Row variable", cat_cols, key="ct_row")
        with c2:
            col_var = st.selectbox("Column variable", [c for c in cat_cols if c != row_var], key="ct_col")

        normalize = st.selectbox(
            "Normalize",
            ["None (Counts)", "By Row (%)", "By Column (%)", "By Total (%)"],
            key="ct_norm",
        )
        
        norm_map = {
            "None (Counts)": False,
            "By Row (%)": "index",
            "By Column (%)": "columns",
            "By Total (%)": "all",
        }
        norm_arg = norm_map[normalize]

        # Limit categories
        top_rows = st.slider("Max row categories", 3, 20, 10, key="ct_rows")
        top_cols = st.slider("Max column categories", 3, 20, 10, key="ct_cols")

        top_row_vals = df[row_var].value_counts().head(top_rows).index
        top_col_vals = df[col_var].value_counts().head(top_cols).index
        filtered = df[df[row_var].isin(top_row_vals) & df[col_var].isin(top_col_vals)]

        ct = pd.crosstab(filtered[row_var], filtered[col_var], normalize=norm_arg)
        if norm_arg:
            ct = (ct * 100).round(2)

        st.markdown(f"#### {row_var} × {col_var}")
        st.dataframe(ct.style.background_gradient(cmap="Blues"), use_container_width=True)

        # Heatmap
        fig = px.imshow(
            ct,
            text_auto=True,
            color_continuous_scale="Blues",
            title=f"Cross Tabulation: {row_var} × {col_var}",
        )
        fig.update_layout(template="plotly_white", height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Stacked bar
        ct_counts = pd.crosstab(filtered[row_var], filtered[col_var])
        fig_bar = px.bar(
            ct_counts.reset_index().melt(id_vars=row_var),
            x=row_var, y="value", color=col_var,
            title=f"Stacked Bar: {row_var} by {col_var}",
            template="plotly_white",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.markdown("### Pivot Table")
        if not numeric_cols:
            st.info("Pivot tables require at least one numeric column.")
            return

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            pivot_idx = st.selectbox("Rows", cat_cols, key="piv_idx")
        with c2:
            pivot_cols = st.selectbox("Columns", [c for c in cat_cols if c != pivot_idx], key="piv_col")
        with c3:
            pivot_val = st.selectbox("Values", numeric_cols, key="piv_val")
        with c4:
            agg_func = st.selectbox("Aggregation", ["mean", "sum", "count", "min", "max", "median"], key="piv_agg")

        try:
            pivot = df.pivot_table(
                values=pivot_val,
                index=pivot_idx,
                columns=pivot_cols,
                aggfunc=agg_func,
            ).round(4)

            st.dataframe(pivot.style.background_gradient(cmap="YlOrRd"), use_container_width=True)

            # Download pivot
            csv = pivot.to_csv()
            st.download_button(
                "Download Pivot Table (CSV)",
                csv,
                file_name="pivot_table.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Could not generate pivot table: {str(e)}")

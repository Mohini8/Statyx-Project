import streamlit as st
import pandas as pd
from services.Dataset_Service import get_session_df, set_session_df
from services.Cleaning_Service import apply_cleaning_pipeline
from utils.Dataframe_Utils import get_missing_summary
from utils.Column_Utils import get_all_columns, get_numeric_columns


def render():
    st.markdown("## Data Cleaning")

    df = get_session_df()
    if df is None:
        st.warning("No dataset loaded. Please upload a file in the Upload module first.")
        return

    original_df = df.copy()

    tab1, tab2, tab3, tab4 = st.tabs(["Missing Values", "Duplicates", "Column Types", "Drop Columns"])

    with tab1:
        st.markdown("### Missing Value Analysis")
        missing_summary = get_missing_summary(df)
        if missing_summary.empty:
            st.success("No missing values detected in your dataset.")
        else:
            st.dataframe(missing_summary, use_container_width=True)
            st.markdown("### Handle Missing Values")
            strategy = st.selectbox(
                "Select strategy",
                ["None", "Drop rows", "Fill with mean", "Fill with median",
                 "Fill with mode", "Fill with zero", "Forward fill", "Backward fill", "Drop column"],
            )
            apply_to = st.radio("Apply to", ["All columns with missing values", "Select specific columns"])
            cols = None
            if apply_to == "Select specific columns":
                missing_cols = list(missing_summary["Column"])
                cols = st.multiselect("Select columns", missing_cols)

            if st.button("Apply Missing Value Strategy", key="apply_missing"):
                if strategy != "None":
                    with st.spinner("Applying strategy..."):
                        new_df, summary = apply_cleaning_pipeline(df, missing_strategy=strategy, missing_cols=cols)
                    set_session_df(new_df)
                    st.success(f"Strategy applied. Rows: {summary['rows_before']:,} → {summary['rows_after']:,}")
                    st.rerun()

    with tab2:
        st.markdown("### Duplicate Detection")
        dup_count = df.duplicated().sum()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Duplicate Rows", f"{dup_count:,}")
        with col2:
            st.metric("Percentage", f"{round(dup_count / len(df) * 100, 2)}%")

        if dup_count > 0:
            with st.expander("Preview Duplicates"):
                st.dataframe(df[df.duplicated(keep=False)].head(20), use_container_width=True)

            subset = st.multiselect(
                "Detect duplicates based on (leave empty for all columns)",
                options=get_all_columns(df),
            )
            keep = st.selectbox("Keep", ["first", "last"])
            if st.button("Remove Duplicates", key="remove_dups"):
                new_df, removed = apply_cleaning_pipeline(df, remove_dups=True, dup_subset=subset or None).__iter__().__next__(), 0
                new_df, summary = apply_cleaning_pipeline(df, remove_dups=True, dup_subset=subset or None)
                set_session_df(new_df)
                st.success(f"Removed {summary['rows_removed']:,} duplicate rows.")
                st.rerun()
        else:
            st.success("No duplicate rows detected in your dataset.")

    with tab3:
        st.markdown("### Column Type Conversion")
        st.caption("Convert column data types to ensure correct analysis.")
        
        cols = get_all_columns(df)
        col_types = {}
        
        for col in cols[:20]:  # Limit to first 20 for UI
            current = str(df[col].dtype)
            new_type = st.selectbox(
                f"{col} (current: {current})",
                ["keep", "numeric", "string", "datetime", "category", "boolean"],
                key=f"type_{col}",
            )
            if new_type != "keep":
                col_types[col] = new_type

        if col_types and st.button("Apply Type Conversions", key="apply_types"):
            new_df, summary = apply_cleaning_pipeline(df, type_conversions=col_types)
            set_session_df(new_df)
            st.success(f"Applied {summary.get('type_conversions', 0)} type conversion(s).")
            st.rerun()

    with tab4:
        st.markdown("### Drop Columns")
        st.caption("Remove columns that are not needed for your analysis.")
        
        drop_cols = st.multiselect("Select columns to drop", options=get_all_columns(df))
        
        if drop_cols:
            st.warning(f"This will permanently remove {len(drop_cols)} column(s) from your working dataset.")
            if st.button("Drop Selected Columns", key="drop_cols"):
                new_df, summary = apply_cleaning_pipeline(df, drop_cols=drop_cols)
                set_session_df(new_df)
                st.success(f"Dropped {len(drop_cols)} column(s). Dataset now has {len(new_df.columns)} columns.")
                st.rerun()

    # Sidebar preview
    st.markdown("---")
    st.markdown("### Current Dataset Preview")
    st.caption(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    st.dataframe(df.head(10), use_container_width=True)

    # Reset button
    if st.button("Reset to Original", type="secondary"):
        set_session_df(original_df)
        st.info("Dataset reset to original upload.")
        st.rerun()

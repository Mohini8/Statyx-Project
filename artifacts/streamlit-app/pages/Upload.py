import streamlit as st
import pandas as pd
from utils.Dataframe_Utils import load_dataframe, get_dataframe_info
from utils.File_Utils import format_file_size
from services.Dataset_Service import set_session_df, set_session_filename, get_session_df
from services.AI_Service import generate_auto_insights


def render():
    st.markdown("## Upload Dataset")
    st.markdown("Upload a CSV or Excel file to begin your analysis.")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls"],
        help="Supported formats: CSV, Excel (.xlsx, .xls). Max size: 200MB",
    )

    if uploaded_file is not None:
        with st.spinner("Loading dataset..."):
            df = load_dataframe(uploaded_file)

        if df is None:
            st.error("Failed to load the file. Please check the format and try again.")
            return

        set_session_df(df)
        set_session_filename(uploaded_file.name)

        st.success(f"Successfully loaded **{uploaded_file.name}**")

        # File info metrics
        col1, col2, col3, col4 = st.columns(4)
        info = get_dataframe_info(df)
        with col1:
            st.metric("Rows", f"{info['rows']:,}")
        with col2:
            st.metric("Columns", f"{info['columns']}")
        with col3:
            st.metric("Missing Values", f"{sum(info['missing_counts'].values()):,}")
        with col4:
            st.metric("File Size", format_file_size(uploaded_file.size))

        st.markdown("---")

        # Data preview
        st.markdown("### Data Preview")
        preview_rows = st.slider("Rows to preview", 5, min(100, len(df)), 10, key="preview_rows")
        st.dataframe(df.head(preview_rows), use_container_width=True)

        # Column info
        with st.expander("Column Information"):
            col_info = pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.astype(str).values,
                "Non-Null Count": df.count().values,
                "Null Count": df.isnull().sum().values,
                "Null %": (df.isnull().sum() / len(df) * 100).round(2).astype(str).add("%").values,
                "Unique Values": df.nunique().values,
            })
            st.dataframe(col_info, use_container_width=True)

        # Auto insights preview
        with st.expander("Quick AI Insights"):
            insights = generate_auto_insights(df)
            for ins in insights[:4]:
                icon = {"info": "ℹ️", "warning": "⚠️", "success": "✅", "alert": "🔴"}.get(ins["severity"], "📊")
                st.markdown(f"**{icon} {ins['title']}**")
                st.caption(ins["description"])
                st.markdown("")

        # Sample dataset download
        st.markdown("---")
        st.markdown("### Use Sample Dataset")
        st.caption("Not ready to upload your own data? Try our built-in sample dataset.")
        if st.button("Load Sample Dataset (Iris)", key="load_sample"):
            from sklearn.datasets import load_iris
            iris = load_iris(as_frame=True)
            sample_df = iris.frame
            sample_df["target_name"] = sample_df["target"].map({0: "setosa", 1: "versicolor", 2: "virginica"})
            set_session_df(sample_df)
            set_session_filename("iris_sample.csv")
            st.success("Sample dataset loaded! Navigate to other modules to analyze it.")
            st.rerun()

    else:
        # Empty state
        current_df = get_session_df()
        if current_df is not None:
            st.info("A dataset is already loaded in your session. Upload a new file to replace it, or navigate to other modules to continue your analysis.")
        else:
            st.markdown(
                """
                <div style="text-align:center; padding:60px 20px; background:#f0f9ff; border-radius:12px; border:1px dashed #93c5fd;">
                    <div style="font-size:48px; margin-bottom:16px;">📊</div>
                    <h3 style="color:#1e40af; margin:0 0 8px 0;">No dataset loaded</h3>
                    <p style="color:#64748b; margin:0;">Upload a CSV or Excel file above to get started with your analysis.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

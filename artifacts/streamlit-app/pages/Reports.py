import streamlit as st
import pandas as pd
from services.Dataset_Service import get_session_df, get_session_filename
from services.Report_Service import generate_pdf_report, generate_word_report
from services.AI_Service import generate_auto_insights


def render():
    st.markdown("## Report Generation")
    st.markdown("Generate professional reports from your analysis. Download as PDF or Word document.")

    df = get_session_df()
    if df is None:
        st.warning("No dataset loaded. Please upload a file in the Upload module first.")
        return

    filename = get_session_filename() or "dataset"

    st.markdown("### Report Options")
    col1, col2 = st.columns(2)
    with col1:
        include_stats = st.checkbox("Include descriptive statistics", value=True)
        include_insights = st.checkbox("Include AI insights", value=True)
    with col2:
        include_columns = st.checkbox("Include column summary", value=True)
        include_correlation = st.checkbox("Include correlation matrix", value=True)

    st.markdown("---")
    
    # Generate insights for report
    insights = []
    if include_insights:
        with st.spinner("Generating insights..."):
            insights = generate_auto_insights(df)

    # Report preview
    st.markdown("### Report Preview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Missing Values", f"{df.isnull().sum().sum():,}")
    with col4:
        st.metric("Insights", len(insights))

    if include_stats:
        st.markdown("#### Descriptive Statistics Preview")
        numeric_df = df.select_dtypes(include=["number"])
        if not numeric_df.empty:
            st.dataframe(numeric_df.describe().round(4), use_container_width=True)

    if include_insights and insights:
        st.markdown("#### AI Insights Preview")
        for ins in insights[:3]:
            icon = {"info": "ℹ️", "warning": "⚠️", "success": "✅"}.get(ins["severity"], "📊")
            st.caption(f"{icon} **{ins['title']}**: {ins['description']}")

    st.markdown("---")
    st.markdown("### Download Report")

    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("Generate PDF Report", use_container_width=True, type="primary"):
            with st.spinner("Generating PDF..."):
                pdf_bytes = generate_pdf_report(df, filename, insights if include_insights else None)
            if pdf_bytes:
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"statyx_report_{filename.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.error("PDF generation failed. Ensure reportlab is installed.")

    with c2:
        if st.button("Generate Word Report", use_container_width=True):
            with st.spinner("Generating Word document..."):
                docx_bytes = generate_word_report(df, filename, insights if include_insights else None)
            if docx_bytes:
                st.download_button(
                    label="Download Word",
                    data=docx_bytes,
                    file_name=f"statyx_report_{filename.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            else:
                st.error("Word generation failed. Ensure python-docx is installed.")

    with c3:
        # CSV download always available
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name=f"{filename.replace(' ', '_')}_cleaned.csv",
            mime="text/csv",
            use_container_width=True,
        )

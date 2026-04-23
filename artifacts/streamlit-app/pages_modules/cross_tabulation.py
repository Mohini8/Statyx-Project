import streamlit as st
import pandas as pd

from services.cross_tab_service import cross_tab_analysis


def render():

    st.header("🔗 Cross Tabulation")

    df = st.session_state.df

    # 👉 KEEP YOUR CROSS TAB CODE


    if df is None:
        st.warning("Upload dataset first")
        st.stop()

    row = st.selectbox("Row Variable", df.columns)
    col = st.selectbox("Column Variable", df.columns)

    if st.button("Generate Analysis"):

        results = cross_tab_analysis(df,row,col)

        if results["type"]=="categorical":

            st.dataframe(results["counts"])

        elif results["type"]=="numeric":

            st.write("Correlation:",results["correlation"])

        st.write("p-value:",results["p_value"])

    if st.button("⬅ Back"):
        st.session_state.step = "statistics"
        st.rerun()
import streamlit as st

from visualization.chart_builder import build_chart



import streamlit as st

def render():

    st.header("📈 Visualizations")

    df = st.session_state.df

    # 👉 KEEP YOUR FULL VISUALIZATION CODE

    if df is None:
        st.warning("Upload dataset first")
        st.stop()

    plot_type = st.selectbox(
        "Plot Type",
        ["pie","bar","line","scatter","histogram","boxplot"]
    )

    cols = st.multiselect("Select Columns", df.columns)

    if st.button("Generate Plot"):

        if not cols:
            st.error("Select columns")
            st.stop()

        try:
            fig = build_chart(df, plot_type, cols)
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Error: {str(e)}")

    if st.button("⬅ Back"):
        st.session_state.step = "statistics"
        st.rerun()
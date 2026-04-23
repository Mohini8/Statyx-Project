import streamlit as st

def render():

    st.header("💬 Feedback")

    feedback = st.text_area("Your feedback")

    if st.button("Submit"):
        st.success("Thanks!")

    if st.button("⬅ Back"):
        st.session_state.step = "statistics"
        st.rerun()
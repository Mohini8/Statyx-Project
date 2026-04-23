import streamlit as st

def require_login():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True
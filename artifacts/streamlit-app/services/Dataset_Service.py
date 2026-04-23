import pandas as pd
import streamlit as st
from utils.Dataframe_Utils import load_dataframe


def get_session_df() -> pd.DataFrame | None:
    """Get the current DataFrame from session state."""
    return st.session_state.get("df", None)


def set_session_df(df: pd.DataFrame) -> None:
    """Set the current DataFrame in session state."""
    st.session_state["df"] = df


def get_session_filename() -> str:
    return st.session_state.get("filename", "")


def set_session_filename(name: str) -> None:
    st.session_state["filename"] = name


def reset_session() -> None:
    """Clear all session data."""
    for key in ["df", "filename", "cleaned_df"]:
        if key in st.session_state:
            del st.session_state[key]

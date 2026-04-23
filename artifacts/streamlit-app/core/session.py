import streamlit as st

def init_session():

    # ===============================
    # 🔐 AUTH
    # ===============================
    st.session_state.setdefault("logged_in", False)

    # ===============================
    # 🔁 WORKFLOW CONTROL (NEW)
    # ===============================
    st.session_state.setdefault("step", "landing")

    # ===============================
    # 📂 DATA (KEEP YOUR EXISTING)
    # ===============================
    st.session_state.setdefault("df", None)
    st.session_state.setdefault("preview", None)
    st.session_state.setdefault("clean_df", None)
    st.session_state.setdefault("stats", None)

    # ===============================
    # 🧹 CLEANING STATE (KEEP)
    # ===============================
    st.session_state.setdefault("clean_issues", [])
    st.session_state.setdefault("clean_preview", None)
    st.session_state.setdefault("clean_download", None)
    st.session_state.setdefault("clean_actions", {})

    # ===============================
    # 📊 REPORTS (KEEP)
    # ===============================
    st.session_state.setdefault("word_report", None)
    st.session_state.setdefault("pdf_report", None)

    # ===============================
    # ⚙️ FLAGS (NEW - VERY IMPORTANT)
    # ===============================
    st.session_state.setdefault("uploaded", False)
    st.session_state.setdefault("cleaned", False)
    st.session_state.setdefault("stats_done", False)
import streamlit as st
from core.session import init_session
from core.ui import load_css, render_navbar

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Research Analysis Tool",
    layout="wide",
    page_icon="📊"
)

# ---------- INIT ----------
init_session()
load_css()
render_navbar()

# ---------- ROUTING ----------
step = st.session_state.step

if step == "landing":
    from pages_modules import landing
    landing.render()

elif step == "login":
    from pages_modules import login
    login.render()

elif step == "upload":
    from pages_modules import upload
    upload.render()

elif step == "cleaning":
    from pages_modules import cleaning
    cleaning.render()

elif step == "statistics":
    from pages_modules import statistics
    statistics.render()

elif step == "visualizations":
    from pages_modules import visualizations
    visualizations.render()

elif step == "ai_analysis":
    from pages_modules import ai_analysis
    ai_analysis.render()

elif step == "cross_tabulation":
    from pages_modules import cross_tabulation
    cross_tabulation.render()

elif step == "feedback":
    from pages_modules import feedback
    feedback.render()

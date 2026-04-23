import streamlit as st
import pandas as pd


def render():


    # ---------- Custom CSS ----------
    st.markdown("""
    <style>

    /* Page background (LIGHT BLUE GRADIENT) */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f8fafc, #e0f2fe) !important;
    }

    /* Remove header */
    header {visibility: hidden;}

    /* Remove sidebar */
    [data-testid="stSidebar"] {display: none;}

    /* Reduce top spacing */
    .block-container {
        padding-top: 2rem !important;
    }

    /* Title */
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        color: #0f172a;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #475569;
        margin-bottom: 2rem;
    }

    /* Upload box */
    [data-testid="stFileUploader"] {
        border: 2px dashed #3b82f6 !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        background: white !important;
    }

    /* Button */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 0.8rem;
        font-weight: 600;
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color: white;
        border: none;
    }

    .stButton > button:hover {
        transform: scale(1.03);
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------- Layout ----------


    st.markdown('<div class="title">📤 Upload Your Dataset</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Upload CSV or Excel file to begin analysis</div>', unsafe_allow_html=True)


    # ---------- File Upload ----------
    file = st.file_uploader("", label_visibility="collapsed")

    if file:

        # ---------- Read File ----------
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        df.columns = df.columns.str.strip().str.lower()

        st.session_state.df = df
        st.session_state.preview = df.head()

        st.markdown('<div class="success-box">✅ Upload successful</div>', unsafe_allow_html=True)

        # ---------- Preview ----------
        st.markdown("### 🔍 Preview")
        st.dataframe(st.session_state.preview, use_container_width=True)

        # ---------- Continue Button ----------
        if st.button("Continue → Cleaning"):
            st.session_state.step = "cleaning"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

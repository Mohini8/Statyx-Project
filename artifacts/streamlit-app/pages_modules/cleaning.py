import streamlit as st
import pandas as pd
import io

from services.cleaning_service import detect_issues, is_numeric_like
from utils.column_utils import infer_column_type


def render():

    # ----------------------------
    # 🌈 MODERN LIGHT UI STYLING
    # ----------------------------
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #eef6ff, #f8fbff);
        color: #1e293b;
    }

    h1, h2, h3 {
        color: #0f172a;
    }

    .stButton>button {
        background: #2563eb;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: none;
    }

    .stButton>button:hover {
        background: #1d4ed8;
    }

    .block-container {
        padding-top: 1rem;
    }

    .stDataFrame {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🧹 AI Data Cleaning")
    st.caption("Smart detection • Custom fixes • Clean dataset in seconds")

    df = st.session_state.get("df", None)

    if df is None:
        st.warning("Upload dataset first")
        return

    st.subheader("📊 Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)

    # Initialize states
    if "clean_issues" not in st.session_state:
        st.session_state.clean_issues = []

    if "clean_actions" not in st.session_state:
        st.session_state.clean_actions = {}

    if "clean_preview" not in st.session_state:
        st.session_state.clean_preview = None

    if "clean_download" not in st.session_state:
        st.session_state.clean_download = None

    # ----------------------------
    # 🔍 DETECT ISSUES
    # ----------------------------
    if st.button("🔍 Detect Issues"):
        issues = detect_issues(df)

        st.session_state.clean_issues = issues
        st.session_state.clean_actions = {}
        st.session_state.clean_preview = None
        st.session_state.clean_download = None

    # ----------------------------
    # ⚠️ SHOW ISSUES + FIX OPTIONS
    # ----------------------------
    if st.session_state.clean_issues:

        st.subheader(f"⚠️ Found {len(st.session_state.clean_issues)} Issues")

        issues_df = pd.DataFrame(st.session_state.clean_issues)
        st.dataframe(issues_df, use_container_width=True)

        st.markdown("### 🔧 Choose Fix Methods")

        for idx, issue in enumerate(st.session_state.clean_issues):

            col = issue["column"]
            dtype = issue["dtype"]
            issue_type = issue["issue"]

            with st.container():
                st.markdown(f"""
                <div style='padding:10px; border-radius:10px; background:#ffffff; margin-bottom:10px;'>
                <b>{col}</b> → {issue_type} ({issue['count']})
                </div>
                """, unsafe_allow_html=True)

                key_prefix = f"{idx}_{col}_{issue_type}"

                # Numeric
                if dtype == "numeric":
                    method = st.selectbox(
                        f"{col} Fix Method",
                        ["mean", "median", "zero", "custom"],
                        key=f"{key_prefix}_method"
                    )
                else:
                    method = st.selectbox(
                        f"{col} Fix Method",
                        ["mode", "custom"],
                        key=f"{key_prefix}_method"
                    )

                custom_val = None
                if method == "custom":
                    custom_val = st.text_input(
                        f"Custom value for {col}",
                        key=f"{key_prefix}_custom"
                    )

                st.session_state.clean_actions[key_prefix] = {
                    "column": col,
                    "method": method,
                    "custom": custom_val
                }

                st.divider()

        # ----------------------------
        # ✅ APPLY FIXES
        # ----------------------------
        if st.button("✅ Apply All Fixes"):

            for action in st.session_state.clean_actions.values():

                col = action["column"]
                method = action["method"]
                custom = action["custom"]

                col_type = infer_column_type(df[col])

                # ---- NUMERIC ----
                if col_type == "numeric":

                    df[col] = pd.to_numeric(df[col], errors="coerce")

                    if method == "mean":
                        df[col].fillna(df[col].mean(), inplace=True)

                    elif method == "median":
                        df[col].fillna(df[col].median(), inplace=True)

                    elif method == "zero":
                        df[col].fillna(0, inplace=True)

                    elif method == "custom" and custom:
                        df[col].fillna(float(custom), inplace=True)

                # ---- CATEGORICAL ----
                else:

                    numeric_mask = df[col].apply(is_numeric_like)
                    df.loc[numeric_mask, col] = pd.NA

                    if method == "mode":
                        df[col].fillna(df[col].mode()[0], inplace=True)

                    elif method == "custom" and custom:
                        df[col].fillna(str(custom), inplace=True)

            st.session_state.df = df
            st.session_state.clean_preview = df.head(20)

            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            st.session_state.clean_download = buffer.getvalue()

            st.success("✅ Cleaning applied successfully!")

    # ----------------------------
    # 📥 CLEANED OUTPUT
    # ----------------------------
    if st.session_state.clean_preview is not None:

        st.subheader("✅ Cleaned Dataset Preview")
        st.dataframe(st.session_state.clean_preview, use_container_width=True)

        st.download_button(
            "⬇️ Download Cleaned Dataset",
            st.session_state.clean_download,
            file_name="cleaned_dataset.csv",
            mime="text/csv"
        )

    # ----------------------------
    # ➡️ CONTINUE
    # ----------------------------
    if st.button("➡️ Continue to Statistics"):
        st.session_state.step = "statistics"
        st.rerun()
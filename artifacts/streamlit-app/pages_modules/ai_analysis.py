import streamlit as st
import pandas as pd

from ai.embedding_model import model
from services.ai_service import run_ai_analysis




def render():

    st.header("🧠 AI Analysis")

    df = st.session_state.df

    # 👉 KEEP YOUR AI CODE
    TEST_DESCRIPTIONS = {
        "independent_t_test": "compare mean of a continuous variable between two independent groups",
        "anova": "compare mean across more than two groups",
        "chi_square": "association between two categorical variables",
        "pearson_correlation": "linear correlation"
    }

    TEST_NAMES = list(TEST_DESCRIPTIONS.keys())

    TEST_TEXTS = [f"passage: {TEST_DESCRIPTIONS[t]}" for t in TEST_NAMES]

    TEST_EMBEDDINGS = model.encode(
        TEST_TEXTS,
        convert_to_tensor=True
    )

    st.header("AI Objective Analysis")

    df = st.session_state.df

    if df is None:
        st.warning("Upload data first")
        st.stop()

    objective = st.text_input(
        "Enter objective (e.g., 'Is outcome associated with gender?')"
    )

    if st.button("Run Suggested Tests"):

        result = run_ai_analysis(
            df,
            objective,
            TEST_EMBEDDINGS,
            TEST_NAMES
        )

        if result is None:
            st.error("Could not infer columns")
            st.stop()

        valid_results, target, group = result

        for test in valid_results:

            st.subheader(test["test"])

            result_df = pd.DataFrame(
                list(test["result"].items()),
                columns=["Metric","Value"]
            )

            st.table(result_df)

            p_val = test["result"].get("p_value")

            if p_val:

                if p_val < 0.05:
                    st.success("Statistically significant relationship")

                else:
                    st.warning("No statistically significant relationship")

    if st.button("⬅ Back"):
        st.session_state.step = "statistics"
        st.rerun()
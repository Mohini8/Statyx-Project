import streamlit as st
import pandas as pd

from ai.embedding_model import model
from ai.objective_engine import analyze_objective




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

    target_col = st.selectbox("Target column (optional override)", ["Auto"] + list(df.columns), index=0)
    group_col = st.selectbox("Relevant column/group (optional override)", ["Auto"] + list(df.columns), index=0)

    if st.button("Run Suggested Tests"):

        result = analyze_objective(
            df,
            objective,
            TEST_EMBEDDINGS,
            TEST_NAMES,
            None if target_col == "Auto" else target_col,
            None if group_col == "Auto" else group_col
        )

        if result is None:
            st.error("Could not infer columns")
            st.session_state.ai_analysis_result = None
        else:
            valid_results, target, group, additional_tests = result
            st.session_state.ai_analysis_result = {
                "valid_results": valid_results,
                "target": target,
                "group": group,
                "additional_tests": additional_tests,
            }

    analysis_state = st.session_state.get("ai_analysis_result")

    if analysis_state:
        valid_results = analysis_state["valid_results"]
        target = analysis_state["target"]
        group = analysis_state["group"]
        additional_tests = analysis_state["additional_tests"]

        st.info(f"Selected columns → target: **{target}**, relevant/group: **{group}**")

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

        st.markdown("### Additional Possible Tests")
        if additional_tests:
            available_options = [
                f"{item['test_key']} (confidence={item['confidence']})"
                for item in additional_tests
            ]
            selected = st.multiselect(
                "Select any additional tests to execute",
                options=available_options,
                key="ai_additional_selected_tests"
            )

            if st.button("Run Selected Additional Tests"):
                for label in selected:
                    selected_key = label.split(" (confidence=")[0]
                    try:
                        from stats.stats_tests import TEST_REGISTRY
                        res = TEST_REGISTRY[selected_key](df, target, group)
                        if isinstance(res, dict):
                            st.subheader(selected_key.replace("_", " ").title())
                            st.table(pd.DataFrame(list(res.items()), columns=["Metric", "Value"]))
                    except Exception as exc:
                        st.warning(f"Could not execute {selected_key}: {exc}")
        else:
            st.caption("No additional relevant tests identified for this objective and column pair.")

    if st.button("⬅ Back"):
        st.session_state.step = "statistics"
        st.rerun()

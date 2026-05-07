from ai.embedding_model import model
from ai.column_inference import infer_columns_from_objective
from ai.test_selector import rank_tests
from stats.stats_tests import TEST_REGISTRY
import pandas as pd


def _is_numeric(series):
    return pd.api.types.is_numeric_dtype(series)


def _is_binary(series):
    return series.dropna().nunique() == 2


def _is_categorical(series):
    return (not _is_numeric(series)) or series.dropna().nunique() < 20


def _is_test_applicable(df, test_key, target, group):
    if target not in df.columns or group not in df.columns or target == group:
        return False

    target_s = df[target]
    group_s = df[group]
    target_num = _is_numeric(target_s)
    group_num = _is_numeric(group_s)
    target_bin = _is_binary(target_s)
    group_levels = group_s.dropna().nunique()

    if test_key in {"chi_square", "fisher_exact", "mcnemar_test", "phi_coefficient", "cramers_v", "odds_ratio", "relative_risk", "mutual_information"}:
        return _is_categorical(target_s) and _is_categorical(group_s)

    if test_key in {"independent_t_test", "mann_whitney_u", "cohens_d", "hedges_g"}:
        # These implementations compare two numeric columns directly, not numeric target + categorical group labels.
        return target_num and group_num

    if test_key in {"anova", "kruskal_wallis"}:
        return target_num and _is_categorical(group_s) and group_levels > 2

    if test_key in {"pearson_correlation", "spearman_correlation", "kendall_tau"}:
        return target_num and group_num

    if test_key in {"linear_regression"}:
        return target_num and group_num

    if test_key in {"logistic_regression", "probit_regression"}:
        return target_bin and group_num

    if test_key == "poisson_regression":
        return target_num and group_num and (target_s.dropna() >= 0).all()

    if test_key in {"binomial_test", "z_test_proportion", "two_proportion_ztest"}:
        return target_bin and _is_categorical(group_s)

    # skip tests requiring repeated measures, special inputs, or survival/time-series context
    unsupported = {
        "cox_regression", "kaplan_meier", "anova_rm", "paired_t_test", "cochran_q", "wilcoxon",
        "friedman_test", "roc_auc", "durbin_watson", "breusch_pagan", "adf_test", "ljung_box",
        "wald_test", "hosmer_lemeshow", "chisquare_gof", "variance_ratio", "rank_biserial",
        "tukey_hsd", "one_sample_t_test", "two_sample_ztest", "shapiro_test", "ks_test",
        "levene_test", "bartlett_test", "jarque_bera", "anderson_darling"
    }
    return test_key not in unsupported

def analyze_objective(df, objective, test_embeddings, test_names, target_col=None, group_col=None, max_attempts=30):

    query_emb = model.encode(
        f"query: {objective}",
        convert_to_tensor=True
    )

    ranked_tests = rank_tests(query_emb, test_embeddings, test_names)

    target, group = infer_columns_from_objective(df, objective)
    target = target_col or target
    group = group_col or group

    results = []
    ranked_applicable = []

    if not target or not group:
        return None

    for test_key, confidence in ranked_tests[:max_attempts]:

        if test_key not in TEST_REGISTRY:
            continue

        if not _is_test_applicable(df, test_key, target, group):
            continue

        ranked_applicable.append((test_key, confidence))

        try:

            result = TEST_REGISTRY[test_key](df, target, group)

            if isinstance(result, dict):

                results.append({
                    "test_key": test_key,
                    "test": test_key.replace("_", " ").title(),
                    "confidence": round(confidence,3),
                    "result": result
                })

        except Exception:
            continue

        if len(results) >= 5:
            break

    additional_tests = [
        {"test_key": test_key, "confidence": round(confidence, 3)}
        for test_key, confidence in ranked_applicable
        if test_key not in {item["test_key"] for item in results}
    ]

    return results, target, group, additional_tests

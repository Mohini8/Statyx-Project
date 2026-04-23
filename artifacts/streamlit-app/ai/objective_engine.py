from ai.embedding_model import model
from ai.column_inference import infer_columns_from_objective
from ai.test_selector import rank_tests
from stats.stats_tests import TEST_REGISTRY

def analyze_objective(df, objective, test_embeddings, test_names):

    query_emb = model.encode(
        f"query: {objective}",
        convert_to_tensor=True
    )

    ranked_tests = rank_tests(query_emb, test_embeddings, test_names)

    target, group = infer_columns_from_objective(df, objective)

    results = []

    if not target or not group:
        return None

    for test_key, confidence in ranked_tests[:10]:

        if test_key not in TEST_REGISTRY:
            continue

        if test_key in ["cox_regression", "kaplan_meier"]:
            continue

        try:

            result = TEST_REGISTRY[test_key](df, target, group)

            if isinstance(result, dict):

                results.append({
                    "test": test_key.replace("_", " ").title(),
                    "confidence": round(confidence,3),
                    "result": result
                })

        except Exception:
            continue

        if len(results) >= 5:
            break

    return results, target, group
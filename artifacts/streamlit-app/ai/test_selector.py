from sentence_transformers import util

def rank_tests(query_emb, test_embeddings, test_names):

    scores = util.cos_sim(query_emb, test_embeddings)[0]

    ranked_tests = sorted(
        zip(test_names, scores.tolist()),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked_tests
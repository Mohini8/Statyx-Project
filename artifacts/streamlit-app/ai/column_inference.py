from sentence_transformers import util
from ai.embedding_model import model
import pandas as pd
import numpy as np

def infer_columns_from_objective(df, objective):
    """
    Infer target and group columns based on objective using semantic similarity.
    Returns the columns most relevant to the objective text.
    """
    col_names = df.columns.tolist()

    col_embs = model.encode(
        [f"column: {c}" for c in col_names],
        convert_to_tensor=True
    )

    query_emb = model.encode(
        f"query: {objective}",
        convert_to_tensor=True
    )

    scores = util.cos_sim(query_emb, col_embs)[0]

    ranked = sorted(
        zip(col_names, scores.tolist()),
        key=lambda x: x[1],
        reverse=True
    )

    # Get column metadata
    col_metadata = {}
    for col in col_names:
        is_numeric = pd.api.types.is_numeric_dtype(df[col])
        nunique = df[col].nunique()
        col_metadata[col] = {
            "is_numeric": is_numeric,
            "nunique": nunique,
            "is_binary": nunique == 2,
            "is_categorical": not is_numeric and nunique < 10
        }

    # Strategy: Pick the top binary/categorical column as target_col,
    # and the next most relevant categorical/low-cardinality column as group_col
    target_col = None
    group_col = None

    # First pass: find target_col (binary preferred)
    for col, score in ranked:
        if target_col is None:
            if col_metadata[col]["is_binary"]:
                target_col = col
                break

    # If no binary column found, pick top scoring categorical
    if target_col is None:
        for col, score in ranked:
            if col_metadata[col]["is_categorical"] or col_metadata[col]["nunique"] < 20:
                target_col = col
                break

    # Second pass: find group_col from remaining columns (excluding target)
    for col, score in ranked:
        if group_col is None and col != target_col:
            if col_metadata[col]["is_categorical"] or col_metadata[col]["nunique"] < 20:
                group_col = col
                break

    # Fallback: if still no columns found, use highest scored categorical
    if group_col is None:
        for col, score in ranked:
            if col != target_col and (col_metadata[col]["is_categorical"] or col_metadata[col]["nunique"] < 20):
                group_col = col
                break

    return target_col, group_col
import pandas as pd
import numpy as np
from typing import List, Tuple


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    return list(df.select_dtypes(include=[np.number]).columns)


def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    return list(df.select_dtypes(include=["object", "category"]).columns)


def get_all_columns(df: pd.DataFrame) -> List[str]:
    return list(df.columns)


def get_column_unique_values(df: pd.DataFrame, col: str, max_vals: int = 20) -> List:
    vals = df[col].dropna().unique().tolist()
    return vals[:max_vals]


def infer_column_role(df: pd.DataFrame, col: str) -> str:
    """Infer whether a column is numeric, categorical, datetime, or other."""
    dtype = df[col].dtype
    n_unique = df[col].nunique()
    n_rows = len(df)

    if pd.api.types.is_datetime64_any_dtype(df[col]):
        return "datetime"
    elif pd.api.types.is_numeric_dtype(df[col]):
        if n_unique / n_rows < 0.05 and n_unique < 20:
            return "categorical_numeric"
        return "numeric"
    elif pd.api.types.is_object_dtype(df[col]):
        if n_unique / n_rows < 0.5:
            return "categorical"
        return "text"
    return "other"


def get_column_summary(df: pd.DataFrame, col: str) -> dict:
    """Get a summary for a single column."""
    role = infer_column_role(df, col)
    summary = {
        "column": col,
        "dtype": str(df[col].dtype),
        "role": role,
        "n_missing": int(df[col].isnull().sum()),
        "pct_missing": round(df[col].isnull().sum() / len(df) * 100, 2),
        "n_unique": int(df[col].nunique()),
    }

    if role in ("numeric", "categorical_numeric"):
        summary.update({
            "mean": round(float(df[col].mean()), 4),
            "median": round(float(df[col].median()), 4),
            "std": round(float(df[col].std()), 4),
            "min": round(float(df[col].min()), 4),
            "max": round(float(df[col].max()), 4),
        })
    elif role == "categorical":
        top = df[col].value_counts().head(5)
        summary["top_values"] = top.to_dict()

    return summary

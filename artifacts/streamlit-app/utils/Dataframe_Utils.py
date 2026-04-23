import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Any


def load_dataframe(file, filename: str = "") -> Optional[pd.DataFrame]:
    """Load CSV or Excel file into a DataFrame."""
    try:
        name = (filename or "").lower()
        if name.endswith(".csv"):
            df = pd.read_csv(file)
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file)
        else:
            return None
        return df
    except Exception:
        return None


def get_dataframe_info(df: pd.DataFrame) -> Dict[str, Any]:
    """Get comprehensive info about a DataFrame."""
    info = {
        "shape": df.shape,
        "rows": len(df),
        "columns": len(df.columns),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "numeric_cols": list(df.select_dtypes(include=[np.number]).columns),
        "categorical_cols": list(df.select_dtypes(include=["object", "category"]).columns),
        "datetime_cols": list(df.select_dtypes(include=["datetime"]).columns),
        "missing_counts": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        "duplicate_count": df.duplicated().sum(),
    }
    return info


def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary DataFrame of missing values."""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    return pd.DataFrame({
        "Column": missing.index,
        "Missing Count": missing.values,
        "Missing %": missing_pct.values,
        "Data Type": df.dtypes.astype(str).values,
    }).query("`Missing Count` > 0").sort_values("Missing %", ascending=False).reset_index(drop=True)


def handle_missing_values(df: pd.DataFrame, strategy: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Handle missing values with different strategies."""
    df = df.copy()
    cols = columns if columns else df.columns.tolist()

    for col in cols:
        if col not in df.columns:
            continue
        if strategy == "Drop rows":
            df = df.dropna(subset=[col])
        elif strategy == "Fill with mean" and pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].mean())
        elif strategy == "Fill with median" and pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        elif strategy == "Fill with mode":
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])
        elif strategy == "Fill with zero":
            df[col] = df[col].fillna(0)
        elif strategy == "Forward fill":
            df[col] = df[col].ffill()
        elif strategy == "Backward fill":
            df[col] = df[col].bfill()
        elif strategy == "Drop column":
            df = df.drop(columns=[col])

    return df


def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None, keep: str = "first") -> Tuple[pd.DataFrame, int]:
    """Remove duplicate rows."""
    original_len = len(df)
    df = df.drop_duplicates(subset=subset, keep=keep)
    removed = original_len - len(df)
    return df, removed


def convert_column_types(df: pd.DataFrame, conversions: Dict[str, str]) -> pd.DataFrame:
    """Convert column data types."""
    df = df.copy()
    for col, dtype in conversions.items():
        if col not in df.columns:
            continue
        try:
            if dtype == "numeric":
                df[col] = pd.to_numeric(df[col], errors="coerce")
            elif dtype == "string":
                df[col] = df[col].astype(str)
            elif dtype == "datetime":
                df[col] = pd.to_datetime(df[col], errors="coerce")
            elif dtype == "boolean":
                df[col] = df[col].astype(bool)
            elif dtype == "category":
                df[col] = df[col].astype("category")
        except Exception:
            pass
    return df

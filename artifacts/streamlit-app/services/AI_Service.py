import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from scipy import stats


def generate_auto_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Generate automatic insights from a DataFrame."""
    insights = []
    numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
    cat_cols = list(df.select_dtypes(include=["object", "category"]).columns)

    # Dataset overview
    insights.append({
        "type": "overview",
        "icon": "chart",
        "title": "Dataset Overview",
        "description": f"Your dataset has {len(df):,} rows and {len(df.columns)} columns. "
                       f"It contains {len(numeric_cols)} numeric and {len(cat_cols)} categorical columns.",
        "severity": "info",
    })

    # Missing values insight
    missing = df.isnull().sum()
    cols_with_missing = missing[missing > 0]
    if len(cols_with_missing) > 0:
        worst_col = cols_with_missing.idxmax()
        worst_pct = round(cols_with_missing.max() / len(df) * 100, 1)
        insights.append({
            "type": "quality",
            "icon": "warning",
            "title": "Missing Values Detected",
            "description": f"{len(cols_with_missing)} column(s) have missing values. "
                           f"'{worst_col}' has the most at {worst_pct}% missing. "
                           "Consider using the Data Cleaning module to handle these.",
            "severity": "warning",
        })
    else:
        insights.append({
            "type": "quality",
            "icon": "check",
            "title": "No Missing Values",
            "description": "Great! Your dataset has no missing values — it is complete and ready for analysis.",
            "severity": "success",
        })

    # Duplicate rows
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        insights.append({
            "type": "quality",
            "icon": "warning",
            "title": f"{dup_count:,} Duplicate Rows Found",
            "description": f"There are {dup_count:,} duplicate rows in your dataset ({round(dup_count/len(df)*100, 1)}%). "
                           "Remove them in the Data Cleaning module for cleaner analysis.",
            "severity": "warning",
        })

    # Skewness insights for numeric columns
    if numeric_cols:
        skewness = df[numeric_cols].skew().abs()
        highly_skewed = skewness[skewness > 2].index.tolist()
        if highly_skewed:
            cols_str = ", ".join(f"'{c}'" for c in highly_skewed[:3])
            insights.append({
                "type": "distribution",
                "icon": "info",
                "title": "Highly Skewed Distributions",
                "description": f"Column(s) {cols_str} have high skewness (>2). "
                               "Consider log-transformation or outlier removal for more accurate statistical tests.",
                "severity": "info",
            })

    # Correlation insights
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr().abs()
        np.fill_diagonal(corr.values, 0)
        max_corr = corr.max().max()
        if max_corr > 0.8:
            idx = corr.stack().idxmax()
            insights.append({
                "type": "correlation",
                "icon": "link",
                "title": "Strong Correlation Detected",
                "description": f"Columns '{idx[0]}' and '{idx[1]}' have a very high correlation of {round(max_corr, 3)}. "
                               "This may indicate multicollinearity — consider removing one for ML models.",
                "severity": "info",
            })

    # Cardinality check
    for col in cat_cols:
        n_unique = df[col].nunique()
        if n_unique > 0.9 * len(df) and len(df) > 100:
            insights.append({
                "type": "cardinality",
                "icon": "info",
                "title": f"High Cardinality: '{col}'",
                "description": f"Column '{col}' has {n_unique:,} unique values (~{round(n_unique/len(df)*100)}% of rows). "
                               "This may be an ID or free-text column — consider excluding it from categorical analysis.",
                "severity": "info",
            })

    # Numeric outlier detection (IQR method)
    for col in numeric_cols[:5]:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr > 0:
            outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
            if len(outliers) > 0:
                pct = round(len(outliers) / len(df) * 100, 1)
                insights.append({
                    "type": "outlier",
                    "icon": "alert",
                    "title": f"Outliers in '{col}'",
                    "description": f"{len(outliers):,} outliers detected in '{col}' ({pct}% of data using IQR method). "
                                   "Outliers can skew statistics and visualizations.",
                    "severity": "warning",
                })
                break  # Only report one outlier insight to avoid overload

    return insights


def run_ai_analysis(
    df: pd.DataFrame,
    objective: str,
    test_embeddings: Any,
    test_names: List[str],
) -> Optional[tuple[list[Dict[str, Any]], str, str]]:
    numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
    cat_cols = list(df.select_dtypes(include=["object", "category"]).columns)

    if not objective or not numeric_cols:
        return None

    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)
        if a_norm == 0 or b_norm == 0:
            return 0.0
        return float(np.dot(a, b) / (a_norm * b_norm))

    # Simple keyword inference fallback
    objective_lower = objective.lower()
    if "correlation" in objective_lower or "associate" in objective_lower:
        chosen_test = "pearson_correlation"
    elif "anova" in objective_lower or "difference" in objective_lower:
        chosen_test = "anova"
    elif "chi" in objective_lower or "categorical" in objective_lower:
        chosen_test = "chi_square"
    else:
        chosen_test = "independent_t_test"

    valid_results = []
    target = numeric_cols[0] if numeric_cols else ""
    group = cat_cols[0] if cat_cols else ""

    if chosen_test == "pearson_correlation" and len(numeric_cols) >= 2:
        x = df[numeric_cols[0]].dropna()
        y = df[numeric_cols[1]].dropna()
        if len(x) > 1 and len(y) > 1:
            stat, pval = stats.pearsonr(x, y)
            valid_results.append({
                "test": "Pearson correlation",
                "result": {"correlation": round(float(stat), 4), "p_value": round(float(pval), 6)},
            })
            target = numeric_cols[0]
            group = numeric_cols[1]

    elif chosen_test == "chi_square" and len(cat_cols) >= 2:
        contingency = pd.crosstab(df[cat_cols[0]], df[cat_cols[1]])
        if contingency.size > 0:
            chi2, p, _, _ = stats.chi2_contingency(contingency)
            valid_results.append({
                "test": "Chi-square",
                "result": {"chi2": round(float(chi2), 4), "p_value": round(float(p), 6)},
            })
            target = cat_cols[0]
            group = cat_cols[1]

    elif chosen_test in ("independent_t_test", "anova") and numeric_cols and cat_cols:
        groups = df[[numeric_cols[0], cat_cols[0]]].dropna().groupby(cat_cols[0])[numeric_cols[0]]
        group_count = len(groups)
        if group_count >= 2:
            samples = [group.values for _, group in groups]
            if chosen_test == "independent_t_test" and group_count == 2:
                stat, pval = stats.ttest_ind(samples[0], samples[1], equal_var=False)
                valid_results.append({
                    "test": "Independent t-test",
                    "result": {"statistic": round(float(stat), 6), "p_value": round(float(pval), 6)},
                })
            elif chosen_test == "anova":
                stat, pval = stats.f_oneway(*samples)
                valid_results.append({
                    "test": "One-way ANOVA",
                    "result": {"statistic": round(float(stat), 6), "p_value": round(float(pval), 6)},
                })
            target = numeric_cols[0]
            group = cat_cols[0]

    if not valid_results:
        valid_results.append({
            "test": "No valid statistical test found",
            "result": {"error": "Unable to infer a valid test from the provided dataset."},
        })

    return valid_results, target, group

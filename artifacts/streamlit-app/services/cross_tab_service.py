import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, pearsonr, ttest_ind, f_oneway
import statsmodels.api as sm

def bin_numeric_variable(series, n_bins=5):
    """Bin a numeric variable into categorical ranges."""
    return pd.cut(series, bins=n_bins, duplicates='drop')

def cross_tab_analysis(df, row, col, prevalence=False):
    row_is_numeric = pd.api.types.is_numeric_dtype(df[row])
    col_is_numeric = pd.api.types.is_numeric_dtype(df[col])
    
    # Get actual cardinality
    row_nunique = df[row].nunique()
    col_nunique = df[col].nunique()
    
    # If numeric variable has too many unique values (continuous), bin it
    if row_is_numeric and row_nunique > 10:
        df = df.copy()
        df[row] = bin_numeric_variable(df[row])
        row_is_numeric = False
    
    if col_is_numeric and col_nunique > 10:
        df = df.copy()
        df[col] = bin_numeric_variable(df[col])
        col_is_numeric = False

    results = {}

    # =====================================================
    # CASE 1: BOTH CATEGORICAL (or binned)
    # =====================================================
    if not row_is_numeric and not col_is_numeric:
        results["type"] = "categorical"
        results["description"] = "Both variables are categorical → Performing Crosstab + Chi-square"

        try:
            counts = pd.crosstab(df[row], df[col])
            results["counts"] = counts

            row_percent = counts.div(counts.sum(axis=1), axis=0) * 100
            col_percent = counts.div(counts.sum(axis=0), axis=1) * 100
            results["row_percent"] = row_percent.round(2)
            results["col_percent"] = col_percent.round(2)

            # Chi-square test
            try:
                chi2, p, dof, _ = chi2_contingency(counts)
                results["chi_square"] = {
                    "chi2": round(float(chi2), 3),
                    "p_value": round(float(p), 4),
                    "dof": dof,
                    "significant": p < 0.05
                }
            except Exception as e:
                results["chi_square"] = {"error": str(e)}

            # ========================
            # PREVALENCE (Binary outcome)
            # ========================
            if prevalence:
                if df[col].nunique() == 2:
                    outcome_var = col
                    exposure_var = row
                elif df[row].nunique() == 2:
                    outcome_var = row
                    exposure_var = col
                else:
                    outcome_var = None

                if outcome_var:
                    positive = sorted(df[outcome_var].dropna().unique())[-1]
                    prev = (
                        df.groupby(exposure_var)[outcome_var]
                        .apply(lambda x: (x == positive).mean() * 100)
                        .reset_index(name=f"Prevalence of {positive} (%)")
                    )
                    results["prevalence"] = prev.to_dict(orient="records")
                else:
                    results["prevalence"] = {"error": "Prevalence requires one binary variable."}
        except Exception as e:
            results["error"] = f"Categorical analysis failed: {str(e)}"
            return results

    # =====================================================
    # CASE 2: ONE NUMERIC + ONE CATEGORICAL
    # =====================================================
    elif row_is_numeric ^ col_is_numeric:
        results["type"] = "mixed"
        results["description"] = "Numeric vs Categorical detected → Performing Mean Comparison"

        if row_is_numeric:
            numeric_var = row
            group_var = col
        else:
            numeric_var = col
            group_var = row

        try:
            # Drop NA
            data = df[[numeric_var, group_var]].dropna()
            results["data_points"] = len(data)

            summary = data.groupby(group_var)[numeric_var].agg(["count", "mean", "std"])
            summary["Mean ± SD"] = summary.apply(
                lambda x: f"{x['mean']:.2f} ± {x['std']:.2f}", axis=1
            )
            results["group_summary"] = summary[["count", "Mean ± SD"]].to_dict(orient="index")

            groups = data[group_var].unique()

            # ---- Two Groups → T-test
            if len(groups) == 2:
                g1 = data[data[group_var] == groups[0]][numeric_var]
                g2 = data[data[group_var] == groups[1]][numeric_var]

                t_stat, p_val = ttest_ind(g1, g2, equal_var=False)

                results["test"] = {
                    "type": "t-test",
                    "t_statistic": round(float(t_stat), 3),
                    "p_value": round(float(p_val), 4),
                    "significant": p_val < 0.05
                }

            # ---- More than 2 → ANOVA
            elif len(groups) > 2:
                samples = [
                    data[data[group_var] == g][numeric_var]
                    for g in groups
                ]

                f_stat, p_val = f_oneway(*samples)

                results["test"] = {
                    "type": "anova",
                    "f_statistic": round(float(f_stat), 3),
                    "p_value": round(float(p_val), 4),
                    "significant": p_val < 0.05
                }

            # ---- Logistic regression if categorical is binary
            if data[group_var].nunique() == 2:
                try:
                    y = pd.get_dummies(data[group_var], drop_first=True)
                    X = sm.add_constant(data[numeric_var])

                    model = sm.Logit(y, X).fit(disp=False)

                    coef = model.params.iloc[1]  # Fixed deprecation warning
                    or_val = np.exp(coef)

                    results["logistic_regression"] = {
                        "odds_ratio": round(float(or_val), 3),
                        "variable": numeric_var
                    }
                except Exception as e:
                    results["logistic_regression"] = {"error": str(e)}

            # ========================
            # PREVALENCE (if categorical is binary)
            # ========================
            if prevalence and data[group_var].nunique() == 2:
                prev = (
                    data.groupby(group_var)[numeric_var]
                    .count()
                    .reset_index(name="N")
                )
                results["group_distribution"] = prev.to_dict(orient="records")
        except Exception as e:
            results["error"] = f"Mixed analysis failed: {str(e)}"
            return results

    # =====================================================
    # CASE 3: BOTH NUMERIC
    # =====================================================
    elif row_is_numeric and col_is_numeric:
        results["type"] = "numeric"
        results["description"] = "Both variables numeric → Performing Correlation"

        try:
            data = df[[row, col]].dropna()
            results["data_points"] = len(data)

            r, p = pearsonr(data[row], data[col])

            results["correlation"] = {
                "r": round(float(r), 3),
                "p_value": round(float(p), 4),
                "significant": p < 0.05
            }
        except Exception as e:
            results["error"] = f"Correlation analysis failed: {str(e)}"
            return results

    return results
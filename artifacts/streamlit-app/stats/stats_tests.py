# tests.py

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

def prepare_for_logistic(df, target_col, group_col):
    data = df[[target_col, group_col]].dropna().copy()

    # Encode target (binary)
    if data[target_col].dtype == "object":
        data[target_col] = data[target_col].astype("category").cat.codes

    # Encode predictor
    if data[group_col].dtype == "object":
        data = pd.get_dummies(data, columns=[group_col], drop_first=True)

    return data


# ---------------------------------------------------------
# 1. Independent T-Test
# ---------------------------------------------------------
def independent_t_test(df, col1, col2):
    t, p = stats.ttest_ind(df[col1].dropna(), df[col2].dropna())
    return {"t_stat": t, "p_value": p}


# ---------------------------------------------------------
# 2. Paired T-Test
# ---------------------------------------------------------
def paired_t_test(df, col1, col2):
    t, p = stats.ttest_rel(df[col1], df[col2])
    return {"t_stat": t, "p_value": p}


# ---------------------------------------------------------
# 3. One-way ANOVA
# ---------------------------------------------------------
def anova(df, dependent, group):
    groups = [g[dependent].dropna() for _, g in df.groupby(group)]
    f, p = stats.f_oneway(*groups)
    return {"f_stat": f, "p_value": p}


# ---------------------------------------------------------
# 4. Chi-square Test
# ---------------------------------------------------------
def chi_square(df, col1, col2):
    table = pd.crosstab(df[col1], df[col2])
    chi2, p, dof, expected = stats.chi2_contingency(table)
    return {"chi2": chi2, "p_value": p, "dof": dof}


# ---------------------------------------------------------
# 5. Mann-Whitney U
# ---------------------------------------------------------
def mann_whitney_u(df, col1, col2):
    u, p = stats.mannwhitneyu(df[col1], df[col2])
    return {"U": u, "p_value": p}


# ---------------------------------------------------------
# 6. Kruskal-Wallis
# ---------------------------------------------------------
def kruskal_wallis(df, dependent, group):
    groups = [g[dependent] for _, g in df.groupby(group)]
    h, p = stats.kruskal(*groups)
    return {"H": h, "p_value": p}


# ---------------------------------------------------------
# 7. Pearson Correlation
# ---------------------------------------------------------
def pearson(df, col1, col2):
    r, p = stats.pearsonr(df[col1], df[col2])
    return {"r": r, "p_value": p}


# ---------------------------------------------------------
# 8. Spearman Correlation
# ---------------------------------------------------------
def spearman(df, col1, col2):
    rho, p = stats.spearmanr(df[col1], df[col2])
    return {"rho": rho, "p_value": p}


# ---------------------------------------------------------
# 9. Kendall Tau
# ---------------------------------------------------------
def kendall_tau(df, col1, col2):
    tau, p = stats.kendalltau(df[col1], df[col2])
    return {"tau": tau, "p_value": p}


# ---------------------------------------------------------
# 10. Linear Regression
# ---------------------------------------------------------
def linear_regression(df, y, x):
    model = sm.OLS(df[y], sm.add_constant(df[x])).fit()
    return {"summary": model.summary().as_text()}


# ---------------------------------------------------------
# 11. Logistic Regression
# ---------------------------------------------------------
import statsmodels.api as sm

def logistic_regression(df, target_col, group_col):
    data = prepare_for_logistic(df, target_col, group_col)

    y = data[target_col]
    X = data.drop(columns=[target_col])
    X = sm.add_constant(X)

    model = sm.Logit(y, X).fit(disp=False)

    return {
        "coef": model.params.to_dict(),
        "p_values": model.pvalues.to_dict(),
        "odds_ratio": (model.params.apply(np.exp)).to_dict()
    }



# ---------------------------------------------------------
# 12. Wilcoxon Signed-Rank
# ---------------------------------------------------------
def wilcoxon_test(df, col1, col2):
    stat, p = stats.wilcoxon(df[col1], df[col2])
    return {"stat": stat, "p_value": p}


# ---------------------------------------------------------
# 13. Friedman Test
# ---------------------------------------------------------
def friedman(df, c1, c2, c3):
    stat, p = stats.friedmanchisquare(df[c1], df[c2], df[c3])
    return {"stat": stat, "p_value": p}


# ---------------------------------------------------------
# 14. Binomial Test
# ---------------------------------------------------------
def binomial_test(df, col, success):
    count_success = (df[col] == success).sum()
    n = len(df[col])
    p = stats.binomtest(count_success, n)
    return {"proportion_success": count_success/n, "p_value": p.pvalue}


# ---------------------------------------------------------
# 15. Shapiro-Wilk Normality Test
# ---------------------------------------------------------
def shapiro(df, col):
    stat, p = stats.shapiro(df[col])
    return {"W": stat, "p_value": p}


# ---------------------------------------------------------
# 16. Kolmogorov-Smirnov Test
# ---------------------------------------------------------
def ks(df, col):
    stat, p = stats.kstest(df[col], 'norm')
    return {"KS_stat": stat, "p_value": p}


# ---------------------------------------------------------
# 17. Levene’s Test for Homogeneity of Variance
# ---------------------------------------------------------
def levene(df, col1, col2):
    stat, p = stats.levene(df[col1], df[col2])
    return {"Levene_stat": stat, "p_value": p}


# ---------------------------------------------------------
# 18. Bartlett’s Test
# ---------------------------------------------------------
def bartlett(df, col1, col2):
    stat, p = stats.bartlett(df[col1], df[col2])
    return {"stat": stat, "p_value": p}


# ---------------------------------------------------------
# 19. Tukey HSD
# ---------------------------------------------------------
def tukey(df, dependent, group):
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    res = pairwise_tukeyhsd(df[dependent], df[group])
    return {"summary": str(res)}


# ---------------------------------------------------------
# 20. ROC-AUC Score
# ---------------------------------------------------------
def roc_auc(df, y_true, y_prob):
    from sklearn.metrics import roc_auc_score
    auc = roc_auc_score(df[y_true], df[y_prob])
    return {"roc_auc": auc}


# ---------------------------------------------------------
# 21. Cohen’s d (effect size)
# ---------------------------------------------------------
def cohens_d(df, col1, col2):
    g1, g2 = df[col1], df[col2]
    d = (g1.mean() - g2.mean()) / np.sqrt((g1.var() + g2.var()) / 2)
    return {"cohens_d": d}


# ---------------------------------------------------------
# 22. Hedges g
# ---------------------------------------------------------
def hedges_g(df, col1, col2):
    g1, g2 = df[col1], df[col2]
    d = (g1.mean() - g2.mean()) / np.sqrt((g1.var() + g2.var()) / 2)
    correction = 1 - (3 / (4*(len(g1)+len(g2))-9))
    return {"hedges_g": d * correction}


# ---------------------------------------------------------
# 23. Fisher Exact Test
# ---------------------------------------------------------
def fisher_exact(df, col1, col2):
    table = pd.crosstab(df[col1], df[col2])
    odds, p = stats.fisher_exact(table)
    return {"odds_ratio": odds, "p_value": p}


# ---------------------------------------------------------
# 24. McNemar’s Test
# ---------------------------------------------------------
def mcnemar(df, col1, col2):
    from statsmodels.stats.contingency_tables import mcnemar
    table = pd.crosstab(df[col1], df[col2])
    result = mcnemar(table, exact=True)
    return {"statistic": result.statistic, "p_value": result.pvalue}


# ---------------------------------------------------------
# 25. Cochran’s Q Test
# ---------------------------------------------------------
def cochran_q(df, *cols):
    from statsmodels.stats.contingency_tables import cochrans_q
    data = df[list(cols)]
    stat, p = cochrans_q(data)
    return {"Q": stat, "p_value": p}


# ---------------------------------------------------------
# 26. Durbin-Watson Test
# ---------------------------------------------------------
def durbin_watson(df, residuals):
    from statsmodels.stats.stattools import durbin_watson
    return {"DW": durbin_watson(df[residuals])}


# ---------------------------------------------------------
# 27. Breusch-Pagan (heteroscedasticity)
# ---------------------------------------------------------
def breusch_pagan(df, y, x):
    from statsmodels.stats.diagnostic import het_breuschpagan
    model = sm.OLS(df[y], sm.add_constant(df[x])).fit()
    lm, lm_p, f, f_p = het_breuschpagan(model.resid, model.model.exog)
    return {"LM": lm, "p_value": lm_p}


# ---------------------------------------------------------
# 28. Jarque-Bera Test
# ---------------------------------------------------------
def jarque_bera(df, col):
    jb, p = stats.jarque_bera(df[col])
    return {"JB": jb, "p_value": p}


# ---------------------------------------------------------
# 29. Anderson-Darling Normality Test
# ---------------------------------------------------------
def anderson(df, col):
    res = stats.anderson(df[col])
    return {"statistic": res.statistic, "critical_values": res.critical_values.tolist()}


# ---------------------------------------------------------
# 30. Z-Test for proportion
# ---------------------------------------------------------
def z_test_prop(df, col, success, p0):
    count = (df[col] == success).sum()
    n = len(df[col])
    p_hat = count / n
    z = (p_hat - p0) / np.sqrt(p0*(1-p0)/n)
    p = stats.norm.sf(abs(z))*2
    return {"z_stat": z, "p_value": p}


# ---------------------------------------------------------
# 31. Two-Proportion Z-Test
# ---------------------------------------------------------
def two_proportion_z(df, col1, val1, col2, val2):
    n1 = len(df[col1])
    n2 = len(df[col2])
    p1 = (df[col1] == val1).sum()/n1
    p2 = (df[col2] == val2).sum()/n2
    p = (p1*n1 + p2*n2) / (n1+n2)
    z = (p1 - p2) / np.sqrt(p*(1-p)*(1/n1 + 1/n2))
    pval = stats.norm.sf(abs(z))*2
    return {"z_stat": z, "p_value": pval}


# ---------------------------------------------------------
# 32. One-Sample T-Test
# ---------------------------------------------------------
def one_sample_t(df, col, popmean):
    t, p = stats.ttest_1samp(df[col], popmean)
    return {"t": t, "p_value": p}


# ---------------------------------------------------------
# 33. Two-Sample Z-Test (means)
# ---------------------------------------------------------
def z_test_means(df, col1, col2):
    m1, m2 = df[col1].mean(), df[col2].mean()
    s1, s2 = df[col1].std(), df[col2].std()
    n1, n2 = len(df[col1]), len(df[col2])
    z = (m1 - m2) / np.sqrt(s1**2/n1 + s2**2/n2)
    p = stats.norm.sf(abs(z))*2
    return {"z": z, "p_value": p}


# ---------------------------------------------------------
# 34. ANOVA Repeated Measures
# ---------------------------------------------------------
def anova_rm(df, subject, within, dv):
    model = smf.mixedlm(f"{dv} ~ {within}", df, groups=df[subject])
    result = model.fit()
    return {"summary": result.summary().as_text()}


# ---------------------------------------------------------
# 35. Poisson Regression
# ---------------------------------------------------------
def poisson_regression(df, y, x):
    model = sm.GLM(df[y], sm.add_constant(df[x]), family=sm.families.Poisson()).fit()
    return {"summary": model.summary().as_text()}


# ---------------------------------------------------------
# 36. Probit Regression
# ---------------------------------------------------------
def probit_regression(df, y, x):
    model = sm.Probit(df[y], sm.add_constant(df[x])).fit()
    return {"summary": model.summary().as_text()}


# ---------------------------------------------------------
# 37. Cox Proportional Hazards Model
# ---------------------------------------------------------
def cox_regression(df, time, event, covariate):
    from lifelines import CoxPHFitter
    cph = CoxPHFitter()
    subdf = df[[time, event, covariate]]
    cph.fit(subdf, time, event_col=event)
    return {"summary": cph.summary.to_string()}


# ---------------------------------------------------------
# 38. Kaplan-Meier Survival Curve
# ---------------------------------------------------------
def kaplan(df, time, event):
    from lifelines import KaplanMeierFitter
    km = KaplanMeierFitter()
    km.fit(df[time], df[event])
    return {"survival_table": km.event_table.to_string()}


# ---------------------------------------------------------
# 39. ADF Test (Stationarity)
# ---------------------------------------------------------
def adf(df, col):
    from statsmodels.tsa.stattools import adfuller
    stat, p, _, _, _, _ = adfuller(df[col])
    return {"ADF_stat": stat, "p_value": p}


# ---------------------------------------------------------
# 40. Ljung-Box Test
# ---------------------------------------------------------
def ljung_box(df, col, lags=10):
    from statsmodels.stats.diagnostic import acorr_ljungbox
    res = acorr_ljungbox(df[col], lags=[lags], return_df=True)
    return res.to_dict()


# ---------------------------------------------------------
# 41. Wald Test
# ---------------------------------------------------------
def wald_test(df, y, x):
    model = sm.OLS(df[y], sm.add_constant(df[x])).fit()
    return {"wald": model.wald_test_terms().table.to_string()}


# ---------------------------------------------------------
# 42. Hosmer-Lemeshow Test
# ---------------------------------------------------------
def hosmer(df, y_true, y_prob):
    from statsmodels.stats.diagnostic import breaks_homoscedasticity
    return {"Not_Exact_HL": "Manual HL test to be added, use calibration curves instead"}


# ---------------------------------------------------------
# 43. Chi-square GOF
# ---------------------------------------------------------
def chisquare_gof(df, col):
    stat, p = stats.chisquare(df[col])
    return {"stat": stat, "p_value": p}


# ---------------------------------------------------------
# 44. Variance Ratio F-Test
# ---------------------------------------------------------

def f_test(df, col1, col2):
    f = df[col1].var() / df[col2].var()
    df1, df2 = len(df[col1])-1, len(df[col2])-1
    p = 1 - stats.f.cdf(f, df1, df2)
    return {"F": f, "p_value": p}


# ---------------------------------------------------------
# 45. Rank-Biserial Correlation
# ---------------------------------------------------------

def rank_biserial(df, col1, col2):
    u, _ = stats.mannwhitneyu(df[col1], df[col2])
    n1, n2 = len(df[col1]), len(df[col2])
    r = 1 - (2*u)/(n1*n2)
    return {"rank_biserial": r}


# ---------------------------------------------------------
# 46. Phi Coefficient
# ---------------------------------------------------------

def phi(df, col1, col2):
    table = pd.crosstab(df[col1], df[col2]).values
    num = (table[0][0]*table[1][1]) - (table[0][1]*table[1][0])
    den = np.sqrt(table.sum(axis=1).prod() * table.sum(axis=0).prod())
    return {"phi": num/den}


# ---------------------------------------------------------
# 47. Cramer's V
# ---------------------------------------------------------

def cramers_v(df, col1, col2):
    table = pd.crosstab(df[col1], df[col2]).values
    chi2 = stats.chi2_contingency(table)[0]
    n = table.sum()
    r, k = table.shape
    return {"cramers_v": np.sqrt(chi2/(n*(min(r-1, k-1))))}


# ---------------------------------------------------------
# 48. Odds Ratio
# ---------------------------------------------------------

def odds_ratio(df, col1, col2):
    table = pd.crosstab(df[col1], df[col2]).values
    OR = (table[0][0]*table[1][1]) / (table[0][1]*table[1][0])
    return {"odds_ratio": OR}


# ---------------------------------------------------------
# 49. Relative Risk
# ---------------------------------------------------------

def relative_risk(df, col1, col2):
    table = pd.crosstab(df[col1], df[col2]).values
    risk1 = table[0][0] / table[0].sum()
    risk2 = table[1][0] / table[1].sum()
    return {"relative_risk": risk1/risk2}


# ---------------------------------------------------------
# 50. Mutual Information Score
# ---------------------------------------------------------

def mutual_info(df, col1, col2):
    from sklearn.metrics import mutual_info_score
    mi = mutual_info_score(df[col1], df[col2])
    return {"mutual_information": mi}


TEST_REGISTRY = {
    "independent_t_test": independent_t_test,
    "paired_t_test": paired_t_test,
    "anova": anova,
    "chi_square": chi_square,
    "mann_whitney_u": mann_whitney_u,
    "kruskal_wallis": kruskal_wallis,
    "pearson_correlation": pearson,
    "spearman_correlation": spearman,
    "kendall_tau": kendall_tau,
    "linear_regression": linear_regression,
    "logistic_regression": logistic_regression,
    "wilcoxon": wilcoxon_test,
    "friedman_test": friedman,
    "binomial_test": binomial_test,
    "shapiro_test": shapiro,
    "ks_test": ks,
    "levene_test": levene,
    "bartlett_test": bartlett,
    "tukey_hsd": tukey,
    "roc_auc": roc_auc,
    "cohens_d": cohens_d,
    "hedges_g": hedges_g,
    "fisher_exact": fisher_exact,
    "mcnemar_test": mcnemar,
    "cochran_q": cochran_q,
    "durbin_watson": durbin_watson,
    "breusch_pagan": breusch_pagan,
    "jarque_bera": jarque_bera,
    "anderson_darling": anderson,
    "z_test_proportion": z_test_prop,
    "two_proportion_ztest": two_proportion_z,
    "one_sample_t_test": one_sample_t,
    "two_sample_ztest": z_test_means,
    "anova_rm": anova_rm,
    "poisson_regression": poisson_regression,
    "probit_regression": probit_regression,
    "cox_regression": cox_regression,
    "kaplan_meier": kaplan,
    "adf_test": adf,
    "ljung_box": ljung_box,
    "wald_test": wald_test,
    "hosmer_lemeshow": hosmer,
    "chisquare_gof": chisquare_gof,
    "variance_ratio": f_test,
    "rank_biserial": rank_biserial,
    "phi_coefficient": phi,
    "cramers_v": cramers_v,
    "odds_ratio": odds_ratio,
    "relative_risk": relative_risk,
    "mutual_information": mutual_info
}

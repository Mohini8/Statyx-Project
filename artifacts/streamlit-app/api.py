import base64
import io
from typing import Any, Dict, List, Optional, TypedDict

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from scipy import stats
from sentence_transformers import SentenceTransformer

from services.Cleaning_Service import apply_cleaning_pipeline, detect_issues, is_numeric_like
from services.Statistics_Service import (
    descriptive_statistics,
    build_overall_categorical_table,
    get_categorical_details,
    get_numeric_interpretations,
)
from services.AI_Service import generate_auto_insights
from services.Report_Service import generate_pdf_report, generate_word_report
from services.cross_tab_service import cross_tab_analysis
from services.visualization_service import generate_plot
from utils.Dataframe_Utils import load_dataframe
from ai.objective_engine import analyze_objective
from stats.stats_tests import TEST_REGISTRY

MODEL = SentenceTransformer("intfloat/e5-base")
TEST_DESCRIPTIONS = {
    "independent_t_test": "compare mean of a continuous variable between two independent groups",
    "paired_t_test": "compare mean before and after intervention on same subjects",
    "one_sample_t_test": "compare mean against known population value",
    "anova": "compare mean across more than two groups",
    "anova_rm": "compare repeated measurements",
    "mann_whitney_u": "nonparametric comparison between two independent groups",
    "kruskal_wallis": "nonparametric comparison across multiple groups",
    "chi_square": "association between two categorical variables",
    "fisher_exact": "association between two binary variables",
    "chisquare_gof": "goodness of fit test",
    "mcnemar_test": "paired categorical association",
    "cochran_q": "compare proportions across repeated groups",
    "pearson_correlation": "linear correlation",
    "spearman_correlation": "rank based correlation",
    "kendall_tau": "ordinal association",
    "mutual_information": "nonlinear dependency",
    "linear_regression": "predict continuous outcome",
    "logistic_regression": "predict binary outcome",
    "poisson_regression": "model count outcome",
    "probit_regression": "binary outcome with probit",
    "cohens_d": "effect size",
    "hedges_g": "bias corrected effect size",
    "phi_coefficient": "binary association",
    "cramers_v": "categorical association strength",
    "odds_ratio": "odds comparison",
    "relative_risk": "risk comparison"
}
TEST_NAMES = list(TEST_DESCRIPTIONS.keys())
TEST_TEXTS = [f"passage: {desc}" for desc in TEST_DESCRIPTIONS.values()]
TEST_EMBEDDINGS = MODEL.encode(TEST_TEXTS, convert_to_tensor=True)

app = FastAPI(title="Statyx Python Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


class DatasetPayload(BaseModel):
    rows: List[Dict[str, Any]]


class CleanAction(BaseModel):
    column: str
    dtype: Optional[str] = None
    method: str
    custom: Optional[str] = None
    keep: Optional[str] = None
    dup_subset: Optional[List[str]] = None
    drop_column: Optional[bool] = False


class CleanRequest(DatasetPayload):
    actions: List[CleanAction]


class AiRequest(DatasetPayload):
    objective: Optional[str] = None
    target_col: Optional[str] = None
    group_col: Optional[str] = None
    additional_tests: Optional[List[str]] = None


class VisualizationRequest(DatasetPayload):
    chartType: str
    columns: List[str]
    options: Optional[Dict[str, Any]] = None


class CrossTabRequest(DatasetPayload):
    row: str
    col: str
    prevalence: Optional[bool] = False


class ReportRequest(DatasetPayload):
    format: str
    fileName: Optional[str] = "dataset"
    insights: Optional[List[Dict[str, Any]]] = None


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.map(lambda c: str(c).strip().lower())
    return df


def df_preview(df: pd.DataFrame, rows: int = 10) -> List[Dict[str, Any]]:
    return df.head(rows).replace({np.nan: None}).to_dict(orient="records")


def encode_png(fig) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def compute_objective_tests(df: pd.DataFrame, objective: str, target_col: Optional[str] = None, group_col: Optional[str] = None, additional_tests: Optional[List[str]] = None) -> Dict[str, Any]:
    objective_lower = objective.lower()
    if not target_col or not group_col:
        mentioned = [c for c in df.columns if c.lower().replace("_", " ") in objective_lower]
        if len(mentioned) >= 2:
            target_col = target_col or mentioned[0]
            group_col = group_col or mentioned[1]

    result = analyze_objective(
        df,
        objective,
        TEST_EMBEDDINGS,
        TEST_NAMES,
        target_col=target_col,
        group_col=group_col,
        max_attempts=50,
    )
    if result is None:
        return {"top_tests": [], "additional_test_options": [], "additional_test_results": [], "target": target_col, "group": group_col}

    top_tests, target, group, additional_options = result

    additional_results: List[Dict[str, Any]] = []
    for key in (additional_tests or []):
        if key not in TEST_REGISTRY:
            continue
        try:
            out = TEST_REGISTRY[key](df, target, group)
            if isinstance(out, dict) and out:
                additional_results.append({"test_key": key, "test": f"{key.replace('_', ' ').title()} ({target} vs {group})", "result": out})
        except Exception:
            continue

    return {
        "top_tests": top_tests,
        "additional_test_options": additional_options,
        "additional_test_results": additional_results,
        "target": target,
        "group": group,
    }

@app.post("/api/python/upload")
async def upload_dataset(file: UploadFile = File(...)) -> JSONResponse:
    content = await file.read()
    df = load_dataframe(io.BytesIO(content), file.filename)
    if df is None:
        raise HTTPException(status_code=400, detail="Unable to parse uploaded file. Use CSV or Excel.")

    df = normalize_dataframe(df)
    return JSONResponse(
        content=jsonable_encoder({
            "preview": df_preview(df),
            "rows": df.replace({np.nan: None}).to_dict(orient="records"),
            "columns": list(df.columns),
            "rowCount": len(df),
            "columnCount": len(df.columns),
            "info": {
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "missing": df.isnull().sum().to_dict(),
                "duplicateCount": int(df.duplicated().sum()),
            },
        })
    )


@app.post("/api/python/clean/detect")
def detect_cleaning(request: DatasetPayload) -> JSONResponse:
    df = normalize_dataframe(pd.DataFrame(request.rows))
    issues = detect_issues(df)
    return JSONResponse(content=jsonable_encoder({"issues": issues, "preview": df_preview(df), "columns": list(df.columns)}))


@app.post("/api/python/clean/apply")
def apply_cleaning(request: CleanRequest) -> JSONResponse:
    df = normalize_dataframe(pd.DataFrame(request.rows))
    for action in request.actions:
        if action.column == "__duplicates__":
            continue
        if action.drop_column:
            df = df.drop(columns=[action.column], errors="ignore")
            continue
        if action.column not in df.columns:
            continue

        if action.dtype == "numeric":
            df[action.column] = pd.to_numeric(df[action.column], errors="coerce")
            if action.method == "mean":
                df[action.column].fillna(df[action.column].mean(), inplace=True)
            elif action.method == "median":
                df[action.column].fillna(df[action.column].median(), inplace=True)
            elif action.method == "zero":
                df[action.column].fillna(0, inplace=True)
            elif action.method == "custom" and action.custom is not None:
                try:
                    df[action.column].fillna(float(action.custom), inplace=True)
                except Exception:
                    df[action.column].fillna(action.custom, inplace=True)
        else:
            numeric_mask = df[action.column].apply(is_numeric_like)
            df.loc[numeric_mask, action.column] = pd.NA
            if action.method == "mode":
                mode_val = df[action.column].mode()
                if len(mode_val) > 0:
                    df[action.column].fillna(mode_val[0], inplace=True)
            elif action.method == "custom" and action.custom is not None:
                df[action.column].fillna(str(action.custom), inplace=True)

    if any(action.column == "__duplicates__" for action in request.actions):
        df = df.drop_duplicates()

    preview = df_preview(df)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return JSONResponse(
        content=jsonable_encoder({
            "preview": preview,
            "cleanedCsv": base64.b64encode(csv_buffer.getvalue().encode("utf-8")).decode("utf-8"),
            "columns": list(df.columns),
        })
    )


@app.post("/api/python/stats/summary")
def stats_summary(request: DatasetPayload) -> JSONResponse:
    df = normalize_dataframe(pd.DataFrame(request.rows))
    descriptive_df = descriptive_statistics(df)
    categorical_df = build_overall_categorical_table(df)

    categorical_records: List[Dict[str, Any]] = []
    if not categorical_df.empty:
        for _, row in categorical_df.iterrows():
            categorical_records.append({
                "column": row["column"],
                "count": int(row["count"]),
                "unique": int(row["unique"]),
                "top": row["top"],
                "freq": int(row["freq"]),
                "top_percentage": float(row["top_percentage"]),
            })

    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    return JSONResponse(
        content=jsonable_encoder({
            "descriptive": descriptive_df.reset_index().rename(columns={"index": "statistic"}).replace({np.nan: None}).to_dict(orient="records"),
            "categorical": categorical_records,
            "categoricalDetails": get_categorical_details(df),
            "numericInterpretations": get_numeric_interpretations(df),
            "numericColumns": numeric_cols,
            "categoricalColumns": cat_cols,
            "preview": df_preview(df),
            "columns": list(df.columns),
        })
    )


@app.post("/api/python/visualization")
def visualization(request: VisualizationRequest) -> JSONResponse:
    df = normalize_dataframe(pd.DataFrame(request.rows))
    if not request.columns or len(request.columns) == 0:
        raise HTTPException(status_code=400, detail="At least one column is required for visualization.")

    try:
        fig = generate_plot(df, request.chartType, request.columns)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Visualization generation failed: {error}")

    img_base64 = encode_png(fig)
    return JSONResponse(content=jsonable_encoder({"imageBase64": img_base64}))


@app.post("/api/python/ai/insights")
def ai_insights(request: AiRequest) -> JSONResponse:
    df = normalize_dataframe(pd.DataFrame(request.rows))
    insights = generate_auto_insights(df)
    objective = request.objective or ""
    analysis = compute_objective_tests(
        df,
        objective,
        request.target_col,
        request.group_col,
        request.additional_tests,
    ) if objective else {"top_tests": [], "additional_test_options": [], "additional_test_results": [], "target": request.target_col, "group": request.group_col}
    return JSONResponse(content=jsonable_encoder({"insights": insights, "tests": analysis["top_tests"], "additionalTests": analysis["additional_test_options"], "additionalTestResults": analysis["additional_test_results"], "target": analysis["target"], "group": analysis["group"], "columns": list(df.columns)}))


@app.post("/api/python/cross-tab")
def cross_tab(request: CrossTabRequest) -> JSONResponse:
    df = normalize_dataframe(pd.DataFrame(request.rows))
    result = cross_tab_analysis(df, request.row, request.col, request.prevalence or False)

    # Convert DataFrames to records for JSON serialization
    if "counts" in result and isinstance(result["counts"], pd.DataFrame):
        result["counts"] = result["counts"].reset_index().fillna("").to_dict(orient="records")
    if "row_percent" in result and isinstance(result["row_percent"], pd.DataFrame):
        result["row_percent"] = result["row_percent"].reset_index().fillna("").to_dict(orient="records")
    if "col_percent" in result and isinstance(result["col_percent"], pd.DataFrame):
        result["col_percent"] = result["col_percent"].reset_index().fillna("").to_dict(orient="records")
    if "group_summary" in result and isinstance(result["group_summary"], dict):
        # Already dict
        pass

    return JSONResponse(content=jsonable_encoder({"result": result}))


@app.post("/api/python/report")
def report(request: ReportRequest) -> JSONResponse:
    df = normalize_dataframe(pd.DataFrame(request.rows))
    filename = request.fileName or "dataset"
    if request.format.lower() == "pdf":
        content = generate_pdf_report(df, filename, request.insights or [])
        content_type = "application/pdf"
        extension = "pdf"
    else:
        content = generate_word_report(df, filename, request.insights or [])
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        extension = "docx"

    if not content:
        raise HTTPException(status_code=500, detail="Report generation failed.")

    return JSONResponse(
        content=jsonable_encoder({
            "fileName": f"{filename}.{extension}",
            "contentBase64": base64.b64encode(content).decode("utf-8"),
            "contentType": content_type,
        })
    )


@app.post("/api/python/feedback")
def feedback(request: BaseModel) -> JSONResponse:
    return JSONResponse(content={"success": True, "message": "Thanks for your feedback."})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8502)

import { useEffect, useMemo, useState } from "react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, UploadCloud, Wand2, BarChart3, LineChart, BrainCircuit, Network, FileText, DownloadCloud, CheckCircle2, MessageSquare } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LabelList,
} from "recharts";
import {
  uploadDataset,
  detectCleaningIssues,
  applyCleaning,
  fetchStatsSummary,
  generateVisualization,
  runAiInsights,
  runCrossTab,
  generateReport,
  submitFeedback,
  DatasetRow,
} from "@/lib/python-api";

type CategoryChartOptions = {
  chartType: "Column" | "Bar";
  sort: "None" | "Descending" | "Ascending";
  showLabels: boolean;
  showLegend: boolean;
  color: string;
  title: string;
  titleSize: number;
  axisSize: number;
  barWidth: number;
  height: number;
  bg: string;
  grid: boolean;
  legendPosition: "top" | "bottom" | "left" | "right";
};

type StatsResult = {
  descriptive: any[];
  categorical: any[];
  categoricalDetails: Record<string, { category: string; count: number; percentage: number }[]>;
  numericInterpretations: { column: string; mean: number; std: number; median: number; min: number; max: number; summary: string }[];
  numericColumns: string[];
  categoricalColumns: string[];
};

const CHART_TYPES = [
  { value: "histogram", label: "Histogram" },
  { value: "bar", label: "Bar" },
  { value: "line", label: "Line" },
  { value: "scatter", label: "Scatter" },
  { value: "boxplot", label: "Box Plot" },
  { value: "pie", label: "Pie" },
];

const TABS: Record<string, { title: string; description: string }> = {
  upload: { title: "Upload Data", description: "Start by uploading your dataset so the Python analytics backend can process it." },
  clean: { title: "Data Cleaning", description: "Detect missing values, duplicate rows, and apply smart cleaning strategies." },
  statistics: { title: "Statistics", description: "Produce descriptive summaries and category-level statistics from your dataset." },
  visualizations: { title: "Visualizations", description: "Render charts and plots from the dataset using backend Python logic." },
  "ai-analysis": { title: "AI Analysis", description: "Ask the AI engine for smart test recommendations and model-driven insights." },
  "cross-tabulation": { title: "Cross Tabulation", description: "Explore relationships between categorical variables with cross-tab analysis." },
  reports: { title: "Reports", description: "Export PDF or Word reports built from the current dataset and generated insights." },
};

function renderTable(rows: DatasetRow[], columns: string[]) {
  if (!rows.length || !columns.length) {
    return <div className="text-sm text-muted-foreground">No preview available.</div>;
  }

  return (
    <div className="overflow-x-auto border border-border rounded-lg bg-background">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-muted text-muted-foreground">
          <tr>
            {columns.map((column) => (
              <th key={column} className="px-3 py-2 uppercase tracking-wide text-xs font-medium">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 8).map((row, index) => (
            <tr key={index} className={index % 2 === 0 ? "bg-card" : "bg-background"}>
              {columns.map((column) => (
                <td key={column} className="px-3 py-2 align-top text-sm text-foreground">
                  {String(row[column] ?? "").slice(0, 80)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Analytics() {
  const [, setLocation] = useLocation();
  const [page, setPage] = useState<string>("upload");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [datasetRows, setDatasetRows] = useState<DatasetRow[]>([]);
  const [datasetColumns, setDatasetColumns] = useState<string[]>([]);
  const [previewRows, setPreviewRows] = useState<DatasetRow[]>([]);
  const [fileInfo, setFileInfo] = useState<{ rowCount: number; columnCount: number; info: any } | null>(null);

  const [cleanIssues, setCleanIssues] = useState<any[]>([]);
  const [cleanActions, setCleanActions] = useState<Record<string, any>>({});
  const [cleanPreview, setCleanPreview] = useState<DatasetRow[]>([]);
  const [cleanDownload, setCleanDownload] = useState<string | null>(null);

  const [statsResult, setStatsResult] = useState<StatsResult | null>(null);
  const [categoryChartOptions, setCategoryChartOptions] = useState<Record<string, CategoryChartOptions>>({});
  const [visualizationImage, setVisualizationImage] = useState<string | null>(null);
  const [chartType, setChartType] = useState<string>(CHART_TYPES[0].value);
  const [visualizationColumns, setVisualizationColumns] = useState<string[]>([]);

  const [objective, setObjective] = useState<string>("");
  const [aiResult, setAiResult] = useState<{ insights: any[]; tests: any[] } | null>(null);

  const [crossRow, setCrossRow] = useState<string>("");
  const [crossCol, setCrossCol] = useState<string>("");
  const [crossPrevalence, setCrossPrevalence] = useState<boolean>(false);
  const [crossResult, setCrossResult] = useState<any | null>(null);

  const [reportStatus, setReportStatus] = useState<string | null>(null);

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const currentPage = searchParams.get("page") || "upload";
    setPage(currentPage);
  }, [window.location.search]);

  useEffect(() => {
    if (datasetColumns.length > 0 && visualizationColumns.length === 0) {
      setVisualizationColumns([datasetColumns[0]]);
    }
  }, [datasetColumns, visualizationColumns.length]);

  const datasetLoaded = datasetRows.length > 0;
  const moduleTitle = TABS[page]?.title ?? "Upload Data";
  const moduleDescription = TABS[page]?.description ?? "Work with your dataset using backend Python logic.";

  const handleFileUpload = async (file: File | null) => {
    if (!file) {
      return;
    }

    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      const result = await uploadDataset(file);
      setDatasetRows(result.rows);
      setPreviewRows(result.preview);
      setDatasetColumns(result.columns);
      setFileInfo({ rowCount: result.rowCount, columnCount: result.columnCount, info: result.info });
      setCleanIssues([]);
      setCleanActions({});
      setCleanPreview([]);
      setCleanDownload(null);
      setSuccess("Dataset uploaded successfully.");
    } catch (err: any) {
      setError(err.message || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleDetectIssues = async () => {
    if (!datasetLoaded) {
      setError("Upload a dataset first.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const result = await detectCleaningIssues(datasetRows);
      setCleanIssues(result.issues);
      setCleanActions({});
      setCleanPreview([]);
      setCleanDownload(null);
      setPreviewRows(result.preview);
      setSuccess("Cleaning issues detected.");
    } catch (err: any) {
      setError(err.message || "Could not detect issues.");
    } finally {
      setLoading(false);
    }
  };

  const handleApplyCleaning = async () => {
    if (!datasetLoaded) {
      setError("Upload a dataset first.");
      return;
    }

    setError(null);
    setLoading(true);
    try {
      const actions = cleanIssues
        .map((issue, index) => {
          const issueKey = `${issue.column}-${issue.issue}-${index}`;
          if (issue.column === "__duplicates__") {
            const selected = cleanActions[issueKey] ?? "remove";
            return selected === "remove"
              ? { column: issue.column, method: "remove", custom: null, drop_column: false }
              : null;
          }

          return {
            column: issue.column,
            dtype: issue.dtype,
            method: cleanActions[issueKey] || (issue.dtype === "numeric" ? "mean" : "mode"),
            custom: cleanActions[`${issueKey}_custom`],
            drop_column: false,
          };
        })
        .filter(Boolean);

      const result = await applyCleaning(datasetRows, actions as any[]);
      const rows = result.preview;
      setDatasetRows(rows.length > 0 ? rows : datasetRows);
      setCleanPreview(rows);
      setCleanDownload(result.cleanedCsv);
      setPreviewRows(rows);
      setSuccess("Cleaning applied successfully.");
    } catch (err: any) {
      setError(err.message || "Unable to apply cleaning.");
    } finally {
      setLoading(false);
    }
  };

  const downloadCleanedDataset = () => {
    if (!cleanDownload) {
      return;
    }
    const decoded = atob(cleanDownload);
    const blob = new Blob([decoded], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "cleaned_dataset.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  const getDefaultCategoryChartOptions = (column: string): CategoryChartOptions => ({
    chartType: "Column",
    sort: "None",
    showLabels: true,
    showLegend: true,
    color: "#4F76C7",
    title: `Distribution of ${column}`,
    titleSize: 18,
    axisSize: 12,
    barWidth: 0.6,
    height: 420,
    bg: "#ffffff",
    grid: true,
    legendPosition: "top",
  });

  const updateCategoryChartOption = <K extends keyof CategoryChartOptions>(
    column: string,
    key: K,
    value: CategoryChartOptions[K],
  ) => {
    setCategoryChartOptions((prev) => ({
      ...prev,
      [column]: {
        ...prev[column],
        [key]: value,
      },
    }));
  };

  const getVisualizationRequirements = (type: string) => {
    switch (type) {
      case "histogram":
      case "boxplot":
      case "pie":
        return { min: 1, max: 1, requiresNumeric: type !== "pie", requiresCategorical: type === "pie" };
      case "scatter":
      case "line":
        return { min: 2, max: 2, requiresNumeric: true, requiresCategorical: false };
      case "bar":
        return { min: 2, max: 2, requiresNumeric: true, requiresCategorical: false };
      default:
        return { min: 1, max: 2, requiresNumeric: false, requiresCategorical: false };
    }
  };

  const inferColumnType = (column: string) => {
    const values = datasetRows
      .map((row) => row[column])
      .filter((value) => value !== null && value !== undefined && String(value).trim() !== "");

    if (values.length === 0) {
      return "categorical";
    }

    return values.every((value) => {
      const normalized = String(value).trim();
      return normalized !== "" && !Number.isNaN(Number(normalized));
    })
      ? "numeric"
      : "categorical";
  };

  const isNumericColumn = (column: string) => inferColumnType(column) === "numeric";
  const isCategoricalColumn = (column: string) => inferColumnType(column) === "categorical";

  const getVisualizationColumnOptions = (type: string) => {
    switch (type) {
      case "histogram":
      case "boxplot":
        return datasetColumns.filter(isNumericColumn);
      case "scatter":
      case "line":
        return datasetColumns.filter(isNumericColumn);
      case "bar":
        return datasetColumns;
      case "pie":
        return datasetColumns.filter(isCategoricalColumn);
      default:
        return datasetColumns;
    }
  };

  useEffect(() => {
    if (!datasetLoaded) {
      return;
    }

    const requirements = getVisualizationRequirements(chartType);
    if (visualizationColumns.length > requirements.max) {
      setVisualizationColumns(visualizationColumns.slice(0, requirements.max));
      return;
    }

    if (visualizationColumns.length >= requirements.min) {
      return;
    }

    if (requirements.max === 1) {
      const defaultValue = getVisualizationColumnOptions(chartType)[0] ?? datasetColumns[0];
      setVisualizationColumns(defaultValue ? [defaultValue] : []);
      return;
    }

    const defaultValues = datasetColumns.slice(0, requirements.max);
    setVisualizationColumns(defaultValues);
  }, [chartType, datasetColumns, datasetLoaded]);

  const getVisualizationHint = () => {
    switch (chartType) {
      case "histogram":
        return "Select exactly one numeric column. Histograms display the numeric distribution.";
      case "boxplot":
        return "Select exactly one numeric column. Box plots show spread, median, and outliers.";
      case "scatter":
        return "Select exactly two numeric columns. Scatter plots require numeric x/y pairs.";
      case "line":
        return "Select exactly two numeric columns. Line plots show trends across numeric values.";
      case "bar":
        return "Select one categorical column and one numeric column. The numeric column will be aggregated by the categorical column.";
      case "pie":
        return "Select exactly one categorical column. Pie charts require categorical data.";
      default:
        return "Select the appropriate columns for the chosen visualization type.";
    }
  };

  const handleComputeStatistics = async () => {
    if (!datasetLoaded) {
      setError("Upload a dataset first.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const result = await fetchStatsSummary(datasetRows);
      setStatsResult(result);
      const initialOptions: Record<string, CategoryChartOptions> = {};
      (result.categoricalColumns || []).forEach((column) => {
        initialOptions[column] = getDefaultCategoryChartOptions(column);
      });
      setCategoryChartOptions(initialOptions);
      setSuccess("Statistics generated.");
    } catch (err: any) {
      setError(err.message || "Statistics generation failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateVisualization = async () => {
    if (!datasetLoaded) {
      setError("Upload a dataset first.");
      return;
    }

    const selectedColumns = visualizationColumns.filter(Boolean);
    const requirements = getVisualizationRequirements(chartType);
    if (selectedColumns.length < requirements.min || selectedColumns.length > requirements.max) {
      setError(`Select ${requirements.min} ${requirements.min === 1 ? "column" : "columns"} for ${chartType} visualization.`);
      return;
    }

    const columnTypes = selectedColumns.map((column) => inferColumnType(column));

    if (chartType === "histogram" || chartType === "boxplot") {
      if (columnTypes[0] !== "numeric") {
        setError(`The selected column must be numeric for ${chartType} plots.`);
        return;
      }
    }

    if (chartType === "scatter" || chartType === "line") {
      if (!columnTypes.every((type) => type === "numeric")) {
        setError(`Both selected columns must be numeric for ${chartType} plots.`);
        return;
      }
      if (selectedColumns[0] === selectedColumns[1]) {
        setError(`Select two different numeric columns for ${chartType} plots.`);
        return;
      }
    }

    if (chartType === "bar") {
      if (selectedColumns[0] === selectedColumns[1]) {
        setError("Select two different columns for bar plots.");
        return;
      }
      if (columnTypes.length === 2 && columnTypes[1] !== "numeric") {
        setError("The second selected column must be numeric for bar plots.");
        return;
      }
      if (columnTypes.length === 2 && columnTypes[0] !== "categorical") {
        setError("The first selected column must be categorical for bar plots.");
        return;
      }
    }

    if (chartType === "pie") {
      if (columnTypes[0] !== "categorical") {
        setError("Pie charts require a categorical column.");
        return;
      }
    }

    setError(null);
    setLoading(true);
    try {
      const result = await generateVisualization(datasetRows, chartType, selectedColumns);
      setVisualizationImage(result.imageBase64);
      setSuccess("Visualization generated.");
    } catch (err: any) {
      setError(err.message || "Visualization failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleRunAiAnalysis = async () => {
    if (!datasetLoaded) {
      setError("Upload a dataset first.");
      return;
    }
    if (!objective.trim()) {
      setError("Enter an objective for AI analysis.");
      return;
    }

    setError(null);
    setLoading(true);
    try {
      const result = await runAiInsights(datasetRows, objective);
      setAiResult({ insights: result.insights, tests: result.tests });
      setSuccess("AI analysis completed.");
    } catch (err: any) {
      setError(err.message || "AI analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleCrossTab = async () => {
    if (!datasetLoaded) {
      setError("Upload a dataset first.");
      return;
    }
    if (!crossRow || !crossCol) {
      setError("Select both row and column fields.");
      return;
    }

    setError(null);
    setLoading(true);
    try {
      const result = await runCrossTab(datasetRows, crossRow, crossCol, crossPrevalence);
      setCrossResult(result.result);
      setSuccess("Cross-tabulation completed.");
    } catch (err: any) {
      setError(err.message || "Cross-tabulation failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async (format: "pdf" | "docx") => {
    if (!datasetLoaded) {
      setError("Upload a dataset first.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const result = await generateReport(datasetRows, format, "statyx-report", aiResult?.insights ?? []);
      const blob = new Blob([Uint8Array.from(atob(result.contentBase64), (c) => c.charCodeAt(0))], { type: result.contentType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = result.fileName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setReportStatus(`${format.toUpperCase()} report downloaded.`);
    } catch (err: any) {
      setError(err.message || "Report generation failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFeedback = async () => {
    setError(null);
    setSuccess(null);
    try {
      const result = await submitFeedback("Feature request or feedback submitted.");
      setSuccess(result.message);
    } catch (err: any) {
      setError(err.message || "Feedback submission failed.");
    }
  };

  const moduleContent = useMemo(() => {
    switch (page) {
      case "upload":
        return (
          <div className="space-y-6">
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle>Upload dataset</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">Upload a CSV or Excel file to start the analysis workflow.</p>
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={(event) => handleFileUpload(event.target.files?.[0] ?? null)}
                  className="block w-full cursor-pointer rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground"
                />
                {fileInfo && (
                  <div className="grid gap-3 sm:grid-cols-3">
                    <div className="rounded-lg border border-border p-4 bg-card">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">Rows</p>
                      <p className="mt-2 text-2xl font-semibold">{fileInfo.rowCount}</p>
                    </div>
                    <div className="rounded-lg border border-border p-4 bg-card">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">Columns</p>
                      <p className="mt-2 text-2xl font-semibold">{fileInfo.columnCount}</p>
                    </div>
                    <div className="rounded-lg border border-border p-4 bg-card">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">Duplicate rows</p>
                      <p className="mt-2 text-2xl font-semibold">{fileInfo.info.duplicateCount}</p>
                    </div>
                  </div>
                )}
                {previewRows.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold">Preview</h3>
                    {renderTable(previewRows, datasetColumns)}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        );

      case "clean":
        return (
          <div className="space-y-6">
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle>Data Cleaning</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {!datasetLoaded ? (
                  <p className="text-sm text-muted-foreground">Upload a dataset first to access cleaning tools.</p>
                ) : (
                  <>
                    <Button onClick={handleDetectIssues} disabled={loading}>
                      <UploadCloud className="mr-2 h-4 w-4" /> Detect Issues
                    </Button>
                    {cleanIssues.length > 0 && (
                      <div className="space-y-4">
                        <div className="grid gap-3 sm:grid-cols-2">
                          {cleanIssues.map((issue, index) => {
                            const issueKey = `${issue.column}-${issue.issue}-${index}`;
                            const defaultValue = issue.issue === "Duplicate rows" ? "remove" : issue.dtype === "numeric" ? "mean" : "mode";
                            const selectedMethod = cleanActions[issueKey] || defaultValue;

                            return (
                              <div key={issueKey} className="rounded-xl border border-border p-4 bg-card">
                                <h4 className="font-medium">
                                  {issue.issue === "Duplicate rows" ? "Duplicate rows" : issue.column}
                                </h4>
                                <p className="text-sm text-muted-foreground">{issue.issue}</p>
                                {issue.issue === "Duplicate rows" ? (
                                  <div className="mt-3">
                                    <label className="flex items-center gap-2 text-sm font-medium">
                                      <input
                                        type="checkbox"
                                        checked={selectedMethod === "remove"}
                                        onChange={(event) =>
                                          setCleanActions((prev) => ({
                                            ...prev,
                                            [issueKey]: event.target.checked ? "remove" : "ignore",
                                          }))
                                        }
                                      />
                                      Remove duplicate rows
                                    </label>
                                  </div>
                                ) : (
                                  <div className="mt-3 space-y-2">
                                    <label className="block text-sm font-medium">Fix method</label>
                                    <select
                                      className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                                      value={selectedMethod}
                                      onChange={(event) => setCleanActions((prev) => ({ ...prev, [issueKey]: event.target.value }))}
                                    >
                                      {issue.dtype === "numeric" ? (
                                        <>
                                          <option value="mean">Fill with mean</option>
                                          <option value="zero">Fill with zero</option>
                                          <option value="custom">Custom value</option>
                                        </>
                                      ) : (
                                        <>
                                          <option value="mode">Fill with mode</option>
                                          <option value="custom">Fill with custom</option>
                                        </>
                                      )}
                                    </select>
                                    {selectedMethod === "custom" && (
                                      <Input
                                        placeholder="Custom fill value"
                                        value={cleanActions[`${issueKey}_custom`] || ""}
                                        onChange={(event) => setCleanActions((prev) => ({
                                          ...prev,
                                          [`${issueKey}_custom`]: event.target.value,
                                        }))}
                                      />
                                    )}
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                        <Button onClick={handleApplyCleaning} disabled={loading}>
                          <Wand2 className="mr-2 h-4 w-4" /> Apply Cleaning
                        </Button>
                      </div>
                    )}
                    {cleanPreview.length > 0 && (
                      <div className="space-y-3">
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                          <h3 className="text-lg font-semibold">Cleaned preview</h3>
                          {cleanDownload && (
                            <Button onClick={downloadCleanedDataset} variant="secondary" size="sm">
                              <DownloadCloud className="mr-2 h-4 w-4" /> Download Cleaned CSV
                            </Button>
                          )}
                        </div>
                        {renderTable(cleanPreview, datasetColumns)}
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        );

      case "statistics":
        return (
          <div className="space-y-6">
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle>Statistics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {!datasetLoaded ? (
                  <p className="text-sm text-muted-foreground">Upload your dataset and then generate statistics.</p>
                ) : (
                  <>
                    <Button onClick={handleComputeStatistics} disabled={loading}>
                      <BarChart3 className="mr-2 h-4 w-4" /> Generate Summary
                    </Button>
                    {statsResult && (
                      <div className="space-y-6">
                        <div className="rounded-xl border border-border bg-card p-4">
                          <h3 className="text-lg font-semibold">Overall Numerical Summary</h3>
                          {statsResult.descriptive.length > 0 ? (
                            <div className="mt-3 overflow-x-auto">
                              {renderTable(statsResult.descriptive, Object.keys(statsResult.descriptive[0] || {}))}
                            </div>
                          ) : (
                            <p className="text-sm text-muted-foreground">No numeric columns detected in the dataset.</p>
                          )}
                          {statsResult.numericInterpretations.length > 0 && (
                            <div className="mt-4 grid gap-3 sm:grid-cols-2">
                              {statsResult.numericInterpretations.map((item) => (
                                <div key={item.column} className="rounded-lg border border-border p-4 bg-background">
                                  <h4 className="font-semibold">{item.column}</h4>
                                  <p className="text-sm text-muted-foreground mt-1">{item.summary}</p>
                                  <div className="mt-3 grid gap-2 text-sm">
                                    <div>Mean: {item.mean}</div>
                                    <div>Std: {item.std}</div>
                                    <div>Median: {item.median}</div>
                                    <div>Range: {item.min} – {item.max}</div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>

                        <div className="rounded-xl border border-border bg-card p-4">
                          <h3 className="text-lg font-semibold">Overall Categorical Summary</h3>
                          {statsResult.categorical.length > 0 ? (
                            <div className="mt-3 overflow-x-auto">
                              {renderTable(statsResult.categorical, ["column", "count", "unique", "top", "freq", "top_percentage"])}
                            </div>
                          ) : (
                            <p className="text-sm text-muted-foreground">No categorical columns detected in the dataset.</p>
                          )}
                        </div>

                        {statsResult.categoricalColumns.map((column) => {
                          const details = statsResult.categoricalDetails[column] || [];
                          const options = categoryChartOptions[column] || getDefaultCategoryChartOptions(column);
                          const sortedData = [...details];

                          if (options.sort === "Descending") {
                            sortedData.sort((a, b) => b.count - a.count);
                          } else if (options.sort === "Ascending") {
                            sortedData.sort((a, b) => a.count - b.count);
                          }

                          const dominant = sortedData[0];
                          const ratioText = sortedData.length === 2
                            ? `The two categories differ by approximately ${(sortedData[0].count / Math.max(sortedData[1].count, 1)).toFixed(1)}:1.`
                            : "Other categories are less frequent, which suggests a concentration in the dominant group.";

                          const legendProps = options.legendPosition === "top" || options.legendPosition === "bottom"
                            ? { verticalAlign: options.legendPosition as "top" | "bottom", align: "center" as const }
                            : { verticalAlign: "middle" as const, align: options.legendPosition as "left" | "right" };

                          return (
                            <div key={column} className="rounded-xl border border-border bg-card p-4">
                              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                                <div>
                                  <h3 className="text-lg font-semibold">{column}</h3>
                                  <p className="text-sm text-muted-foreground">Category counts and distribution for this field.</p>
                                </div>
                                <div className="grid gap-2 sm:grid-cols-2">
                                  <div className="rounded-lg border border-border bg-background p-3 text-sm">
                                    <div className="font-semibold">Dominant</div>
                                    <div className="mt-1">{dominant?.category ?? "N/A"} — {dominant?.percentage ?? 0}%</div>
                                  </div>
                                  <div className="rounded-lg border border-border bg-background p-3 text-sm">
                                    <div className="font-semibold">Unique values</div>
                                    <div className="mt-1">{details.length}</div>
                                  </div>
                                </div>
                              </div>

                              <div className="mt-4 rounded-xl border border-border bg-background p-4">
                                <div className="grid gap-3 lg:grid-cols-4">
                                  <div>
                                    <label className="block text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">Chart Type</label>
                                    <select
                                      value={options.chartType}
                                      onChange={(event) => updateCategoryChartOption(column, "chartType", event.target.value as CategoryChartOptions["chartType"])}
                                      className="mt-2 w-full rounded-lg border border-border bg-background px-2 py-2 text-sm"
                                    >
                                      <option value="Column">Column</option>
                                      <option value="Bar">Bar</option>
                                    </select>
                                  </div>
                                  <div>
                                    <label className="block text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">Sort</label>
                                    <select
                                      value={options.sort}
                                      onChange={(event) => updateCategoryChartOption(column, "sort", event.target.value as CategoryChartOptions["sort"])}
                                      className="mt-2 w-full rounded-lg border border-border bg-background px-2 py-2 text-sm"
                                    >
                                      <option value="None">None</option>
                                      <option value="Descending">Descending</option>
                                      <option value="Ascending">Ascending</option>
                                    </select>
                                  </div>
                                  <div>
                                    <label className="block text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">Bar Color</label>
                                    <input
                                      type="color"
                                      value={options.color}
                                      onChange={(event) => updateCategoryChartOption(column, "color", event.target.value)}
                                      className="mt-2 h-9 w-full rounded-lg border border-border bg-background p-0"
                                    />
                                  </div>
                                  <div>
                                    <label className="block text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">Background</label>
                                    <input
                                      type="color"
                                      value={options.bg}
                                      onChange={(event) => updateCategoryChartOption(column, "bg", event.target.value)}
                                      className="mt-2 h-9 w-full rounded-lg border border-border bg-background p-0"
                                    />
                                  </div>
                                </div>

                                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                                  <div>
                                    <label className="block text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">Title</label>
                                    <input
                                      value={options.title}
                                      onChange={(event) => updateCategoryChartOption(column, "title", event.target.value)}
                                      className="mt-2 w-full rounded-lg border border-border bg-background px-2 py-2 text-sm"
                                    />
                                  </div>
                                  <div>
                                    <label className="block text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">Title size</label>
                                    <input
                                      type="range"
                                      min={10}
                                      max={40}
                                      value={options.titleSize}
                                      onChange={(event) => updateCategoryChartOption(column, "titleSize", Number(event.target.value))}
                                      className="mt-3 w-full"
                                    />
                                    <div className="text-sm text-muted-foreground">{options.titleSize}px</div>
                                  </div>
                                  <div>
                                    <label className="block text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">Axis size</label>
                                    <input
                                      type="range"
                                      min={8}
                                      max={25}
                                      value={options.axisSize}
                                      onChange={(event) => updateCategoryChartOption(column, "axisSize", Number(event.target.value))}
                                      className="mt-3 w-full"
                                    />
                                    <div className="text-sm text-muted-foreground">{options.axisSize}px</div>
                                  </div>
                                </div>

                                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                                  <div>
                                    <label className="block text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">Bar width</label>
                                    <input
                                      type="range"
                                      min={0.1}
                                      max={1.0}
                                      step={0.05}
                                      value={options.barWidth}
                                      onChange={(event) => updateCategoryChartOption(column, "barWidth", Number(event.target.value))}
                                      className="mt-3 w-full"
                                    />
                                    <div className="text-sm text-muted-foreground">{options.barWidth.toFixed(2)}</div>
                                  </div>
                                  <div>
                                    <label className="block text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">Height</label>
                                    <input
                                      type="range"
                                      min={300}
                                      max={800}
                                      value={options.height}
                                      onChange={(event) => updateCategoryChartOption(column, "height", Number(event.target.value))}
                                      className="mt-3 w-full"
                                    />
                                    <div className="text-sm text-muted-foreground">{options.height}px</div>
                                  </div>
                                  <div>
                                    <label className="block text-xs font-medium uppercase tracking-[0.24em] text-muted-foreground">Legend</label>
                                    <select
                                      value={options.legendPosition}
                                      onChange={(event) => updateCategoryChartOption(column, "legendPosition", event.target.value as CategoryChartOptions["legendPosition"])}
                                      className="mt-2 w-full rounded-lg border border-border bg-background px-2 py-2 text-sm"
                                    >
                                      <option value="top">Top</option>
                                      <option value="bottom">Bottom</option>
                                      <option value="left">Left</option>
                                      <option value="right">Right</option>
                                    </select>
                                  </div>
                                </div>

                                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                                  <label className="inline-flex items-center gap-2 text-sm">
                                    <input
                                      type="checkbox"
                                      checked={options.showLabels}
                                      onChange={(event) => updateCategoryChartOption(column, "showLabels", event.target.checked)}
                                      className="h-4 w-4 rounded border border-border text-primary"
                                    />
                                    Show labels
                                  </label>
                                  <label className="inline-flex items-center gap-2 text-sm">
                                    <input
                                      type="checkbox"
                                      checked={options.showLegend}
                                      onChange={(event) => updateCategoryChartOption(column, "showLegend", event.target.checked)}
                                      className="h-4 w-4 rounded border border-border text-primary"
                                    />
                                    Show legend
                                  </label>
                                  <label className="inline-flex items-center gap-2 text-sm">
                                    <input
                                      type="checkbox"
                                      checked={options.grid}
                                      onChange={(event) => updateCategoryChartOption(column, "grid", event.target.checked)}
                                      className="h-4 w-4 rounded border border-border text-primary"
                                    />
                                    Show grid
                                  </label>
                                </div>
                              </div>

                              <div className="mt-6 rounded-xl border border-border bg-white p-4" style={{ backgroundColor: options.bg }}>
                                <ResponsiveContainer width="100%" height={options.height}>
                                  <BarChart
                                    data={sortedData}
                                    layout={options.chartType === "Bar" ? "vertical" : "horizontal"}
                                    margin={{ top: 20, right: 20, left: 20, bottom: 20 }}
                                  >
                                    {options.grid && <CartesianGrid strokeDasharray="3 3" />}
                                    {options.chartType === "Bar" ? (
                                      <>
                                        <XAxis type="number" tick={{ fontSize: options.axisSize }} />
                                        <YAxis dataKey="category" type="category" tick={{ fontSize: options.axisSize }} width={140} />
                                      </>
                                    ) : (
                                      <>
                                        <XAxis dataKey="category" type="category" tick={{ fontSize: options.axisSize }} interval={0} angle={-20} textAnchor="end" height={70} />
                                        <YAxis type="number" tick={{ fontSize: options.axisSize }} />
                                      </>
                                    )}
                                    <Tooltip cursor={{ fill: "rgba(0,0,0,0.04)" }} />
                                    {options.showLegend && <Legend {...legendProps} />}
                                    <Bar dataKey="count" fill={options.color} barSize={Math.max(10, Math.round(options.barWidth * 40))} name="Count">
                                      {options.showLabels && <LabelList dataKey="count" position={options.chartType === "Bar" ? "right" : "top"} />}
                                    </Bar>
                                  </BarChart>
                                </ResponsiveContainer>
                              </div>

                              <div className="mt-4 rounded-lg border border-border bg-background p-4">
                                <p className="text-sm text-muted-foreground">
                                  In the present dataset, <strong>{dominant?.category ?? "N/A"}</strong> was the most frequently observed category for <strong>{column}</strong>, accounting for <strong>{dominant?.percentage ?? 0}%</strong> of cases. {ratioText}
                                </p>
                              </div>

                              <div className="mt-4 overflow-x-auto">
                                {renderTable(details, ["category", "count", "percentage"])}
                              </div>
                            </div>
                          );
                        })}

                        <div className="rounded-xl border border-border bg-card p-4">
                          <h3 className="text-lg font-semibold">Download Full Statistics Report</h3>
                          <div className="mt-4 grid gap-3 sm:grid-cols-2">
                            <Button onClick={() => handleGenerateReport("docx")} disabled={loading}>
                              <FileText className="mr-2 h-4 w-4" /> Download Word (.docx)
                            </Button>
                            <Button onClick={() => handleGenerateReport("pdf")} disabled={loading}>
                              <DownloadCloud className="mr-2 h-4 w-4" /> Download PDF (.pdf)
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        );

      case "visualizations":
        return (
          <div className="space-y-6">
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle>Visualizations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {!datasetLoaded ? (
                  <p className="text-sm text-muted-foreground">Upload your dataset before generating charts.</p>
                ) : (
                  <>
                    <div className="rounded-xl border border-border bg-background p-4 text-sm text-muted-foreground">
                      {getVisualizationHint()}
                    </div>
                    <div className="grid gap-4 sm:grid-cols-3">
                      <div>
                        <label className="block text-sm font-medium mb-2">Chart type</label>
                        <select
                          value={chartType}
                          onChange={(event) => setChartType(event.target.value)}
                          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                        >
                          {CHART_TYPES.map((type) => (
                            <option key={type.value} value={type.value}>{type.label}</option>
                          ))}
                        </select>
                      </div>
                      <div className="sm:col-span-2">
                        {chartType === "bar" ? (
                          <div className="grid gap-4 sm:grid-cols-2">
                            <div>
                              <label className="block text-sm font-medium mb-2">Category column</label>
                              <select
                                value={visualizationColumns[0] ?? ""}
                                onChange={(event) => setVisualizationColumns([event.target.value, visualizationColumns[1] ?? ""])}
                                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                              >
                                {datasetColumns.filter(isCategoricalColumn).map((column) => (
                                  <option key={column} value={column}>{column}</option>
                                ))}
                              </select>
                            </div>
                            <div>
                              <label className="block text-sm font-medium mb-2">Numeric column</label>
                              <select
                                value={visualizationColumns[1] ?? ""}
                                onChange={(event) => setVisualizationColumns([visualizationColumns[0] ?? "", event.target.value])}
                                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                              >
                                {datasetColumns.filter(isNumericColumn).map((column) => (
                                  <option key={column} value={column}>{column}</option>
                                ))}
                              </select>
                            </div>
                          </div>
                        ) : chartType === "scatter" || chartType === "line" ? (
                          <div className="grid gap-4 sm:grid-cols-2">
                            <div>
                              <label className="block text-sm font-medium mb-2">X column</label>
                              <select
                                value={visualizationColumns[0] ?? ""}
                                onChange={(event) => setVisualizationColumns([event.target.value, visualizationColumns[1] ?? ""])}
                                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                              >
                                {datasetColumns.filter(isNumericColumn).map((column) => (
                                  <option key={column} value={column}>{column}</option>
                                ))}
                              </select>
                            </div>
                            <div>
                              <label className="block text-sm font-medium mb-2">Y column</label>
                              <select
                                value={visualizationColumns[1] ?? ""}
                                onChange={(event) => setVisualizationColumns([visualizationColumns[0] ?? "", event.target.value])}
                                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                              >
                                {datasetColumns.filter(isNumericColumn).map((column) => (
                                  <option key={column} value={column}>{column}</option>
                                ))}
                              </select>
                            </div>
                          </div>
                        ) : (
                          <>
                            <label className="block text-sm font-medium mb-2">Columns</label>
                            <select
                              value={visualizationColumns[0] ?? ""}
                              onChange={(event) => setVisualizationColumns([event.target.value])}
                              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                            >
                              {getVisualizationColumnOptions(chartType).map((column) => (
                                <option key={column} value={column}>{column}</option>
                              ))}
                            </select>
                          </>
                        )}
                        <p className="mt-2 text-sm text-muted-foreground">
                          Required columns: {getVisualizationRequirements(chartType).min}
                          {getVisualizationRequirements(chartType).max !== getVisualizationRequirements(chartType).min ? ` to ${getVisualizationRequirements(chartType).max}` : ""}.
                        </p>
                        {visualizationColumns.length > 0 && (
                          <p className="mt-1 text-sm text-muted-foreground">
                            Selected: {visualizationColumns.filter(Boolean).join(", ")} — {visualizationColumns.filter(Boolean).map((column) => `${column} (${inferColumnType(column)})`).join("; ")}
                          </p>
                        )}
                      </div>
                    </div>
                    <Button onClick={handleGenerateVisualization} disabled={loading}>
                      <LineChart className="mr-2 h-4 w-4" /> Generate Chart
                    </Button>
                    {visualizationImage && (
                      <div className="rounded-xl border border-border overflow-hidden bg-card">
                        <img src={`data:image/png;base64,${visualizationImage}`} alt="Visualization" className="w-full" />
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        );

      case "ai-analysis":
        return (
          <div className="space-y-6">
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle>AI Objective Analysis</CardTitle>
                <p className="text-sm text-muted-foreground mt-2">Auto-generated analysis with academic-style interpretation</p>
              </CardHeader>
              <CardContent className="space-y-4">
                {!datasetLoaded ? (
                  <p className="text-sm text-muted-foreground">Upload a dataset and provide an objective to run the AI engine.</p>
                ) : (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-2">Enter objective</label>
                      <input
                        type="text"
                        value={objective}
                        onChange={(event) => setObjective(event.target.value)}
                        placeholder="e.g., 'Is outcome associated with gender?'"
                        className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                      />
                      <p className="mt-2 text-xs text-muted-foreground">Describe your analysis objective in natural language for AI-powered test recommendations.</p>
                    </div>
                    <Button onClick={handleRunAiAnalysis} disabled={loading}>
                      <BrainCircuit className="mr-2 h-4 w-4" /> Run Suggested Tests
                    </Button>

                    {aiResult && (
                      <div className="space-y-6 mt-6 border-t border-border pt-6">
                        {aiResult.insights && aiResult.insights.length > 0 && (
                          <div className="rounded-xl border border-border bg-card p-4">
                            <h3 className="text-lg font-semibold mb-4">📊 AI Insights</h3>
                            <ul className="space-y-3">
                              {aiResult.insights.map((insight, idx) => (
                                <li key={idx} className="rounded-lg bg-background p-3">
                                  <p className="text-sm">{typeof insight === "string" ? insight : insight.description || JSON.stringify(insight)}</p>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {aiResult.tests && aiResult.tests.length > 0 && (
                          <div className="space-y-4">
                            <h3 className="text-lg font-semibold">📈 Suggested Tests</h3>
                            {aiResult.tests.map((test, idx) => {
                              const pVal = test.result?.p_value;
                              const isSignificant = pVal !== null && pVal !== undefined && pVal < 0.05;

                              return (
                                <div key={idx} className="rounded-xl border border-border bg-card p-4">
                                  <div className="flex items-center justify-between mb-3">
                                    <h4 className="font-semibold text-base">{test.test}</h4>
                                    <span className="inline-block rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                                      Confidence: {(test.confidence * 100).toFixed(1)}%
                                    </span>
                                  </div>

                                  <div className="overflow-x-auto mb-4">
                                    <table className="min-w-full text-sm border border-border rounded-lg">
                                      <thead className="bg-muted text-muted-foreground">
                                        <tr>
                                          <th className="px-3 py-2 text-left font-medium">Metric</th>
                                          <th className="px-3 py-2 text-left font-medium">Value</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {Object.entries(test.result || {}).map(([key, value]) => {
                                          if (key === "interpretation") return null;
                                          return (
                                            <tr key={key} className="border-t border-border">
                                              <td className="px-3 py-2 font-medium text-foreground">
                                                {key.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase())}
                                              </td>
                                              <td className="px-3 py-2 text-foreground">
                                                {typeof value === "number" ? value.toString() : String(value)}
                                              </td>
                                            </tr>
                                          );
                                        })}
                                      </tbody>
                                    </table>
                                  </div>

                                  {pVal !== null && pVal !== undefined && (
                                    <div
                                      className={`mb-4 rounded-lg p-3 ${
                                        isSignificant
                                          ? "bg-green-500/10 border border-green-500/20"
                                          : "bg-amber-500/10 border border-amber-500/20"
                                      }`}
                                    >
                                      <p
                                        className={`text-sm font-medium ${
                                          isSignificant ? "text-green-700" : "text-amber-700"
                                        }`}
                                      >
                                        {isSignificant
                                          ? `✓ Statistically significant relationship (p = ${pVal.toFixed(4)})`
                                          : `✗ No statistically significant relationship (p = ${pVal.toFixed(4)})`}
                                      </p>
                                    </div>
                                  )}

                                  {test.result?.interpretation && (
                                    <div className="rounded-lg bg-background p-3 border border-border">
                                      <p className="text-xs font-medium text-muted-foreground mb-1">Interpretation</p>
                                      <p className="text-sm text-foreground">
                                        {test.result.interpretation}
                                      </p>
                                      <p className="text-xs text-muted-foreground mt-2">
                                        These findings should be interpreted in the context of sample size, data quality, and domain knowledge.
                                      </p>
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        )}

                        {!aiResult.tests || aiResult.tests.length === 0 ? (
                          <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-4">
                            <p className="text-sm text-amber-700">
                              Only limited suitable tests could be applied to this dataset. Try refining your objective or ensure the dataset has sufficient numeric and categorical columns.
                            </p>
                          </div>
                        ) : null}
                      </div>
                    )}

                    {/* Cross Tabulation Section */}
                    <div className="border-t border-border pt-6 mt-6">
                      <h3 className="text-lg font-semibold mb-4">🔍 Cross Tabulation Analysis</h3>
                      <p className="text-sm text-muted-foreground mb-4">Research-grade statistical decision engine for variable relationships</p>

                      <div className="grid gap-4 sm:grid-cols-2 mb-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">Row Variable</label>
                          <select
                            value={crossRow}
                            onChange={(event) => setCrossRow(event.target.value)}
                            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                          >
                            <option value="">Select row field</option>
                            {datasetColumns.map((column) => (
                              <option key={column} value={column}>{column}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Column Variable</label>
                          <select
                            value={crossCol}
                            onChange={(event) => setCrossCol(event.target.value)}
                            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                          >
                            <option value="">Select column field</option>
                            {datasetColumns.map((column) => (
                              <option key={column} value={column}>{column}</option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 mb-4">
                        <input
                          type="checkbox"
                          id="prevalence"
                          checked={crossPrevalence}
                          onChange={(event) => setCrossPrevalence(event.target.checked)}
                          className="rounded border-border"
                        />
                        <label htmlFor="prevalence" className="text-sm font-medium">Show Prevalence</label>
                      </div>

                      <Button onClick={handleCrossTab} disabled={loading || !crossRow || !crossCol}>
                        Generate Analysis
                      </Button>

                      {crossResult && (
                        <div className="space-y-6 mt-6">
                          {crossResult.description && (
                            <div className="rounded-lg bg-blue-500/10 border border-blue-500/20 p-4">
                              <p className="text-sm text-blue-700">{crossResult.description}</p>
                            </div>
                          )}

                          {/* Categorical Case */}
                          {crossResult.type === "categorical" && (
                            <>
                              {crossResult.counts && (
                                <div className="rounded-xl border border-border bg-card p-4">
                                  <h4 className="font-semibold mb-4">Counts</h4>
                                  <div className="overflow-x-auto">
                                    <table className="min-w-full text-sm border border-border rounded-lg">
                                      <thead className="bg-muted text-muted-foreground">
                                        <tr>
                                          {Object.keys(crossResult.counts[0] || {}).map((key) => (
                                            <th key={key} className="px-3 py-2 text-left font-medium">{key}</th>
                                          ))}
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {crossResult.counts.map((row: any, idx: number) => (
                                          <tr key={idx} className="border-t border-border">
                                            {Object.values(row).map((value: any, jdx: number) => (
                                              <td key={jdx} className="px-3 py-2 text-foreground">{String(value)}</td>
                                            ))}
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                </div>
                              )}

                              {crossResult.row_percent && (
                                <div className="rounded-xl border border-border bg-card p-4">
                                  <h4 className="font-semibold mb-4">Row Percentage (%)</h4>
                                  <div className="overflow-x-auto">
                                    <table className="min-w-full text-sm border border-border rounded-lg">
                                      <thead className="bg-muted text-muted-foreground">
                                        <tr>
                                          {Object.keys(crossResult.row_percent[0] || {}).map((key) => (
                                            <th key={key} className="px-3 py-2 text-left font-medium">{key}</th>
                                          ))}
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {crossResult.row_percent.map((row: any, idx: number) => (
                                          <tr key={idx} className="border-t border-border">
                                            {Object.values(row).map((value: any, jdx: number) => (
                                              <td key={jdx} className="px-3 py-2 text-foreground">
                                                {typeof value === "number" ? value.toFixed(2) : String(value)}
                                              </td>
                                            ))}
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                </div>
                              )}

                              {crossResult.col_percent && (
                                <div className="rounded-xl border border-border bg-card p-4">
                                  <h4 className="font-semibold mb-4">Column Percentage (%)</h4>
                                  <div className="overflow-x-auto">
                                    <table className="min-w-full text-sm border border-border rounded-lg">
                                      <thead className="bg-muted text-muted-foreground">
                                        <tr>
                                          {Object.keys(crossResult.col_percent[0] || {}).map((key) => (
                                            <th key={key} className="px-3 py-2 text-left font-medium">{key}</th>
                                          ))}
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {crossResult.col_percent.map((row: any, idx: number) => (
                                          <tr key={idx} className="border-t border-border">
                                            {Object.values(row).map((value: any, jdx: number) => (
                                              <td key={jdx} className="px-3 py-2 text-foreground">
                                                {typeof value === "number" ? value.toFixed(2) : String(value)}
                                              </td>
                                            ))}
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                </div>
                              )}

                              {crossResult.chi_square && (
                                <div className="rounded-xl border border-border bg-card p-4">
                                  <h4 className="font-semibold mb-4">Chi-Square Test</h4>
                                  <div className="space-y-2">
                                    <p className="text-sm">Chi-square = {crossResult.chi_square.chi2?.toFixed(3)}</p>
                                    <p className="text-sm">p-value = {crossResult.chi_square.p_value?.toFixed(4)}</p>
                                    <p className="text-sm">Degrees of freedom = {crossResult.chi_square.dof}</p>
                                    <div className={`mt-2 rounded-lg p-3 ${
                                      crossResult.chi_square.significant
                                        ? "bg-green-500/10 border border-green-500/20"
                                        : "bg-amber-500/10 border border-amber-500/20"
                                    }`}>
                                      <p className={`text-sm font-medium ${
                                        crossResult.chi_square.significant ? "text-green-700" : "text-amber-700"
                                      }`}>
                                        {crossResult.chi_square.significant
                                          ? "✓ Statistically significant association detected."
                                          : "✗ No statistically significant association detected."}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {crossResult.prevalence && (
                                <div className="rounded-xl border border-border bg-card p-4">
                                  <h4 className="font-semibold mb-4">Prevalence</h4>
                                  <div className="overflow-x-auto">
                                    <table className="min-w-full text-sm border border-border rounded-lg">
                                      <thead className="bg-muted text-muted-foreground">
                                        <tr>
                                          <th className="px-3 py-2 text-left font-medium">Group</th>
                                          <th className="px-3 py-2 text-left font-medium">Prevalence (%)</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {crossResult.prevalence.map((row: any, idx: number) => (
                                          <tr key={idx} className="border-t border-border">
                                            <td className="px-3 py-2 font-medium text-foreground">{row[Object.keys(row)[0]]}</td>
                                            <td className="px-3 py-2 text-foreground">{row[Object.keys(row)[1]]?.toFixed(2)}</td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                </div>
                              )}
                            </>
                          )}

                          {/* Mixed Case */}
                          {crossResult.type === "mixed" && (
                            <>
                              <div className="rounded-xl border border-border bg-card p-4">
                                <h4 className="font-semibold mb-4">Group Summary</h4>
                                <div className="overflow-x-auto">
                                  <table className="min-w-full text-sm border border-border rounded-lg">
                                    <thead className="bg-muted text-muted-foreground">
                                      <tr>
                                        <th className="px-3 py-2 text-left font-medium">Group</th>
                                        <th className="px-3 py-2 text-left font-medium">Count</th>
                                        <th className="px-3 py-2 text-left font-medium">Mean ± SD</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {Object.entries(crossResult.group_summary || {}).map(([group, data]: [string, any]) => (
                                        <tr key={group} className="border-t border-border">
                                          <td className="px-3 py-2 font-medium text-foreground">{group}</td>
                                          <td className="px-3 py-2 text-foreground">{data.count}</td>
                                          <td className="px-3 py-2 text-foreground">{data["Mean ± SD"]}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              </div>

                              {crossResult.test && (
                                <div className="rounded-xl border border-border bg-card p-4">
                                  <h4 className="font-semibold mb-4">{crossResult.test.type === "t-test" ? "Independent T-test" : "ANOVA"}</h4>
                                  <div className="space-y-2">
                                    <p className="text-sm">
                                      {crossResult.test.type === "t-test" ? "T-statistic" : "F-statistic"} = {crossResult.test.t_statistic || crossResult.test.f_statistic}
                                    </p>
                                    <p className="text-sm">p-value = {crossResult.test.p_value?.toFixed(4)}</p>
                                    <div className={`mt-2 rounded-lg p-3 ${
                                      crossResult.test.significant
                                        ? "bg-green-500/10 border border-green-500/20"
                                        : "bg-amber-500/10 border border-amber-500/20"
                                    }`}>
                                      <p className={`text-sm font-medium ${
                                        crossResult.test.significant ? "text-green-700" : "text-amber-700"
                                      }`}>
                                        {crossResult.test.significant
                                          ? "✓ Statistically significant difference detected."
                                          : "✗ No statistically significant difference detected."}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {crossResult.logistic_regression && (
                                <div className="rounded-xl border border-border bg-card p-4">
                                  <h4 className="font-semibold mb-4">Logistic Regression</h4>
                                  <p className="text-sm">
                                    Odds Ratio per unit increase in {crossResult.logistic_regression.variable}: {crossResult.logistic_regression.odds_ratio?.toFixed(3)}
                                  </p>
                                </div>
                              )}

                              {crossResult.group_distribution && (
                                <div className="rounded-xl border border-border bg-card p-4">
                                  <h4 className="font-semibold mb-4">Group Distribution</h4>
                                  <div className="overflow-x-auto">
                                    <table className="min-w-full text-sm border border-border rounded-lg">
                                      <thead className="bg-muted text-muted-foreground">
                                        <tr>
                                          <th className="px-3 py-2 text-left font-medium">Group</th>
                                          <th className="px-3 py-2 text-left font-medium">N</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {crossResult.group_distribution.map((row: any, idx: number) => (
                                          <tr key={idx} className="border-t border-border">
                                            <td className="px-3 py-2 font-medium text-foreground">{row[Object.keys(row)[0]]}</td>
                                            <td className="px-3 py-2 text-foreground">{row.N}</td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                </div>
                              )}
                            </>
                          )}

                          {/* Numeric Case */}
                          {crossResult.type === "numeric" && (
                            <div className="rounded-xl border border-border bg-card p-4">
                              <h4 className="font-semibold mb-4">Pearson Correlation</h4>
                              <div className="space-y-2">
                                <p className="text-sm">Correlation coefficient (r) = {crossResult.correlation.r?.toFixed(3)}</p>
                                <p className="text-sm">p-value = {crossResult.correlation.p_value?.toFixed(4)}</p>
                                <div className={`mt-2 rounded-lg p-3 ${
                                  crossResult.correlation.significant
                                    ? "bg-green-500/10 border border-green-500/20"
                                    : "bg-amber-500/10 border border-amber-500/20"
                                }`}>
                                  <p className={`text-sm font-medium ${
                                    crossResult.correlation.significant ? "text-green-700" : "text-amber-700"
                                  }`}>
                                    {crossResult.correlation.significant
                                      ? "✓ Statistically significant correlation detected."
                                      : "✗ No statistically significant correlation detected."}
                                  </p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        );

      case "cross-tabulation":
        return (
          <div className="space-y-6">
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle>Cross Tabulation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {!datasetLoaded ? (
                  <p className="text-sm text-muted-foreground">Upload a dataset and choose categorical columns.</p>
                ) : (
                  <>
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div>
                        <label className="block text-sm font-medium mb-2">Row variable</label>
                        <select
                          value={crossRow}
                          onChange={(event) => setCrossRow(event.target.value)}
                          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                        >
                          <option value="">Select row field</option>
                          {datasetColumns.map((column) => (
                            <option key={column} value={column}>{column}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Column variable</label>
                        <select
                          value={crossCol}
                          onChange={(event) => setCrossCol(event.target.value)}
                          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                        >
                          <option value="">Select column field</option>
                          {datasetColumns.map((column) => (
                            <option key={column} value={column}>{column}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    <Button onClick={handleCrossTab} disabled={loading}>
                      <Network className="mr-2 h-4 w-4" /> Run Cross Tab
                    </Button>
                    {crossResult && (
                      <div className="rounded-xl border border-border bg-card p-4">
                        <h3 className="text-lg font-semibold">Result</h3>
                        <pre className="mt-3 overflow-x-auto text-sm text-muted-foreground">{JSON.stringify(crossResult, null, 2)}</pre>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        );

      case "reports":
        return (
          <div className="space-y-6">
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle>Reports</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {!datasetLoaded ? (
                  <p className="text-sm text-muted-foreground">Upload data and run analysis before exporting reports.</p>
                ) : (
                  <>
                    <div className="grid gap-4 sm:grid-cols-2">
                      <Button onClick={() => handleGenerateReport("pdf")} disabled={loading}>
                        <DownloadCloud className="mr-2 h-4 w-4" /> Download PDF
                      </Button>
                      <Button onClick={() => handleGenerateReport("docx")} disabled={loading}>
                        <FileText className="mr-2 h-4 w-4" /> Download Word
                      </Button>
                    </div>
                    {reportStatus && <div className="text-sm text-muted-foreground">{reportStatus}</div>}
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        );

      default:
        return <div>Unknown section.</div>;
    }
  }, [page, datasetLoaded, datasetColumns, previewRows, cleanIssues, cleanPreview, statsResult, visualizationImage, objective, aiResult, crossRow, crossCol, crossPrevalence, crossResult, reportStatus, loading, cleanActions]);

  return (
    <div className="flex-1 px-6 py-8 md:px-8 md:py-10 space-y-6 bg-background">
      <div className="max-w-6xl mx-auto space-y-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary">Analytics</p>
            <h1 className="text-3xl font-bold tracking-tight">{moduleTitle}</h1>
            <p className="mt-2 text-sm text-muted-foreground max-w-2xl">{moduleDescription}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.keys(TABS).map((tab) => (
              <Button
                key={tab}
                variant={tab === page ? "secondary" : "ghost"}
                onClick={() => setLocation(`/dashboard/analytics?page=${tab}`)}
                size="sm"
              >
                {TABS[tab].title}
              </Button>
            ))}
          </div>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert variant="default">
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {loading ? (
          <div className="flex items-center justify-center rounded-2xl border border-border bg-card p-10">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          moduleContent
        )}
      </div>
    </div>
  );
}

export type DatasetRow = Record<string, unknown>;

const jsonHeaders = {
  "Accept": "application/json",
  "Content-Type": "application/json",
};

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(path, {
    credentials: "include",
    ...init,
    headers: {
      ...jsonHeaders,
      ...(init.headers ?? {}),
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail || errorBody?.error || response.statusText);
  }

  return response.json();
}

export async function uploadDataset(file: File) {
  const body = new FormData();
  body.append("file", file);

  const response = await fetch("/api/python/upload", {
    method: "POST",
    body,
    credentials: "include",
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail || errorBody?.error || response.statusText);
  }

  return response.json() as Promise<{ preview: DatasetRow[]; rows: DatasetRow[]; columns: string[]; rowCount: number; columnCount: number; info: any }>;
}

export async function detectCleaningIssues(rows: DatasetRow[]) {
  return request<{ issues: any[]; preview: DatasetRow[]; columns: string[] }>(
    "/api/python/clean/detect",
    {
      method: "POST",
      body: JSON.stringify({ rows }),
    },
  );
}

export async function applyCleaning(rows: DatasetRow[], actions: any[]) {
  return request<{ preview: DatasetRow[]; cleanedCsv: string; columns: string[] }>(
    "/api/python/clean/apply",
    {
      method: "POST",
      body: JSON.stringify({ rows, actions }),
    },
  );
}

export async function fetchStatsSummary(rows: DatasetRow[]) {
  return request<{
    descriptive: any[];
    categorical: any[];
    categoricalDetails: Record<string, any[]>;
    numericInterpretations: any[];
    numericColumns: string[];
    categoricalColumns: string[];
    preview: DatasetRow[];
    columns: string[];
  }>(
    "/api/python/stats/summary",
    {
      method: "POST",
      body: JSON.stringify({ rows }),
    },
  );
}

export async function generateVisualization(rows: DatasetRow[], chartType: string, columns: string[]) {
  return request<{ imageBase64: string }>(
    "/api/python/visualization",
    {
      method: "POST",
      body: JSON.stringify({ rows, chartType, columns }),
    },
  );
}

export async function runAiInsights(rows: DatasetRow[], objective: string) {
  return request<{ insights: any[]; tests: any[]; columns: string[] }>(
    "/api/python/ai/insights",
    {
      method: "POST",
      body: JSON.stringify({ rows, objective }),
    },
  );
}

export async function runCrossTab(rows: DatasetRow[], row: string, col: string, prevalence?: boolean) {
  return request<{ result: any }>(
    "/api/python/cross-tab",
    {
      method: "POST",
      body: JSON.stringify({ rows, row, col, prevalence }),
    },
  );
}

export async function generateReport(rows: DatasetRow[], format: "pdf" | "docx", fileName: string, insights: any[] = []) {
  return request<{ fileName: string; contentBase64: string; contentType: string }>(
    "/api/python/report",
    {
      method: "POST",
      body: JSON.stringify({ rows, format, fileName, insights }),
    },
  );
}

export async function submitFeedback(feedback: string) {
  return request<{ success: boolean; message: string }>(
    "/api/python/feedback",
    {
      method: "POST",
      body: JSON.stringify({ feedback }),
    },
  );
}

import { Router, type IRouter } from "express";
import { db, datasetsTable, usersTable } from "@workspace/db";
import { eq, and, sum, count } from "drizzle-orm";
import { GetDatasetParams, DeleteDatasetParams } from "@workspace/api-zod";

const router: IRouter = Router();

function requireAuth(req: any, res: any, next: any): void {
  if (!req.session.userId) {
    res.status(401).json({ error: "Not authenticated" });
    return;
  }
  next();
}

router.get("/datasets", requireAuth, async (req, res): Promise<void> => {
  const datasets = await db
    .select()
    .from(datasetsTable)
    .where(eq(datasetsTable.userId, req.session.userId!))
    .orderBy(datasetsTable.uploadedAt);

  res.json(
    datasets.map((d) => ({
      id: d.id,
      name: d.name,
      fileName: d.fileName,
      fileSize: d.fileSize,
      rowCount: d.rowCount,
      columnCount: d.columnCount,
      status: d.status,
      uploadedAt: d.uploadedAt.toISOString(),
    })),
  );
});

router.get("/datasets/summary", requireAuth, async (req, res): Promise<void> => {
  const userId = req.session.userId!;

  const datasets = await db
    .select()
    .from(datasetsTable)
    .where(eq(datasetsTable.userId, userId));

  const totalDatasets = datasets.length;
  const totalRows = datasets.reduce((sum, d) => sum + (d.rowCount ?? 0), 0);
  const readyDatasets = datasets.filter((d) => d.status === "ready").length;

  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  const recentUploads = datasets.filter((d) => d.uploadedAt > oneWeekAgo).length;

  res.json({ totalDatasets, totalRows, recentUploads, readyDatasets });
});

router.get("/datasets/:id", requireAuth, async (req, res): Promise<void> => {
  const params = GetDatasetParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [dataset] = await db
    .select()
    .from(datasetsTable)
    .where(and(eq(datasetsTable.id, params.data.id), eq(datasetsTable.userId, req.session.userId!)));

  if (!dataset) {
    res.status(404).json({ error: "Dataset not found" });
    return;
  }

  res.json({
    id: dataset.id,
    name: dataset.name,
    fileName: dataset.fileName,
    fileSize: dataset.fileSize,
    rowCount: dataset.rowCount,
    columnCount: dataset.columnCount,
    status: dataset.status,
    uploadedAt: dataset.uploadedAt.toISOString(),
  });
});

router.delete("/datasets/:id", requireAuth, async (req, res): Promise<void> => {
  const params = DeleteDatasetParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [dataset] = await db
    .delete(datasetsTable)
    .where(and(eq(datasetsTable.id, params.data.id), eq(datasetsTable.userId, req.session.userId!)))
    .returning();

  if (!dataset) {
    res.status(404).json({ error: "Dataset not found" });
    return;
  }

  res.sendStatus(204);
});

export default router;

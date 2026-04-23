import { useAuth } from "@/hooks/use-auth";
import { useGetDatasetsSummary, useListDatasets } from "@workspace/api-client-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "wouter";
import { formatDistanceToNow } from "date-fns";
import { FileSpreadsheet, Database, Upload, CheckCircle2, AlertCircle, Clock } from "lucide-react";
import { motion } from "framer-motion";
import { Skeleton } from "@/components/ui/skeleton";

export default function Dashboard() {
  const { user } = useAuth();
  const { data: summary, isLoading: loadingSummary } = useGetDatasetsSummary();
  const { data: datasets, isLoading: loadingDatasets } = useListDatasets();

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto w-full space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Welcome back, {user?.name?.split(' ')[0] || 'Researcher'}</h1>
        <p className="text-muted-foreground mt-2">Here's what's happening with your data today.</p>
      </div>

      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        <motion.div variants={itemVariants}>
          <Card className="border-border/50 shadow-sm hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Datasets</CardTitle>
              <Database className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              {loadingSummary ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="text-2xl font-bold">{summary?.totalDatasets || 0}</div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="border-border/50 shadow-sm hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Rows Analyzed</CardTitle>
              <FileSpreadsheet className="h-4 w-4 text-chart-2" />
            </CardHeader>
            <CardContent>
              {loadingSummary ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="text-2xl font-bold">{(summary?.totalRows || 0).toLocaleString()}</div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="border-border/50 shadow-sm hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">Ready for Analysis</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-chart-3" />
            </CardHeader>
            <CardContent>
              {loadingSummary ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="text-2xl font-bold">{summary?.readyDatasets || 0}</div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="border-border/50 shadow-sm hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">Recent Uploads</CardTitle>
              <Clock className="h-4 w-4 text-chart-4" />
            </CardHeader>
            <CardContent>
              {loadingSummary ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="text-2xl font-bold">{summary?.recentUploads || 0}</div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight">Recent Datasets</h2>
          <Link href="/dashboard/analytics?page=upload">
            <Button size="sm" className="gap-2">
              <Upload size={14} />
              Upload Data
            </Button>
          </Link>
        </div>

        {loadingDatasets ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <Card key={i} className="p-4 border-border/50 shadow-sm">
                <div className="flex items-center space-x-4">
                  <Skeleton className="h-10 w-10 rounded-lg" />
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-1/4" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : datasets?.length === 0 ? (
          <Card className="border-dashed border-border p-12 text-center flex flex-col items-center justify-center bg-card/50">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <Upload className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-1">No datasets yet</h3>
            <p className="text-muted-foreground text-sm max-w-sm mb-6">
              Upload your first dataset to start cleaning, analyzing, and generating insights with Statyx AI.
            </p>
            <Link href="/dashboard/analytics?page=upload">
              <Button>Upload your first dataset</Button>
            </Link>
          </Card>
        ) : (
          <div className="grid gap-3">
            {datasets?.slice(0, 5).map((dataset) => (
              <Link key={dataset.id} href={`/dashboard/analytics?page=statistics`}>
                <Card className="border-border/50 shadow-sm hover:shadow-md transition-all cursor-pointer hover:border-primary/30 group">
                  <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center space-x-4">
                      <div className={`p-2 rounded-lg ${
                        dataset.status === 'ready' ? 'bg-primary/10 text-primary' : 
                        dataset.status === 'processing' ? 'bg-chart-4/10 text-chart-4' : 
                        'bg-destructive/10 text-destructive'
                      }`}>
                        <FileSpreadsheet size={20} />
                      </div>
                      <div>
                        <h4 className="font-medium text-foreground group-hover:text-primary transition-colors">
                          {dataset.name}
                        </h4>
                        <div className="flex items-center text-xs text-muted-foreground mt-1 space-x-3">
                          <span>{formatFileSize(dataset.fileSize)}</span>
                          <span>•</span>
                          <span>{dataset.rowCount ? `${dataset.rowCount.toLocaleString()} rows` : 'Calculating...'}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4 sm:space-x-8 text-sm">
                      <div className="flex items-center space-x-1.5">
                        {dataset.status === 'ready' && <CheckCircle2 className="h-4 w-4 text-chart-3" />}
                        {dataset.status === 'processing' && <Clock className="h-4 w-4 text-chart-4 animate-pulse" />}
                        {dataset.status === 'error' && <AlertCircle className="h-4 w-4 text-destructive" />}
                        <span className="capitalize text-muted-foreground">{dataset.status}</span>
                      </div>
                      <div className="text-muted-foreground hidden sm:block">
                        {formatDistanceToNow(new Date(dataset.uploadedAt), { addSuffix: true })}
                      </div>
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

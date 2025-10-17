"use client";

import { useState, useEffect } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DataTable } from "@/components/data/data-table";
import { ExcelTable } from "@/components/data/excel-table";
import { ChartBuilder } from "@/components/charts/chart-builder";
import { ChartRenderer } from "@/components/charts/chart-renderer";
import { TransformationPanel } from "@/components/transformations/transformation-panel";
import { ShareDialog } from "@/components/sharing/share-dialog";
import { FileUpload } from "@/components/chat/file-upload";
import { DataQualityDashboard } from "@/components/data/data-quality-dashboard";
import { ColumnStatsPanel } from "@/components/data/column-stats-panel";
import { SQLQueryEditor } from "@/components/sql/sql-query-editor";
import { UndoRedoToolbar } from "@/components/history/undo-redo-toolbar";
import { NLChartInput } from "@/components/nl/nl-chart-input";
import { VersionHistory } from "@/components/versions/version-history";
import { BarChart3, Table2, Upload, Wand2, Share2, Code, Activity, Lightbulb, Sparkles, Clock } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { transformationsApi, aiApi, previewApi } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

export default function AnalyticsPage() {
  const [data, setData] = useState<any[]>([]);
  const [hasData, setHasData] = useState(false);
  const [fileId, setFileId] = useState<number | null>(null);
  const [showShare, setShowShare] = useState(false);
  const [selectedColumn, setSelectedColumn] = useState<string | null>(null);
  const [insights, setInsights] = useState<any[]>([]);
  const [chartSuggestions, setChartSuggestions] = useState<any[]>([]);
  const [generatedChart, setGeneratedChart] = useState<any>(null);
  const { toast } = useToast();

  // Listen for file upload events
  useEffect(() => {
    const handleFileUpload = async (event: any) => {
      const fileData = event.detail;
      if (fileData?.id) {
        await loadFileData(fileData.id);
      }
    };

    window.addEventListener('fileUploaded', handleFileUpload);
    return () => window.removeEventListener('fileUploaded', handleFileUpload);
  }, []);

  const loadFileData = async (id: number) => {
    setFileId(id);

    try {
      // Load actual data from backend
      const dataResponse = await previewApi.getFileData(id, 1000);
      setData(dataResponse.data.data);
      setHasData(true);

      // Auto-generate insights
      const [insightsRes, suggestionsRes] = await Promise.all([
        aiApi.autoInsights(id),
        aiApi.chartSuggestions(id)
      ]);
      
      setInsights(insightsRes.data.insights);
      setChartSuggestions(suggestionsRes.data.suggestions);
    } catch (error) {
      console.error("Failed to load data:", error);
      toast({
        title: "Error",
        description: "Failed to load file data",
        variant: "destructive",
      });
    }
  };

  const handleChartGenerate = async (config: any) => {
    if (!fileId || !data.length) return;

    try {
      // Generate chart with real data
      setGeneratedChart({
        data: data,
        config: {
          type: config.chart_type || config.type,
          xColumn: config.x_column || config.xColumn,
          yColumn: config.y_column || config.yColumn,
          title: config.title,
          color: config.color || '#8B9BF8'
        }
      });

      toast({
        title: "Success",
        description: "Chart generated successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to generate chart",
        variant: "destructive",
      });
    }
  };

  const handleTransform = async (operation: any) => {
    if (!fileId) return;

    try {
      // Execute transformation
      switch (operation.operation) {
        case "rename":
          await transformationsApi.renameColumn(fileId, operation.column, operation.new_name);
          break;
        case "delete":
          await transformationsApi.deleteColumn(fileId, operation.column);
          break;
        case "cast":
          await transformationsApi.castColumn(fileId, operation.column, operation.data_type);
          break;
        case "derive":
          await transformationsApi.deriveColumn(fileId, operation.new_column, operation.formula);
          break;
      }

      toast({
        title: "Success",
        description: "Transformation applied successfully",
      });

      // Reload data
      await loadFileData(fileId);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to apply transformation",
        variant: "destructive",
      });
    }
  };

  const handleExport = () => {
    toast({
      title: "Export",
      description: "Export functionality coming soon",
    });
  };

  const columns = data.length > 0 ? Object.keys(data[0]) : [];

  return (
    <MainLayout>
      <div className="container mx-auto max-w-7xl p-6">
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold">Analytics</h1>
              <p className="text-muted-foreground">
                Explore and visualize your data
              </p>
            </div>
            {hasData && (
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setShowShare(true)}>
                  <Share2 className="mr-2 h-4 w-4" />
                  Share
                </Button>
              </div>
            )}
          </div>
          {hasData && (
            <UndoRedoToolbar 
              fileId={fileId} 
              onUndo={() => {
                toast({
                  title: "Refreshing",
                  description: "Reloading data after undo",
                });
              }} 
            />
          )}
        </div>

        {hasData && insights.length > 0 && (
          <Card className="mb-6 p-4">
            <div className="mb-3 flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              <h3 className="font-semibold">AI Insights</h3>
              <Badge variant="secondary">{insights.length} found</Badge>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {insights.slice(0, 4).map((insight, i) => (
                <div key={i} className="rounded-lg border border-border p-3">
                  <div className="mb-1 flex items-center gap-2">
                    <Badge variant={
                      insight.type === "warning" ? "destructive" :
                        insight.type === "success" ? "default" : "secondary"
                    } className="text-xs">
                      {insight.type}
                    </Badge>
                    <span className="text-sm font-medium">{insight.title}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">{insight.description}</p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {!hasData ? (
          <Card className="p-12 text-center">
            <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No data loaded</h3>
            <p className="text-muted-foreground mb-6">
              Upload a file to start analyzing your data
            </p>
            <div className="max-w-md mx-auto">
              <FileUpload />
            </div>
          </Card>
        ) : (
          <Tabs defaultValue="table" className="space-y-6">
            <TabsList>
              <TabsTrigger value="quality">
                <Activity className="mr-2 h-4 w-4" />
                Quality
              </TabsTrigger>
              <TabsTrigger value="table">
                <Table2 className="mr-2 h-4 w-4" />
                Data Table
              </TabsTrigger>
              <TabsTrigger value="sql">
                <Code className="mr-2 h-4 w-4" />
                SQL
              </TabsTrigger>
              <TabsTrigger value="transform">
                <Wand2 className="mr-2 h-4 w-4" />
                Transform
              </TabsTrigger>
              <TabsTrigger value="charts">
                <BarChart3 className="mr-2 h-4 w-4" />
                Charts
              </TabsTrigger>
              <TabsTrigger value="versions">
                <Clock className="mr-2 h-4 w-4" />
                Versions
              </TabsTrigger>
            </TabsList>

            <TabsContent value="quality" className="space-y-4">
              <DataQualityDashboard data={data} />
            </TabsContent>

            <TabsContent value="table" className="space-y-4">
              <ExcelTable
                data={data}
                onExport={handleExport}
                showRowNumbers={true}
                pageSize={50}
              />
            </TabsContent>

            <TabsContent value="sql" className="space-y-4">
              <SQLQueryEditor 
                fileId={fileId} 
                onResult={(result) => {
                  if (result.success) {
                    setData(result.data);
                    toast({
                      title: "Query Executed",
                      description: `Returned ${result.rowCount} rows`,
                    });
                  } else {
                    toast({
                      title: "Query Error",
                      description: result.error,
                      variant: "destructive",
                    });
                  }
                }} 
              />
            </TabsContent>

            <TabsContent value="transform" className="space-y-4">
              <Card className="p-6">
                <TransformationPanel columns={columns} onTransform={handleTransform} />
              </Card>
            </TabsContent>

            <TabsContent value="versions" className="space-y-4">
              <Card className="p-6">
                <h3 className="mb-4 text-lg font-semibold">Version History</h3>
                <VersionHistory 
                  fileId={fileId!} 
                  onRestore={() => {
                    toast({
                      title: "Reloading",
                      description: "Refreshing data after restore",
                    });
                  }} 
                />
              </Card>
            </TabsContent>

            <TabsContent value="charts" className="space-y-4">
              <Card className="p-4">
                <div className="mb-3">
                  <h3 className="mb-2 text-sm font-semibold">Natural Language Chart</h3>
                  <p className="mb-3 text-xs text-muted-foreground">
                    Describe the chart you want in plain English
                  </p>
                </div>
                <NLChartInput fileId={fileId} onGenerate={handleChartGenerate} />
              </Card>

              {chartSuggestions.length > 0 && (
                <Card className="p-4">
                  <div className="mb-3 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-primary" />
                    <h3 className="font-semibold">AI Chart Suggestions</h3>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {chartSuggestions.map((suggestion, i) => (
                      <div
                        key={i}
                        className="cursor-pointer rounded-lg border border-border p-3 hover:bg-accent"
                        onClick={() => handleChartGenerate(suggestion)}
                      >
                        <div className="mb-2 flex items-center justify-between">
                          <Badge variant="secondary">{suggestion.chart_type}</Badge>
                          <span className="text-xs text-muted-foreground">
                            {(suggestion.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <h4 className="mb-1 text-sm font-medium">{suggestion.title}</h4>
                        <p className="text-xs text-muted-foreground">{suggestion.reason}</p>
                      </div>
                    ))}
                  </div>
                </Card>
              )}
              
              <Card className="p-6">
                <ChartBuilder data={data} onGenerate={handleChartGenerate} />
              </Card>
              
              {generatedChart && (
                <Card className="p-6">
                  <ChartRenderer 
                    data={generatedChart.data} 
                    config={generatedChart.config} 
                  />
                </Card>
              )}
            </TabsContent>
          </Tabs>
        )}

        {showShare && fileId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
            <Card className="w-full max-w-md p-6">
              <ShareDialog analysisId={fileId} onClose={() => setShowShare(false)} />
            </Card>
          </div>
        )}

        {selectedColumn && (
          <ColumnStatsPanel
            column={selectedColumn}
            data={data}
            onClose={() => setSelectedColumn(null)}
          />
        )}
      </div>
    </MainLayout>
  );
}

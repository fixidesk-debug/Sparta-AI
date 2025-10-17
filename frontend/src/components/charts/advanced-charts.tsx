"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Activity, BarChart3, TrendingUp } from "lucide-react";
import { advancedChartsApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface AdvancedChartsProps {
  fileId: number;
  columns: string[];
}

export function AdvancedCharts({ fileId, columns }: AdvancedChartsProps) {
  const [chartType, setChartType] = useState("heatmap");
  const [selectedColumn, setSelectedColumn] = useState("");
  const [groupByColumn, setGroupByColumn] = useState("");
  const [chartData, setChartData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const numericColumns = columns; // In production, filter to only numeric columns

  const generateChart = async () => {
    setLoading(true);
    try {
      let response;

      switch (chartType) {
        case "heatmap":
          response = await advancedChartsApi.generateHeatmap(fileId);
          break;
        case "boxplot":
          if (!selectedColumn) {
            toast({
              title: "Column Required",
              description: "Please select a column for the box plot",
              variant: "destructive",
            });
            return;
          }
          response = await advancedChartsApi.generateBoxPlot(fileId, selectedColumn, groupByColumn || undefined);
          break;
        case "violin":
          if (!selectedColumn) {
            toast({
              title: "Column Required",
              description: "Please select a column for the violin plot",
              variant: "destructive",
            });
            return;
          }
          response = await advancedChartsApi.generateViolinPlot(fileId, selectedColumn, groupByColumn || undefined);
          break;
        case "histogram":
          if (!selectedColumn) {
            toast({
              title: "Column Required",
              description: "Please select a column for the histogram",
              variant: "destructive",
            });
            return;
          }
          response = await advancedChartsApi.generateHistogram(fileId, selectedColumn);
          break;
        case "scatter-matrix":
          response = await advancedChartsApi.generateScatterMatrix(fileId);
          break;
        default:
          return;
      }

      setChartData(response.data);
      toast({
        title: "Chart Generated",
        description: `${chartType} chart created successfully`,
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to generate chart",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="h-5 w-5" />
          <h3 className="text-lg font-semibold">Advanced Charts</h3>
        </div>

        <Tabs value={chartType} onValueChange={setChartType}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
            <TabsTrigger value="boxplot">Box Plot</TabsTrigger>
            <TabsTrigger value="violin">Violin</TabsTrigger>
            <TabsTrigger value="histogram">Histogram</TabsTrigger>
            <TabsTrigger value="scatter-matrix">Scatter Matrix</TabsTrigger>
          </TabsList>

          <TabsContent value="heatmap" className="space-y-4 mt-4">
            <p className="text-sm text-muted-foreground">
              Generate a correlation heatmap showing relationships between numeric columns
            </p>
          </TabsContent>

          <TabsContent value="boxplot" className="space-y-4 mt-4">
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label>Column</Label>
                <Select value={selectedColumn} onValueChange={setSelectedColumn}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select column" />
                  </SelectTrigger>
                  <SelectContent>
                    {numericColumns.map((col) => (
                      <SelectItem key={col} value={col}>
                        {col}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label>Group By (Optional)</Label>
                <Select value={groupByColumn} onValueChange={setGroupByColumn}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select grouping column" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {columns.map((col) => (
                      <SelectItem key={col} value={col}>
                        {col}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="violin" className="space-y-4 mt-4">
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label>Column</Label>
                <Select value={selectedColumn} onValueChange={setSelectedColumn}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select column" />
                  </SelectTrigger>
                  <SelectContent>
                    {numericColumns.map((col) => (
                      <SelectItem key={col} value={col}>
                        {col}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label>Group By (Optional)</Label>
                <Select value={groupByColumn} onValueChange={setGroupByColumn}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select grouping column" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    {columns.map((col) => (
                      <SelectItem key={col} value={col}>
                        {col}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="histogram" className="space-y-4 mt-4">
            <div className="grid gap-2">
              <Label>Column</Label>
              <Select value={selectedColumn} onValueChange={setSelectedColumn}>
                <SelectTrigger>
                  <SelectValue placeholder="Select column" />
                </SelectTrigger>
                <SelectContent>
                  {numericColumns.map((col) => (
                    <SelectItem key={col} value={col}>
                      {col}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </TabsContent>

          <TabsContent value="scatter-matrix" className="space-y-4 mt-4">
            <p className="text-sm text-muted-foreground">
              Generate a scatter plot matrix showing pairwise relationships between all numeric columns
            </p>
          </TabsContent>
        </Tabs>

        <Button onClick={generateChart} disabled={loading} className="w-full mt-4">
          {loading ? "Generating..." : "Generate Chart"}
        </Button>
      </Card>

      {chartData && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">{chartData.title}</h3>
          
          <div className="space-y-4">
            {chartType === "heatmap" && (
              <div className="grid gap-2">
                <p className="text-sm text-muted-foreground">
                  Correlation matrix with {chartData.columns?.length} columns
                </p>
                <div className="text-xs font-mono bg-muted p-4 rounded overflow-auto max-h-96">
                  <pre>{JSON.stringify(chartData.data?.slice(0, 10), null, 2)}</pre>
                </div>
              </div>
            )}

            {chartType === "boxplot" && (
              <div className="space-y-2">
                {chartData.data?.map((box: any, i: number) => (
                  <div key={i} className="p-3 bg-muted rounded">
                    <p className="font-medium text-sm">{box.group}</p>
                    <div className="grid grid-cols-5 gap-2 mt-2 text-xs">
                      <div>
                        <span className="text-muted-foreground">Min:</span> {box.min?.toFixed(2)}
                      </div>
                      <div>
                        <span className="text-muted-foreground">Q1:</span> {box.q1?.toFixed(2)}
                      </div>
                      <div>
                        <span className="text-muted-foreground">Median:</span> {box.median?.toFixed(2)}
                      </div>
                      <div>
                        <span className="text-muted-foreground">Q3:</span> {box.q3?.toFixed(2)}
                      </div>
                      <div>
                        <span className="text-muted-foreground">Max:</span> {box.max?.toFixed(2)}
                      </div>
                    </div>
                    {box.outliers?.length > 0 && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {box.outliers.length} outliers detected
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}

            {chartType === "violin" && (
              <div className="space-y-2">
                {chartData.data?.map((violin: any, i: number) => (
                  <div key={i} className="p-3 bg-muted rounded">
                    <p className="font-medium text-sm">{violin.group}</p>
                    <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                      <div>
                        <span className="text-muted-foreground">Mean:</span> {violin.mean?.toFixed(2)}
                      </div>
                      <div>
                        <span className="text-muted-foreground">Median:</span> {violin.median?.toFixed(2)}
                      </div>
                      <div>
                        <span className="text-muted-foreground">Std:</span> {violin.std?.toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {chartType === "histogram" && (
              <div className="space-y-2">
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Mean:</span> {chartData.mean?.toFixed(2)}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Median:</span> {chartData.median?.toFixed(2)}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Std Dev:</span> {chartData.std?.toFixed(2)}
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  {chartData.total_count} total values
                </p>
              </div>
            )}

            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const dataStr = JSON.stringify(chartData, null, 2);
                const blob = new Blob([dataStr], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${chartType}_data.json`;
                link.click();
                URL.revokeObjectURL(url);
              }}
            >
              Download Data
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}

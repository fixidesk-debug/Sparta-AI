"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { X, BarChart3, Hash, Calendar, Type } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ColumnStatsPanelProps {
  column: string;
  data: any[];
  onClose: () => void;
}

export function ColumnStatsPanel({ column, data, onClose }: ColumnStatsPanelProps) {
  const values = data.map((row) => row[column]).filter((v) => v !== null && v !== undefined);
  
  const stats = calculateStats(values);
  const distribution = calculateDistribution(values);

  return (
    <Card className="fixed right-6 top-20 w-80 max-h-[calc(100vh-8rem)] overflow-y-auto p-4 shadow-lg z-50">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            {getColumnIcon(stats.type)}
          </div>
          <div>
            <h3 className="font-semibold">{column}</h3>
            <Badge variant="secondary" className="text-xs">
              {stats.type}
            </Badge>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="mb-2 text-sm font-medium">Summary</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Count:</span>
              <span className="font-medium">{stats.count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Unique:</span>
              <span className="font-medium">{stats.unique}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Missing:</span>
              <span className="font-medium">{stats.missing}</span>
            </div>
            {stats.type === "number" && (
              <>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Mean:</span>
                  <span className="font-medium">{stats.mean?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Median:</span>
                  <span className="font-medium">{stats.median?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Std Dev:</span>
                  <span className="font-medium">{stats.stdDev?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Min:</span>
                  <span className="font-medium">{stats.min}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Max:</span>
                  <span className="font-medium">{stats.max}</span>
                </div>
              </>
            )}
          </div>
        </div>

        {stats.type === "number" && (
          <div>
            <h4 className="mb-2 text-sm font-medium">Distribution</h4>
            <div className="space-y-1">
              {distribution.map((bin, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground w-20">
                    {bin.range}
                  </span>
                  <div className="flex-1 h-6 bg-muted rounded overflow-hidden">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${bin.percentage}%` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground w-12 text-right">
                    {bin.count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {stats.type === "string" && stats.topValues && (
          <div>
            <h4 className="mb-2 text-sm font-medium">Top Values</h4>
            <div className="space-y-2">
              {stats.topValues.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="truncate flex-1">{item.value}</span>
                  <Badge variant="secondary">{item.count}</Badge>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}

function getColumnIcon(type: string) {
  switch (type) {
    case "number":
      return <Hash className="h-4 w-4 text-primary" />;
    case "date":
      return <Calendar className="h-4 w-4 text-primary" />;
    default:
      return <Type className="h-4 w-4 text-primary" />;
  }
}

function calculateStats(values: any[]) {
  const count = values.length;
  const unique = new Set(values).size;
  const missing = values.filter((v) => v === null || v === undefined).length;

  // Detect type
  const firstValue = values[0];
  let type = "string";
  if (typeof firstValue === "number") {
    type = "number";
  } else if (firstValue instanceof Date || !isNaN(Date.parse(firstValue))) {
    type = "date";
  }

  const stats: any = { count, unique, missing, type };

  if (type === "number") {
    const numbers = values.filter((v) => typeof v === "number");
    if (numbers.length > 0) {
      stats.mean = numbers.reduce((a, b) => a + b, 0) / numbers.length;
      stats.min = Math.min(...numbers);
      stats.max = Math.max(...numbers);
      
      const sorted = [...numbers].sort((a, b) => a - b);
      stats.median = sorted[Math.floor(sorted.length / 2)];
      
      const variance = numbers.reduce((sum, val) => sum + Math.pow(val - stats.mean, 2), 0) / numbers.length;
      stats.stdDev = Math.sqrt(variance);
    }
  }

  if (type === "string") {
    const counts = values.reduce((acc, val) => {
      acc[val] = (acc[val] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    stats.topValues = Object.entries(counts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([value, count]) => ({ value, count }));
  }

  return stats;
}

function calculateDistribution(values: any[]) {
  const numbers = values.filter((v) => typeof v === "number");
  if (numbers.length === 0) return [];

  const min = Math.min(...numbers);
  const max = Math.max(...numbers);
  const binCount = 10;
  const binSize = (max - min) / binCount;

  const bins = Array.from({ length: binCount }, (_, i) => ({
    min: min + i * binSize,
    max: min + (i + 1) * binSize,
    count: 0,
  }));

  numbers.forEach((num) => {
    const binIndex = Math.min(Math.floor((num - min) / binSize), binCount - 1);
    bins[binIndex].count++;
  });

  const maxCount = Math.max(...bins.map((b) => b.count));

  return bins.map((bin) => ({
    range: `${bin.min.toFixed(1)}-${bin.max.toFixed(1)}`,
    count: bin.count,
    percentage: (bin.count / maxCount) * 100,
  }));
}

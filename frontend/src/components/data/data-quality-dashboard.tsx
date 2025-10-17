"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, CheckCircle, AlertTriangle } from "lucide-react";

interface DataQualityDashboardProps {
  data: any[];
}

export function DataQualityDashboard({ data }: DataQualityDashboardProps) {
  if (data.length === 0) return null;

  const columns = Object.keys(data[0]);
  const totalCells = data.length * columns.length;

  const quality = analyzeDataQuality(data, columns);

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-500";
    if (score >= 70) return "text-yellow-500";
    return "text-red-500";
  };

  const getScoreIcon = (score: number) => {
    if (score >= 90) return <CheckCircle className="h-5 w-5 text-green-500" />;
    if (score >= 70) return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    return <AlertCircle className="h-5 w-5 text-red-500" />;
  };

  return (
    <Card className="p-6 mb-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Data Quality</h3>
          <p className="text-sm text-muted-foreground">
            Overall health of your dataset
          </p>
        </div>
        <div className="flex items-center gap-2">
          {getScoreIcon(quality.score)}
          <span className={`text-2xl font-bold ${getScoreColor(quality.score)}`}>
            {quality.score}%
          </span>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-border p-4">
          <div className="mb-2 text-sm text-muted-foreground">Completeness</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold">
              {((1 - quality.missingRate) * 100).toFixed(1)}%
            </span>
            <span className="text-sm text-muted-foreground">
              {quality.missingCells} missing
            </span>
          </div>
        </div>

        <div className="rounded-lg border border-border p-4">
          <div className="mb-2 text-sm text-muted-foreground">Duplicates</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold">{quality.duplicates}</span>
            <span className="text-sm text-muted-foreground">
              {((quality.duplicates / data.length) * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        <div className="rounded-lg border border-border p-4">
          <div className="mb-2 text-sm text-muted-foreground">Data Types</div>
          <div className="flex flex-wrap gap-1">
            {Object.entries(quality.typeDistribution).map(([type, count]) => (
              <Badge key={type} variant="secondary" className="text-xs">
                {type}: {count}
              </Badge>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border p-4">
          <div className="mb-2 text-sm text-muted-foreground">Outliers</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold">{quality.outliers}</span>
            <span className="text-sm text-muted-foreground">detected</span>
          </div>
        </div>
      </div>

      {quality.issues.length > 0 && (
        <div className="mt-4 space-y-2">
          <h4 className="text-sm font-medium">Issues Found</h4>
          {quality.issues.map((issue, i) => (
            <div
              key={i}
              className="flex items-start gap-2 rounded-lg bg-muted p-3 text-sm"
            >
              <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5" />
              <span>{issue}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

function analyzeDataQuality(data: any[], columns: string[]) {
  const totalCells = data.length * columns.length;
  let missingCells = 0;
  let outliers = 0;
  const typeDistribution: Record<string, number> = {};
  const issues: string[] = [];

  // Count missing values and detect types
  columns.forEach((col) => {
    const values = data.map((row) => row[col]);
    const missing = values.filter((v) => v === null || v === undefined || v === "").length;
    missingCells += missing;

    // Detect type
    const firstValue = values.find((v) => v !== null && v !== undefined);
    let type = "string";
    if (typeof firstValue === "number") {
      type = "number";
    } else if (firstValue instanceof Date || !isNaN(Date.parse(firstValue))) {
      type = "date";
    } else if (typeof firstValue === "boolean") {
      type = "boolean";
    }

    typeDistribution[type] = (typeDistribution[type] || 0) + 1;

    // Check for high missing rate
    const missingRate = missing / data.length;
    if (missingRate > 0.3) {
      issues.push(`Column "${col}" has ${(missingRate * 100).toFixed(1)}% missing values`);
    }

    // Detect outliers for numeric columns
    if (type === "number") {
      const numbers = values.filter((v) => typeof v === "number");
      if (numbers.length > 0) {
        const sorted = [...numbers].sort((a, b) => a - b);
        const q1 = sorted[Math.floor(sorted.length * 0.25)];
        const q3 = sorted[Math.floor(sorted.length * 0.75)];
        const iqr = q3 - q1;
        const lowerBound = q1 - 1.5 * iqr;
        const upperBound = q3 + 1.5 * iqr;
        
        const columnOutliers = numbers.filter((n) => n < lowerBound || n > upperBound).length;
        outliers += columnOutliers;
        
        if (columnOutliers > 0) {
          issues.push(`Column "${col}" has ${columnOutliers} outliers`);
        }
      }
    }
  });

  // Detect duplicates
  const duplicates = data.length - new Set(data.map((row) => JSON.stringify(row))).size;
  if (duplicates > 0) {
    issues.push(`${duplicates} duplicate rows found`);
  }

  const missingRate = missingCells / totalCells;
  const completenessScore = (1 - missingRate) * 100;
  const duplicateScore = (1 - duplicates / data.length) * 100;
  const score = Math.round((completenessScore + duplicateScore) / 2);

  return {
    score,
    missingCells,
    missingRate,
    duplicates,
    outliers,
    typeDistribution,
    issues,
  };
}

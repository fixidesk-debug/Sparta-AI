/**
 * Chart Data Processor for Sparta AI
 * 
 * Utilities for processing, transforming, and analyzing data for visualization
 */

import {
  DataPoint,
  Dataset,
  StatisticalSummary,
  DataTransformOptions,
  ProcessedData,
  DataAnalysis,
  ChartRecommendation,
} from '../types/visualization';

/**
 * Calculate statistical summary for a dataset
 */
export function calculateStatistics(data: number[]): StatisticalSummary {
  if (data.length === 0) {
    return { count: 0 };
  }

  const sorted = [...data].sort((a, b) => a - b);
  const count = sorted.length;
  const sum = sorted.reduce((acc, val) => acc + val, 0);
  const mean = sum / count;

  // Variance and standard deviation
  const squaredDiffs = sorted.map(val => Math.pow(val - mean, 2));
  const variance = squaredDiffs.reduce((acc, val) => acc + val, 0) / count;
  const std = Math.sqrt(variance);

  // Quartiles
  const q1Index = Math.floor(count * 0.25);
  const medianIndex = Math.floor(count * 0.5);
  const q3Index = Math.floor(count * 0.75);

  const q1 = sorted[q1Index];
  const median = sorted[medianIndex];
  const q3 = sorted[q3Index];

  // IQR and outliers
  const iqr = q3 - q1;
  const lowerBound = q1 - 1.5 * iqr;
  const upperBound = q3 + 1.5 * iqr;
  const outliers = sorted.filter(val => val < lowerBound || val > upperBound);

  // Mode (most frequent value)
  const frequency: Record<number, number> = {};
  sorted.forEach(val => {
    frequency[val] = (frequency[val] || 0) + 1;
  });
  const maxFrequency = Math.max(...Object.values(frequency));
  const modes = Object.keys(frequency)
    .filter(key => frequency[Number(key)] === maxFrequency)
    .map(Number);
  const mode = modes.length === sorted.length ? undefined : modes[0];

  return {
    mean,
    median,
    mode,
    std,
    variance,
    min: sorted[0],
    max: sorted[count - 1],
    q1,
    q3,
    count,
    outliers,
  };
}

/**
 * Transform and process dataset
 */
export function processData(
  data: DataPoint[],
  options: DataTransformOptions = {}
): ProcessedData {
  let processed = [...data];
  const transformations: string[] = [];

  // Filter data
  if (options.filter) {
    processed = processed.filter(options.filter);
    transformations.push('filtered');
  }

  // Group by field
  if (options.groupBy) {
    // Group and aggregate
    const groups: Record<string, DataPoint[]> = {};
    processed.forEach(point => {
      const key = String(point.metadata?.[options.groupBy!] || 'unknown');
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(point);
    });

    // Aggregate groups
    if (options.aggregate) {
      processed = Object.keys(groups).map(key => {
        const groupData = groups[key];
        const yValues = groupData.map(p => Number(p.y)).filter(v => !isNaN(v));
        let aggregatedY: number;

        switch (options.aggregate) {
          case 'sum':
            aggregatedY = yValues.reduce((sum, val) => sum + val, 0);
            break;
          case 'mean':
            aggregatedY = yValues.reduce((sum, val) => sum + val, 0) / yValues.length;
            break;
          case 'median':
            const sorted = [...yValues].sort((a, b) => a - b);
            aggregatedY = sorted[Math.floor(sorted.length / 2)];
            break;
          case 'min':
            aggregatedY = Math.min(...yValues);
            break;
          case 'max':
            aggregatedY = Math.max(...yValues);
            break;
          default:
            aggregatedY = yValues[0];
        }

        return {
          x: key,
          y: aggregatedY,
          label: key,
          metadata: { group: key, count: groupData.length },
        };
      });
      transformations.push(`grouped by ${options.groupBy}`, `aggregated by ${options.aggregate}`);
    }
  }

  // Sort data
  if (options.sortBy) {
    processed.sort((a, b) => {
      const aVal = options.sortBy === 'x' ? a.x : a.y;
      const bVal = options.sortBy === 'x' ? b.x : b.y;
      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return options.sortOrder === 'desc' ? -comparison : comparison;
    });
    transformations.push(`sorted by ${options.sortBy} ${options.sortOrder || 'asc'}`);
  }

  // Normalize data
  if (options.normalize) {
    const yValues = processed.map(p => Number(p.y)).filter(v => !isNaN(v));
    const min = Math.min(...yValues);
    const max = Math.max(...yValues);
    const range = max - min;

    if (range > 0) {
      processed = processed.map(point => ({
        ...point,
        y: ((Number(point.y) - min) / range),
      }));
      transformations.push('normalized');
    }
  }

  // Limit data points
  if (options.limit && processed.length > options.limit) {
    processed = processed.slice(0, options.limit);
    transformations.push(`limited to ${options.limit} points`);
  }

  // Calculate statistics
  const yValues = processed.map(p => Number(p.y)).filter(v => !isNaN(v));
  const statistics = calculateStatistics(yValues);

  return {
    original: data,
    processed,
    metadata: {
      transformations,
      originalCount: data.length,
      processedCount: processed.length,
      droppedCount: data.length - processed.length,
      statistics,
    },
  };
}

/**
 * Downsample large datasets for performance
 */
export function downsampleData(
  data: DataPoint[],
  targetSize: number,
  method: 'lttb' | 'random' | 'minmax' | 'average' = 'lttb'
): DataPoint[] {
  if (data.length <= targetSize) {
    return data;
  }

  switch (method) {
    case 'random':
      return downsampleRandom(data, targetSize);
    case 'minmax':
      return downsampleMinMax(data, targetSize);
    case 'average':
      return downsampleAverage(data, targetSize);
    case 'lttb':
    default:
      return downsampleLTTB(data, targetSize);
  }
}

/**
 * Largest Triangle Three Buckets (LTTB) downsampling algorithm
 * Preserves the visual appearance of the data better than random sampling
 */
function downsampleLTTB(data: DataPoint[], targetSize: number): DataPoint[] {
  if (targetSize <= 2) {
    return [data[0], data[data.length - 1]];
  }

  const sampled: DataPoint[] = [];
  const bucketSize = (data.length - 2) / (targetSize - 2);

  // Always include first point
  sampled.push(data[0]);

  let a = 0;
  for (let i = 0; i < targetSize - 2; i++) {
    const avgRangeStart = Math.floor((i + 1) * bucketSize) + 1;
    const avgRangeEnd = Math.floor((i + 2) * bucketSize) + 1;
    const avgRangeLength = avgRangeEnd - avgRangeStart;

    // Calculate average point in next bucket
    let avgX = 0;
    let avgY = 0;
    for (let j = avgRangeStart; j < avgRangeEnd; j++) {
      avgX += Number(data[j].x);
      avgY += Number(data[j].y);
    }
    avgX /= avgRangeLength;
    avgY /= avgRangeLength;

    // Find point in current bucket with largest triangle area
    const rangeStart = Math.floor(i * bucketSize) + 1;
    const rangeEnd = Math.floor((i + 1) * bucketSize) + 1;
    let maxArea = -1;
    let maxAreaIndex = rangeStart;

    const pointAX = Number(data[a].x);
    const pointAY = Number(data[a].y);

    for (let j = rangeStart; j < rangeEnd; j++) {
      const pointBX = Number(data[j].x);
      const pointBY = Number(data[j].y);
      
      // Calculate triangle area
      const area = Math.abs(
        (pointAX - avgX) * (pointBY - pointAY) -
        (pointAX - pointBX) * (avgY - pointAY)
      ) / 2;

      if (area > maxArea) {
        maxArea = area;
        maxAreaIndex = j;
      }
    }

    sampled.push(data[maxAreaIndex]);
    a = maxAreaIndex;
  }

  // Always include last point
  sampled.push(data[data.length - 1]);

  return sampled;
}

/**
 * Random downsampling
 */
function downsampleRandom(data: DataPoint[], targetSize: number): DataPoint[] {
  const sampled: DataPoint[] = [data[0]]; // Always include first
  const step = data.length / targetSize;
  
  for (let i = 1; i < targetSize - 1; i++) {
    const index = Math.floor(i * step + Math.random() * step);
    sampled.push(data[Math.min(index, data.length - 1)]);
  }
  
  sampled.push(data[data.length - 1]); // Always include last
  return sampled;
}

/**
 * Min-Max downsampling - preserves peaks and valleys
 */
function downsampleMinMax(data: DataPoint[], targetSize: number): DataPoint[] {
  const sampled: DataPoint[] = [data[0]];
  const bucketSize = Math.floor(data.length / targetSize);
  
  for (let i = 1; i < targetSize - 1; i++) {
    const start = i * bucketSize;
    const end = Math.min(start + bucketSize, data.length);
    const bucket = data.slice(start, end);
    
    // Find min and max in bucket
    let min = bucket[0];
    let max = bucket[0];
    
    bucket.forEach(point => {
      if (Number(point.y) < Number(min.y)) min = point;
      if (Number(point.y) > Number(max.y)) max = point;
    });
    
    // Add both min and max to preserve extremes
    if (Number(min.x) < Number(max.x)) {
      sampled.push(min, max);
    } else {
      sampled.push(max, min);
    }
  }
  
  sampled.push(data[data.length - 1]);
  return sampled;
}

/**
 * Average downsampling
 */
function downsampleAverage(data: DataPoint[], targetSize: number): DataPoint[] {
  const sampled: DataPoint[] = [data[0]];
  const bucketSize = Math.floor(data.length / targetSize);
  
  for (let i = 1; i < targetSize - 1; i++) {
    const start = i * bucketSize;
    const end = Math.min(start + bucketSize, data.length);
    const bucket = data.slice(start, end);
    
    // Calculate average
    const avgX = bucket.reduce((sum, p) => sum + Number(p.x), 0) / bucket.length;
    const avgY = bucket.reduce((sum, p) => sum + Number(p.y), 0) / bucket.length;
    
    sampled.push({
      x: avgX,
      y: avgY,
      label: bucket[0].label,
    });
  }
  
  sampled.push(data[data.length - 1]);
  return sampled;
}

/**
 * Analyze data and recommend chart types
 */
export function analyzeData(datasets: Dataset[]): DataAnalysis {
  if (datasets.length === 0 || datasets[0].data.length === 0) {
    return {
      dataType: 'mixed',
      dimensions: 0,
      pointCount: 0,
      hasNulls: false,
      hasOutliers: false,
      recommendations: [],
    };
  }

  const allData = datasets.flatMap(d => d.data);
  const firstPoint = allData[0];

  // Determine data type
  const hasNumericX = typeof firstPoint.x === 'number';
  const hasNumericY = typeof firstPoint.y === 'number';
  const hasZ = firstPoint.z !== undefined;
  const hasDate = firstPoint.x instanceof Date;

  let dataType: 'numerical' | 'categorical' | 'temporal' | 'mixed';
  if (hasDate) {
    dataType = 'temporal';
  } else if (hasNumericX && hasNumericY) {
    dataType = 'numerical';
  } else if (!hasNumericX && hasNumericY) {
    dataType = 'categorical';
  } else {
    dataType = 'mixed';
  }

  const dimensions = hasZ ? 3 : 2;
  const pointCount = allData.length;

  // Check for nulls
  const hasNulls = allData.some(p => p.x == null || p.y == null);

  // Check for outliers (numerical data only)
  let hasOutliers = false;
  let distribution: 'normal' | 'uniform' | 'skewed' | 'bimodal' | undefined;
  
  if (hasNumericY) {
    const yValues = allData.map(p => Number(p.y)).filter(v => !isNaN(v));
    const stats = calculateStatistics(yValues);
    hasOutliers = (stats.outliers?.length || 0) > 0;
    
    // Simple distribution detection based on skewness
    if (stats.mean !== undefined && stats.median !== undefined && stats.std !== undefined) {
      const skewness = (stats.mean - stats.median) / stats.std;
      if (Math.abs(skewness) < 0.5) {
        distribution = 'normal';
      } else {
        distribution = 'skewed';
      }
    }
  }

  // Generate recommendations
  const recommendations = generateRecommendations({
    dataType,
    dimensions,
    pointCount,
    hasOutliers,
    datasetCount: datasets.length,
  });

  return {
    dataType,
    dimensions,
    pointCount,
    hasNulls,
    hasOutliers,
    distribution,
    recommendations,
  };
}

/**
 * Generate chart type recommendations based on data characteristics
 */
function generateRecommendations(context: {
  dataType: string;
  dimensions: number;
  pointCount: number;
  hasOutliers: boolean;
  datasetCount: number;
}): ChartRecommendation[] {
  const recommendations: ChartRecommendation[] = [];

  // Temporal data
  if (context.dataType === 'temporal') {
    recommendations.push({
      type: 'line',
      confidence: 0.9,
      reason: 'Time series data works best with line charts',
    });
    recommendations.push({
      type: 'area',
      confidence: 0.7,
      reason: 'Area charts show trends over time effectively',
    });
  }

  // Categorical data
  else if (context.dataType === 'categorical') {
    recommendations.push({
      type: 'bar',
      confidence: 0.9,
      reason: 'Categorical data is best displayed with bar charts',
    });
    if (context.pointCount < 10) {
      recommendations.push({
        type: 'pie',
        confidence: 0.7,
        reason: 'Small categorical datasets can use pie charts',
      });
    }
  }

  // Numerical data
  else if (context.dataType === 'numerical') {
    if (context.datasetCount === 1) {
      recommendations.push({
        type: 'scatter',
        confidence: 0.8,
        reason: 'Scatter plots show relationships in numerical data',
      });
      if (context.pointCount > 50) {
        recommendations.push({
          type: 'histogram',
          confidence: 0.75,
          reason: 'Histogram shows distribution of large numerical datasets',
        });
      }
    } else {
      recommendations.push({
        type: 'scatter',
        confidence: 0.85,
        reason: 'Multiple datasets work well as scatter plots',
      });
      recommendations.push({
        type: 'line',
        confidence: 0.7,
        reason: 'Line charts compare multiple series effectively',
      });
    }

    if (context.hasOutliers) {
      recommendations.push({
        type: 'box',
        confidence: 0.8,
        reason: 'Box plots highlight outliers and distribution',
      });
    }
  }

  // 3D data
  if (context.dimensions === 3) {
    recommendations.push({
      type: 'heatmap',
      confidence: 0.85,
      reason: '3D data visualizes well as a heatmap',
    });
    recommendations.push({
      type: 'bubble',
      confidence: 0.7,
      reason: 'Bubble charts can represent 3 dimensions',
    });
  }

  // Multiple datasets
  if (context.datasetCount > 3) {
    recommendations.push({
      type: 'correlation',
      confidence: 0.75,
      reason: 'Correlation matrix shows relationships between multiple variables',
    });
  }

  // Sort by confidence
  recommendations.sort((a, b) => b.confidence - a.confidence);

  return recommendations;
}

/**
 * Detect data type from sample
 */
export function detectDataType(value: unknown): 'number' | 'string' | 'date' | 'boolean' | 'unknown' {
  try {
    if (value == null) return 'unknown';
    if (typeof value === 'number') return 'number';
    if (typeof value === 'boolean') return 'boolean';
    if (value instanceof Date) return 'date';
    if (typeof value === 'string') {
      const parsed = Date.parse(value);
      if (!isNaN(parsed)) return 'date';
      return 'string';
    }
    return 'unknown';
  } catch {
    return 'unknown';
  }
}

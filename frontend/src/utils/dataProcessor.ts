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

// Helper utilities
function safeNumber(v: unknown, fallback = NaN): number {
  const n = Number(v as any);
  return Number.isFinite(n) ? n : fallback;
}

function ensureBucketRange(start: number, end: number, length: number) {
  const s = Math.max(0, Math.min(length, start));
  const e = Math.max(s, Math.min(length, end));
  return { s, e };
}

/**
 * Safely run a potentially unsafe operation and return a fallback on error.
 */
function safeRun<T>(fn: () => T, fallback: T): T {
  try {
    return fn();
  } catch (err) {
    // Keep error handling lightweight here (UI should not crash on bad input)
    // eslint-disable-next-line no-console
    console.error('dataProcessor: caught error', err);
    return fallback;
  }
}

/**
 * Calculate statistical summary for a dataset
 */
export function calculateStatistics(data: number[]): StatisticalSummary {
  if (!Array.isArray(data) || data.length === 0) return { count: 0 };

  // Filter and coerce to numbers once
  const nums: number[] = data.map(v => safeNumber(v)).filter(n => !Number.isNaN(n));
  if (nums.length === 0) return { count: 0 };

  // Single-pass Welford algorithm for mean and variance
  let mean = 0;
  let M2 = 0;
  let count = 0;
  let min = Infinity;
  let max = -Infinity;

  for (let i = 0; i < nums.length; i++) {
    const x = nums[i];
    count++;
    const delta = x - mean;
    mean += delta / count;
    M2 += delta * (x - mean);
    if (x < min) min = x;
    if (x > max) max = x;
  }

  const variance = M2 / count;
  const std = Math.sqrt(variance);

  // Quartiles - require sorted array
  const sorted = nums.slice().sort((a, b) => a - b);
  const quartile = (arr: number[], p: number) => {
    const pos = (arr.length - 1) * p;
    const base = Math.floor(pos);
    const rest = pos - base;
    if (arr[base + 1] !== undefined) return arr[base] + rest * (arr[base + 1] - arr[base]);
    return arr[base];
  };

  const q1 = quartile(sorted, 0.25);
  const median = quartile(sorted, 0.5);
  const q3 = quartile(sorted, 0.75);

  // IQR and outliers
  const iqr = q3 - q1;
  const lowerBound = q1 - 1.5 * iqr;
  const upperBound = q3 + 1.5 * iqr;
  const outliers = sorted.filter(val => val < lowerBound || val > upperBound);

  // Mode using Map for performance
  const freq = new Map<number, number>();
  for (let i = 0; i < sorted.length; i++) {
    const v = sorted[i];
    freq.set(v, (freq.get(v) || 0) + 1);
  }
  let mode: number | undefined;
  if (freq.size > 0) {
    let maxFreq = 0;
    freq.forEach((v, k) => {
      if (v > maxFreq) {
        maxFreq = v;
        mode = k;
      }
    });
    if (maxFreq === 1 && freq.size === sorted.length) mode = undefined;
  }

  return {
    mean,
    median,
    mode,
    std,
    variance,
    min,
    max,
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

    // Aggregate groups (if requested) with safer numeric handling
    if (options.aggregate) {
      processed = Object.keys(groups).map(key => {
        const groupData = groups[key];
        const yValues = groupData.map(p => safeNumber(p.y)).filter(v => !Number.isNaN(v));

        let aggregatedY: number | undefined = undefined;
        if (yValues.length === 0) {
          aggregatedY = undefined;
        } else {
          switch (options.aggregate) {
            case 'sum':
              aggregatedY = yValues.reduce((sum, val) => sum + val, 0);
              break;
            case 'mean':
              aggregatedY = yValues.reduce((sum, val) => sum + val, 0) / yValues.length;
              break;
            case 'median':
              const sortedY = [...yValues].sort((a, b) => a - b);
              aggregatedY = sortedY[Math.floor(sortedY.length / 2)];
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
        }

        return {
          x: key,
          y: aggregatedY,
          label: key,
          metadata: { group: key, count: groupData.length },
        } as unknown as DataPoint;
      });
      transformations.push(`grouped by ${options.groupBy}`, `aggregated by ${options.aggregate}`);
    }
  }

  // Sort data
  if (options.sortBy) {
    processed.sort((a, b) => {
      const aVal = options.sortBy === 'x' ? safeNumber(a.x) : safeNumber(a.y);
      const bVal = options.sortBy === 'x' ? safeNumber(b.x) : safeNumber(b.y);
      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return options.sortOrder === 'desc' ? -comparison : comparison;
    });
    transformations.push(`sorted by ${options.sortBy} ${options.sortOrder || 'asc'}`);
  }

  // Normalize data
  if (options.normalize) {
    const yValues = processed.map(p => safeNumber(p.y)).filter(v => !Number.isNaN(v));
    if (yValues.length > 0) {
      const min = Math.min(...yValues);
      const max = Math.max(...yValues);
      const range = max - min;

      if (range > 0) {
        processed = processed.map(point => ({
          ...point,
          y: Number.isNaN(safeNumber(point.y)) ? point.y : ((safeNumber(point.y) - min) / range),
        }));
        transformations.push('normalized');
      }
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
    const { s: avgRangeStart, e: avgRangeEnd } = ensureBucketRange(
      Math.floor((i + 1) * bucketSize) + 1,
      Math.floor((i + 2) * bucketSize) + 1,
      data.length
    );
    const avgRangeLength = Math.max(1, avgRangeEnd - avgRangeStart);

    // Calculate average point in next bucket (use local vars to avoid repeated conversions)
    let avgX = 0;
    let avgY = 0;
    for (let j = avgRangeStart; j < avgRangeEnd; j++) {
      avgX += safeNumber(data[j].x, 0);
      avgY += safeNumber(data[j].y, 0);
    }
    avgX /= avgRangeLength;
    avgY /= avgRangeLength;

    // Find point in current bucket with largest triangle area
    const { s: rangeStart, e: rangeEnd } = ensureBucketRange(
      Math.floor(i * bucketSize) + 1,
      Math.floor((i + 1) * bucketSize) + 1,
      data.length
    );
    let maxArea = -1;
    let maxAreaIndex = rangeStart;

    const pointAX = safeNumber(data[a].x, 0);
    const pointAY = safeNumber(data[a].y, 0);

    for (let j = rangeStart; j < rangeEnd; j++) {
  const pointBX = safeNumber(data[j].x, 0);
  const pointBY = safeNumber(data[j].y, 0);
      
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
  // Defensive guards
  if (!Array.isArray(data) || data.length === 0 || !Number.isFinite(targetSize) || targetSize <= 0) return [];
  if (data.length <= targetSize) return data.slice();

  const sampled: DataPoint[] = [];
  sampled.push(data[0]); // Always include first
  const step = data.length / targetSize;

  for (let i = 1; i < targetSize - 1; i++) {
    // compute a randomized index within the bucket [i*step, (i+1)*step)
    const base = Math.floor(i * step);
    const span = Math.max(1, Math.floor(step));
    const randOffset = Math.floor(Math.random() * span);
    const index = Math.min(data.length - 1, base + randOffset);
    sampled.push(data[index]);
  }

  sampled.push(data[data.length - 1]); // Always include last
  return sampled;
}

/**
 * Min-Max downsampling - preserves peaks and valleys
 */
function downsampleMinMax(data: DataPoint[], targetSize: number): DataPoint[] {
  const sampled: DataPoint[] = [data[0]];
  const bucketSize = Math.max(1, Math.floor(data.length / targetSize));
  
  for (let i = 1; i < targetSize - 1; i++) {
    const start = i * bucketSize;
    const end = Math.min(start + bucketSize, data.length);
    const bucket = data.slice(start, end);
    if (bucket.length === 0) continue;
    
    // Find min and max in bucket (use safeNumber once per item)
    let min = bucket[0];
    let max = bucket[0];
    for (let k = 0; k < bucket.length; k++) {
      const point = bucket[k];
      const val = safeNumber(point.y, NaN);
      if (Number.isNaN(val)) continue;
      if (val < safeNumber(min.y, val)) min = point;
      if (val > safeNumber(max.y, val)) max = point;
    }
    
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
  const bucketSize = Math.max(1, Math.floor(data.length / targetSize));
  
  for (let i = 1; i < targetSize - 1; i++) {
    const start = i * bucketSize;
    const end = Math.min(start + bucketSize, data.length);
    const bucket = data.slice(start, end);
    if (bucket.length === 0) continue;
    
    // Calculate average using safeNumber and local accumulators
    let sumX = 0;
    let sumY = 0;
    let count = 0;
    for (let k = 0; k < bucket.length; k++) {
      const p = bucket[k];
      const nx = safeNumber(p.x, NaN);
      const ny = safeNumber(p.y, NaN);
      if (Number.isNaN(nx) || Number.isNaN(ny)) continue;
      sumX += nx;
      sumY += ny;
      count++;
    }
    if (count === 0) continue;
    const avgX = sumX / count;
    const avgY = sumY / count;
    
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
  if (!Array.isArray(datasets) || datasets.length === 0) {
    return {
      dataType: 'mixed',
      dimensions: 0,
      pointCount: 0,
      hasNulls: false,
      hasOutliers: false,
      recommendations: [],
    };
  }

  // Avoid creating large flattened arrays when possible; sample first non-empty dataset
  let firstPoint: DataPoint | undefined = undefined;
  for (let i = 0; i < datasets.length && !firstPoint; i++) {
    if (datasets[i].data && datasets[i].data.length > 0) firstPoint = datasets[i].data[0];
  }
  if (!firstPoint) {
    return {
      dataType: 'mixed',
      dimensions: 0,
      pointCount: 0,
      hasNulls: false,
      hasOutliers: false,
      recommendations: [],
    };
  }

  // Determine data type from a sample
  const hasNumericX = typeof firstPoint.x === 'number';
  const hasNumericY = typeof firstPoint.y === 'number';
  const hasZ = firstPoint.z !== undefined;
  const hasDate = firstPoint.x instanceof Date || (typeof firstPoint.x === 'string' && !Number.isNaN(Date.parse(firstPoint.x)));

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
  // Count points and detect nulls with a single pass over datasets to avoid extra allocations
  let pointCount = 0;
  let hasNulls = false;
  const yValuesForStats: number[] = [];
  for (let di = 0; di < datasets.length; di++) {
    const d = datasets[di];
    for (let pi = 0; pi < d.data.length; pi++) {
      const p = d.data[pi];
      pointCount++;
      if (p.x == null || p.y == null) hasNulls = true;
      if (typeof p.y === 'number') yValuesForStats.push(p.y);
      else {
        const n = safeNumber(p.y);
        if (!Number.isNaN(n)) yValuesForStats.push(n);
      }
    }
  }

  // Check for outliers (numerical data only)
  let hasOutliers = false;
  let distribution: 'normal' | 'uniform' | 'skewed' | 'bimodal' | undefined;
  
  if (hasNumericY && yValuesForStats.length > 0) {
    const stats = safeRun(() => calculateStatistics(yValuesForStats), { count: 0 });
    hasOutliers = (stats.outliers?.length || 0) > 0;
    
    // Simple distribution detection based on skewness (guard against zero std)
    if (stats.mean !== undefined && stats.median !== undefined && stats.std !== undefined && stats.std > 0) {
      const skewness = (stats.mean - stats.median) / stats.std;
      distribution = Math.abs(skewness) < 0.5 ? 'normal' : 'skewed';
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
  if (value == null) return 'unknown';
  if (typeof value === 'number') return 'number';
  if (typeof value === 'boolean') return 'boolean';
  if (value instanceof Date && !Number.isNaN(value.getTime())) return 'date';
  if (typeof value === 'string') {
    // Lightweight date detection: avoid heavy parsing for very long strings
    const s = value.trim();
    if (s.length === 0 || s.length > 100) return 'string';
    const parsed = Date.parse(s);
    return Number.isFinite(parsed) && !Number.isNaN(parsed) ? 'date' : 'string';
  }
  return 'unknown';
}

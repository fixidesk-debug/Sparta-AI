/**
 * Visualization Types and Interfaces for Sparta AI
 * 
 * Comprehensive type definitions for chart rendering, configuration,
 * and data processing across all supported visualization types.
 */

import { Data as PlotData, Layout, Config } from 'plotly.js';

// ============================================================================
// Chart Types
// ============================================================================

export type ChartType =
  | 'line'
  | 'bar'
  | 'scatter'
  | 'histogram'
  | 'box'
  | 'violin'
  | 'heatmap'
  | 'correlation'
  | 'pie'
  | 'area'
  | 'bubble'
  | 'candlestick'
  | 'waterfall'
  | 'funnel'
  | 'sunburst'
  | 'treemap'
  | 'sankey'
  | 'custom';

export type ColorScheme = 
  | 'default'
  | 'viridis'
  | 'plasma'
  | 'inferno'
  | 'magma'
  | 'blues'
  | 'reds'
  | 'greens'
  | 'categorical'
  | 'diverging';

export type ExportFormat = 'png' | 'svg' | 'pdf' | 'json' | 'csv';

export type Theme = 'light' | 'dark' | 'auto';

// ============================================================================
// Data Structures
// ============================================================================

/**
 * Standardized data point for all chart types
 */
export interface DataPoint {
  x: number | string | Date;
  y: number | string | Date;
  z?: number;
  label?: string;
  color?: string;
  size?: number;
  metadata?: Record<string, unknown>;
}

/**
 * Dataset with metadata
 */
export interface Dataset {
  id: string;
  name: string;
  data: DataPoint[];
  type?: ChartType;
  color?: string;
  visible?: boolean;
  metadata?: Record<string, unknown>;
}

/**
 * Statistical summary for a dataset
 */
export interface StatisticalSummary {
  mean?: number;
  median?: number;
  mode?: number;
  std?: number;
  variance?: number;
  min?: number;
  max?: number;
  q1?: number;
  q3?: number;
  count?: number;
  outliers?: number[];
}

// ============================================================================
// Chart Configuration
// ============================================================================

/**
 * Comprehensive chart configuration interface
 */
export interface ChartConfig {
  // Chart identification
  id: string;
  type: ChartType;
  
  // Data
  datasets: Dataset[];
  
  // Layout configuration
  title?: string;
  subtitle?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  zAxisLabel?: string;
  
  // Styling
  width?: number | string;
  height?: number | string;
  colorScheme?: ColorScheme;
  theme?: Theme;
  
  // Interactivity
  interactive?: boolean;
  zoomEnabled?: boolean;
  panEnabled?: boolean;
  hoverEnabled?: boolean;
  clickEnabled?: boolean;
  
  // Features
  showLegend?: boolean;
  showGrid?: boolean;
  showAxes?: boolean;
  showTooltips?: boolean;
  
  // Performance
  downsample?: boolean;
  maxDataPoints?: number;
  renderMode?: 'svg' | 'webgl';
  
  // Accessibility
  ariaLabel?: string;
  ariaDescription?: string;
  keyboardNavigation?: boolean;
  
  // Advanced options
  customLayout?: Partial<Layout>;
  customConfig?: Partial<Config>;
  annotations?: Annotation[];
  
  // Metadata
  metadata?: Record<string, unknown>;
}

/**
 * Chart annotation for highlighting features
 */
export interface Annotation {
  type: 'line' | 'rect' | 'circle' | 'text' | 'arrow';
  x?: number | string;
  y?: number | string;
  x0?: number | string;
  y0?: number | string;
  x1?: number | string;
  y1?: number | string;
  text?: string;
  color?: string;
  opacity?: number;
  showarrow?: boolean;
}

// ============================================================================
// Chart Rendering
// ============================================================================

/**
 * Processed data ready for Plotly rendering
 */
export interface PlotlyData {
  data: Partial<PlotData>[];
  layout: Partial<Layout>;
  config: Partial<Config>;
}

/**
 * Chart rendering options
 */
export interface RenderOptions {
  responsive?: boolean;
  displayModeBar?: boolean;
  displayLogo?: boolean;
  modeBarButtons?: string[][];
  locale?: string;
  doubleClickDelay?: number;
}

// ============================================================================
// Interaction Events
// ============================================================================

/**
 * Chart interaction event data
 */
export interface ChartInteraction {
  type: 'click' | 'hover' | 'select' | 'zoom' | 'pan' | 'reset';
  points?: InteractionPoint[];
  range?: AxisRange;
  timestamp: number;
}

/**
 * Individual point interaction data
 */
export interface InteractionPoint {
  datasetIndex: number;
  pointIndex: number;
  x: number | string | Date;
  y: number | string | Date;
  z?: number;
  label?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Axis range for zoom/pan events
 */
export interface AxisRange {
  x?: [number | string, number | string];
  y?: [number | string, number | string];
  z?: [number | string, number | string];
}

// ============================================================================
// Export Configuration
// ============================================================================

/**
 * Export options for chart download
 */
export interface ExportOptions {
  format: ExportFormat;
  filename?: string;
  width?: number;
  height?: number;
  scale?: number;
  backgroundColor?: string;
  includeData?: boolean;
  includeMetadata?: boolean;
}

/**
 * Export result with status
 */
export interface ExportResult {
  success: boolean;
  format: ExportFormat;
  filename: string;
  size?: number;
  blob?: Blob;
  dataUrl?: string;
  error?: string;
}

// ============================================================================
// Performance Optimization
// ============================================================================

/**
 * Performance optimization settings
 */
export interface PerformanceSettings {
  enabled: boolean;
  downsampleThreshold: number;
  downsampleMethod: 'lttb' | 'random' | 'minmax' | 'average';
  lazyLoad: boolean;
  virtualizeData: boolean;
  cacheResults: boolean;
  debounceMs: number;
}

/**
 * Performance metrics
 */
export interface PerformanceMetrics {
  dataPoints: number;
  renderTime: number;
  interactionLatency: number;
  memoryUsage?: number;
  fps?: number;
}

// ============================================================================
// Theme Configuration
// ============================================================================

/**
 * Chart theme configuration
 */
export interface ChartTheme {
  name: string;
  
  // Colors
  backgroundColor: string;
  textColor: string;
  gridColor: string;
  axisColor: string;
  
  // Fonts
  fontFamily: string;
  fontSize: number;
  titleFontSize: number;
  
  // Chart colors
  colorPalette: string[];
  
  // Styling
  borderWidth: number;
  opacity: number;
  
  // Plotly-specific
  plotlyTemplate?: string;
}

// ============================================================================
// Accessibility
// ============================================================================

/**
 * Accessibility configuration
 */
export interface AccessibilityConfig {
  enabled: boolean;
  keyboardNavigation: boolean;
  screenReaderSupport: boolean;
  highContrastMode: boolean;
  focusIndicators: boolean;
  ariaLive: 'polite' | 'assertive' | 'off';
  announceChanges: boolean;
  describePlot: boolean;
}

/**
 * Chart description for screen readers
 */
export interface ChartDescription {
  title: string;
  summary: string;
  dataDescription: string;
  statisticalSummary?: string;
  trendDescription?: string;
  keyFindings?: string[];
}

// ============================================================================
// Error Handling
// ============================================================================

/**
 * Chart error information
 */
export interface ChartError {
  code: string;
  message: string;
  details?: string;
  timestamp: number;
  recoverable: boolean;
  suggestion?: string;
}

/**
 * Validation result
 */
export interface ValidationResult {
  valid: boolean;
  errors: ChartError[];
  warnings: string[];
}

// ============================================================================
// Component Props
// ============================================================================

/**
 * Main ChartRenderer component props
 */
export interface ChartRendererProps {
  config: ChartConfig;
  className?: string;
  style?: React.CSSProperties;
  onInteraction?: (event: ChartInteraction) => void;
  onError?: (error: ChartError) => void;
  onLoad?: () => void;
  onExport?: (result: ExportResult) => void;
  performanceSettings?: Partial<PerformanceSettings>;
  accessibilityConfig?: Partial<AccessibilityConfig>;
}

/**
 * Chart controls component props
 */
export interface ChartControlsProps {
  chartId: string;
  availableTypes: ChartType[];
  currentType: ChartType;
  exportFormats: ExportFormat[];
  onTypeChange: (type: ChartType) => void;
  onExport: (format: ExportFormat) => void;
  onReset: () => void;
  onToggleLegend: () => void;
  onToggleGrid: () => void;
  disabled?: boolean;
}

/**
 * Chart legend component props
 */
export interface ChartLegendProps {
  datasets: Dataset[];
  onToggleDataset: (datasetId: string) => void;
  onHighlightDataset: (datasetId: string | null) => void;
  interactive?: boolean;
  position?: 'top' | 'right' | 'bottom' | 'left';
}

// ============================================================================
// Data Processing
// ============================================================================

/**
 * Data transformation options
 */
export interface DataTransformOptions {
  normalize?: boolean;
  aggregate?: 'sum' | 'mean' | 'median' | 'min' | 'max';
  groupBy?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filter?: (point: DataPoint) => boolean;
  limit?: number;
}

/**
 * Data processor result
 */
export interface ProcessedData {
  original: DataPoint[];
  processed: DataPoint[];
  metadata: {
    transformations: string[];
    originalCount: number;
    processedCount: number;
    droppedCount: number;
    statistics?: StatisticalSummary;
  };
}

// ============================================================================
// Auto-detection
// ============================================================================

/**
 * Chart type recommendation
 */
export interface ChartRecommendation {
  type: ChartType;
  confidence: number;
  reason: string;
  alternatives?: Array<{
    type: ChartType;
    confidence: number;
  }>;
}

/**
 * Data analysis result for auto-detection
 */
export interface DataAnalysis {
  dataType: 'numerical' | 'categorical' | 'temporal' | 'mixed';
  dimensions: number;
  pointCount: number;
  hasNulls: boolean;
  hasOutliers: boolean;
  distribution?: 'normal' | 'uniform' | 'skewed' | 'bimodal';
  correlation?: number;
  recommendations: ChartRecommendation[];
}

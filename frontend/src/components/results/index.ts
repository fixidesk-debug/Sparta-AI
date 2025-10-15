/**
 * Analysis Results Components - Index
 * Export all analysis card components
 */

// Main card components
export {
  AnalysisCard,
  MetricCard,
  ProgressBar,
  StatusIndicator,
  StatisticalResult,
  ComparisonCard,
} from './AnalysisCards';

export type {
  AnalysisCardProps,
  MetricCardProps,
  ProgressBarProps,
  StatusIndicatorProps,
  StatisticalResultProps,
  ComparisonCardProps,
} from './AnalysisCards';

// Specialized card components
export {
  TimelineCard,
  DistributionCard,
  CorrelationCard,
  TrendCard,
  CategoryCard,
  AlertCard,
} from './SpecializedCards';

export type {
  TimelineCardProps,
  DistributionCardProps,
  CorrelationCardProps,
  TrendCardProps,
  CategoryCardProps,
  AlertCardProps,
} from './SpecializedCards';

// Example dashboard
export { AnalysisDashboardExample } from './AnalysisDashboardExample';

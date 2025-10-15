/**
 * Example: Integrated Chart Visualization Component
 * 
 * Demonstrates how to use the visualization system with the Sparta AI chat interface
 */

import React, { useState, useMemo } from 'react';
import { ChartRenderer } from './ChartRenderer';
import { ChartControls } from './ChartControls';
import {
  ChartConfig,
  ChartType,
  ExportFormat,
  ChartInteraction,
  ChartError,
} from '../types/visualization';
import { analyzeData } from '../utils/dataProcessor';
import { exportChart } from '../utils/exportManager';

interface VisualizationPanelProps {
  /** Initial chart configuration from AI */
  initialConfig: ChartConfig;
  /** Callback when chart is modified */
  onConfigChange?: (config: ChartConfig) => void;
  /** Optional CSS class */
  className?: string;
}

/**
 * Integrated visualization panel with controls
 */
export const VisualizationPanel: React.FC<VisualizationPanelProps> = ({
  initialConfig,
  onConfigChange,
  className = '',
}) => {
  const [config, setConfig] = useState<ChartConfig>(initialConfig);
  const [showLegend, setShowLegend] = useState(config.showLegend !== false);
  const [showGrid, setShowGrid] = useState(config.showGrid !== false);
  const [isExporting, setIsExporting] = useState(false);

  // Sanitize strings before logging to avoid log injection (CWE-117)
  const sanitizeForLog = (value: unknown, maxLen = 300) => {
    try {
      if (value == null) return '';
      const s = String(value);
      const cleaned = s.replace(/\s+/g, ' ').replace(/[^\x20-\x7E]/g, '');
      return cleaned.length > maxLen ? cleaned.slice(0, maxLen) + '...' : cleaned;
    } catch {
      return '';
    }
  };

  // Analyze data for available chart types (memoized to avoid re-computation on each render)
  const analysis = useMemo(() => analyzeData(config.datasets), [config.datasets]);
  const availableTypes: ChartType[] = useMemo(() => analysis.recommendations.map(r => r.type), [analysis.recommendations]);

  // Handle chart type change
  const handleTypeChange = (type: ChartType) => {
    const newConfig = { ...config, type };
    setConfig(newConfig);
    onConfigChange?.(newConfig);
  };

  // Handle export
  const handleExport = async (format: ExportFormat) => {
    setIsExporting(true);
    try {
      const chartElement = document.getElementById(`chart-${config.id}`);
      if (!chartElement) {
        // eslint-disable-next-line no-console
        console.error('Chart element not found');
        return;
      }

      const result = await exportChart(chartElement, config, {
        format,
        filename: `${config.id}_${Date.now()}`,
        width: 1920,
        height: 1080,
        scale: 2,
        includeData: format === 'json',
      });

      if (result.success) {
        // eslint-disable-next-line no-console
        console.log(`Exported as ${sanitizeForLog(result.format)}:`, sanitizeForLog(result.filename));
      } else {
        // eslint-disable-next-line no-console
        console.error('Export failed:', sanitizeForLog(result.error));
      }
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Export error:', sanitizeForLog((error as any)?.message || error));
    } finally {
      setIsExporting(false);
    }
  };

  // Handle reset view
  const handleReset = () => {
    // Reset will be handled by Plotly internally via keyboard shortcut
    console.log('Reset view');
  };

  // Toggle legend visibility
  const handleToggleLegend = () => {
    const newShowLegend = !showLegend;
    setShowLegend(newShowLegend);
    setConfig({ ...config, showLegend: newShowLegend });
  };

  // Toggle grid visibility
  const handleToggleGrid = () => {
    const newShowGrid = !showGrid;
    setShowGrid(newShowGrid);
    setConfig({ ...config, showGrid: newShowGrid });
  };

  // Handle chart interactions
  const handleInteraction = (event: ChartInteraction) => {
    try {
      // eslint-disable-next-line no-console
      console.log('Chart interaction:', sanitizeForLog(event.type));

      if (event.type === 'click' && event.points) {
        // Show point details (sanitize any labels)
        event.points.forEach(point => {
          // eslint-disable-next-line no-console
          console.log(`Clicked: ${sanitizeForLog(point.label || 'Point')} (${point.x}, ${point.y})`);
        });
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Interaction handler error:', sanitizeForLog((err as any)?.message || err));
    }
  };

  // Handle chart errors
  const handleError = (error: ChartError) => {
    // Sanitize and forward
    // eslint-disable-next-line no-console
    console.error('Chart error:', sanitizeForLog(error.code), sanitizeForLog(error.message));
    if (error.details) {
      // eslint-disable-next-line no-console
      console.error('Details:', sanitizeForLog(JSON.stringify(error.details)));
    }
    // Optionally forward to parent
    if (onConfigChange) {
      try {
        onConfigChange({ ...config });
      } catch {
        // swallow to avoid UI breakage
      }
    }
  };

  return (
    <div className={`visualization-panel ${className}`}>
      {/* Controls */}
      <ChartControls
        chartId={config.id}
        availableTypes={availableTypes.length > 0 ? availableTypes : ['line', 'bar', 'scatter']}
        currentType={config.type}
        exportFormats={['png', 'svg', 'json', 'csv']}
        onTypeChange={handleTypeChange}
        onExport={handleExport}
        onReset={handleReset}
        onToggleLegend={handleToggleLegend}
        onToggleGrid={handleToggleGrid}
        disabled={isExporting}
      />

      {/* Chart */}
      <div id={`chart-${config.id}`} className="chart-container">
        <ChartRenderer
          config={config}
          onInteraction={handleInteraction}
          onError={handleError}
          performanceSettings={{
            enabled: true,
            downsampleThreshold: 1000,
            downsampleMethod: 'lttb',
            cacheResults: true,
            debounceMs: 100,
          }}
          accessibilityConfig={{
            enabled: true,
            keyboardNavigation: true,
            screenReaderSupport: true,
            announceChanges: true,
            describePlot: true,
          }}
          className="rounded-lg shadow-lg"
        />
      </div>

      {/* Export status */}
      {isExporting && (
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p className="text-sm text-blue-700 dark:text-blue-300">
            ⏳ Exporting chart...
          </p>
        </div>
      )}

      {/* Data summary */}
      <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Data Summary
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-500 dark:text-gray-400">Datasets:</span>
            <span className="ml-2 font-medium text-gray-900 dark:text-gray-100">
              {config.datasets.length}
            </span>
          </div>
          <div>
            <span className="text-gray-500 dark:text-gray-400">Points:</span>
            <span className="ml-2 font-medium text-gray-900 dark:text-gray-100">
              {config.datasets.reduce((sum, d) => sum + d.data.length, 0)}
            </span>
          </div>
          <div>
            <span className="text-gray-500 dark:text-gray-400">Type:</span>
            <span className="ml-2 font-medium text-gray-900 dark:text-gray-100">
              {config.type}
            </span>
          </div>
          <div>
            <span className="text-gray-500 dark:text-gray-400">Theme:</span>
            <span className="ml-2 font-medium text-gray-900 dark:text-gray-100">
              {config.theme || 'light'}
            </span>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <h4 className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-2">
            💡 Recommended Chart Types
          </h4>
          <ul className="space-y-1 text-sm">
            {analysis.recommendations.slice(0, 3).map((rec, idx) => (
              <li key={idx} className="text-blue-600 dark:text-blue-400">
                <strong>{rec.type}</strong> ({Math.round(rec.confidence * 100)}%): {rec.reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default VisualizationPanel;

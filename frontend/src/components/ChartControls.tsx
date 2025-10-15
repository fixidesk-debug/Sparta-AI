/**
 * ChartControls Component for Sparta AI
 * 
 * Control panel for chart interactions: type selection, export, reset, etc.
 */

import React from 'react';
import { ChartControlsProps, ChartType, ExportFormat } from '../types/visualization';

/**
 * Chart type display names
 */
const CHART_TYPE_NAMES: Record<ChartType, string> = {
  line: 'Line Chart',
  bar: 'Bar Chart',
  scatter: 'Scatter Plot',
  histogram: 'Histogram',
  box: 'Box Plot',
  violin: 'Violin Plot',
  heatmap: 'Heatmap',
  correlation: 'Correlation Matrix',
  pie: 'Pie Chart',
  area: 'Area Chart',
  bubble: 'Bubble Chart',
  candlestick: 'Candlestick',
  waterfall: 'Waterfall',
  funnel: 'Funnel',
  sunburst: 'Sunburst',
  treemap: 'Treemap',
  sankey: 'Sankey Diagram',
  custom: 'Custom',
};

/**
 * Export format icons
 */
const EXPORT_ICONS: Record<ExportFormat, string> = {
  png: '🖼️',
  svg: '📐',
  pdf: '📄',
  json: '📊',
  csv: '📑',
};

export const ChartControls: React.FC<ChartControlsProps> = ({
  chartId,
  availableTypes,
  currentType,
  exportFormats,
  onTypeChange,
  onExport,
  onReset,
  onToggleLegend,
  onToggleGrid,
  disabled = false,
}) => {
  return (
    <div className="chart-controls bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
      <div className="flex flex-wrap items-center gap-4">
        {/* Chart Type Selector */}
        <div className="flex items-center gap-2">
          <label
            htmlFor={`chart-type-${chartId}`}
            className="text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Chart Type:
          </label>
          <select
            id={`chart-type-${chartId}`}
            value={currentType}
            onChange={(e) => onTypeChange(e.target.value as ChartType)}
            disabled={disabled}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {availableTypes.map((type) => (
              <option key={type} value={type}>
                {CHART_TYPE_NAMES[type]}
              </option>
            ))}
          </select>
        </div>

        {/* Divider */}
        <div className="h-8 w-px bg-gray-300 dark:bg-gray-600" />

        {/* Export Buttons */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Export:
          </span>
          {exportFormats.map((format) => (
            <button
              key={format}
              onClick={() => onExport(format)}
              disabled={disabled}
              className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500"
              title={`Export as ${format.toUpperCase()}`}
              aria-label={`Export as ${format.toUpperCase()}`}
            >
              <span className="mr-1">{EXPORT_ICONS[format]}</span>
              {format.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Divider */}
        <div className="h-8 w-px bg-gray-300 dark:bg-gray-600" />

        {/* View Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={onToggleLegend}
            disabled={disabled}
            className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500"
            title="Toggle Legend"
            aria-label="Toggle Legend"
          >
            📊 Legend
          </button>
          <button
            onClick={onToggleGrid}
            disabled={disabled}
            className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500"
            title="Toggle Grid"
            aria-label="Toggle Grid"
          >
            📏 Grid
          </button>
          <button
            onClick={onReset}
            disabled={disabled}
            className="px-3 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            title="Reset View"
            aria-label="Reset View"
          >
            🔄 Reset
          </button>
        </div>
      </div>

      {/* Keyboard shortcuts hint */}
      <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          <strong>Keyboard Shortcuts:</strong> R = Reset View | E = Export PNG
        </p>
      </div>
    </div>
  );
};

export default ChartControls;

/**
 * ChartDisplay Component
 * Interactive data visualization using Plotly
 */

import React, { useState, useCallback, useMemo } from 'react';
import Plot from 'react-plotly.js';
import { Visualization } from '../types/chat';

interface ChartDisplayProps {
  visualization: Visualization;
  className?: string;
  onExport?: (format: 'png' | 'svg' | 'json') => void;
}

export const ChartDisplay: React.FC<ChartDisplayProps> = ({
  visualization,
  className = '',
  onExport,
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Parse chart config
  const chartConfig = useMemo(() => {
    try {
      return typeof visualization.config === 'string'
        ? JSON.parse(visualization.config)
        : visualization.config;
    } catch (err) {
      setError('Failed to parse chart configuration');
      return null;
    }
  }, [visualization.config]);

  // Handle export
  const handleExport = useCallback(
    (format: 'png' | 'svg' | 'json') => {
      if (onExport) {
        onExport(format);
      } else {
        // Default export using Plotly's download feature
        const filename = `${visualization.title || 'chart'}.${format}`;
        // This would trigger Plotly's built-in export
        console.log(`Exporting chart as ${filename}`);
      }
    },
    [onExport, visualization.title]
  );

  const toggleFullscreen = useCallback(() => {
    setIsFullscreen((prev) => !prev);
  }, []);

  if (error || !chartConfig) {
    return (
      <div
        className={`chart-error p-4 bg-red-50 border border-red-200 rounded-lg ${className}`}
        role="alert"
      >
        <div className="flex items-start gap-2">
          <svg
            className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <h4 className="font-semibold text-red-800">Chart Error</h4>
            <p className="text-sm text-red-700">{error || 'Unable to display chart'}</p>
          </div>
        </div>
      </div>
    );
  }

  const containerClass = isFullscreen
    ? 'fixed inset-0 z-50 bg-white p-4'
    : `chart-display bg-white border border-gray-200 rounded-lg p-4 ${className}`;

  return (
    <div className={containerClass}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          {visualization.title && (
            <h3 className="text-lg font-semibold text-gray-900">{visualization.title}</h3>
          )}
          <p className="text-sm text-gray-500 capitalize">{visualization.type} chart</p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          {/* Export dropdown */}
          <div className="relative group">
            <button
              type="button"
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Export chart"
              title="Export chart"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
            </button>

            {/* Dropdown menu */}
            <div className="absolute right-0 mt-2 w-32 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <button
                type="button"
                onClick={() => handleExport('png')}
                className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-t-lg focus:outline-none focus:bg-gray-100"
              >
                Export as PNG
              </button>
              <button
                type="button"
                onClick={() => handleExport('svg')}
                className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 focus:outline-none focus:bg-gray-100"
              >
                Export as SVG
              </button>
              <button
                type="button"
                onClick={() => handleExport('json')}
                className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-b-lg focus:outline-none focus:bg-gray-100"
              >
                Export as JSON
              </button>
            </div>
          </div>

          {/* Fullscreen toggle */}
          <button
            type="button"
            onClick={toggleFullscreen}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          >
            {isFullscreen ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
                />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="chart-container">
        <Plot
          data={chartConfig.data || []}
          layout={{
            ...chartConfig.layout,
            autosize: true,
            responsive: true,
            height: isFullscreen ? window.innerHeight - 150 : 400,
          }}
          config={{
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            responsive: true,
          }}
          style={{ width: '100%' }}
          useResizeHandler
        />
      </div>

      {/* Footer info */}
      {visualization.metadata && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">{visualization.metadata}</p>
        </div>
      )}
    </div>
  );
};

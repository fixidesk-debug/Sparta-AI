/**
 * ChartRenderer Component for Sparta AI
 * 
 * Main visualization component that renders interactive charts using Plotly.js
 * with comprehensive features including theming, accessibility, and performance optimization
 */

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
// @ts-ignore - plotly.js will be installed via npm
import Plotly from 'plotly.js-dist-min';
import {
  ChartRendererProps,
  ChartInteraction,
  ChartError,
  PerformanceSettings,
  ChartDescription,
} from '../types/visualization';
import { convertToPlotly } from '../utils/plotlyConverter';
import { downsampleData, analyzeData } from '../utils/dataProcessor';
import { exportChart } from '../utils/exportManager';
import './ChartRenderer.css';

/**
 * Default performance settings
 */
const DEFAULT_PERFORMANCE: PerformanceSettings = {
  enabled: true,
  downsampleThreshold: 1000,
  downsampleMethod: 'lttb',
  lazyLoad: false,
  virtualizeData: false,
  cacheResults: true,
  debounceMs: 100,
};

/**
 * Main ChartRenderer component
 */
export const ChartRenderer: React.FC<ChartRendererProps> = ({
  config,
  className = '',
  style = {},
  onInteraction,
  onError,
  onLoad,
  onExport,
  performanceSettings,
  accessibilityConfig,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ChartError | null>(null);
  const [isRendered, setIsRendered] = useState(false);

  // Merge performance settings
  const perfSettings = useMemo(
    () => ({ ...DEFAULT_PERFORMANCE, ...performanceSettings }),
    [performanceSettings]
  );

  // Process and optimize data
  const processedConfig = useMemo(() => {
    const newConfig = { ...config };

    // Apply downsampling if needed
    if (perfSettings.enabled) {
      newConfig.datasets = config.datasets.map(dataset => {
        if (dataset.data.length > perfSettings.downsampleThreshold) {
          return {
            ...dataset,
            data: downsampleData(
              dataset.data,
              perfSettings.downsampleThreshold,
              perfSettings.downsampleMethod
            ),
          };
        }
        return dataset;
      });
    }

    return newConfig;
  }, [config, perfSettings]);

  // Generate chart description for accessibility
  const chartDescription = useMemo<ChartDescription>(() => {
    const analysis = analyzeData(processedConfig.datasets);
    const datasetCount = processedConfig.datasets.length;
    const pointCount = analysis.pointCount;

    return {
      title: config.title || 'Chart visualization',
      summary: `A ${config.type} chart with ${datasetCount} dataset${datasetCount > 1 ? 's' : ''} and ${pointCount} data points.`,
      dataDescription: processedConfig.datasets.map(d => `${d.name}: ${d.data.length} points`).join(', '),
      statisticalSummary: analysis.distribution ? `Distribution: ${analysis.distribution}` : undefined,
      trendDescription: analysis.recommendations[0]?.reason,
    };
  }, [config, processedConfig]);

  // Convert to Plotly format
  const plotlyData = useMemo(() => {
    try {
      return convertToPlotly(processedConfig);
    } catch (err) {
      const chartError: ChartError = {
        code: 'CONVERSION_ERROR',
        message: 'Failed to convert chart data',
        details: err instanceof Error ? err.message : 'Unknown error',
        timestamp: Date.now(),
        recoverable: false,
      };
      setError(chartError);
      onError?.(chartError);
      return null;
    }
  }, [processedConfig, onError]);

  // Render chart
  const renderChart = useCallback(async () => {
    if (!chartRef.current || !plotlyData) return;

    try {
      setIsLoading(true);
      setError(null);

      // Create new plot
      await Plotly.newPlot(
        chartRef.current,
        plotlyData.data,
        plotlyData.layout,
        plotlyData.config
      );

      // Add event listeners
      if (config.clickEnabled !== false && onInteraction) {
        (chartRef.current as any).on('plotly_click', (data: { points: unknown[] }) => {
          const interaction: ChartInteraction = {
            type: 'click',
            points: data.points.map((p: unknown) => {
              const point = p as Record<string, unknown>;
              return {
                datasetIndex: (point.curveNumber as number) || 0,
                pointIndex: (point.pointIndex as number) || 0,
                x: point.x as number | string | Date,
                y: point.y as number | string | Date,
                label: (point.data as { name?: string })?.name,
              };
            }),
            timestamp: Date.now(),
          };
          onInteraction(interaction);
        });
      }

      if (config.hoverEnabled !== false && onInteraction) {
        (chartRef.current as any).on('plotly_hover', (data: { points: unknown[] }) => {
          const interaction: ChartInteraction = {
            type: 'hover',
            points: data.points.map((p: unknown) => {
              const point = p as Record<string, unknown>;
              return {
                datasetIndex: (point.curveNumber as number) || 0,
                pointIndex: (point.pointIndex as number) || 0,
                x: point.x as number | string | Date,
                y: point.y as number | string | Date,
              };
            }),
            timestamp: Date.now(),
          };
          onInteraction(interaction);
        });
      }

      // Relayout event for zoom/pan
      (chartRef.current as any).on('plotly_relayout', (data: Record<string, unknown>) => {
        if (onInteraction && (data['xaxis.range[0]'] || data['yaxis.range[0]'])) {
          const interaction: ChartInteraction = {
            type: 'zoom',
            range: {
              x: data['xaxis.range[0]'] !== undefined
                ? [data['xaxis.range[0]'] as string | number, data['xaxis.range[1]'] as string | number]
                : undefined,
              y: data['yaxis.range[0]'] !== undefined
                ? [data['yaxis.range[0]'] as string | number, data['yaxis.range[1]'] as string | number]
                : undefined,
            },
            timestamp: Date.now(),
          };
          onInteraction(interaction);
        }
      });

      setIsRendered(true);
      setIsLoading(false);
      onLoad?.();
    } catch (err) {
      const chartError: ChartError = {
        code: 'RENDER_ERROR',
        message: 'Failed to render chart',
        details: err instanceof Error ? err.message : 'Unknown error',
        timestamp: Date.now(),
        recoverable: true,
        suggestion: 'Try refreshing the page or checking your data format',
      };
      setError(chartError);
      setIsLoading(false);
      onError?.(chartError);
    }
  }, [chartRef, plotlyData, config, onInteraction, onLoad, onError]);

  // Initial render
  useEffect(() => {
    const element = chartRef.current;
    renderChart();

    // Cleanup
    return () => {
      if (element && isRendered) {
        Plotly.purge(element);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [renderChart, isRendered]);

  // Handle window resize
  useEffect(() => {
    if (!chartRef.current || !isRendered) return;

    const handleResize = () => {
      if (chartRef.current) {
        Plotly.Resizer.resize(chartRef.current);
      }
    };

    // Debounce resize
    let timeoutId: NodeJS.Timeout;
    const debouncedResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(handleResize, perfSettings.debounceMs);
    };

    window.addEventListener('resize', debouncedResize);

    return () => {
      window.removeEventListener('resize', debouncedResize);
      clearTimeout(timeoutId);
    };
  }, [isRendered, perfSettings.debounceMs]);

  // Keyboard navigation for accessibility
  useEffect(() => {
    if (!chartRef.current || !accessibilityConfig?.keyboardNavigation) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (!onInteraction) return;

      switch (e.key) {
        case 'r':
        case 'R':
          // Reset zoom
          if (chartRef.current) {
            Plotly.relayout(chartRef.current, {
              'xaxis.autorange': true,
              'yaxis.autorange': true,
            });
            onInteraction({
              type: 'reset',
              timestamp: Date.now(),
            });
          }
          break;

        case 'e':
        case 'E':
          // Export chart
          if (chartRef.current && onExport) {
            exportChart(chartRef.current, config, {
              format: 'png',
              filename: config.id,
            }).then(onExport);
          }
          break;
      }
    };

    chartRef.current.addEventListener('keydown', handleKeyDown);
    const currentRef = chartRef.current;

    return () => {
      currentRef?.removeEventListener('keydown', handleKeyDown);
    };
  }, [accessibilityConfig, onInteraction, onExport, config]);

  // Compute dimensions
  const dimensions = {
    width: config.width || '100%',
    height: config.height || '500px',
  };

  // Render error state
  if (error && !error.recoverable) {
    return (
      <div
        className={`chart-error ${className}`}
        style={style}
        role="alert"
        aria-live="assertive"
      >
        <div className="p-8 text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">
            Failed to Render Chart
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-2">{error.message}</p>
          {error.details && (
            <p className="text-sm text-gray-500 dark:text-gray-500 mb-4">
              {error.details}
            </p>
          )}
          {error.suggestion && (
            <p className="text-sm text-blue-600 dark:text-blue-400">
              💡 {error.suggestion}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`chart-renderer relative ${className}`}
      style={{ ...style, ...dimensions }}
      role="img"
      aria-label={config.ariaLabel || chartDescription.title}
      aria-describedby={`chart-desc-${config.id}`}
      tabIndex={accessibilityConfig?.keyboardNavigation ? 0 : -1}
    >
      {/* Loading overlay */}
      {isLoading && (
        <div
          className="absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 z-10"
          role="status"
          aria-live="polite"
        >
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading chart...</p>
          </div>
        </div>
      )}

      {/* Recoverable error overlay */}
      {error && error.recoverable && (
        <div
          className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 dark:border-yellow-600 text-yellow-800 dark:text-yellow-200 px-4 py-2 rounded-lg shadow-lg z-20"
          role="alert"
        >
          <p className="text-sm font-medium">{error.message}</p>
        </div>
      )}

      {/* Chart container */}
      <div
        ref={chartRef}
        className="w-full h-full chart-container-min-height"
      />

      {/* Hidden description for screen readers */}
      <div id={`chart-desc-${config.id}`} className="sr-only">
        <p>{chartDescription.summary}</p>
        <p>{chartDescription.dataDescription}</p>
        {chartDescription.statisticalSummary && <p>{chartDescription.statisticalSummary}</p>}
        {chartDescription.trendDescription && <p>{chartDescription.trendDescription}</p>}
        {chartDescription.keyFindings && (
          <ul>
            {chartDescription.keyFindings.map((finding, idx) => (
              <li key={idx}>{finding}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ChartRenderer;

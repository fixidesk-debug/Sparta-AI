/**
 * Plotly Data Converter for Sparta AI
 * 
 * Converts standardized chart configurations to Plotly.js format
 */

import { Data as PlotData, Layout, Config } from 'plotly.js';
import {
  ChartConfig,
  Dataset,
  PlotlyData,
  ChartTheme,
} from '../types/visualization';
import { getTheme, getColorScheme } from './chartThemes';

/**
 * Convert chart configuration to Plotly format
 */
export function convertToPlotly(config: ChartConfig): PlotlyData {
  try {
    const theme = getTheme(config.theme || 'light');
    const colorPalette = config.colorScheme
      ? getColorScheme(config.colorScheme)
      : theme.colorPalette;

    // Convert datasets to Plotly traces
    const data = config.datasets.map((dataset, index) =>
      convertDatasetToTrace(dataset, config.type, colorPalette[index % colorPalette.length], theme)
    );

    // Build layout
    const layout = buildLayout(config, theme);

    // Build config
    const plotConfig = buildConfig(config);

    return { data, layout, config: plotConfig };
  } catch (err) {
    // Fail-safe: return empty plot but surface error via console and rethrow for upstream handling
    console.error('Error converting to Plotly format', err);
    throw err;
  }
}

/**
 * Convert dataset to Plotly trace
 */
function convertDatasetToTrace(
  dataset: Dataset,
  chartType: string,
  defaultColor: string,
  theme: ChartTheme
): Partial<PlotData> {
  const baseTrace: Partial<PlotData> = {
    name: dataset.name,
    visible: dataset.visible !== false ? true : ('legendonly' as const),
    marker: {
      color: dataset.color || defaultColor,
    },
  };

  // Extract x and y values
  const xValues = dataset.data.map(d => d.x);
  const yValues = dataset.data.map(d => d.y);
  const labels = dataset.data.map(d => d.label || '');

  switch (chartType) {
    case 'line':
      return {
        ...baseTrace,
        type: 'scatter',
        mode: 'lines',
        x: xValues,
        y: yValues,
        line: {
          color: dataset.color || defaultColor,
          width: 2,
        },
      };

    case 'scatter':
      return {
        ...baseTrace,
        type: 'scatter',
        mode: 'markers',
        x: xValues,
        y: yValues,
        marker: {
          ...baseTrace.marker,
          size: dataset.data.map(d => d.size || 8),
        },
      };

    case 'bar':
      return {
        ...baseTrace,
        type: 'bar',
        x: xValues,
        y: yValues,
        text: labels,
      };

    case 'histogram':
      return {
        ...baseTrace,
        type: 'histogram',
        x: yValues, // Use y values for histogram distribution
      } as Partial<PlotData>;

    case 'box':
      return {
        ...baseTrace,
        type: 'box',
        y: yValues,
        boxmean: 'sd',
      };

    case 'violin':
      return {
        ...baseTrace,
        type: 'violin',
        y: yValues,
      } as Partial<PlotData>;

    case 'heatmap':
      return {
        ...baseTrace,
        type: 'heatmap',
        z: reshapeDataForHeatmap(dataset.data),
        colorscale: 'Viridis',
        showscale: true,
      };

    case 'correlation':
      return {
        ...baseTrace,
        type: 'heatmap',
        z: reshapeDataForHeatmap(dataset.data),
        colorscale: 'RdBu',
        showscale: true,
        texttemplate: '%{z:.2f}',
        textfont: { size: 10 },
      } as Partial<PlotData>;

    case 'pie':
      return {
        ...baseTrace,
        type: 'pie',
        labels: labels.length > 0 ? labels : xValues,
        values: yValues,
        textinfo: 'label+percent',
        textposition: 'auto',
      };

    case 'area':
      return {
        ...baseTrace,
        type: 'scatter',
        mode: 'lines',
        x: xValues,
        y: yValues,
        fill: 'tozeroy',
        line: {
          color: dataset.color || defaultColor,
          width: 2,
        },
      };

    case 'bubble':
      return {
        ...baseTrace,
        type: 'scatter',
        mode: 'markers',
        x: xValues,
        y: yValues,
        marker: {
          ...baseTrace.marker,
          size: dataset.data.map(d => (d.z || 10) as number),
          sizemode: 'diameter',
          sizeref: 2,
        },
      };

    case 'waterfall':
      return {
        ...baseTrace,
        type: 'waterfall',
        x: xValues,
        y: yValues,
        text: labels,
        textposition: 'outside',
      };

    case 'funnel':
      return {
        ...baseTrace,
        type: 'funnel',
        x: yValues,
        y: xValues,
        text: labels,
      };

    case 'sunburst':
      return {
        ...baseTrace,
        type: 'sunburst',
        labels: labels,
        parents: dataset.data.map(d => d.metadata?.parent as string || ''),
        values: yValues,
      };

    case 'treemap':
      return {
        ...baseTrace,
        type: 'treemap',
        labels: labels,
        parents: dataset.data.map(d => d.metadata?.parent as string || ''),
        values: yValues,
      };

    default:
      return {
        ...baseTrace,
        type: 'scatter',
        mode: 'markers',
        x: xValues,
        y: yValues,
      };
  }
}

/**
 * Reshape data array into 2D matrix for heatmap
 */
function reshapeDataForHeatmap(data: Array<{ x: unknown; y: unknown; z?: number }>): number[][] {
  if (!data || data.length === 0) return [];

  // If z values exist, create matrix from x, y, z
  if (data[0].z !== undefined) {
    const xValues = Array.from(new Set(data.map(d => d.x)));
    const yValues = Array.from(new Set(data.map(d => d.y)));

    // Build quick lookup map for (x,y) -> z
    const lookup = new Map<string, number>();
    for (const point of data) {
      const key = `${String(point.x)}::${String(point.y)}`;
      lookup.set(key, point.z ?? 0);
    }

    const matrix: number[][] = new Array(yValues.length);
    for (let i = 0; i < yValues.length; i++) {
      const yVal = yValues[i];
      const row: number[] = new Array(xValues.length);
      for (let j = 0; j < xValues.length; j++) {
        const xVal = xValues[j];
        const key = `${String(xVal)}::${String(yVal)}`;
        row[j] = lookup.get(key) ?? 0;
      }
      matrix[i] = row;
    }

    return matrix;
  }

  // Otherwise, assume data is already in matrix format
  // Group by y value (row) in insertion order
  const grouped: Map<string, number[]> = new Map();
  for (const point of data) {
    const key = String(point.y);
    const arr = grouped.get(key) || [];
    arr.push(Number(point.x) || 0);
    if (!grouped.has(key)) grouped.set(key, arr);
  }

  return Array.from(grouped.values());
}

/**
 * Build Plotly layout from configuration
 */
function buildLayout(config: ChartConfig, theme: ChartTheme): Partial<Layout> {
  const { fontFamily, titleFontSize, fontSize, textColor, gridColor, axisColor, backgroundColor } = theme;

  const buildTitle = (text?: string) => text ? { text, font: { family: fontFamily, size: fontSize, color: textColor } } : undefined;

  const layout: Partial<Layout> = {
    title: config.title ? {
      text: config.title,
      font: {
        family: fontFamily,
        size: titleFontSize,
        color: textColor,
      },
    } : undefined,

    xaxis: {
      title: buildTitle(config.xAxisLabel),
      showgrid: config.showGrid !== false,
      gridcolor: gridColor,
      color: axisColor,
      zeroline: true,
      visible: config.showAxes !== false,
    },

    yaxis: {
      title: buildTitle(config.yAxisLabel),
      showgrid: config.showGrid !== false,
      gridcolor: gridColor,
      color: axisColor,
      zeroline: true,
      visible: config.showAxes !== false,
    },

    showlegend: config.showLegend !== false,
    legend: {
      font: {
        family: theme.fontFamily,
        size: theme.fontSize,
        color: theme.textColor,
      },
    },

    plot_bgcolor: backgroundColor,
    paper_bgcolor: backgroundColor,

    font: {
      family: fontFamily,
      size: fontSize,
      color: textColor,
    },

    autosize: true,

    margin: {
      l: 60,
      r: 30,
      t: config.title ? 80 : 40,
      b: 60,
    },

    hovermode: config.hoverEnabled !== false ? 'closest' : false,

    dragmode: config.zoomEnabled !== false ? 'zoom' : false,
  };

  // Apply custom layout overrides
  if (config.customLayout) {
    Object.assign(layout, config.customLayout);
  }

  // Add annotations
  if (config.annotations && config.annotations.length > 0) {
    layout.annotations = config.annotations.map(ann => ({
      x: ann.x,
      y: ann.y,
      text: ann.text,
      showarrow: ann.showarrow !== false,
      arrowcolor: ann.color,
      font: {
        color: ann.color || theme.textColor,
      },
    }));
  }

  return layout;
}

/**
 * Build Plotly config
 */
function buildConfig(config: ChartConfig): Partial<Config> {
  const plotConfig: Partial<Config> = {
    responsive: true,
    displayModeBar: config.interactive !== false,
    displaylogo: false,
    
    modeBarButtonsToRemove: [],
    
    toImageButtonOptions: {
      format: 'png',
      filename: config.id,
      height: 800,
      width: 1200,
      scale: 2,
    },
  };

  // Remove interaction buttons if not enabled
  if (!config.zoomEnabled) {
    plotConfig.modeBarButtonsToRemove?.push('zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d');
  }

  if (!config.panEnabled) {
    plotConfig.modeBarButtonsToRemove?.push('pan2d');
  }

  // Apply custom config overrides
  if (config.customConfig) {
    Object.assign(plotConfig, config.customConfig);
  }

  return plotConfig;
}

/**
 * Create default chart configuration
 */
export function createDefaultConfig(type: string): Partial<ChartConfig> {
  return {
    type: type as ChartConfig['type'],
    interactive: true,
    zoomEnabled: true,
    panEnabled: true,
    hoverEnabled: true,
    showLegend: true,
    showGrid: true,
    showAxes: true,
    showTooltips: true,
    theme: 'light',
    colorScheme: 'default',
  };
}

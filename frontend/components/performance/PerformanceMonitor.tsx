import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Activity,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Settings,
  Maximize2,
  X,
  BarChart2,
  PieChart,
  Zap,
  Database,
  Clock,
  Cpu,
  HardDrive,
  Wifi,
} from '../icons';
import './PerformanceMonitor.scss';

// =====================
// Type Definitions
// =====================

export type WidgetSize = '1x1' | '2x1' | '2x2' | '1x2';

export type WidgetState = 'normal' | 'warning' | 'critical' | 'offline' | 'loading' | 'error' | 'success' | 'updated';

export type ChartType = 'line' | 'area' | 'bar' | 'gauge' | 'sparkline' | 'heatmap' | 'progress-ring' | 'timeline';

export type TrendDirection = 'up' | 'down' | 'neutral';

export interface MetricData {
  value: number;
  unit?: string;
  label: string;
  trend?: TrendDirection;
  trendValue?: number;
  status?: 'good' | 'warning' | 'critical';
  threshold?: number;
}

export interface ChartDataPoint {
  timestamp: number;
  value: number;
  label?: string;
}

export interface TimelineEvent {
  timestamp: number;
  label: string;
  type: 'milestone' | 'event' | 'alert';
}

export interface Widget {
  id: string;
  title: string;
  type: 'metric' | 'chart';
  chartType?: ChartType;
  size: WidgetSize;
  state: WidgetState;
  position: { x: number; y: number };
  data?: MetricData | ChartDataPoint[] | TimelineEvent[];
  icon?: React.ReactNode;
  color?: string;
  refreshInterval?: number;
  lastUpdated?: number;
}

export interface PerformanceMonitorProps {
  widgets?: Widget[];
  onWidgetUpdate?: (widgetId: string, data: any) => void;
  onWidgetMove?: (widgetId: string, position: { x: number; y: number }) => void;
  onWidgetResize?: (widgetId: string, size: WidgetSize) => void;
  onWidgetRemove?: (widgetId: string) => void;
  onWidgetRefresh?: (widgetId: string) => void;
  onWidgetSettings?: (widgetId: string) => void;
  enableDragDrop?: boolean;
  enableResize?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
  theme?: 'dark' | 'light';
}

// =====================
// Helper Functions
// =====================

const formatValue = (value: number, decimals: number = 2): string => {
  if (value >= 1000000) return `${(value / 1000000).toFixed(decimals)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(decimals)}K`;
  return value.toFixed(decimals);
};

const getStatusColor = (status?: 'good' | 'warning' | 'critical'): string => {
  switch (status) {
    case 'good': return 'var(--color-success)';
    case 'warning': return 'var(--color-warning)';
    case 'critical': return 'var(--color-error)';
    default: return 'var(--color-primary)';
  }
};

const getTrendIcon = (trend?: TrendDirection) => {
  switch (trend) {
    case 'up': return <TrendingUp size={16} />;
    case 'down': return <TrendingDown size={16} />;
    default: return null;
  }
};

const getWidgetGridSize = (size: WidgetSize): string => {
  switch (size) {
    case '1x1': return 'grid-1x1';
    case '2x1': return 'grid-2x1';
    case '2x2': return 'grid-2x2';
    case '1x2': return 'grid-1x2';
    default: return 'grid-1x1';
  }
};

// =====================
// Chart Components
// =====================

const LineChart: React.FC<{ data: ChartDataPoint[]; color: string }> = ({ data, color }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data || data.length === 0) return;

    const svg = svgRef.current;
    const width = svg.clientWidth;
    const height = svg.clientHeight;
    const padding = 20;

    const maxValue = Math.max(...data.map(d => d.value));
    const minValue = Math.min(...data.map(d => d.value));
    const range = maxValue - minValue || 1;

    const points = data.map((point, index) => {
      const x = (index / (data.length - 1)) * (width - padding * 2) + padding;
      const y = height - padding - ((point.value - minValue) / range) * (height - padding * 2);
      return `${x},${y}`;
    }).join(' ');

    const areaPoints = `${padding},${height - padding} ${points} ${width - padding},${height - padding}`;

    svg.innerHTML = `
      <defs>
        <linearGradient id="lineGradient-${color}" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:${color};stop-opacity:0.3" />
          <stop offset="100%" style="stop-color:${color};stop-opacity:0" />
        </linearGradient>
      </defs>
      <polygon points="${areaPoints}" fill="url(#lineGradient-${color})" class="chart-area" />
      <polyline points="${points}" fill="none" stroke="${color}" stroke-width="2" class="chart-line" />
      ${data.map((point, index) => {
        const x = (index / (data.length - 1)) * (width - padding * 2) + padding;
        const y = height - padding - ((point.value - minValue) / range) * (height - padding * 2);
        return `<circle cx="${x}" cy="${y}" r="3" fill="${color}" class="chart-point" />`;
      }).join('')}
    `;
  }, [data, color]);

  return <svg ref={svgRef} className="chart-svg" />;
};

const BarChart: React.FC<{ data: ChartDataPoint[]; color: string }> = ({ data, color }) => {
  const maxValue = Math.max(...data.map(d => d.value));

  return (
    <div className="bar-chart">
      {data.map((point, index) => (
        <div key={index} className="bar-container">
          <div
            className="bar"
            style={{
              height: `${(point.value / maxValue) * 100}%`,
              backgroundColor: color,
            }}
          >
            <div className="bar-value">{formatValue(point.value, 0)}</div>
          </div>
          {point.label && <div className="bar-label">{point.label}</div>}
        </div>
      ))}
    </div>
  );
};

const GaugeChart: React.FC<{ value: number; max: number; color: string }> = ({ value, max, color }) => {
  const percentage = (value / max) * 100;
  const angle = (percentage / 100) * 270 - 135;

  return (
    <div className="gauge-chart">
      <svg className="gauge-svg" viewBox="0 0 200 200">
        <defs>
          <linearGradient id={`gaugeGradient-${color}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style={{ stopColor: color, stopOpacity: 0.3 }} />
            <stop offset="100%" style={{ stopColor: color, stopOpacity: 1 }} />
          </linearGradient>
        </defs>
        <circle
          cx="100"
          cy="100"
          r="80"
          fill="none"
          stroke="var(--color-gray-700)"
          strokeWidth="12"
          strokeDasharray="502.4"
          strokeDashoffset="125.6"
          transform="rotate(-135 100 100)"
        />
        <circle
          cx="100"
          cy="100"
          r="80"
          fill="none"
          stroke={`url(#gaugeGradient-${color})`}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray="502.4"
          strokeDashoffset={502.4 - (502.4 * 0.75 * percentage) / 100}
          transform="rotate(-135 100 100)"
          className="gauge-arc"
        />
        <line
          x1="100"
          y1="100"
          x2="100"
          y2="30"
          stroke="var(--color-gray-100)"
          strokeWidth="3"
          strokeLinecap="round"
          transform={`rotate(${angle} 100 100)`}
          className="gauge-needle"
        />
        <circle cx="100" cy="100" r="8" fill="var(--color-gray-100)" />
      </svg>
      <div className="gauge-value">
        <span className="gauge-number">{formatValue(value)}</span>
        <span className="gauge-max">/ {formatValue(max)}</span>
      </div>
    </div>
  );
};

const ProgressRing: React.FC<{ value: number; max: number; color: string; label: string }> = ({
  value,
  max,
  color,
  label,
}) => {
  const percentage = (value / max) * 100;
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (circumference * percentage) / 100;

  return (
    <div className="progress-ring">
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle
          cx="60"
          cy="60"
          r="45"
          fill="none"
          stroke="var(--color-gray-700)"
          strokeWidth="10"
        />
        <circle
          cx="60"
          cy="60"
          r="45"
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          transform="rotate(-90 60 60)"
          className="progress-ring-circle"
        />
        <text
          x="60"
          y="55"
          textAnchor="middle"
          className="progress-ring-value"
          fill="var(--color-gray-100)"
        >
          {percentage.toFixed(0)}%
        </text>
        <text
          x="60"
          y="70"
          textAnchor="middle"
          className="progress-ring-label"
          fill="var(--color-gray-400)"
        >
          {label}
        </text>
      </svg>
    </div>
  );
};

const Sparkline: React.FC<{ data: ChartDataPoint[]; color: string }> = ({ data, color }) => {
  const maxValue = Math.max(...data.map(d => d.value));
  const minValue = Math.min(...data.map(d => d.value));
  const range = maxValue - minValue || 1;

  const points = data.map((point, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - ((point.value - minValue) / range) * 100;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg className="sparkline-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
};

const Timeline: React.FC<{ events: TimelineEvent[] }> = ({ events }) => {
  const sortedEvents = [...events].sort((a, b) => a.timestamp - b.timestamp);

  return (
    <div className="timeline-chart">
      {sortedEvents.map((event, index) => (
        <div key={index} className={`timeline-event timeline-${event.type}`}>
          <div className="timeline-marker" />
          <div className="timeline-content">
            <div className="timeline-label">{event.label}</div>
            <div className="timeline-time">
              {new Date(event.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// =====================
// Widget Component
// =====================

const WidgetComponent: React.FC<{
  widget: Widget;
  onRefresh?: () => void;
  onSettings?: () => void;
  onRemove?: () => void;
  onFullscreen?: () => void;
}> = ({ widget, onRefresh, onSettings, onRemove, onFullscreen }) => {
  const [isHovered, setIsHovered] = useState(false);

  const renderMetricCard = (data: MetricData) => (
    <div className="metric-card">
      <div className="metric-header">
        <div className="metric-icon">{widget.icon}</div>
        <div className="metric-label">{data.label}</div>
      </div>
      <div className="metric-body">
        <div className="metric-value-container">
          <span className="metric-value" style={{ color: getStatusColor(data.status) }}>
            {formatValue(data.value)}
          </span>
          {data.unit && <span className="metric-unit">{data.unit}</span>}
        </div>
        {data.trend && (
          <div className={`metric-trend trend-${data.trend}`}>
            {getTrendIcon(data.trend)}
            {data.trendValue && (
              <span className="metric-trend-value">
                {data.trendValue > 0 ? '+' : ''}{data.trendValue.toFixed(1)}%
              </span>
            )}
          </div>
        )}
      </div>
      {data.threshold && (
        <div className="metric-threshold">
          Threshold: {formatValue(data.threshold)}{data.unit}
        </div>
      )}
      {data.status && (
        <div className={`metric-status status-${data.status}`}>
          {data.status === 'good' ? 'Optimal' : data.status === 'warning' ? 'Warning' : 'Critical'}
        </div>
      )}
    </div>
  );

  const renderChart = (chartType: ChartType, data: any) => {
    const color = widget.color || 'var(--color-primary)';

    switch (chartType) {
      case 'line':
      case 'area':
        return <LineChart data={data as ChartDataPoint[]} color={color} />;
      case 'bar':
        return <BarChart data={data as ChartDataPoint[]} color={color} />;
      case 'gauge':
        const metricData = data as MetricData;
        return (
          <GaugeChart
            value={metricData.value}
            max={metricData.threshold || 100}
            color={color}
          />
        );
      case 'sparkline':
        return <Sparkline data={data as ChartDataPoint[]} color={color} />;
      case 'progress-ring':
        const ringData = data as MetricData;
        return (
          <ProgressRing
            value={ringData.value}
            max={ringData.threshold || 100}
            color={color}
            label={ringData.label}
          />
        );
      case 'timeline':
        return <Timeline events={data as TimelineEvent[]} />;
      default:
        return <div className="chart-placeholder">Chart type not supported</div>;
    }
  };

  const getStateIcon = () => {
    switch (widget.state) {
      case 'warning': return <AlertTriangle size={16} />;
      case 'critical': return <XCircle size={16} />;
      case 'success': return <CheckCircle size={16} />;
      case 'error': return <XCircle size={16} />;
      case 'offline': return <Wifi size={16} />;
      default: return null;
    }
  };

  return (
    <div
      className={`widget widget-${widget.state} ${getWidgetGridSize(widget.size)}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {widget.state === 'loading' && (
        <div className="widget-loading">
          <div className="skeleton-loader" />
        </div>
      )}

      {widget.state === 'offline' && (
        <div className="widget-overlay">
          <div className="widget-overlay-content">
            <Wifi size={32} />
            <p>No Data Available</p>
          </div>
        </div>
      )}

      {widget.state === 'error' && (
        <div className="widget-overlay">
          <div className="widget-overlay-content">
            <XCircle size={32} />
            <p>Error Loading Data</p>
            {onRefresh && (
              <button className="widget-retry-btn" onClick={onRefresh}>
                Retry
              </button>
            )}
          </div>
        </div>
      )}

      <div className="widget-header">
        <div className="widget-title-section">
          <h3 className="widget-title">{widget.title}</h3>
          {getStateIcon() && (
            <span className={`widget-state-icon state-${widget.state}`}>
              {getStateIcon()}
            </span>
          )}
        </div>
        {isHovered && (
          <div className="widget-actions">
            {onRefresh && (
              <button
                className="widget-action-btn"
                onClick={onRefresh}
                title="Refresh"
              >
                <RefreshCw size={16} />
              </button>
            )}
            {onSettings && (
              <button
                className="widget-action-btn"
                onClick={onSettings}
                title="Settings"
              >
                <Settings size={16} />
              </button>
            )}
            {onFullscreen && (
              <button
                className="widget-action-btn"
                onClick={onFullscreen}
                title="Fullscreen"
              >
                <Maximize2 size={16} />
              </button>
            )}
            {onRemove && (
              <button
                className="widget-action-btn widget-action-remove"
                onClick={onRemove}
                title="Remove"
              >
                <X size={16} />
              </button>
            )}
          </div>
        )}
      </div>

      <div className="widget-content">
        {widget.type === 'metric' && widget.data && renderMetricCard(widget.data as MetricData)}
        {widget.type === 'chart' && widget.chartType && widget.data && renderChart(widget.chartType, widget.data)}
      </div>

      {widget.lastUpdated && (
        <div className="widget-footer">
          <Clock size={12} />
          <span>Updated {new Date(widget.lastUpdated).toLocaleTimeString()}</span>
        </div>
      )}
    </div>
  );
};

// =====================
// Main Component
// =====================

const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  widgets: initialWidgets = [],
  onWidgetUpdate,
  onWidgetMove,
  onWidgetResize,
  onWidgetRemove,
  onWidgetRefresh,
  onWidgetSettings,
  enableDragDrop = false,
  enableResize = false,
  autoRefresh = true,
  refreshInterval = 5000,
  theme = 'dark',
}) => {
  const [widgets, setWidgets] = useState<Widget[]>(initialWidgets);
  const [fullscreenWidget, setFullscreenWidget] = useState<string | null>(null);

  useEffect(() => {
    setWidgets(initialWidgets);
  }, [initialWidgets]);

  // Auto-refresh logic
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      widgets.forEach(widget => {
        if (widget.refreshInterval && onWidgetUpdate) {
          onWidgetUpdate(widget.id, widget.data);
        }
      });
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, widgets, onWidgetUpdate]);

  const handleWidgetRefresh = useCallback((widgetId: string) => {
    setWidgets(prev =>
      prev.map(w =>
        w.id === widgetId
          ? { ...w, state: 'updated' as WidgetState, lastUpdated: Date.now() }
          : w
      )
    );

    // Reset updated state after animation
    setTimeout(() => {
      setWidgets(prev =>
        prev.map(w =>
          w.id === widgetId ? { ...w, state: 'normal' as WidgetState } : w
        )
      );
    }, 1000);

    onWidgetRefresh?.(widgetId);
  }, [onWidgetRefresh]);

  const handleWidgetRemove = useCallback((widgetId: string) => {
    setWidgets(prev => prev.filter(w => w.id !== widgetId));
    onWidgetRemove?.(widgetId);
  }, [onWidgetRemove]);

  const handleFullscreen = useCallback((widgetId: string) => {
    setFullscreenWidget(widgetId === fullscreenWidget ? null : widgetId);
  }, [fullscreenWidget]);

  return (
    <div className={`performance-monitor theme-${theme}`}>
      <div className="performance-monitor-grid">
        {widgets.map(widget => (
          <WidgetComponent
            key={widget.id}
            widget={widget}
            onRefresh={() => handleWidgetRefresh(widget.id)}
            onSettings={() => onWidgetSettings?.(widget.id)}
            onRemove={() => handleWidgetRemove(widget.id)}
            onFullscreen={() => handleFullscreen(widget.id)}
          />
        ))}
      </div>

      {fullscreenWidget && (
        <div className="fullscreen-overlay">
          <div className="fullscreen-widget">
            <button
              className="fullscreen-close"
              onClick={() => setFullscreenWidget(null)}
              aria-label="Close fullscreen"
              title="Close fullscreen"
            >
              <X size={24} />
            </button>
            <WidgetComponent
              widget={widgets.find(w => w.id === fullscreenWidget)!}
              onRefresh={() => handleWidgetRefresh(fullscreenWidget)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceMonitor;

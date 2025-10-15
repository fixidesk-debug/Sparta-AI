import React, { useState, useEffect } from 'react';
import PerformanceMonitor, {
  Widget,
  ChartDataPoint,
  TimelineEvent,
  MetricData,
} from './PerformanceMonitor';
import {
  Cpu,
  HardDrive,
  Activity,
  Database,
  Zap,
  Clock,
  Users,
  TrendingUp,
} from 'lucide-react';

const PerformanceMonitorExample: React.FC = () => {
  const [widgets, setWidgets] = useState<Widget[]>([]);

  // Generate sample data
  useEffect(() => {
    const now = Date.now();
    
    // Generate time series data for charts
    const generateTimeSeriesData = (points: number, min: number, max: number): ChartDataPoint[] => {
      return Array.from({ length: points }, (_, i) => ({
        timestamp: now - (points - i) * 60000,
        value: Math.random() * (max - min) + min,
        label: i % 5 === 0 ? `T${i}` : undefined,
      }));
    };

    // Generate timeline events
    const generateTimelineEvents = (): TimelineEvent[] => [
      {
        timestamp: now - 3600000,
        label: 'System startup completed',
        type: 'milestone',
      },
      {
        timestamp: now - 2700000,
        label: 'Database backup initiated',
        type: 'event',
      },
      {
        timestamp: now - 1800000,
        label: 'High memory usage detected',
        type: 'alert',
      },
      {
        timestamp: now - 900000,
        label: 'API deployment successful',
        type: 'milestone',
      },
      {
        timestamp: now - 300000,
        label: 'Cache cleared',
        type: 'event',
      },
    ];

    const initialWidgets: Widget[] = [
      // Row 1: Metric Cards
      {
        id: 'cpu-usage',
        title: 'CPU Usage',
        type: 'metric',
        size: '1x1',
        state: 'normal',
        position: { x: 0, y: 0 },
        icon: <Cpu size={20} />,
        color: '#00d4ff',
        data: {
          value: 67.3,
          unit: '%',
          label: 'CPU Utilization',
          trend: 'up',
          trendValue: 5.2,
          status: 'warning',
          threshold: 80,
        } as MetricData,
        lastUpdated: now,
      },
      {
        id: 'memory-usage',
        title: 'Memory Usage',
        type: 'metric',
        size: '1x1',
        state: 'normal',
        position: { x: 3, y: 0 },
        icon: <HardDrive size={20} />,
        color: '#00ff88',
        data: {
          value: 4.2,
          unit: 'GB',
          label: 'RAM Used',
          trend: 'down',
          trendValue: -2.1,
          status: 'good',
          threshold: 8,
        } as MetricData,
        lastUpdated: now,
      },
      {
        id: 'network-traffic',
        title: 'Network Traffic',
        type: 'metric',
        size: '1x1',
        state: 'success',
        position: { x: 6, y: 0 },
        icon: <Activity size={20} />,
        color: '#06b6d4',
        data: {
          value: 125.7,
          unit: 'Mbps',
          label: 'Throughput',
          trend: 'up',
          trendValue: 12.3,
          status: 'good',
          threshold: 1000,
        } as MetricData,
        lastUpdated: now,
      },
      {
        id: 'active-users',
        title: 'Active Users',
        type: 'metric',
        size: '1x1',
        state: 'normal',
        position: { x: 9, y: 0 },
        icon: <Users size={20} />,
        color: '#a855f7',
        data: {
          value: 1247,
          label: 'Online',
          trend: 'up',
          trendValue: 8.7,
          status: 'good',
        } as MetricData,
        lastUpdated: now,
      },

      // Row 2: Line Chart and Gauge
      {
        id: 'cpu-history',
        title: 'CPU History (24h)',
        type: 'chart',
        chartType: 'line',
        size: '2x1',
        state: 'normal',
        position: { x: 0, y: 1 },
        color: '#00d4ff',
        data: generateTimeSeriesData(24, 30, 90),
        lastUpdated: now,
      },
      {
        id: 'disk-usage-gauge',
        title: 'Disk Usage',
        type: 'chart',
        chartType: 'gauge',
        size: '1x1',
        state: 'normal',
        position: { x: 6, y: 1 },
        color: '#f97316',
        data: {
          value: 456,
          threshold: 1000,
          label: 'GB Used',
        } as MetricData,
        lastUpdated: now,
      },
      {
        id: 'database-performance',
        title: 'Database Performance',
        type: 'metric',
        size: '1x1',
        state: 'warning',
        position: { x: 9, y: 1 },
        icon: <Database size={20} />,
        color: '#fbbf24',
        data: {
          value: 89.4,
          unit: 'ms',
          label: 'Avg Query Time',
          trend: 'up',
          trendValue: 15.2,
          status: 'warning',
          threshold: 100,
        } as MetricData,
        lastUpdated: now,
      },

      // Row 3: Bar Chart and Progress Rings
      {
        id: 'request-distribution',
        title: 'Request Distribution',
        type: 'chart',
        chartType: 'bar',
        size: '2x1',
        state: 'normal',
        position: { x: 0, y: 2 },
        color: '#00ff88',
        data: [
          { timestamp: now, value: 1250, label: 'GET' },
          { timestamp: now, value: 850, label: 'POST' },
          { timestamp: now, value: 430, label: 'PUT' },
          { timestamp: now, value: 280, label: 'DELETE' },
          { timestamp: now, value: 120, label: 'PATCH' },
        ] as ChartDataPoint[],
        lastUpdated: now,
      },
      {
        id: 'api-health',
        title: 'API Health',
        type: 'chart',
        chartType: 'progress-ring',
        size: '1x1',
        state: 'normal',
        position: { x: 6, y: 2 },
        color: '#10b981',
        data: {
          value: 98.7,
          threshold: 100,
          label: 'Uptime',
        } as MetricData,
        lastUpdated: now,
      },
      {
        id: 'cache-hit-rate',
        title: 'Cache Hit Rate',
        type: 'chart',
        chartType: 'progress-ring',
        size: '1x1',
        state: 'normal',
        position: { x: 9, y: 2 },
        color: '#00d4ff',
        data: {
          value: 87.3,
          threshold: 100,
          label: 'Hit Rate',
        } as MetricData,
        lastUpdated: now,
      },

      // Row 4: Area Chart and Sparklines
      {
        id: 'memory-history',
        title: 'Memory Usage (24h)',
        type: 'chart',
        chartType: 'area',
        size: '2x1',
        state: 'normal',
        position: { x: 0, y: 3 },
        color: '#00ff88',
        data: generateTimeSeriesData(24, 2, 7),
        lastUpdated: now,
      },
      {
        id: 'response-time-spark',
        title: 'Response Time Trend',
        type: 'chart',
        chartType: 'sparkline',
        size: '1x1',
        state: 'normal',
        position: { x: 6, y: 3 },
        color: '#00d4ff',
        data: generateTimeSeriesData(20, 50, 200),
        lastUpdated: now,
      },
      {
        id: 'error-rate-spark',
        title: 'Error Rate Trend',
        type: 'chart',
        chartType: 'sparkline',
        size: '1x1',
        state: 'critical',
        position: { x: 9, y: 3 },
        color: '#ef4444',
        data: generateTimeSeriesData(20, 0, 5),
        lastUpdated: now,
      },

      // Row 5: Timeline (large widget)
      {
        id: 'system-timeline',
        title: 'System Events Timeline',
        type: 'chart',
        chartType: 'timeline',
        size: '2x2',
        state: 'normal',
        position: { x: 0, y: 4 },
        color: '#06b6d4',
        data: generateTimelineEvents(),
        lastUpdated: now,
      },

      // Additional widgets
      {
        id: 'throughput',
        title: 'Requests/sec',
        type: 'metric',
        size: '1x1',
        state: 'normal',
        position: { x: 6, y: 4 },
        icon: <Zap size={20} />,
        color: '#fbbf24',
        data: {
          value: 3542,
          unit: 'req/s',
          label: 'Throughput',
          trend: 'up',
          trendValue: 18.5,
          status: 'good',
        } as MetricData,
        lastUpdated: now,
      },
      {
        id: 'latency',
        title: 'Avg Latency',
        type: 'metric',
        size: '1x1',
        state: 'normal',
        position: { x: 9, y: 4 },
        icon: <Clock size={20} />,
        color: '#06b6d4',
        data: {
          value: 42.3,
          unit: 'ms',
          label: 'Response Time',
          trend: 'down',
          trendValue: -5.8,
          status: 'good',
          threshold: 100,
        } as MetricData,
        lastUpdated: now,
      },

      // Additional metric cards
      {
        id: 'bandwidth',
        title: 'Bandwidth Usage',
        type: 'metric',
        size: '1x1',
        state: 'normal',
        position: { x: 6, y: 5 },
        icon: <TrendingUp size={20} />,
        color: '#a855f7',
        data: {
          value: 234.5,
          unit: 'GB',
          label: 'Data Transfer',
          trend: 'up',
          trendValue: 12.4,
          status: 'good',
          threshold: 1000,
        } as MetricData,
        lastUpdated: now,
      },
      {
        id: 'offline-widget',
        title: 'External API Status',
        type: 'metric',
        size: '1x1',
        state: 'offline',
        position: { x: 9, y: 5 },
        icon: <Activity size={20} />,
        color: '#6b7280',
        data: {
          value: 0,
          label: 'Status',
          status: 'critical',
        } as MetricData,
        lastUpdated: now - 300000,
      },
    ];

    setWidgets(initialWidgets);

    // Simulate real-time updates
    const interval = setInterval(() => {
      setWidgets(prevWidgets =>
        prevWidgets.map(widget => {
          // Skip offline widgets
          if (widget.state === 'offline') return widget;

          const now = Date.now();
          let newData = widget.data;

          // Update metric data
          if (widget.type === 'metric' && widget.data) {
            const metricData = widget.data as MetricData;
            const variance = (Math.random() - 0.5) * 10;
            const newValue = Math.max(0, metricData.value + variance);

            newData = {
              ...metricData,
              value: newValue,
              trend: variance > 0 ? 'up' : variance < 0 ? 'down' : 'neutral',
              trendValue: Math.abs(variance),
              status:
                newValue > (metricData.threshold || 100) * 0.8
                  ? 'warning'
                  : newValue > (metricData.threshold || 100) * 0.9
                  ? 'critical'
                  : 'good',
            } as MetricData;
          }

          // Update chart data (add new point, remove old)
          if (
            widget.type === 'chart' &&
            (widget.chartType === 'line' || widget.chartType === 'area' || widget.chartType === 'sparkline') &&
            Array.isArray(widget.data)
          ) {
            const chartData = widget.data as ChartDataPoint[];
            const lastValue = chartData[chartData.length - 1]?.value || 50;
            const variance = (Math.random() - 0.5) * 20;
            const newValue = Math.max(0, lastValue + variance);

            newData = [
              ...chartData.slice(1),
              {
                timestamp: now,
                value: newValue,
              },
            ] as ChartDataPoint[];
          }

          return {
            ...widget,
            data: newData,
            lastUpdated: now,
            state: 'updated',
          };
        })
      );

      // Reset updated state
      setTimeout(() => {
        setWidgets(prevWidgets =>
          prevWidgets.map(w => ({
            ...w,
            state: w.state === 'updated' ? 'normal' : w.state,
          }))
        );
      }, 500);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleWidgetUpdate = (widgetId: string, data: any) => {
    console.log('Widget updated:', widgetId, data);
  };

  const handleWidgetRemove = (widgetId: string) => {
    setWidgets(prevWidgets => prevWidgets.filter(w => w.id !== widgetId));
    console.log('Widget removed:', widgetId);
  };

  const handleWidgetRefresh = (widgetId: string) => {
    console.log('Widget refresh requested:', widgetId);
    
    // Simulate refresh with new data
    setWidgets(prevWidgets =>
      prevWidgets.map(w => {
        if (w.id !== widgetId) return w;

        const now = Date.now();
        let newData = w.data;

        if (w.type === 'metric' && w.data) {
          const metricData = w.data as MetricData;
          newData = {
            ...metricData,
            value: Math.random() * 100,
          } as MetricData;
        }

        return {
          ...w,
          data: newData,
          lastUpdated: now,
        };
      })
    );
  };

  const handleWidgetSettings = (widgetId: string) => {
    console.log('Widget settings opened:', widgetId);
    alert(`Settings for widget: ${widgetId}\n\nThis would open a settings dialog where you can:\n- Change refresh interval\n- Adjust thresholds\n- Customize appearance\n- Configure alerts`);
  };

  return (
    <div style={{ minHeight: '100vh' }}>
      <PerformanceMonitor
        widgets={widgets}
        onWidgetUpdate={handleWidgetUpdate}
        onWidgetRemove={handleWidgetRemove}
        onWidgetRefresh={handleWidgetRefresh}
        onWidgetSettings={handleWidgetSettings}
        autoRefresh={false}
        theme="dark"
      />
    </div>
  );
};

export default PerformanceMonitorExample;

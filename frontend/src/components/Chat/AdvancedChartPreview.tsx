/**
 * Advanced Chart Preview Component
 * Interactive data visualizations with expand/collapse functionality
 */

import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  ScatterChart,
  Scatter,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { ChartData } from '../../types/chat.types';

interface AdvancedChartPreviewProps {
  chart: ChartData;
  onExpand?: (chartId: string) => void;
  onDownload?: (chartId: string, format: 'png' | 'svg' | 'csv') => void;
}

export const AdvancedChartPreview: React.FC<AdvancedChartPreviewProps> = ({
  chart,
  onExpand,
  onDownload,
}) => {
  const [isExpanded, setIsExpanded] = useState(chart.isExpanded);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);

  const handleExpand = () => {
    setIsExpanded(!isExpanded);
    onExpand?.(chart.id);
  };

  const handleDownload = (format: 'png' | 'svg' | 'csv') => {
    onDownload?.(chart.id, format);
    setShowDownloadMenu(false);
  };

  const getChartHeight = () => {
    if (isExpanded) return 500;
    return 280;
  };

  const colors = [
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // purple
    '#ec4899', // pink
    '#06b6d4', // cyan
    '#f97316', // orange
  ];

  const renderChart = () => {
    const commonProps = {
      data: chart.data,
      margin: { top: 10, right: 30, left: 0, bottom: 0 },
    };

    switch (chart.type) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={getChartHeight()}>
            <LineChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis
                dataKey={chart.config?.xAxisKey || 'name'}
                stroke="#94a3b8"
                style={{ fontSize: '12px' }}
              />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(30, 41, 59, 0.95)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#f8fafc',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
              {chart.config?.yAxisKeys?.map((key: string, index: number) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={getChartHeight()}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis
                dataKey={chart.config?.xAxisKey || 'name'}
                stroke="#94a3b8"
                style={{ fontSize: '12px' }}
              />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(30, 41, 59, 0.95)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#f8fafc',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
              {chart.config?.yAxisKeys?.map((key: string, index: number) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={colors[index % colors.length]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={getChartHeight()}>
            <PieChart>
              <Pie
                data={chart.data}
                dataKey={chart.config?.valueKey || 'value'}
                nameKey={chart.config?.nameKey || 'name'}
                cx="50%"
                cy="50%"
                outerRadius={isExpanded ? 180 : 100}
                label={isExpanded}
                labelLine={isExpanded}
              >
                {chart.data.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(30, 41, 59, 0.95)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#f8fafc',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={getChartHeight()}>
            <ScatterChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis
                dataKey={chart.config?.xAxisKey || 'x'}
                stroke="#94a3b8"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                dataKey={chart.config?.yAxisKey || 'y'}
                stroke="#94a3b8"
                style={{ fontSize: '12px' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(30, 41, 59, 0.95)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#f8fafc',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
              <Scatter name="Data Points" data={chart.data} fill="#3b82f6" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'area':
        return (
          <ResponsiveContainer width="100%" height={getChartHeight()}>
            <AreaChart {...commonProps}>
              <defs>
                {chart.config?.yAxisKeys?.map((key: string, index: number) => (
                  <linearGradient key={key} id={`gradient-${index}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={colors[index % colors.length]} stopOpacity={0.8} />
                    <stop offset="95%" stopColor={colors[index % colors.length]} stopOpacity={0} />
                  </linearGradient>
                ))}
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis
                dataKey={chart.config?.xAxisKey || 'name'}
                stroke="#94a3b8"
                style={{ fontSize: '12px' }}
              />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(30, 41, 59, 0.95)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#f8fafc',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
              {chart.config?.yAxisKeys?.map((key: string, index: number) => (
                <Area
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={colors[index % colors.length]}
                  fill={`url(#gradient-${index})`}
                  strokeWidth={2}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'heatmap':
        // Simplified heatmap representation - would need a specialized library for full heatmap
        return (
          <HeatmapContainer>
            <HeatmapGrid>
              {chart.data.map((row: any, rowIndex: number) => (
                <HeatmapRow key={rowIndex}>
                  {Object.entries(row).map(([key, value]: [string, any], colIndex: number) => {
                    if (key === 'name') return null;
                    const intensity = typeof value === 'number' ? value / 100 : 0.5;
                    return (
                      <HeatmapCell
                        key={`${rowIndex}-${colIndex}`}
                        $intensity={intensity}
                        title={`${key}: ${value}`}
                      />
                    );
                  })}
                </HeatmapRow>
              ))}
            </HeatmapGrid>
          </HeatmapContainer>
        );

      default:
        return <div>Unsupported chart type: {chart.type}</div>;
    }
  };

  return (
    <ChartContainer
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <ChartHeader>
        <ChartTitleSection>
          <ChartIcon>{getChartIcon(chart.type)}</ChartIcon>
          <ChartTitle>{chart.title}</ChartTitle>
          {chart.config?.subtitle && <ChartSubtitle>{chart.config.subtitle}</ChartSubtitle>}
        </ChartTitleSection>

        <ChartActions>
          <ActionButton
            onClick={handleExpand}
            title={isExpanded ? 'Collapse chart' : 'Expand chart'}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isExpanded ? '🔽' : '🔼'}
          </ActionButton>
          <DownloadButtonContainer>
            <ActionButton
              onClick={() => setShowDownloadMenu(!showDownloadMenu)}
              title="Download chart"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              💾
            </ActionButton>
            <AnimatePresence>
              {showDownloadMenu && (
                <DownloadMenu
                  initial={{ opacity: 0, scale: 0.9, y: -10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9, y: -10 }}
                  transition={{ duration: 0.15 }}
                >
                  <DownloadOption onClick={() => handleDownload('png')}>
                    🖼️ PNG Image
                  </DownloadOption>
                  <DownloadOption onClick={() => handleDownload('svg')}>
                    📐 SVG Vector
                  </DownloadOption>
                  <DownloadOption onClick={() => handleDownload('csv')}>
                    📊 CSV Data
                  </DownloadOption>
                </DownloadMenu>
              )}
            </AnimatePresence>
          </DownloadButtonContainer>
        </ChartActions>
      </ChartHeader>

      <ChartContent $isExpanded={isExpanded}>{renderChart()}</ChartContent>

      {chart.config?.description && (
        <ChartFooter>
          <FooterIcon>ℹ️</FooterIcon>
          <FooterText>{chart.config.description}</FooterText>
        </ChartFooter>
      )}
    </ChartContainer>
  );
};

// Helper function
const getChartIcon = (type: string): string => {
  const icons: Record<string, string> = {
    line: '📈',
    bar: '📊',
    pie: '🥧',
    scatter: '🔵',
    area: '📉',
    heatmap: '🔥',
  };
  return icons[type] || '📊';
};

// Styled Components
const ChartContainer = styled(motion.div)`
  margin: 12px 0;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 8px 32px rgba(10, 14, 39, 0.2);
`;

const ChartHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(10, 14, 39, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  gap: 16px;

  @media (max-width: 640px) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

const ChartTitleSection = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  flex-wrap: wrap;
`;

const ChartIcon = styled.span`
  font-size: 20px;
`;

const ChartTitle = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #f8fafc;
`;

const ChartSubtitle = styled.span`
  font-size: 13px;
  color: #94a3b8;
  font-weight: 400;
`;

const ChartActions = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;

  @media (max-width: 640px) {
    align-self: flex-end;
  }
`;

const ActionButton = styled(motion.button)`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f8fafc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 150ms ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.3);
  }
`;

const DownloadButtonContainer = styled.div`
  position: relative;
`;

const DownloadMenu = styled(motion.div)`
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: rgba(30, 41, 59, 0.98);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
  min-width: 150px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  z-index: 100;
`;

const DownloadOption = styled.button`
  width: 100%;
  padding: 10px 14px;
  background: transparent;
  border: none;
  color: #f8fafc;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  transition: background 150ms ease;
  text-align: left;

  &:hover {
    background: rgba(59, 130, 246, 0.2);
  }

  &:not(:last-child) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }
`;

const ChartContent = styled.div<{ $isExpanded: boolean }>`
  padding: 16px;
  background: rgba(15, 23, 42, 0.4);
  transition: padding 300ms ease;

  ${({ $isExpanded }) =>
    $isExpanded &&
    `
    padding: 24px;
  `}
`;

const ChartFooter = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(10, 14, 39, 0.4);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
`;

const FooterIcon = styled.span`
  font-size: 14px;
  margin-top: 2px;
`;

const FooterText = styled.p`
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.5;
`;

// Heatmap specific components
const HeatmapContainer = styled.div`
  padding: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const HeatmapGrid = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const HeatmapRow = styled.div`
  display: flex;
  gap: 4px;
`;

const HeatmapCell = styled.div<{ $intensity: number }>`
  width: 32px;
  height: 32px;
  border-radius: 4px;
  background: ${({ $intensity }) => {
    const blue = Math.round(59 + (246 - 59) * $intensity);
    const green = Math.round(130 * $intensity);
    const red = Math.round(59 + (246 - 59) * $intensity);
    return `rgba(${red}, ${green}, ${blue}, ${0.4 + $intensity * 0.6})`;
  }};
  cursor: pointer;
  transition: transform 150ms ease;

  &:hover {
    transform: scale(1.1);
  }

  @media (max-width: 640px) {
    width: 24px;
    height: 24px;
  }
`;

/**
 * Specialized Analysis Card Variants
 * Timeline, Distribution, Correlation, Trend, Category, and Alert Cards
 */

import React from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';

// ==================== TypeScript Interfaces ====================

export interface TimelineCardProps {
  title: string;
  milestones: Array<{
    label: string;
    date: string;
    completed: boolean;
    description?: string;
  }>;
}

export interface DistributionCardProps {
  title: string;
  data: number[];
  stats: {
    mean: number;
    median: number;
    stdDev: number;
    min: number;
    max: number;
  };
}

export interface CorrelationCardProps {
  title: string;
  xLabel: string;
  yLabel: string;
  coefficient: number;
  pValue: number;
  data: Array<{ x: number; y: number }>;
}

export interface TrendCardProps {
  title: string;
  value: number;
  change: number;
  direction: 'up' | 'down' | 'stable';
  sparklineData: number[];
  period: string;
}

export interface CategoryCardProps {
  title: string;
  categories: Array<{
    label: string;
    value: number;
    percentage: number;
    color?: string;
  }>;
  total?: number;
}

export interface AlertCardProps {
  type: 'warning' | 'error' | 'info';
  title: string;
  message: string;
  actions?: Array<{ label: string; onClick: () => void; primary?: boolean }>;
  dismissible?: boolean;
  onDismiss?: () => void;
}

// ==================== Timeline Card ====================

export const TimelineCard: React.FC<TimelineCardProps> = ({ title, milestones }) => {
  const completedCount = milestones.filter(m => m.completed).length;
  const progress = (completedCount / milestones.length) * 100;

  return (
    <TimelineContainer>
      <TimelineHeader>
        <TimelineTitle>{title}</TimelineTitle>
        <TimelineProgress>
          {completedCount} / {milestones.length} completed
        </TimelineProgress>
      </TimelineHeader>

      <ProgressBarContainer>
        <ProgressBarFill
          $percentage={progress}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </ProgressBarContainer>

      <MilestoneList>
        {milestones.map((milestone, index) => (
          <MilestoneItem
            key={index}
            $completed={milestone.completed}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <MilestoneMarker $completed={milestone.completed}>
              {milestone.completed ? '✓' : index + 1}
            </MilestoneMarker>
            <MilestoneContent>
              <MilestoneLabel>{milestone.label}</MilestoneLabel>
              <MilestoneDate>{milestone.date}</MilestoneDate>
              {milestone.description && (
                <MilestoneDescription>{milestone.description}</MilestoneDescription>
              )}
            </MilestoneContent>
          </MilestoneItem>
        ))}
      </MilestoneList>
    </TimelineContainer>
  );
};

// ==================== Distribution Card ====================

export const DistributionCard: React.FC<DistributionCardProps> = ({ title, data, stats }) => {
  // Simple histogram visualization
  const bins = 10;
  const histogram = createHistogram(data, bins);
  const maxCount = Math.max(...histogram.map(b => b.count));

  return (
    <DistributionContainer>
      <DistributionHeader>{title}</DistributionHeader>

      <HistogramContainer>
        {histogram.map((bin, index) => (
          <HistogramBar
            key={index}
            $height={(bin.count / maxCount) * 100}
            initial={{ height: 0 }}
            animate={{ height: `${(bin.count / maxCount) * 100}%` }}
            transition={{ delay: index * 0.05, duration: 0.4 }}
            title={`${bin.range}: ${bin.count} items`}
          />
        ))}
      </HistogramContainer>

      <StatsGrid>
        <StatItem>
          <StatLabel>Mean</StatLabel>
          <StatValue>{stats.mean.toFixed(2)}</StatValue>
        </StatItem>
        <StatItem>
          <StatLabel>Median</StatLabel>
          <StatValue>{stats.median.toFixed(2)}</StatValue>
        </StatItem>
        <StatItem>
          <StatLabel>Std Dev</StatLabel>
          <StatValue>{stats.stdDev.toFixed(2)}</StatValue>
        </StatItem>
        <StatItem>
          <StatLabel>Range</StatLabel>
          <StatValue>
            {stats.min.toFixed(1)} - {stats.max.toFixed(1)}
          </StatValue>
        </StatItem>
      </StatsGrid>
    </DistributionContainer>
  );
};

// Helper function for histogram
function createHistogram(data: number[], bins: number) {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const binWidth = (max - min) / bins;

  const histogram = Array.from({ length: bins }, (_, i) => ({
    range: `${(min + i * binWidth).toFixed(1)}-${(min + (i + 1) * binWidth).toFixed(1)}`,
    count: 0,
  }));

  data.forEach(value => {
    const binIndex = Math.min(Math.floor((value - min) / binWidth), bins - 1);
    histogram[binIndex].count++;
  });

  return histogram;
}

// ==================== Correlation Card ====================

export const CorrelationCard: React.FC<CorrelationCardProps> = ({
  title,
  xLabel,
  yLabel,
  coefficient,
  pValue,
  data,
}) => {
  const getCorrelationStrength = (r: number) => {
    const abs = Math.abs(r);
    if (abs > 0.7) return 'Strong';
    if (abs > 0.4) return 'Moderate';
    if (abs > 0.2) return 'Weak';
    return 'Very Weak';
  };

  const getCorrelationColor = (r: number) => {
    const abs = Math.abs(r);
    if (abs > 0.7) return '#10b981';
    if (abs > 0.4) return '#3b82f6';
    if (abs > 0.2) return '#f59e0b';
    return '#94a3b8';
  };

  return (
    <CorrelationContainer>
      <CorrelationHeader>{title}</CorrelationHeader>

      <ScatterPlot>
        <ScatterAxisLabel $position="x">{xLabel}</ScatterAxisLabel>
        <ScatterAxisLabel $position="y">{yLabel}</ScatterAxisLabel>
        <ScatterPoints>
          {data.slice(0, 50).map((point, index) => (
            <ScatterPoint
              key={index}
              $x={(point.x / Math.max(...data.map(d => d.x))) * 100}
              $y={100 - (point.y / Math.max(...data.map(d => d.y))) * 100}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.02 }}
            />
          ))}
        </ScatterPoints>
      </ScatterPlot>

      <CorrelationStats>
        <CorrelationCoefficient $color={getCorrelationColor(coefficient)}>
          r = {coefficient.toFixed(3)}
        </CorrelationCoefficient>
        <CorrelationStrength>{getCorrelationStrength(coefficient)} Correlation</CorrelationStrength>
        <CorrelationPValue $significant={pValue < 0.05}>
          {pValue < 0.001 ? 'p < 0.001' : `p = ${pValue.toFixed(3)}`}
        </CorrelationPValue>
      </CorrelationStats>
    </CorrelationContainer>
  );
};

// ==================== Trend Card ====================

export const TrendCard: React.FC<TrendCardProps> = ({
  title,
  value,
  change,
  direction,
  sparklineData,
  period,
}) => {
  const getTrendIcon = () => {
    if (direction === 'up') return '↗️';
    if (direction === 'down') return '↘️';
    return '→';
  };

  const getTrendColor = () => {
    if (direction === 'up') return '#10b981';
    if (direction === 'down') return '#ef4444';
    return '#64748b';
  };

  return (
    <TrendContainer>
      <TrendHeader>
        <TrendTitle>{title}</TrendTitle>
        <TrendPeriod>{period}</TrendPeriod>
      </TrendHeader>

      <TrendValue>{value.toLocaleString()}</TrendValue>

      <TrendChange $color={getTrendColor()}>
        <TrendIcon>{getTrendIcon()}</TrendIcon>
        <TrendChangeValue>
          {change > 0 ? '+' : ''}
          {change.toFixed(1)}%
        </TrendChangeValue>
        <TrendChangeText>vs. previous period</TrendChangeText>
      </TrendChange>

      <Sparkline>
        {sparklineData.map((value, index) => {
          const maxValue = Math.max(...sparklineData);
          const height = (value / maxValue) * 100;
          return (
            <SparklineBar
              key={index}
              $height={height}
              $color={getTrendColor()}
              initial={{ height: 0 }}
              animate={{ height: `${height}%` }}
              transition={{ delay: index * 0.03 }}
            />
          );
        })}
      </Sparkline>
    </TrendContainer>
  );
};

// ==================== Category Card ====================

export const CategoryCard: React.FC<CategoryCardProps> = ({ title, categories, total }) => {
  return (
    <CategoryContainer>
      <CategoryHeader>{title}</CategoryHeader>

      {total !== undefined && (
        <CategoryTotal>
          Total: <strong>{total.toLocaleString()}</strong>
        </CategoryTotal>
      )}

      <CategoryList>
        {categories.map((category, index) => (
          <CategoryItem
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <CategoryItemHeader>
              <CategoryLabel>{category.label}</CategoryLabel>
              <CategoryValue>{category.value.toLocaleString()}</CategoryValue>
            </CategoryItemHeader>
            <CategoryBarContainer>
              <CategoryBarFill
                $percentage={category.percentage}
                $color={category.color || '#3b82f6'}
                initial={{ width: 0 }}
                animate={{ width: `${category.percentage}%` }}
                transition={{ delay: index * 0.05 + 0.2, duration: 0.6 }}
              />
            </CategoryBarContainer>
            <CategoryPercentage>{category.percentage.toFixed(1)}%</CategoryPercentage>
          </CategoryItem>
        ))}
      </CategoryList>
    </CategoryContainer>
  );
};

// ==================== Alert Card ====================

export const AlertCard: React.FC<AlertCardProps> = ({
  type,
  title,
  message,
  actions,
  dismissible = true,
  onDismiss,
}) => {
  const getAlertIcon = () => {
    switch (type) {
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      case 'info':
        return 'ℹ️';
    }
  };

  const getAlertColor = () => {
    switch (type) {
      case 'warning':
        return '#f59e0b';
      case 'error':
        return '#ef4444';
      case 'info':
        return '#3b82f6';
    }
  };

  return (
    <AlertContainer
      $color={getAlertColor()}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <AlertContent>
        <AlertIcon>{getAlertIcon()}</AlertIcon>
        <AlertTextSection>
          <AlertTitle>{title}</AlertTitle>
          <AlertMessage>{message}</AlertMessage>
        </AlertTextSection>
      </AlertContent>

      {(actions || dismissible) && (
        <AlertActions>
          {actions?.map((action, index) => (
            <AlertButton
              key={index}
              onClick={action.onClick}
              $primary={action.primary}
              $color={getAlertColor()}
            >
              {action.label}
            </AlertButton>
          ))}
          {dismissible && (
            <AlertDismissButton onClick={onDismiss} title="Dismiss">
              ✕
            </AlertDismissButton>
          )}
        </AlertActions>
      )}
    </AlertContainer>
  );
};

// ==================== Styled Components ====================

// Timeline Card
const TimelineContainer = styled.div`
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const TimelineHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const TimelineTitle = styled.h3`
  margin: 0;
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: #f8fafc;
`;

const TimelineProgress = styled.span`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #94a3b8;
`;

const ProgressBarContainer = styled.div`
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 24px;
`;

const ProgressBarFill = styled(motion.div)<{ $percentage: number }>`
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 3px;
`;

const MilestoneList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MilestoneItem = styled(motion.div)<{ $completed: boolean }>`
  display: flex;
  gap: 16px;
  opacity: ${({ $completed }) => ($completed ? 1 : 0.6)};
`;

const MilestoneMarker = styled.div<{ $completed: boolean }>`
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${({ $completed }) =>
    $completed ? 'linear-gradient(135deg, #10b981, #059669)' : 'rgba(255, 255, 255, 0.1)'};
  color: white;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 600;
  border: 2px solid ${({ $completed }) => ($completed ? '#10b981' : 'rgba(255, 255, 255, 0.2)')};
`;

const MilestoneContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const MilestoneLabel = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc;
`;

const MilestoneDate = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #94a3b8;
`;

const MilestoneDescription = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #64748b;
  line-height: 1.5;
`;

// Distribution Card
const DistributionContainer = styled.div`
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const DistributionHeader = styled.h3`
  margin: 0 0 20px;
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: #f8fafc;
`;

const HistogramContainer = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 120px;
  margin-bottom: 20px;
`;

const HistogramBar = styled(motion.div)<{ $height: number }>`
  flex: 1;
  background: linear-gradient(180deg, #3b82f6, #2563eb);
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.8;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 16px;
`;

const StatItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const StatLabel = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #94a3b8;
`;

const StatValue = styled.div`
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
  font-weight: 600;
  color: #f8fafc;
`;

// Correlation Card
const CorrelationContainer = styled.div`
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const CorrelationHeader = styled.h3`
  margin: 0 0 20px;
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: #f8fafc;
`;

const ScatterPlot = styled.div`
  position: relative;
  width: 100%;
  height: 200px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin-bottom: 20px;
`;

const ScatterAxisLabel = styled.div<{ $position: 'x' | 'y' }>`
  position: absolute;
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  font-weight: 500;
  color: #94a3b8;

  ${({ $position }) =>
    $position === 'x'
      ? `
    bottom: -20px;
    left: 50%;
    transform: translateX(-50%);
  `
      : `
    left: -40px;
    top: 50%;
    transform: translateY(-50%) rotate(-90deg);
  `}
`;

const ScatterPoints = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  padding: 12px;
`;

const ScatterPoint = styled(motion.div)<{ $x: number; $y: number }>`
  position: absolute;
  left: ${({ $x }) => $x}%;
  top: ${({ $y }) => $y}%;
  width: 6px;
  height: 6px;
  background: #3b82f6;
  border-radius: 50%;
  opacity: 0.7;
`;

const CorrelationStats = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
`;

const CorrelationCoefficient = styled.div<{ $color: string }>`
  font-family: 'JetBrains Mono', monospace;
  font-size: 24px;
  font-weight: 700;
  color: ${({ $color }) => $color};
`;

const CorrelationStrength = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #cbd5e1;
`;

const CorrelationPValue = styled.div<{ $significant: boolean }>`
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  color: ${({ $significant }) => ($significant ? '#10b981' : '#94a3b8')};
  padding: 4px 10px;
  background: ${({ $significant }) => ($significant ? 'rgba(16, 185, 129, 0.1)' : 'transparent')};
  border-radius: 6px;
`;

// Trend Card
const TrendContainer = styled.div`
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const TrendHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`;

const TrendTitle = styled.h3`
  margin: 0;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #94a3b8;
`;

const TrendPeriod = styled.span`
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #64748b;
`;

const TrendValue = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 36px;
  font-weight: 700;
  color: #f8fafc;
  margin-bottom: 12px;
`;

const TrendChange = styled.div<{ $color: string }>`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  color: ${({ $color }) => $color};
`;

const TrendIcon = styled.span`
  font-size: 18px;
`;

const TrendChangeValue = styled.span`
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 700;
`;

const TrendChangeText = styled.span`
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #94a3b8;
`;

const Sparkline = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 48px;
`;

const SparklineBar = styled(motion.div)<{ $height: number; $color: string }>`
  flex: 1;
  background: ${({ $color }) => $color};
  opacity: 0.7;
  border-radius: 2px 2px 0 0;
`;

// Category Card
const CategoryContainer = styled.div`
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const CategoryHeader = styled.h3`
  margin: 0 0 12px;
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: #f8fafc;
`;

const CategoryTotal = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #94a3b8;
  margin-bottom: 20px;

  strong {
    color: #f8fafc;
    font-weight: 600;
  }
`;

const CategoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const CategoryItem = styled(motion.div)`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const CategoryItemHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CategoryLabel = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #cbd5e1;
`;

const CategoryValue = styled.div`
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc;
`;

const CategoryBarContainer = styled.div`
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
`;

const CategoryBarFill = styled(motion.div)<{ $percentage: number; $color: string }>`
  height: 100%;
  background: ${({ $color }) => $color};
  border-radius: 4px;
`;

const CategoryPercentage = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
  text-align: right;
`;

// Alert Card
const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
`;

const AlertContainer = styled(motion.div)<{ $color: string }>`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 20px;
  background: ${({ $color }) => $color}15;
  border: 1px solid ${({ $color }) => $color};
  border-radius: 12px;
  animation: ${pulse} 2s ease-in-out infinite;
`;

const AlertContent = styled.div`
  display: flex;
  gap: 12px;
  flex: 1;
`;

const AlertIcon = styled.div`
  font-size: 24px;
  flex-shrink: 0;
`;

const AlertTextSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const AlertTitle = styled.h4`
  margin: 0;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc;
`;

const AlertMessage = styled.p`
  margin: 0;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #cbd5e1;
  line-height: 1.5;
`;

const AlertActions = styled.div`
  display: flex;
  gap: 8px;
  flex-shrink: 0;
`;

const AlertButton = styled.button<{ $primary?: boolean; $color: string }>`
  padding: 6px 12px;
  background: ${({ $primary, $color }) => ($primary ? $color : 'transparent')};
  border: 1px solid ${({ $color }) => $color};
  border-radius: 6px;
  color: ${({ $primary }) => ($primary ? 'white' : '#f8fafc')};
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: ${({ $color }) => $color};
    color: white;
  }
`;

const AlertDismissButton = styled.button`
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 16px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #f8fafc;
  }
`;

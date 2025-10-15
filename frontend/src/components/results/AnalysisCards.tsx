/**
 * Analysis Result Cards and Panels
 * Elegant display components for statistical outcomes
 */

import React from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';

// ==================== TypeScript Interfaces ====================

export interface AnalysisCardProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error';
  loading?: boolean;
  disabled?: boolean;
  selected?: boolean;
  onSelect?: () => void;
  actions?: Array<{ label: string; onClick: () => void; icon?: string }>;
  className?: string;
}

export interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  color?: string;
  icon?: string;
  size?: 'small' | 'medium' | 'large';
}

export interface ProgressBarProps {
  label: string;
  value: number;
  max?: number;
  color?: string;
  showLabel?: boolean;
  showPercentage?: boolean;
  variant?: 'default' | 'gradient';
}

export interface StatusIndicatorProps {
  status: 'success' | 'warning' | 'error' | 'info' | 'pending';
  label: string;
  description?: string;
}

export interface StatisticalResultProps {
  metric: string;
  value: number;
  pValue?: number;
  confidenceInterval?: [number, number];
  effectSize?: number;
  significance?: 'high' | 'medium' | 'low' | 'none';
}

export interface ComparisonCardProps {
  leftMetric: { label: string; value: string | number; subtitle?: string };
  rightMetric: { label: string; value: string | number; subtitle?: string };
  comparison?: 'better' | 'worse' | 'equal';
  comparisonText?: string;
}

// ==================== Main Analysis Card ====================

export const AnalysisCard: React.FC<AnalysisCardProps> = ({
  title,
  subtitle,
  icon,
  children,
  variant = 'default',
  loading = false,
  disabled = false,
  selected = false,
  onSelect,
  actions,
  className,
}) => {
  return (
    <CardContainer
      $variant={variant}
      $disabled={disabled}
      $selected={selected}
      $clickable={!!onSelect}
      onClick={onSelect}
      className={className}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={onSelect && !disabled ? { scale: 1.02 } : undefined}
      whileTap={onSelect && !disabled ? { scale: 0.98 } : undefined}
    >
      {/* Header */}
      <CardHeader $variant={variant}>
        <CardHeaderContent>
          {icon && <CardIcon>{icon}</CardIcon>}
          <CardTitleSection>
            <CardTitle>{title}</CardTitle>
            {subtitle && <CardSubtitle>{subtitle}</CardSubtitle>}
          </CardTitleSection>
        </CardHeaderContent>
        {selected && <SelectedBadge>✓</SelectedBadge>}
      </CardHeader>

      {/* Content */}
      <CardContent>
        {loading ? (
          <LoadingContainer>
            <LoadingSkeleton />
            <LoadingSkeleton />
            <LoadingSkeleton />
          </LoadingContainer>
        ) : (
          children
        )}
      </CardContent>

      {/* Actions */}
      {actions && actions.length > 0 && (
        <CardActions>
          {actions.map((action, index) => (
            <ActionButton
              key={index}
              onClick={(e) => {
                e.stopPropagation();
                action.onClick();
              }}
              disabled={disabled}
            >
              {action.icon && <span>{action.icon}</span>}
              {action.label}
            </ActionButton>
          ))}
        </CardActions>
      )}
    </CardContainer>
  );
};

// ==================== Metric Card ====================

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  trend,
  trendValue,
  color,
  icon,
  size = 'medium',
}) => {
  const getTrendIcon = () => {
    if (trend === 'up') return '↗️';
    if (trend === 'down') return '↘️';
    return '→';
  };

  const getTrendColor = () => {
    if (trend === 'up') return '#10b981';
    if (trend === 'down') return '#ef4444';
    return '#64748b';
  };

  return (
    <MetricCardContainer $size={size}>
      {icon && <MetricIcon>{icon}</MetricIcon>}
      <MetricLabel>{label}</MetricLabel>
      <MetricValue $color={color} $size={size}>
        {value}
        {unit && <MetricUnit>{unit}</MetricUnit>}
      </MetricValue>
      {trend && (
        <TrendIndicator $color={getTrendColor()}>
          <TrendIcon>{getTrendIcon()}</TrendIcon>
          {trendValue && <TrendValue>{trendValue}</TrendValue>}
        </TrendIndicator>
      )}
    </MetricCardContainer>
  );
};

// ==================== Progress Bar ====================

export const ProgressBar: React.FC<ProgressBarProps> = ({
  label,
  value,
  max = 100,
  color = '#3b82f6',
  showLabel = true,
  showPercentage = true,
  variant = 'default',
}) => {
  const percentage = Math.min((value / max) * 100, 100);

  return (
    <ProgressContainer>
      {showLabel && (
        <ProgressHeader>
          <ProgressLabel>{label}</ProgressLabel>
          {showPercentage && <ProgressPercentage>{percentage.toFixed(0)}%</ProgressPercentage>}
        </ProgressHeader>
      )}
      <ProgressTrack>
        <ProgressFill
          $percentage={percentage}
          $color={color}
          $variant={variant}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </ProgressTrack>
    </ProgressContainer>
  );
};

// ==================== Status Indicator ====================

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  description,
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'success': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'error': return '#ef4444';
      case 'info': return '#3b82f6';
      case 'pending': return '#64748b';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'success': return '✓';
      case 'warning': return '⚠️';
      case 'error': return '✕';
      case 'info': return 'ℹ️';
      case 'pending': return '○';
    }
  };

  return (
    <StatusContainer>
      <StatusDot $color={getStatusColor()}>
        <StatusIcon>{getStatusIcon()}</StatusIcon>
      </StatusDot>
      <StatusContent>
        <StatusLabel>{label}</StatusLabel>
        {description && <StatusDescription>{description}</StatusDescription>}
      </StatusContent>
    </StatusContainer>
  );
};

// ==================== Statistical Result Display ====================

export const StatisticalResult: React.FC<StatisticalResultProps> = ({
  metric,
  value,
  pValue,
  confidenceInterval,
  effectSize,
  significance,
}) => {
  const getSignificanceStars = (sig?: string) => {
    switch (sig) {
      case 'high': return '***';
      case 'medium': return '**';
      case 'low': return '*';
      default: return '';
    }
  };

  const getSignificanceColor = (sig?: string) => {
    switch (sig) {
      case 'high': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'low': return '#64748b';
      default: return '#94a3b8';
    }
  };

  const formatPValue = (p?: number) => {
    if (!p) return null;
    if (p < 0.001) return 'p < 0.001';
    if (p < 0.01) return 'p < 0.01';
    if (p < 0.05) return 'p < 0.05';
    return `p = ${p.toFixed(3)}`;
  };

  return (
    <StatResultContainer>
      <StatMetricRow>
        <StatMetricLabel>{metric}</StatMetricLabel>
        <StatMetricValue>
          {value.toFixed(3)}
          {significance && (
            <SignificanceStars
              $color={getSignificanceColor(significance)}
              title={`Significance: ${significance}`}
            >
              {getSignificanceStars(significance)}
            </SignificanceStars>
          )}
        </StatMetricValue>
      </StatMetricRow>

      {pValue !== undefined && (
        <StatDetailRow>
          <StatDetailLabel>P-value:</StatDetailLabel>
          <PValueDisplay $significant={pValue < 0.05}>
            {formatPValue(pValue)}
          </PValueDisplay>
        </StatDetailRow>
      )}

      {confidenceInterval && (
        <StatDetailRow>
          <StatDetailLabel>95% CI:</StatDetailLabel>
          <ConfidenceInterval>
            [{confidenceInterval[0].toFixed(2)}, {confidenceInterval[1].toFixed(2)}]
          </ConfidenceInterval>
        </StatDetailRow>
      )}

      {effectSize !== undefined && (
        <StatDetailRow>
          <StatDetailLabel>Effect size:</StatDetailLabel>
          <EffectSizeBadge $magnitude={Math.abs(effectSize)}>
            {effectSize.toFixed(2)}
          </EffectSizeBadge>
        </StatDetailRow>
      )}

      {confidenceInterval && (
        <ConfidenceBar>
          <ConfidenceBarLine />
          <ConfidenceBarMarker style={{ left: '50%' }} />
        </ConfidenceBar>
      )}
    </StatResultContainer>
  );
};

// ==================== Comparison Card ====================

export const ComparisonCard: React.FC<ComparisonCardProps> = ({
  leftMetric,
  rightMetric,
  comparison,
  comparisonText,
}) => {
  const getComparisonIcon = () => {
    if (comparison === 'better') return '✓';
    if (comparison === 'worse') return '✕';
    return '=';
  };

  const getComparisonColor = () => {
    if (comparison === 'better') return '#10b981';
    if (comparison === 'worse') return '#ef4444';
    return '#64748b';
  };

  return (
    <ComparisonContainer>
      <ComparisonMetric>
        <ComparisonLabel>{leftMetric.label}</ComparisonLabel>
        <ComparisonValue>{leftMetric.value}</ComparisonValue>
        {leftMetric.subtitle && <ComparisonSubtitle>{leftMetric.subtitle}</ComparisonSubtitle>}
      </ComparisonMetric>

      <ComparisonDivider>
        {comparison && (
          <ComparisonIcon $color={getComparisonColor()}>
            {getComparisonIcon()}
          </ComparisonIcon>
        )}
        <ComparisonText>vs.</ComparisonText>
        {comparisonText && <ComparisonDetail>{comparisonText}</ComparisonDetail>}
      </ComparisonDivider>

      <ComparisonMetric>
        <ComparisonLabel>{rightMetric.label}</ComparisonLabel>
        <ComparisonValue>{rightMetric.value}</ComparisonValue>
        {rightMetric.subtitle && <ComparisonSubtitle>{rightMetric.subtitle}</ComparisonSubtitle>}
      </ComparisonMetric>
    </ComparisonContainer>
  );
};

// ==================== Styled Components ====================

// Animations
const shimmer = keyframes`
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

// Card Container
const CardContainer = styled(motion.div)<{
  $variant: string;
  $disabled: boolean;
  $selected: boolean;
  $clickable: boolean;
}>`
  position: relative;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid ${({ $variant, $selected }) => {
    if ($selected) return '#3b82f6';
    switch ($variant) {
      case 'success': return 'rgba(16, 185, 129, 0.3)';
      case 'warning': return 'rgba(245, 158, 11, 0.3)';
      case 'error': return 'rgba(239, 68, 68, 0.3)';
      default: return 'rgba(255, 255, 255, 0.1)';
    }
  }};
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  transition: all 0.3s ease;
  cursor: ${({ $clickable }) => ($clickable ? 'pointer' : 'default')};
  opacity: ${({ $disabled }) => ($disabled ? 0.6 : 1)};
  filter: ${({ $disabled }) => ($disabled ? 'grayscale(50%)' : 'none')};

  &:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }

  ${({ $selected }) =>
    $selected &&
    `
    background: rgba(59, 130, 246, 0.05);
    box-shadow: 0 0 0 2px #3b82f6, 0 8px 24px rgba(59, 130, 246, 0.2);
  `}
`;

const CardHeader = styled.div<{ $variant: string }>`
  padding: 20px 24px;
  background: ${({ $variant }) => {
    switch ($variant) {
      case 'success':
        return 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
      case 'warning':
        return 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
      case 'error':
        return 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
      default:
        return 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
    }
  }};
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.1);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover::before {
    opacity: 1;
  }
`;

const CardHeaderContent = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
`;

const CardIcon = styled.div`
  font-size: 24px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
`;

const CardTitleSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const CardTitle = styled.h3`
  margin: 0;
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: white;
  line-height: 1.4;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const CardSubtitle = styled.p`
  margin: 0;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
`;

const SelectedBadge = styled.div`
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  color: #3b82f6;
  border-radius: 50%;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
`;

const CardContent = styled.div`
  padding: 24px;
  background: rgba(255, 255, 255, 0.02);
  min-height: 100px;
`;

const CardActions = styled.div`
  display: flex;
  gap: 8px;
  padding: 16px 24px;
  background: rgba(0, 0, 0, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
`;

const ActionButton = styled.button`
  padding: 8px 16px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #f8fafc;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;

  &:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

// Loading
const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const LoadingSkeleton = styled.div`
  height: 20px;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 100%
  );
  background-size: 200% 100%;
  border-radius: 4px;
  animation: ${shimmer} 1.5s ease-in-out infinite;

  &:nth-child(2) {
    width: 80%;
  }

  &:nth-child(3) {
    width: 60%;
  }
`;

// Metric Card
const MetricCardContainer = styled.div<{ $size: string }>`
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: ${({ $size }) => {
    switch ($size) {
      case 'small': return '12px';
      case 'large': return '24px';
      default: return '16px';
    }
  }};
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
`;

const MetricIcon = styled.div`
  font-size: 32px;
  margin-bottom: 4px;
`;

const MetricLabel = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #94a3b8;
  line-height: 1.4;
`;

const MetricValue = styled.div<{ $color?: string; $size: string }>`
  font-family: 'Inter', sans-serif;
  font-size: ${({ $size }) => {
    switch ($size) {
      case 'small': return '20px';
      case 'large': return '36px';
      default: return '28px';
    }
  }};
  font-weight: 700;
  color: ${({ $color }) => $color || '#f8fafc'};
  line-height: 1.2;
  display: flex;
  align-items: baseline;
  gap: 4px;
`;

const MetricUnit = styled.span`
  font-size: 0.5em;
  font-weight: 500;
  color: #94a3b8;
`;

const TrendIndicator = styled.div<{ $color: string }>`
  display: flex;
  align-items: center;
  gap: 4px;
  color: ${({ $color }) => $color};
  font-size: 14px;
  font-weight: 600;
`;

const TrendIcon = styled.span``;

const TrendValue = styled.span``;

// Progress Bar
const ProgressContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ProgressHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ProgressLabel = styled.span`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #cbd5e1;
`;

const ProgressPercentage = styled.span`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc;
`;

const ProgressTrack = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
`;

const ProgressFill = styled(motion.div)<{
  $percentage: number;
  $color: string;
  $variant: string;
}>`
  height: 100%;
  background: ${({ $color, $variant }) =>
    $variant === 'gradient'
      ? `linear-gradient(90deg, ${$color} 0%, ${$color}dd 100%)`
      : $color};
  border-radius: 4px;
  box-shadow: 0 0 8px ${({ $color }) => $color}80;
`;

// Status Indicator
const StatusContainer = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
`;

const StatusDot = styled.div<{ $color: string }>`
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  background: ${({ $color }) => $color}20;
  border: 2px solid ${({ $color }) => $color};
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: ${pulse} 2s ease-in-out infinite;
`;

const StatusIcon = styled.span`
  font-size: 14px;
`;

const StatusContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
`;

const StatusLabel = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #f8fafc;
  line-height: 1.4;
`;

const StatusDescription = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #94a3b8;
  line-height: 1.5;
`;

// Statistical Results
const StatResultContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
`;

const StatMetricRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
`;

const StatMetricLabel = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #cbd5e1;
`;

const StatMetricValue = styled.div`
  font-family: 'JetBrains Mono', monospace;
  font-size: 18px;
  font-weight: 600;
  color: #f8fafc;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const SignificanceStars = styled.span<{ $color: string }>`
  color: ${({ $color }) => $color};
  font-size: 16px;
  cursor: help;
`;

const StatDetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const StatDetailLabel = styled.span`
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #94a3b8;
`;

const PValueDisplay = styled.span<{ $significant: boolean }>`
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  color: ${({ $significant }) => ($significant ? '#10b981' : '#94a3b8')};
  padding: 2px 8px;
  background: ${({ $significant }) =>
    $significant ? 'rgba(16, 185, 129, 0.1)' : 'transparent'};
  border-radius: 4px;
`;

const ConfidenceInterval = styled.span`
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 400;
  color: #cbd5e1;
`;

const EffectSizeBadge = styled.span<{ $magnitude: number }>`
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 12px;
  background: ${({ $magnitude }) => {
    if ($magnitude > 0.8) return 'rgba(239, 68, 68, 0.15)';
    if ($magnitude > 0.5) return 'rgba(245, 158, 11, 0.15)';
    return 'rgba(16, 185, 129, 0.15)';
  }};
  color: ${({ $magnitude }) => {
    if ($magnitude > 0.8) return '#ef4444';
    if ($magnitude > 0.5) return '#f59e0b';
    return '#10b981';
  }};
`;

const ConfidenceBar = styled.div`
  position: relative;
  height: 4px;
  margin-top: 4px;
`;

const ConfidenceBarLine = styled.div`
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 1px;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
`;

const ConfidenceBarMarker = styled.div`
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border: 2px solid white;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
`;

// Comparison Card
const ComparisonContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 24px;
  align-items: center;

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
    gap: 16px;
  }
`;

const ComparisonMetric = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  text-align: center;
`;

const ComparisonLabel = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #94a3b8;
`;

const ComparisonValue = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: #f8fafc;
  line-height: 1.2;
`;

const ComparisonSubtitle = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: #64748b;
`;

const ComparisonDivider = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;

  @media (max-width: 640px) {
    flex-direction: row;
    justify-content: center;
  }
`;

const ComparisonIcon = styled.div<{ $color: string }>`
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${({ $color }) => $color}20;
  color: ${({ $color }) => $color};
  border-radius: 50%;
  font-size: 18px;
  font-weight: 700;
`;

const ComparisonText = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const ComparisonDetail = styled.div`
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  font-weight: 400;
  color: #94a3b8;
  max-width: 100px;
  text-align: center;
  line-height: 1.4;
`;

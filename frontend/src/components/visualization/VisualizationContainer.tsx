/**
 * Stunning Data Visualization Container Component
 * Modern glassmorphism design with interactive controls
 */

import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import '../styles/visualization.scss';

export interface VisualizationContainerProps {
  title: string;
  subtitle?: string;
  icon?: string;
  children: React.ReactNode;
  onExport?: (format: 'png' | 'svg' | 'pdf' | 'csv' | 'json') => void;
  onFullscreen?: () => void;
  onRefresh?: () => void;
  loading?: boolean;
  error?: Error | null;
  isEmpty?: boolean;
  showControls?: boolean;
  filters?: Array<{ label: string; active: boolean; onClick: () => void }>;
  zoomControls?: boolean;
  className?: string;
}

export const VisualizationContainer: React.FC<VisualizationContainerProps> = ({
  title,
  subtitle,
  icon = '📊',
  children,
  onExport,
  onFullscreen,
  onRefresh,
  loading = false,
  error = null,
  isEmpty = false,
  showControls = true,
  filters,
  zoomControls = false,
  className,
}) => {
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleExport = (format: 'png' | 'svg' | 'pdf' | 'csv' | 'json') => {
    onExport?.(format);
    setShowExportMenu(false);
  };

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    onFullscreen?.();
  };

  const handleRefresh = () => {
    onRefresh?.();
  };

  return (
    <div
      ref={containerRef}
      className={`viz-chart-container ${isFullscreen ? 'viz-chart-container--fullscreen' : ''} ${
        loading ? 'viz-chart-container--loading' : ''
      } ${error ? 'viz-chart-container--error' : ''} ${className || ''}`}
    >
      {/* Header */}
      <div className="viz-chart-header">
        <div className="viz-chart-title-section">
          <h2 className="viz-chart-title">
            <span className="viz-chart-title-icon">{icon}</span>
            {title}
          </h2>
          {subtitle && <p className="viz-chart-subtitle">{subtitle}</p>}
        </div>

        <div className="viz-chart-actions">
          {onRefresh && (
            <button
              className="viz-chart-btn viz-chart-btn--icon"
              onClick={handleRefresh}
              title="Refresh data"
              disabled={loading}
            >
              🔄
            </button>
          )}
          
          {onExport && (
            <ExportButtonContainer>
              <button
                className="viz-chart-btn viz-chart-btn--icon"
                onClick={() => setShowExportMenu(!showExportMenu)}
                title="Export chart"
              >
                💾
              </button>
              
              <AnimatePresence>
                {showExportMenu && (
                  <motion.div
                    className="viz-export-menu"
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    transition={{ duration: 0.15 }}
                  >
                    <button
                      className="viz-export-menu-item"
                      onClick={() => handleExport('png')}
                    >
                      <span className="viz-export-menu-item-icon">🖼️</span>
                      PNG Image
                    </button>
                    <button
                      className="viz-export-menu-item"
                      onClick={() => handleExport('svg')}
                    >
                      <span className="viz-export-menu-item-icon">📐</span>
                      SVG Vector
                    </button>
                    <button
                      className="viz-export-menu-item"
                      onClick={() => handleExport('pdf')}
                    >
                      <span className="viz-export-menu-item-icon">📄</span>
                      PDF Document
                    </button>
                    <button
                      className="viz-export-menu-item"
                      onClick={() => handleExport('csv')}
                    >
                      <span className="viz-export-menu-item-icon">📊</span>
                      CSV Data
                    </button>
                    <button
                      className="viz-export-menu-item"
                      onClick={() => handleExport('json')}
                    >
                      <span className="viz-export-menu-item-icon">📦</span>
                      JSON Data
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </ExportButtonContainer>
          )}
          
          {onFullscreen && (
            <button
              className="viz-chart-btn viz-chart-btn--icon"
              onClick={handleFullscreen}
              title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
            >
              {isFullscreen ? '🔽' : '🔼'}
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="viz-chart-content">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="loading"
              className="viz-loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="viz-loading-spinner" />
              <p className="viz-loading-text">Loading visualization...</p>
            </motion.div>
          ) : error ? (
            <motion.div
              key="error"
              className="viz-error"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="viz-error-icon">⚠️</div>
              <h3 className="viz-error-title">Failed to Load Chart</h3>
              <p className="viz-error-text">{error.message || 'An unexpected error occurred'}</p>
              {onRefresh && (
                <button className="viz-error-retry" onClick={handleRefresh}>
                  Try Again
                </button>
              )}
            </motion.div>
          ) : isEmpty ? (
            <motion.div
              key="empty"
              className="viz-empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="viz-empty-icon">📭</div>
              <h3 className="viz-empty-title">No Data Available</h3>
              <p className="viz-empty-text">
                There is no data to display for this visualization.
                Try adjusting your filters or check back later.
              </p>
            </motion.div>
          ) : (
            <motion.div
              key="content"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              {children}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Controls */}
      {showControls && (filters || zoomControls) && (
        <div className="viz-controls">
          {filters && filters.length > 0 && (
            <div className="viz-filter-group">
              {filters.map((filter, index) => (
                <button
                  key={index}
                  className={`viz-filter-btn ${filter.active ? 'viz-filter-btn--active' : ''}`}
                  onClick={filter.onClick}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          )}
          
          {zoomControls && (
            <div className="viz-zoom-controls">
              <button title="Zoom in">➕</button>
              <button title="Reset zoom">⚪</button>
              <button title="Zoom out">➖</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Additional styled component for proper positioning
const ExportButtonContainer = styled.div`
  position: relative;
`;

// ==================== Status Badge Component ====================
export interface StatusBadgeProps {
  type: 'success' | 'warning' | 'error' | 'info';
  icon?: string;
  children: React.ReactNode;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ type, icon, children }) => {
  const icons = {
    success: '✅',
    warning: '⚠️',
    error: '❌',
    info: 'ℹ️',
  };

  return (
    <span className={`viz-status viz-status--${type}`}>
      <span className="viz-status-icon">{icon || icons[type]}</span>
      {children}
    </span>
  );
};

// ==================== Data Label Component ====================
export interface DataLabelProps {
  value: string | number;
  label?: string;
  color?: string;
}

export const DataLabel: React.FC<DataLabelProps> = ({ value, label, color }) => {
  return (
    <div className="viz-data-label" style={{ color }}>
      {label && <span>{label}: </span>}
      <strong>{value}</strong>
    </div>
  );
};

// ==================== Timestamp Component ====================
export interface TimestampProps {
  date: Date | string;
  format?: 'relative' | 'absolute';
}

export const Timestamp: React.FC<TimestampProps> = ({ date, format = 'relative' }) => {
  const formatDate = (d: Date | string): string => {
    const dateObj = typeof d === 'string' ? new Date(d) : d;
    
    if (format === 'relative') {
      const now = new Date();
      const diff = now.getTime() - dateObj.getTime();
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);
      
      if (minutes < 1) return 'Just now';
      if (minutes < 60) return `${minutes}m ago`;
      if (hours < 24) return `${hours}h ago`;
      if (days < 7) return `${days}d ago`;
    }
    
    return dateObj.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return <span className="viz-timestamp">{formatDate(date)}</span>;
};

// ==================== Loading Skeleton Component ====================
export interface LoadingSkeletonProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string | number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  width = '100%',
  height = '20px',
  borderRadius = '8px',
}) => {
  return (
    <div
      className="viz-skeleton"
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
        borderRadius: typeof borderRadius === 'number' ? `${borderRadius}px` : borderRadius,
      }}
    />
  );
};

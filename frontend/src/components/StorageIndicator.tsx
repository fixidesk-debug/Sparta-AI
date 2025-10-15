/**
 * StorageIndicator Component
 * 
 * Visual display of storage quota and usage
 */

import React, { useMemo } from 'react';
import { StorageIndicatorProps } from '../types/fileManagement';
import './StorageIndicator.css';

// Small sanitizer for logs to avoid control characters being injected into console output
const sanitizeForLog = (v: unknown) => {
  try {
    const s = String(v ?? '');
    return s.replace(/[\x00-\x1F\x7F]+/g, ' ').slice(0, 1000);
  } catch {
    return 'unserializable';
  }
};

// Format bytes for display (moved out to avoid re-creation on each render)
const formatBytes = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`;
};

const colorClasses: Record<'red' | 'yellow' | 'blue', { bg: string; text: string; lightBg: string }> = {
  red: {
    bg: 'bg-red-600 dark:bg-red-500',
    text: 'text-red-600 dark:text-red-400',
    lightBg: 'bg-red-50 dark:bg-red-900/20',
  },
  yellow: {
    bg: 'bg-yellow-600 dark:bg-yellow-500',
    text: 'text-yellow-600 dark:text-yellow-400',
    lightBg: 'bg-yellow-50 dark:bg-yellow-900/20',
  },
  blue: {
    bg: 'bg-blue-600 dark:bg-blue-500',
    text: 'text-blue-600 dark:text-blue-400',
    lightBg: 'bg-blue-50 dark:bg-blue-900/20',
  },
};

const getColor = (percentage: number): 'red' | 'yellow' | 'blue' => {
  if (percentage >= 90) return 'red';
  if (percentage >= 75) return 'yellow';
  return 'blue';
};

// Map percentage to a discrete width class (5% steps) to avoid inline width styles
const widthClassFor = (pct: number) => {
  const p = Math.max(0, Math.min(100, Math.round(pct / 5) * 5));
  return `viz-progress--w-${p}`;
};

const StorageIndicator: React.FC<StorageIndicatorProps> = ({
  quota,
  detailed = false,
  onClick,
  className = '',
}) => {
  const color = getColor(quota.percentage);

  // Compact view
  if (!detailed) {
    return (
      <div
        className={`storage-indicator ${className} ${onClick ? 'cursor-pointer' : ''}`}
        onClick={onClick}
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Storage
          </span>
          <span className={`text-sm font-medium ${colorClasses[color].text}`}>
            {quota.percentage.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className={`${colorClasses[color].bg} h-2 rounded-full transition-all duration-300 ${widthClassFor(
              quota.percentage,
            )}`}
          />
        </div>
        <div className="flex items-center justify-between mt-1">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {formatBytes(quota.used)} used
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {formatBytes(quota.total)} total
          </span>
        </div>
      </div>
    );
  }

  // Detailed view
  return (
    <div
      className={`storage-indicator ${className} ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
    >
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
          Storage Usage
        </h3>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            {formatBytes(quota.used)}
          </span>
          <span className="text-gray-500 dark:text-gray-400">
            / {formatBytes(quota.total)}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {quota.percentage.toFixed(1)}% used
          </span>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {formatBytes(quota.available)} available
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
          <div
            className={`${colorClasses[color].bg} h-3 rounded-full transition-all duration-300 ${widthClassFor(
              quota.percentage,
            )}`}
          />
        </div>
      </div>

      {/* Warning message */}
      {quota.percentage >= 90 && (
        <div className={`p-3 ${colorClasses[color].lightBg} rounded mb-4`}>
          <p className={`text-sm ${colorClasses[color].text}`}>
            ⚠️ You're running out of storage space. Consider deleting unused files.
          </p>
        </div>
      )}

      {/* Usage by type */}
      {Object.keys(quota.byType).length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Storage by Type
          </h4>
          <div className="space-y-2">
            {(() => {
              try {
                const entries = Object.entries(quota.byType || {});
                const sorted = entries.sort(([, a], [, b]) => b - a).slice(0, 5);
                return sorted.map(([type, size]) => {
                  const percentage = quota.used > 0 ? (size / quota.used) * 100 : 0;
                  return (
                    <div key={type}>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-600 dark:text-gray-400 capitalize">{type}</span>
                        <span className="text-gray-900 dark:text-gray-100">
                          {formatBytes(size)} ({percentage.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                        <div
                          className={`bg-gray-400 dark:bg-gray-500 h-1.5 rounded-full ${widthClassFor(
                            percentage,
                          )}`}
                        />
                      </div>
                    </div>
                  );
                });
              } catch (err) {
                console.error('StorageIndicator: failed to render byType:', sanitizeForLog(err));
                return <div className="text-sm text-red-600">Unable to show type breakdown</div>;
              }
            })()}
          </div>
        </div>
      )}

      {/* Usage by folder */}
      {Object.keys(quota.byFolder).length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Storage by Folder
          </h4>
          <div className="space-y-2">
            {(() => {
              try {
                const entries = Object.entries(quota.byFolder || {});
                const sorted = entries.sort(([, a], [, b]) => b - a).slice(0, 5);
                return sorted.map(([folder, size]) => {
                  const percentage = quota.used > 0 ? (size / quota.used) * 100 : 0;
                  return (
                    <div key={folder} className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400 truncate flex-1">📁 {folder || 'Root'}</span>
                      <span className="text-gray-900 dark:text-gray-100 ml-2">
                        {formatBytes(size)} ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                  );
                });
              } catch (err) {
                console.error('StorageIndicator: failed to render byFolder:', sanitizeForLog(err));
                return <div className="text-sm text-red-600">Unable to show folder breakdown</div>;
              }
            })()}
          </div>
        </div>
      )}
    </div>
  );
};

export default StorageIndicator;

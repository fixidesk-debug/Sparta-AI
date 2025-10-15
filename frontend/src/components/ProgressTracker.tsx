/**
 * ProgressTracker Component
 * 
 * Displays upload progress for multiple files with pause/resume/cancel
 */

import React, { useMemo } from 'react';
import { ProgressTrackerProps, UploadTask } from '../types/fileManagement';
import './ProgressTracker.css';

// Small sanitizer for logs to avoid control characters being injected into console output
const sanitizeForLog = (v: unknown) => {
  try {
    const s = String(v ?? '');
    return s.replace(/[\x00-\x1F\x7F]+/g, ' ').slice(0, 1000);
  } catch {
    return 'unserializable';
  }
};

// Map percentage to a discrete width class (5% steps)
const widthClassFor = (pct: number) => {
  const p = Math.max(0, Math.min(100, Math.round(pct / 5) * 5));
  return `pt-progress--w-${p}`;
};

// Format bytes for display (module-level to avoid re-creation)
const formatBytes = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`;
};

// Format time remaining
const formatTime = (seconds: number): string => {
  if (!isFinite(seconds) || seconds < 0) return '--:--';

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs
      .toString()
      .padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

// Get status color
const getStatusColor = (status: string): string => {
  switch (status) {
    case 'completed':
      return 'text-green-600 dark:text-green-400';
    case 'error':
      return 'text-red-600 dark:text-red-400';
    case 'cancelled':
      return 'text-gray-600 dark:text-gray-400';
    case 'uploading':
      return 'text-blue-600 dark:text-blue-400';
    default:
      return 'text-gray-600 dark:text-gray-400';
  }
};

// Get status icon
const getStatusIcon = (status: string): string => {
  switch (status) {
    case 'completed':
      return '✅';
    case 'error':
      return '❌';
    case 'cancelled':
      return '🚫';
    case 'uploading':
      return '⏳';
    case 'processing':
      return '⚙️';
    case 'validating':
      return '🔍';
    case 'paused':
      return '⏸️';
    default:
      return '⏳';
  }
};

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  tasks,
  onCancel,
  onRetry,
  onClear,
  compact = false,
  className = '',
}) => {
  if (tasks.length === 0) {
    return null;
  }


  // Render task elements memoized to reduce per-render allocations
  const taskElements = useMemo(() => {
    return tasks.map((task) => {
      try {
        const isActive = task.status === 'uploading' || task.status === 'processing';
        const isComplete = task.status === 'completed';
        const isError = task.status === 'error';
        const canRetry = isError && (task.retryCount ?? 0) < 3;
        const canCancel = isActive;
        const canClear = isComplete || isError;

        const uploadedChunks = (task.chunks || []).filter((c) => c.uploaded).length;

        return (
          <div
            key={task.id}
            className={`border border-gray-200 dark:border-gray-700 rounded-lg p-4 ${compact ? 'mb-2' : 'mb-4'}`}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <span className="text-xl">{getStatusIcon(task.status)}</span>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 dark:text-gray-100 truncate">{task.file.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{formatBytes(task.file.size)}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 ml-4">
                {canRetry && onRetry && (
                  <button
                    onClick={() => {
                      try {
                        onRetry(task.id);
                      } catch (err) {
                        console.error('onRetry failed:', sanitizeForLog(err));
                      }
                    }}
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
                    title="Retry upload"
                    aria-label="Retry upload"
                  >
                    🔄
                  </button>
                )}
                {canCancel && onCancel && (
                  <button
                    onClick={() => {
                      try {
                        onCancel(task.id);
                      } catch (err) {
                        console.error('onCancel failed:', sanitizeForLog(err));
                      }
                    }}
                    className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                    title="Cancel upload"
                    aria-label="Cancel upload"
                  >
                    ❌
                  </button>
                )}
                {canClear && onClear && (
                  <button
                    onClick={() => {
                      try {
                        onClear(task.id);
                      } catch (err) {
                        console.error('onClear (single) failed:', sanitizeForLog(err));
                      }
                    }}
                    className="text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                    title="Clear"
                    aria-label="Clear upload"
                  >
                    🗑️
                  </button>
                )}
              </div>
            </div>

            {/* Progress bar */}
            {isActive && (
              <div className="mb-2">
                <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
                  <span className={getStatusColor(task.status)}>{task.status === 'uploading' ? 'Uploading' : 'Processing'}</span>
                  <span>{Math.round(task.progress)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className={`bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300 ${widthClassFor(task.progress)}`} />
                </div>
              </div>
            )}

            {/* Stats */}
            {isActive && !compact && (
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>{formatBytes(task.uploadedBytes)} / {formatBytes(task.totalBytes)}</span>
                <span>{formatBytes(task.speed)}/s</span>
                <span>ETA: {formatTime(task.timeRemaining)}</span>
              </div>
            )}

            {/* Chunks info */}
            {isActive && !compact && task.chunks && task.chunks.length > 1 && (
              <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                <span>Chunks: {uploadedChunks} / {task.chunks.length}</span>
              </div>
            )}

            {/* Error message */}
            {isError && task.error && (
              <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
                <p className="text-sm text-red-800 dark:text-red-200">{task.error.message}</p>
                {task.error.details && (<p className="text-xs text-red-600 dark:text-red-300 mt-1">{task.error.details}</p>)}
              </div>
            )}

            {/* Completion time */}
            {isComplete && task.completedAt && !compact && (
              <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Completed {formatTime((task.completedAt.getTime() - task.startedAt.getTime()) / 1000)} ago
              </div>
            )}
          </div>
        );
      } catch (err) {
        console.error('ProgressTracker: failed rendering task', sanitizeForLog(err));
        return (
          <div key={task.id} className="p-2 text-sm text-red-600">Unable to render task</div>
        );
      }
    });
  }, [tasks, compact, onRetry, onCancel, onClear]);

  // Calculate overall stats memoized to avoid repeated array scans
  const {
    totalFiles,
    completedFiles,
    failedFiles,
    activeFiles,
    totalBytes,
    uploadedBytes,
    overallProgress,
  } = useMemo(() => {
    const totalFiles = tasks.length;
    let completedFiles = 0;
    let failedFiles = 0;
    let activeFiles = 0;
    let totalBytes = 0;
    let uploadedBytes = 0;

    for (const t of tasks) {
      if (t.status === 'completed') completedFiles++;
      if (t.status === 'error') failedFiles++;
      if (t.status === 'uploading' || t.status === 'processing') activeFiles++;
      totalBytes += t.totalBytes || 0;
      uploadedBytes += t.uploadedBytes || 0;
    }

    const overallProgress = totalBytes > 0 ? (uploadedBytes / totalBytes) * 100 : 0;
    return { totalFiles, completedFiles, failedFiles, activeFiles, totalBytes, uploadedBytes, overallProgress };
  }, [tasks]);

  return (
    <div className={`progress-tracker ${className}`}>
      {/* Overall stats */}
      {!compact && tasks.length > 1 && (
        <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-gray-900 dark:text-gray-100">
              Upload Progress
            </h3>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {completedFiles} / {totalFiles} files
            </span>
          </div>

              {/* Overall progress bar */}
              <div className="mb-2">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className={`bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300 ${widthClassFor(overallProgress)}`} />
                </div>
              </div>

          {/* Stats */}
          <div className="flex items-center gap-4 text-xs text-gray-600 dark:text-gray-400">
            {activeFiles > 0 && (
              <span className="flex items-center gap-1">
                <span className="text-blue-600 dark:text-blue-400">⏳</span>
                {activeFiles} uploading
              </span>
            )}
            {completedFiles > 0 && (
              <span className="flex items-center gap-1">
                <span className="text-green-600 dark:text-green-400">✅</span>
                {completedFiles} completed
              </span>
            )}
            {failedFiles > 0 && (
              <span className="flex items-center gap-1">
                <span className="text-red-600 dark:text-red-400">❌</span>
                {failedFiles} failed
              </span>
            )}
          </div>
        </div>
      )}

  {/* Individual tasks */}
  <div>{taskElements}</div>

      {/* Clear all button */}
      {!compact && onClear && tasks.some((t) => t.status === 'completed') && (
        <button
          onClick={() => {
            try {
              tasks.filter((t) => t.status === 'completed').forEach((t) => onClear(t.id));
            } catch (err) {
              console.error('Clear completed failed:', sanitizeForLog(err));
            }
          }}
          className="mt-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
        >
          Clear completed
        </button>
      )}
    </div>
  );
};

export default ProgressTracker;

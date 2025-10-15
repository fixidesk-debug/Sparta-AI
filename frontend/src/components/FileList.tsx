/**
 * FileList Component
 * 
 * Displays files in grid or list view with selection and actions
 */

import React, { useState, useCallback } from 'react';
import { FileListProps, FileItem, FileAction } from '../types/fileManagement';

const FileList: React.FC<FileListProps> = ({
  files,
  view = 'grid',
  onFileSelect,
  onFileAction,
  onBulkAction,
  selectedFileIds = [],
  sortBy = 'uploadedAt',
  sortOrder = 'desc',
  loading = false,
  className = '',
}) => {
  const [selectMode, setSelectMode] = useState(false);
  const [localSelectedIds, setLocalSelectedIds] = useState<string[]>(
    selectedFileIds
  );

  // Toggle select mode
  const toggleSelectMode = useCallback(() => {
    setSelectMode(!selectMode);
    if (selectMode) {
      setLocalSelectedIds([]);
    }
  }, [selectMode]);

  // Toggle file selection
  const toggleFileSelection = useCallback(
    (fileId: string) => {
      setLocalSelectedIds(prev =>
        prev.includes(fileId)
          ? prev.filter(id => id !== fileId)
          : [...prev, fileId]
      );
    },
    []
  );

  // Select all files
  const selectAll = useCallback(() => {
    setLocalSelectedIds(files.map(f => f.id));
  }, [files]);

  // Clear selection
  const clearSelection = useCallback(() => {
    setLocalSelectedIds([]);
  }, []);

  // Handle file click
  const handleFileClick = useCallback(
    (file: FileItem) => {
      if (selectMode) {
        toggleFileSelection(file.id);
      } else if (onFileSelect) {
        onFileSelect(file);
      }
    },
    [selectMode, toggleFileSelection, onFileSelect]
  );

  // Handle action click
  const handleActionClick = useCallback(
    (e: React.MouseEvent, action: FileAction, file: FileItem) => {
      e.stopPropagation();
      if (onFileAction) {
        onFileAction(action, file);
      }
    },
    [onFileAction]
  );

  // Format bytes
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

  // Format date
  const formatDate = (date: Date): string => {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 7) {
      return new Date(date).toLocaleDateString();
    } else if (days > 0) {
      return `${days}d ago`;
    } else if (hours > 0) {
      return `${hours}h ago`;
    } else if (minutes > 0) {
      return `${minutes}m ago`;
    } else {
      return 'Just now';
    }
  };

  // Get file icon
  const getFileIcon = (file: FileItem): string => {
    const type = file.type.toLowerCase();
    if (type.startsWith('image/')) return '🖼️';
    if (type.startsWith('video/')) return '🎥';
    if (type.startsWith('audio/')) return '🎵';
    if (type.includes('pdf')) return '📄';
    if (type.includes('text') || type.includes('csv')) return '📝';
    if (type.includes('json')) return '📋';
    if (type.includes('zip') || type.includes('compressed')) return '📦';
    return '📄';
  };

  // Render grid view
  const renderGridView = () => (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      {files.map(file => {
        const isSelected = localSelectedIds.includes(file.id);

        return (
          <div
            key={file.id}
            className={`
              relative group cursor-pointer
              border-2 rounded-lg p-4
              transition-all duration-200
              ${
                isSelected
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }
            `}
            onClick={() => handleFileClick(file)}
          >
            {/* Selection checkbox */}
            {selectMode && (
              <div className="absolute top-2 left-2 z-10">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => toggleFileSelection(file.id)}
                  className="w-4 h-4 rounded"
                  aria-label={`Select ${file.filename}`}
                />
              </div>
            )}

            {/* Thumbnail or icon */}
            <div className="flex items-center justify-center h-24 mb-2">
              {file.thumbnailUrl ? (
                <img
                  src={file.thumbnailUrl}
                  alt={file.filename}
                  className="max-h-full max-w-full object-contain"
                />
              ) : (
                <span className="text-5xl">{getFileIcon(file)}</span>
              )}
            </div>

            {/* File name */}
            <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate mb-1">
              {file.filename}
            </p>

            {/* File size */}
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {formatBytes(file.size)}
            </p>

            {/* Actions (show on hover) */}
            {!selectMode && (
              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={e => handleActionClick(e, 'download', file)}
                  className="p-1 bg-white dark:bg-gray-800 rounded shadow hover:bg-gray-100 dark:hover:bg-gray-700"
                  title="Download"
                  aria-label="Download file"
                >
                  ⬇️
                </button>
              </div>
            )}

            {/* Status indicator */}
            {file.status !== 'ready' && (
              <div className="absolute bottom-2 right-2">
                <span className="text-xs">
                  {file.status === 'uploading' && '⏳'}
                  {file.status === 'processing' && '⚙️'}
                  {file.status === 'error' && '❌'}
                </span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );

  // Render list view
  const renderListView = () => (
    <div className="space-y-2">
      {files.map(file => {
        const isSelected = localSelectedIds.includes(file.id);

        return (
          <div
            key={file.id}
            className={`
              relative group cursor-pointer
              border rounded-lg p-4
              transition-all duration-200
              ${
                isSelected
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }
            `}
            onClick={() => handleFileClick(file)}
          >
            <div className="flex items-center gap-4">
              {/* Selection checkbox */}
              {selectMode && (
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => toggleFileSelection(file.id)}
                  className="w-4 h-4 rounded"
                  aria-label={`Select ${file.filename}`}
                />
              )}

              {/* Icon/Thumbnail */}
              <div className="flex-shrink-0">
                {file.thumbnailUrl ? (
                  <img
                    src={file.thumbnailUrl}
                    alt={file.filename}
                    className="w-12 h-12 object-cover rounded"
                  />
                ) : (
                  <span className="text-3xl">{getFileIcon(file)}</span>
                )}
              </div>

              {/* File info */}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 dark:text-gray-100 truncate">
                  {file.filename}
                </p>
                <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                  <span>{formatBytes(file.size)}</span>
                  <span>{formatDate(file.uploadedAt)}</span>
                  {file.tags.length > 0 && (
                    <div className="flex items-center gap-1">
                      {file.tags.slice(0, 2).map(tag => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                      {file.tags.length > 2 && (
                        <span className="text-xs">+{file.tags.length - 2}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Status */}
              {file.status !== 'ready' && (
                <div className="flex-shrink-0">
                  <span className="text-xl">
                    {file.status === 'uploading' && '⏳'}
                    {file.status === 'processing' && '⚙️'}
                    {file.status === 'error' && '❌'}
                  </span>
                </div>
              )}

              {/* Actions */}
              {!selectMode && (
                <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={e => handleActionClick(e, 'view', file)}
                      className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                      title="View"
                      aria-label="View file"
                    >
                      👁️
                    </button>
                    <button
                      onClick={e => handleActionClick(e, 'download', file)}
                      className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                      title="Download"
                      aria-label="Download file"
                    >
                      ⬇️
                    </button>
                    <button
                      onClick={e => handleActionClick(e, 'share', file)}
                      className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                      title="Share"
                      aria-label="Share file"
                    >
                      🔗
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="text-4xl mb-2">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading files...</p>
        </div>
      </div>
    );
  }

  if (files.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="text-6xl mb-4">📁</div>
          <p className="text-xl font-medium text-gray-900 dark:text-gray-100 mb-2">
            No files yet
          </p>
          <p className="text-gray-600 dark:text-gray-400">
            Upload files to get started
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`file-list ${className}`}>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {files.length} file{files.length !== 1 ? 's' : ''}
          </p>
          {localSelectedIds.length > 0 && (
            <p className="text-sm text-blue-600 dark:text-blue-400">
              {localSelectedIds.length} selected
            </p>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Selection controls */}
          {selectMode && (
            <>
              <button
                onClick={selectAll}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                Select all
              </button>
              <button
                onClick={clearSelection}
                className="text-sm text-gray-600 dark:text-gray-400 hover:underline"
              >
                Clear
              </button>
            </>
          )}

          {/* Select mode toggle */}
          <button
            onClick={toggleSelectMode}
            className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
          >
            {selectMode ? 'Done' : 'Select'}
          </button>

          {/* Bulk actions */}
          {selectMode && localSelectedIds.length > 0 && onBulkAction && (
            <div className="flex items-center gap-1 ml-2 pl-2 border-l border-gray-300 dark:border-gray-600">
              <button
                onClick={() => onBulkAction('download', localSelectedIds)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                title="Download selected"
                aria-label="Download selected files"
              >
                ⬇️
              </button>
              <button
                onClick={() => onBulkAction('delete', localSelectedIds)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-red-600 dark:text-red-400"
                title="Delete selected"
                aria-label="Delete selected files"
              >
                🗑️
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Files */}
      {view === 'grid' ? renderGridView() : renderListView()}
    </div>
  );
};

export default FileList;

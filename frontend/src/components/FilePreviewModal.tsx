/**
 * FilePreviewModal Component
 * 
 * Full-screen modal for previewing files with actions
 */

import React, { useState, useEffect } from 'react';
import { FilePreviewModalProps, FilePreviewData, PreviewType } from '../types/fileManagement';

const FilePreviewModal: React.FC<FilePreviewModalProps> = ({
  file,
  open,
  onClose,
  onDownload,
  onDelete,
  onShare,
}) => {
  const [previewData, setPreviewData] = useState<FilePreviewData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load preview data when modal opens
  useEffect(() => {
    if (open && file) {
      loadPreview();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, file]);

  // Load preview data from server
  const loadPreview = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/files/${file.id}/preview`);
      if (!response.ok) {
        throw new Error('Failed to load preview');
      }

      const data = await response.json();
      setPreviewData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Get preview type based on file type
  const getPreviewType = (): PreviewType => {
    const type = file.type.toLowerCase();
    
    if (type.startsWith('image/')) return 'image';
    if (type === 'application/pdf') return 'pdf';
    if (type === 'application/json') return 'json';
    if (type === 'text/csv' || file.extension === 'csv') return 'csv';
    if (type.startsWith('text/')) return 'text';
    if (type.includes('markdown') || file.extension === 'md') return 'markdown';
    if (
      ['js', 'ts', 'tsx', 'jsx', 'py', 'java', 'cpp', 'c', 'css', 'html'].includes(
        file.extension
      )
    ) {
      return 'code';
    }
    
    return 'none';
  };

  // Render preview content
  const renderPreview = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="text-6xl mb-4">⏳</div>
            <p className="text-gray-600 dark:text-gray-400">Loading preview...</p>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="text-6xl mb-4">❌</div>
            <p className="text-red-600 dark:text-red-400 mb-2">{error}</p>
            <button
              onClick={loadPreview}
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              Try again
            </button>
          </div>
        </div>
      );
    }

    const previewType = getPreviewType();

    switch (previewType) {
      case 'image':
        return (
          <div className="flex items-center justify-center h-full bg-gray-100 dark:bg-gray-900">
            <img
              src={file.url}
              alt={file.filename}
              className="max-h-full max-w-full object-contain"
            />
          </div>
        );

      case 'pdf':
        return (
          <iframe
            src={file.url}
            title={file.filename}
            className="w-full h-full"
          />
        );

      case 'csv':
        if (previewData?.type === 'csv') {
          const data = previewData.data as { headers: string[]; rows: unknown[][] };
          return (
            <div className="overflow-auto h-full p-4">
              <div className="mb-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Showing first 100 rows
                </p>
              </div>
              <table className="min-w-full border-collapse">
                <thead>
                  <tr className="bg-gray-100 dark:bg-gray-800">
                    {data.headers.map((header, i) => (
                      <th
                        key={i}
                        className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left text-sm font-medium"
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.rows.map((row, i) => (
                    <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                      {row.map((cell, j) => (
                        <td
                          key={j}
                          className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm"
                        >
                          {String(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }
        break;

      case 'json':
        if (previewData?.data) {
          return (
            <div className="overflow-auto h-full p-4">
              <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded">
                <code className="text-sm">
                  {JSON.stringify(previewData.data, null, 2)}
                </code>
              </pre>
            </div>
          );
        }
        break;

      case 'text':
      case 'code':
      case 'markdown':
        if (previewData?.data) {
          return (
            <div className="overflow-auto h-full p-4">
              <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded whitespace-pre-wrap">
                <code className="text-sm">{String(previewData.data)}</code>
              </pre>
            </div>
          );
        }
        break;

      default:
        return (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-6xl mb-4">📄</div>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Preview not available for this file type
              </p>
              {onDownload && (
                <button
                  onClick={onDownload}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Download to view
                </button>
              )}
            </div>
          </div>
        );
    }

    return null;
  };

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
    return new Date(date).toLocaleString();
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
      onClick={onClose}
    >
      <div
        className="relative w-full h-full max-w-7xl max-h-screen m-4 bg-white dark:bg-gray-800 rounded-lg shadow-xl flex flex-col"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex-1 min-w-0 mr-4">
            <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100 truncate">
              {file.filename}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {formatBytes(file.size)} • Uploaded {formatDate(file.uploadedAt)}
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {onDownload && (
              <button
                onClick={onDownload}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                title="Download"
                aria-label="Download file"
              >
                ⬇️
              </button>
            )}
            {onShare && (
              <button
                onClick={onShare}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                title="Share"
                aria-label="Share file"
              >
                🔗
              </button>
            )}
            {onDelete && (
              <button
                onClick={onDelete}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-red-600 dark:text-red-400"
                title="Delete"
                aria-label="Delete file"
              >
                🗑️
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              title="Close"
              aria-label="Close preview"
            >
              ❌
            </button>
          </div>
        </div>

        {/* Preview content */}
        <div className="flex-1 overflow-hidden">{renderPreview()}</div>

        {/* Footer with metadata */}
        {file.tags.length > 0 && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Tags:</span>
              {file.tags.map(tag => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FilePreviewModal;

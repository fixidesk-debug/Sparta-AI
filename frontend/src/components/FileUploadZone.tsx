/**
 * FileUploadZone Component
 * 
 * Drag-and-drop file upload zone with validation and preview
 */

import React, { useState, useRef, useCallback, useMemo } from 'react';
import { FileUploadZoneProps } from '../types/fileManagement';

// Sanitizer to avoid log injection and noisy outputs
const sanitizeForLog = (v: unknown) => {
  try {
    const s = String(v ?? '');
    return s.replace(/[\x00-\x1F\x7F]+/g, ' ').slice(0, 1000);
  } catch {
    return 'unserializable';
  }
};

// Pure helper moved out to avoid re-creation per render
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

const FileUploadZone: React.FC<FileUploadZoneProps> = ({
  onFilesSelected,
  onUploadComplete,
  config,
  accept = '*',
  multiple = true,
  disabled = false,
  className = '',
}) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [isDragReject, setIsDragReject] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Validate file against config
  const validateFile = useCallback(
    (file: File): { valid: boolean; error?: string } => {
      if (!config) return { valid: true };

      // Check size
      if (config.maxFileSize && file.size > config.maxFileSize) {
        return {
          valid: false,
          error: `File size exceeds ${formatBytes(config.maxFileSize)}`,
        };
      }

      // Check type
      if (
        config.allowedTypes &&
        config.allowedTypes[0] !== '*' &&
        !config.allowedTypes.some(type => file.type.startsWith(type))
      ) {
        return {
          valid: false,
          error: `File type ${file.type} is not allowed`,
        };
      }

      // Check extension
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (
        extension &&
        config.allowedExtensions &&
        config.allowedExtensions[0] !== '*' &&
        !config.allowedExtensions.includes(extension)
      ) {
        return {
          valid: false,
          error: `File extension .${extension} is not allowed`,
        };
      }

      return { valid: true };
    },
    [config]
  );

  // Handle drag enter
  const handleDragEnter = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();

      if (disabled) return;

      setIsDragActive(true);

      // Check if dragged items are files
      try {
        const hasFiles = Array.from(e.dataTransfer.items).some(
          item => item.kind === 'file'
        );

        if (!hasFiles) {
          setIsDragReject(true);
        }
      } catch (err) {
        console.error('handleDragEnter failed:', sanitizeForLog(err));
      }
    },
    [disabled]
  );

  // Handle drag over
  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();

      if (disabled) return;

      try {
        // Set dropEffect for visual feedback
        e.dataTransfer.dropEffect = isDragReject ? 'none' : 'copy';
      } catch (err) {
        console.error('handleDragOver failed:', sanitizeForLog(err));
      }
    },
    [disabled, isDragReject]
  );

  // Handle drag leave
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    // Only reset if leaving the main container
    if (e.currentTarget === e.target) {
      setIsDragActive(false);
      setIsDragReject(false);
    }
  }, []);

  // Handle drop
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();

      setIsDragActive(false);
      setIsDragReject(false);

      if (disabled) return;

      try {
        // Get files from drop
        const droppedFiles = Array.from(e.dataTransfer.files);

        if (droppedFiles.length === 0) return;

        // Validate and filter files
        const validFiles: File[] = [];
        const errors: string[] = [];

        droppedFiles.forEach(file => {
          const validation = validateFile(file);
          if (validation.valid) {
            validFiles.push(file);
          } else {
            errors.push(`${sanitizeForLog(file.name)}: ${sanitizeForLog(validation.error)}`);
          }
        });

        // Show errors if any (sanitize displayed content)
        if (errors.length > 0) {
          console.error('File validation errors:', sanitizeForLog(errors.join('; ')));
          try {
            alert(`Some files were rejected:\n${errors.join('\n')}`);
          } catch (err) {
            console.warn('Unable to show alert for rejected files');
          }
        }

        // Call callback with valid files (guard external callback)
        if (validFiles.length > 0) {
          try {
            if (!multiple && validFiles.length > 1) {
              onFilesSelected([validFiles[0]]);
            } else {
              onFilesSelected(validFiles);
            }
          } catch (err) {
            console.error('onFilesSelected failed:', sanitizeForLog(err));
          }
        }
      } catch (err) {
        console.error('handleDrop failed:', sanitizeForLog(err));
      }
    },
    [disabled, multiple, validateFile, onFilesSelected]
  );

  // Handle file input change
  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      try {
        const selectedFiles = e.target.files;
        if (!selectedFiles || selectedFiles.length === 0) return;

        const filesArray = Array.from(selectedFiles);

        // Validate files
        const validFiles: File[] = [];
        const errors: string[] = [];

        filesArray.forEach(file => {
          const validation = validateFile(file);
          if (validation.valid) {
            validFiles.push(file);
          } else {
            errors.push(`${sanitizeForLog(file.name)}: ${sanitizeForLog(validation.error)}`);
          }
        });

        // Show errors if any
        if (errors.length > 0) {
          console.error('File validation errors:', sanitizeForLog(errors.join('; ')));
          try {
            alert(`Some files were rejected:\n${errors.join('\n')}`);
          } catch (err) {
            console.warn('Unable to show alert for rejected files');
          }
        }

        // Call callback with valid files
        if (validFiles.length > 0) {
          try {
            onFilesSelected(validFiles);
          } catch (err) {
            console.error('onFilesSelected failed:', sanitizeForLog(err));
          }
        }

        // Reset input
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } catch (err) {
        console.error('handleFileInputChange failed:', sanitizeForLog(err));
      }
    },
    [validateFile, onFilesSelected]
  );

  // Handle click to open file dialog
  const handleClick = useCallback(() => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  }, [disabled]);

  // Get accept string for input (memoized)
  const acceptString = useMemo((): string => {
    if (accept !== '*') return accept;
    if (!config?.allowedExtensions || config.allowedExtensions[0] === '*') {
      return '*';
    }
    return config.allowedExtensions.map(ext => `.${ext}`).join(',');
  }, [accept, config?.allowedExtensions]);

  return (
    <div
      className={`
        file-upload-zone
        relative
        border-2 border-dashed rounded-lg
        transition-all duration-200
        ${
          isDragActive
            ? isDragReject
              ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
              : 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept={acceptString}
        multiple={multiple}
        disabled={disabled}
        onChange={handleFileInputChange}
        aria-label="File upload input"
      />

      <div className="flex flex-col items-center justify-center p-8 text-center">
        {/* Icon */}
        <div
          className={`
            mb-4 text-5xl
            ${
              isDragActive
                ? isDragReject
                  ? 'text-red-500'
                  : 'text-blue-500'
                : 'text-gray-400 dark:text-gray-500'
            }
          `}
        >
          {isDragReject ? '🚫' : '📁'}
        </div>

        {/* Text */}
        <div className="mb-2">
          <p className="text-lg font-medium text-gray-900 dark:text-gray-100">
            {isDragActive
              ? isDragReject
                ? 'Invalid files'
                : 'Drop files here'
              : 'Drag and drop files here'}
          </p>
          {!disabled && (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              or click to browse
            </p>
          )}
        </div>

        {/* File requirements */}
        {config && (
          <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
            {config.maxFileSize && (
              <p>Maximum file size: {formatBytes(config.maxFileSize)}</p>
            )}
            {config.allowedExtensions && config.allowedExtensions[0] !== '*' && (
              <p>
                Allowed types:{' '}
                {config.allowedExtensions.map(ext => `.${ext}`).join(', ')}
              </p>
            )}
            {!multiple && <p>Single file only</p>}
          </div>
        )}
      </div>

      {/* Overlay for drag active state */}
      {isDragActive && (
        <div
          className={`
            absolute inset-0 rounded-lg
            flex items-center justify-center
            ${
              isDragReject
                ? 'bg-red-500/10'
                : 'bg-blue-500/10'
            }
          `}
        >
          <div
            className={`
              text-6xl
              ${isDragReject ? 'text-red-500' : 'text-blue-500'}
            `}
          >
            {isDragReject ? '🚫' : '⬇️'}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploadZone;

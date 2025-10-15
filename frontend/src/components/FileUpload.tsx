/**
 * FileUpload Component
 * Drag-and-drop file upload with progress tracking and validation
 * Enhanced version for Sparta AI chat interface
 */

import React, { useCallback, useState, useRef, useMemo } from 'react';
import { Attachment } from '../types/chat';

interface FileUploadProps {
  onFileSelect: (files: File[]) => void;
  onUploadProgress?: (fileId: string, progress: number) => void;
  maxFileSize?: number; // in MB
  acceptedFormats?: string[];
  maxFiles?: number;
  disabled?: boolean;
  className?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onUploadProgress,
  maxFileSize = 500,
  acceptedFormats = ['.csv', '.xlsx', '.xls', '.json', '.parquet', '.tsv'],
  maxFiles = 5,
  disabled = false,
  className = '',
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<Attachment[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dragCounterRef = useRef(0);

  // Helper: sanitize strings before logging (mitigate log injection CWE-117)
  const sanitizeForLog = useCallback((v: unknown) => {
    try {
      if (v === null || v === undefined) return String(v);
      const s = typeof v === 'string' ? v : JSON.stringify(v);
      return s.replace(/[\r\n]+/g, ' ');
    } catch (err) {
      return '<<unserializable>>';
    }
  }, []);

  const validateFile = useCallback((file: File): string | null => {
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxFileSize) {
      return `File "${file.name}" exceeds maximum size of ${maxFileSize}MB`;
    }

    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedFormats.includes(fileExtension)) {
      return `File "${file.name}" has unsupported format`;
    }

    return null;
  }, [maxFileSize, acceptedFormats]);
  // Note: do not capture `files` directly in the dependency list to avoid
  // unnecessary re-creations; use functional state updates instead.
  const handleFiles = useCallback(
    (fileList: FileList) => {
      try {
        const newErrors: string[] = [];
        const validFiles: File[] = [];

        // Check max files against current state immutably
        // (use files.length from state at call time)
        // We'll compute current length inside a functional update below.
        Array.from(fileList).forEach((file) => {
          const error = validateFile(file);
          if (error) {
            newErrors.push(error);
          } else {
            validFiles.push(file);
          }
        });

        if (newErrors.length > 0) {
          setErrors(newErrors);
        } else {
          setErrors([]);
        }

        if (validFiles.length > 0) {
          const newAttachments: Attachment[] = validFiles.map((file) => ({
            id: `${Date.now()}-${file.name}`,
            filename: file.name,
            name: file.name,
            size: file.size,
            type: file.type || 'application/octet-stream',
            uploadProgress: 0,
            uploadStatus: 'pending' as const,
          }));

          setFiles((prev) => {
            if (prev.length + newAttachments.length > maxFiles) {
              // Preserve previous and add an error instead of silently failing
              setErrors([`Maximum ${maxFiles} files allowed`]);
              return prev;
            }
            return [...prev, ...newAttachments];
          });

          // Guard external callback
          try {
            onFileSelect(validFiles);
          } catch (cbErr) {
            console.error('onFileSelect callback failed:', sanitizeForLog(cbErr));
          }
        }
      } catch (err) {
        console.error('handleFiles error:', sanitizeForLog(err));
        setErrors(['An unexpected error occurred while processing files.']);
      }
    },
    [maxFiles, onFileSelect, validateFile, sanitizeForLog]
  );

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current += 1;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current -= 1;
    if (dragCounterRef.current === 0) {
      setIsDragging(false);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      dragCounterRef.current = 0;

      if (disabled) return;

      try {
        const { files } = e.dataTransfer;
        if (files && files.length > 0) {
          handleFiles(files);
        }
      } catch (err) {
        console.error('handleDrop error:', sanitizeForLog(err));
        setErrors(['Failed to process dropped files.']);
      }
    },
    [disabled, handleFiles, sanitizeForLog]
  );

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      try {
        if (e.target.files && e.target.files.length > 0) {
          handleFiles(e.target.files);
        }
      } catch (err) {
        console.error('file input change error:', sanitizeForLog(err));
        setErrors(['Failed to read selected files.']);
      }
    },
    [handleFiles]
  );

  const handleRemoveFile = useCallback((fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  }, []);

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Move out of render-heavy contexts; stable helper
  const formatFileSize = useCallback((bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }, []);

  const acceptString = useMemo(() => acceptedFormats.join(','), [acceptedFormats]);

  return (
    <div className={`file-upload ${className}`}>
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-6 transition-all
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-label="Upload files"
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedFormats.join(',')}
          onChange={handleFileInputChange}
          className="hidden"
          disabled={disabled}
          aria-label="File upload input"
          title="Select files to upload"
        />

        <div className="flex flex-col items-center justify-center text-center">
          <svg
            className={`w-12 h-12 mb-4 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>

          <p className="text-lg font-semibold text-gray-700 mb-1">
            {isDragging ? 'Drop files here' : 'Drop files to upload'}
          </p>

          <p className="text-sm text-gray-500 mb-2">or click to browse</p>

          <p className="text-xs text-gray-400">
            Max {maxFileSize}MB • {acceptedFormats.join(', ')}
          </p>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="mt-3 space-y-1">
          {errors.map((error, index) => (
            <div key={index} className="text-sm text-red-600">{error}</div>
          ))}
        </div>
      )}

      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((file) => (
            <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <p className="text-sm font-medium">{file.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveFile(file.id);
                }}
                className="text-red-500 hover:text-red-700"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;

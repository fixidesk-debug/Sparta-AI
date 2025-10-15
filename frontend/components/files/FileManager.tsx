import React, { useState, useCallback, useRef } from 'react';
import { 
  Upload, 
  File, 
  Folder, 
  FileText, 
  Image as ImageIcon, 
  Archive, 
  Grid as GridIcon,
  List,
  Search,
  X,
  Check,
  AlertCircle,
  Download,
  Trash2,
  MoreVertical,
  RefreshCw
} from '../icons';
import './FileManager.scss';

export interface FileItem {
  id: string;
  name: string;
  type: 'csv' | 'excel' | 'json' | 'image' | 'pdf' | 'archive' | 'folder' | 'unknown';
  size: number;
  uploadDate: Date;
  thumbnail?: string;
  selected?: boolean;
}

interface FileManagerProps {
  files?: FileItem[];
  onUpload?: (files: File[]) => void;
  onDelete?: (fileIds: string[]) => void;
  onDownload?: (fileIds: string[]) => void;
  maxFileSize?: number;
  allowedTypes?: string[];
}

type ViewMode = 'grid' | 'list';

const FileManager: React.FC<FileManagerProps> = ({
  files = [],
  onUpload,
  onDelete,
  onDownload,
  maxFileSize = 100 * 1024 * 1024, // 100MB
  allowedTypes = ['*']
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date');
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const getFileIcon = (type: FileItem['type']) => {
    const iconProps = { size: 48, strokeWidth: 1.5 };
    
    switch (type) {
      case 'csv':
      case 'excel':
        return <FileText {...iconProps} />;
      case 'json':
        return <FileText {...iconProps} />;
      case 'image':
        return <ImageIcon {...iconProps} />;
      case 'pdf':
        return <FileText {...iconProps} />;
      case 'archive':
        return <Archive {...iconProps} />;
      case 'folder':
        return <Folder {...iconProps} />;
      default:
        return <File {...iconProps} />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (date: Date): string => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.currentTarget === e.target) {
      setIsDragging(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFileUpload(droppedFiles);
  }, []);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      handleFileUpload(selectedFiles);
    }
  };

  const handleFileUpload = async (uploadedFiles: File[]) => {
    setError(null);
    
    // Validate file sizes
    const oversizedFiles = uploadedFiles.filter(f => f.size > maxFileSize);
    if (oversizedFiles.length > 0) {
      setError(`Some files exceed the maximum size of ${formatFileSize(maxFileSize)}`);
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setUploadProgress(i);
      }

      if (onUpload) {
        onUpload(uploadedFiles);
      }

      setSuccessMessage(`Successfully uploaded ${uploadedFiles.length} file(s)`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const toggleFileSelection = (fileId: string) => {
    const newSelected = new Set(selectedFiles);
    if (newSelected.has(fileId)) {
      newSelected.delete(fileId);
    } else {
      newSelected.add(fileId);
    }
    setSelectedFiles(newSelected);
  };

  const selectAll = () => {
    if (selectedFiles.size === files.length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(files.map(f => f.id)));
    }
  };

  const handleBulkDelete = () => {
    if (onDelete && selectedFiles.size > 0) {
      onDelete(Array.from(selectedFiles));
      setSelectedFiles(new Set());
    }
  };

  const handleBulkDownload = () => {
    if (onDownload && selectedFiles.size > 0) {
      onDownload(Array.from(selectedFiles));
    }
  };

  const filteredFiles = files.filter(file =>
    file.name.toLowerCase().includes(searchQuery.toLowerCase())
  ).sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'size':
        return b.size - a.size;
      case 'date':
      default:
        return b.uploadDate.getTime() - a.uploadDate.getTime();
    }
  });

  return (
    <div className="file-manager">
      {/* Header */}
      <div className="file-manager__header">
        <div className="file-manager__header-left">
          <h2 className="file-manager__title">File Manager</h2>
          <span className="file-manager__count">{files.length} files</span>
        </div>
        
        <div className="file-manager__header-right">
          {/* Search */}
          <div className="file-manager__search">
              <Search size={18} />
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="file-manager__search-input"
                aria-label="Search files"
              />
            {searchQuery && (
              <button
                  onClick={() => setSearchQuery('')}
                  className="file-manager__search-clear"
                  aria-label="Clear search"
                  title="Clear search"
                >
                  <X size={16} />
                </button>
            )}
          </div>

          {/* View Toggle */}
          <div className="file-manager__view-toggle">
            <button
              className={`file-manager__view-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
              aria-label="Grid view"
              title="Grid view"
            >
              <GridIcon size={18} />
            </button>
            <button
              className={`file-manager__view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
              aria-label="List view"
              title="List view"
            >
              <List size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="file-manager__alert file-manager__alert--error">
          <AlertCircle size={18} />
          <span>{error}</span>
          <button onClick={() => setError(null)} aria-label="Close error" title="Close">
            <X size={16} />
          </button>
        </div>
      )}

      {successMessage && (
        <div className="file-manager__alert file-manager__alert--success">
          <Check size={18} />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Bulk Actions Bar */}
      {selectedFiles.size > 0 && (
        <div className="file-manager__bulk-actions">
          <div className="file-manager__bulk-info">
            <Check size={18} />
            <span>{selectedFiles.size} selected</span>
          </div>
          <div className="file-manager__bulk-buttons">
            <button onClick={handleBulkDownload} className="file-manager__bulk-btn">
              <Download size={18} />
              Download
            </button>
            <button onClick={handleBulkDelete} className="file-manager__bulk-btn file-manager__bulk-btn--danger">
              <Trash2 size={18} />
              Delete
            </button>
            <button onClick={() => setSelectedFiles(new Set())} className="file-manager__bulk-btn">
              <X size={18} />
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Upload Zone */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileInputChange}
        className="file-manager__file-input"
        aria-label="Upload files"
      />
      <div
        className={`file-manager__upload-zone ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        tabIndex={0}
        aria-label="Upload files"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            fileInputRef.current?.click();
          }
        }}
      >
        
        {isUploading ? (
          <div className="file-manager__upload-progress">
            <div className="file-manager__upload-spinner">
              <RefreshCw size={48} className="spinning" />
            </div>
            <p className="file-manager__upload-text">Uploading files...</p>
            <div className="file-manager__progress-bar">
              <progress
                className="file-manager__progress"
                value={uploadProgress}
                max={100}
                aria-label={`Upload progress ${uploadProgress}%`}
              />
            </div>
            <span className="file-manager__progress-percent">{uploadProgress}%</span>
          </div>
        ) : (
          <>
            <div className="file-manager__upload-icon">
              <Upload size={48} />
            </div>
            <p className="file-manager__upload-text">
              {isDragging ? 'Drop files here' : 'Drag & drop files here'}
            </p>
            <p className="file-manager__upload-subtext">
              or click to browse
            </p>
            <span className="file-manager__upload-limit">
              Max file size: {formatFileSize(maxFileSize)}
            </span>
          </>
        )}
      </div>

      {/* File Content */}
      {files.length === 0 ? (
        <div className="file-manager__empty">
          <div className="file-manager__empty-icon">
            <Folder size={64} />
          </div>
          <h3 className="file-manager__empty-title">No files yet</h3>
          <p className="file-manager__empty-text">
            Upload your first file to get started
          </p>
        </div>
      ) : (
        <>
          {viewMode === 'grid' ? (
            <div className="file-manager__grid">
              {filteredFiles.map((file) => (
                <div
                  key={file.id}
                  className={`file-card ${selectedFiles.has(file.id) ? 'selected' : ''}`}
                  onClick={() => toggleFileSelection(file.id)}
                >
                  {selectedFiles.has(file.id) && (
                    <div className="file-card__selection-badge">
                      <Check size={16} />
                    </div>
                  )}
                  
                  <div className={`file-card__thumbnail file-card__thumbnail--${file.type}`}>
                    {file.thumbnail ? (
                      <img src={file.thumbnail} alt={file.name} />
                    ) : (
                      <div className="file-card__icon">
                        {getFileIcon(file.type)}
                      </div>
                    )}
                  </div>
                  
                  <div className="file-card__metadata">
                    <h4 className="file-card__name" title={file.name}>
                      {file.name}
                    </h4>
                    <div className="file-card__info">
                      <span className="file-card__size">{formatFileSize(file.size)}</span>
                      <span className="file-card__separator">•</span>
                      <span className="file-card__date">{formatDate(file.uploadDate)}</span>
                    </div>
                  </div>

                  <button
                    className="file-card__actions"
                    onClick={(e) => e.stopPropagation()}
                    aria-label={`More options for ${file.name}`}
                    title={`More options for ${file.name}`}
                  >
                    <MoreVertical size={16} />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="file-manager__list">
              <div className="file-list__header">
                <div className="file-list__header-cell file-list__header-cell--checkbox">
                    <input
                      type="checkbox"
                      checked={selectedFiles.size === files.length}
                      onChange={selectAll}
                      className="file-list__checkbox"
                      aria-label="Select all files"
                    />
                </div>
                <div 
                  className="file-list__header-cell file-list__header-cell--name"
                  onClick={() => setSortBy('name')}
                >
                  Name {sortBy === 'name' && '↓'}
                </div>
                <div 
                  className="file-list__header-cell file-list__header-cell--size"
                  onClick={() => setSortBy('size')}
                >
                  Size {sortBy === 'size' && '↓'}
                </div>
                <div 
                  className="file-list__header-cell file-list__header-cell--date"
                  onClick={() => setSortBy('date')}
                >
                  Modified {sortBy === 'date' && '↓'}
                </div>
                <div className="file-list__header-cell file-list__header-cell--actions">
                  Actions
                </div>
              </div>

              <div className="file-list__body">
                {filteredFiles.map((file, index) => (
                  <div
                    key={file.id}
                    className={`file-list__row ${selectedFiles.has(file.id) ? 'selected' : ''} ${index % 2 === 0 ? 'even' : 'odd'}`}
                  >
                    <div className="file-list__cell file-list__cell--checkbox">
                      <input
                        type="checkbox"
                        checked={selectedFiles.has(file.id)}
                        onChange={() => toggleFileSelection(file.id)}
                        className="file-list__checkbox"
                        aria-label={`Select file ${file.name}`}
                      />
                    </div>
                    <div className="file-list__cell file-list__cell--name">
                      <div className={`file-list__icon file-list__icon--${file.type}`}>
                        {getFileIcon(file.type)}
                      </div>
                      <span className="file-list__name" title={file.name}>
                        {file.name}
                      </span>
                    </div>
                    <div className="file-list__cell file-list__cell--size">
                      {formatFileSize(file.size)}
                    </div>
                    <div className="file-list__cell file-list__cell--date">
                      {formatDate(file.uploadDate)}
                    </div>
                    <div className="file-list__cell file-list__cell--actions">
                      <button className="file-list__action-btn" title="Download" aria-label={`Download ${file.name}`}>
                        <Download size={16} />
                      </button>
                      <button className="file-list__action-btn" title="Delete" aria-label={`Delete ${file.name}`}>
                        <Trash2 size={16} />
                      </button>
                      <button className="file-list__action-btn" title="More" aria-label={`More options for ${file.name}`}>
                        <MoreVertical size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default FileManager;

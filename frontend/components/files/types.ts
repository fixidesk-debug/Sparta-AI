/**
 * File Manager Component Type Definitions
 * Sparta AI - Modern File Management Interface
 */

/**
 * Supported file types with specific visual styling
 */
export type FileType = 
  | 'csv'      // CSV data files - Green gradient
  | 'excel'    // Excel spreadsheets - Blue gradient
  | 'json'     // JSON configuration files - Purple gradient
  | 'image'    // Image files (PNG, JPG, etc.) - Pink gradient
  | 'pdf'      // PDF documents - Red gradient
  | 'archive'  // Compressed archives (ZIP, RAR, etc.) - Gray gradient
  | 'folder'   // Directory/folder - Yellow gradient
  | 'unknown'; // Unknown file types - Neutral gradient

/**
 * File item interface representing a single file in the system
 */
export interface FileItem {
  /** Unique identifier for the file */
  id: string;
  
  /** Display name of the file */
  name: string;
  
  /** File type for visual styling and icon selection */
  type: FileType;
  
  /** File size in bytes */
  size: number;
  
  /** Upload or last modification date */
  uploadDate: Date;
  
  /** Optional thumbnail URL for image files */
  thumbnail?: string;
  
  /** Selection state (managed internally by component) */
  selected?: boolean;
  
  /** Optional metadata */
  metadata?: {
    /** Original file extension */
    extension?: string;
    
    /** MIME type */
    mimeType?: string;
    
    /** File description or notes */
    description?: string;
    
    /** Tags for categorization */
    tags?: string[];
    
    /** Sharing/permission level */
    accessLevel?: 'private' | 'shared' | 'public';
  };
}

/**
 * View mode for file display
 */
export type ViewMode = 'grid' | 'list';

/**
 * Sort options for file listing
 */
export type SortBy = 'name' | 'date' | 'size' | 'type';

/**
 * Sort direction
 */
export type SortDirection = 'asc' | 'desc';

/**
 * File Manager component props
 */
export interface FileManagerProps {
  /** Array of files to display */
  files?: FileItem[];
  
  /** Callback when files are uploaded */
  onUpload?: (files: File[]) => void | Promise<void>;
  
  /** Callback when files are deleted */
  onDelete?: (fileIds: string[]) => void | Promise<void>;
  
  /** Callback when files are downloaded */
  onDownload?: (fileIds: string[]) => void | Promise<void>;
  
  /** Callback when a file is clicked/selected */
  onFileClick?: (file: FileItem) => void;
  
  /** Callback when files are selected (bulk selection) */
  onSelectionChange?: (selectedIds: string[]) => void;
  
  /** Maximum file size in bytes (default: 100MB) */
  maxFileSize?: number;
  
  /** Allowed file types/extensions (default: ['*'] for all) */
  allowedTypes?: string[];
  
  /** Enable multi-file selection (default: true) */
  multiSelect?: boolean;
  
  /** Show file actions (download, delete, etc.) (default: true) */
  showActions?: boolean;
  
  /** Custom CSS class name */
  className?: string;
  
  /** Loading state */
  isLoading?: boolean;
  
  /** Error message to display */
  error?: string | null;
  
  /** Success message to display */
  successMessage?: string | null;
}

/**
 * Upload state tracking
 */
export interface UploadState {
  /** Whether upload is in progress */
  isUploading: boolean;
  
  /** Upload progress percentage (0-100) */
  progress: number;
  
  /** Files currently being uploaded */
  files: File[];
  
  /** Error during upload */
  error?: string;
}

/**
 * File validation result
 */
export interface FileValidation {
  /** Whether the file is valid */
  isValid: boolean;
  
  /** Error message if invalid */
  error?: string;
  
  /** File that was validated */
  file: File;
}

/**
 * Bulk operation result
 */
export interface BulkOperationResult {
  /** Number of successful operations */
  success: number;
  
  /** Number of failed operations */
  failed: number;
  
  /** Total number of operations */
  total: number;
  
  /** Error messages for failed operations */
  errors?: string[];
}

/**
 * File filter options
 */
export interface FileFilterOptions {
  /** Search query string */
  query?: string;
  
  /** Filter by file type */
  type?: FileType | FileType[];
  
  /** Filter by date range */
  dateRange?: {
    start: Date;
    end: Date;
  };
  
  /** Filter by size range (in bytes) */
  sizeRange?: {
    min: number;
    max: number;
  };
  
  /** Filter by tags */
  tags?: string[];
}

/**
 * File manager configuration
 */
export interface FileManagerConfig {
  /** Theme configuration */
  theme?: {
    primaryColor?: string;
    borderRadius?: number;
    cardHoverScale?: number;
  };
  
  /** Feature flags */
  features?: {
    enableSearch?: boolean;
    enableSort?: boolean;
    enableFilters?: boolean;
    enableBulkActions?: boolean;
    enableDragDrop?: boolean;
  };
  
  /** Upload configuration */
  upload?: {
    maxFileSize?: number;
    maxFiles?: number;
    allowedTypes?: string[];
    chunkedUpload?: boolean;
    chunkSize?: number;
  };
  
  /** Display configuration */
  display?: {
    defaultView?: ViewMode;
    itemsPerPage?: number;
    showThumbnails?: boolean;
    showMetadata?: boolean;
  };
}

/**
 * File action handler types
 */
export type FileActionHandler = (fileId: string) => void | Promise<void>;
export type BulkActionHandler = (fileIds: string[]) => void | Promise<void>;
export type UploadHandler = (files: File[]) => void | Promise<void>;

/**
 * File manager event types
 */
export type FileManagerEvent =
  | { type: 'upload'; files: File[] }
  | { type: 'delete'; fileIds: string[] }
  | { type: 'download'; fileIds: string[] }
  | { type: 'select'; fileIds: string[] }
  | { type: 'view_change'; mode: ViewMode }
  | { type: 'sort'; sortBy: SortBy; direction: SortDirection }
  | { type: 'filter'; filters: FileFilterOptions }
  | { type: 'search'; query: string };

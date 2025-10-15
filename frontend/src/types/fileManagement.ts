/**
 * File Management Types for Sparta AI
 * 
 * Comprehensive type definitions for file upload, management, and organization
 */

// ============================================================================
// Core File Types
// ============================================================================

export interface FileItem {
  id: string;
  filename: string;
  originalName: string;
  size: number;
  type: string;
  mimeType: string;
  extension: string;
  uploadedAt: Date;
  updatedAt: Date;
  uploadedBy: string;
  
  // Storage
  path: string;
  url?: string;
  thumbnailUrl?: string;
  
  // Metadata
  metadata: FileMetadata;
  
  // Organization
  folderId?: string;
  tags: string[];
  description?: string;
  
  // Status
  status: FileStatus;
  version: number;
  
  // Permissions
  isPublic: boolean;
  sharedWith: string[];
  permissions: FilePermissions;
}

export type FileStatus = 
  | 'uploading'
  | 'processing'
  | 'ready'
  | 'error'
  | 'deleted';

export interface FileMetadata {
  // File properties
  encoding?: string;
  hash?: string;
  checksum?: string;
  
  // Data files
  rows?: number;
  columns?: number;
  columnNames?: string[];
  dataTypes?: Record<string, string>;
  
  // Images
  width?: number;
  height?: number;
  format?: string;
  
  // Documents
  pageCount?: number;
  author?: string;
  title?: string;
  
  // Custom metadata
  custom?: Record<string, unknown>;
}

export interface FilePermissions {
  read: boolean;
  write: boolean;
  delete: boolean;
  share: boolean;
}

// ============================================================================
// Upload Types
// ============================================================================

export interface UploadTask {
  id: string;
  file: File;
  status: UploadStatus;
  progress: number;
  uploadedBytes: number;
  totalBytes: number;
  speed: number; // bytes per second
  timeRemaining: number; // seconds
  startedAt: Date;
  completedAt?: Date;
  error?: UploadError;
  retryCount: number;
  chunks?: ChunkInfo[];
  abortController?: AbortController;
}

export type UploadStatus =
  | 'pending'
  | 'validating'
  | 'uploading'
  | 'processing'
  | 'completed'
  | 'paused'
  | 'cancelled'
  | 'error';

export interface ChunkInfo {
  index: number;
  start: number;
  end: number;
  size: number;
  uploaded: boolean;
  retries: number;
}

export interface UploadError {
  code: string;
  message: string;
  details?: string;
  recoverable: boolean;
  timestamp: Date;
}

export interface UploadConfig {
  // Validation
  maxFileSize: number; // bytes
  allowedTypes: string[];
  allowedExtensions: string[];
  
  // Chunking
  chunkSize: number; // bytes
  enableChunking: boolean;
  chunkingThreshold: number; // bytes
  
  // Network
  maxConcurrentUploads: number;
  maxRetries: number;
  retryDelay: number; // milliseconds
  timeout: number; // milliseconds
  
  // Processing
  generateThumbnails: boolean;
  extractMetadata: boolean;
  validateContent: boolean;
  
  // Callbacks
  onProgress?: (task: UploadTask) => void;
  onComplete?: (file: FileItem) => void;
  onError?: (error: UploadError) => void;
}

// ============================================================================
// Folder Types
// ============================================================================

export interface Folder {
  id: string;
  name: string;
  parentId?: string;
  path: string;
  createdAt: Date;
  updatedAt: Date;
  fileCount: number;
  totalSize: number;
  color?: string;
  icon?: string;
}

export interface FolderTree extends Folder {
  children: FolderTree[];
  files: FileItem[];
  expanded?: boolean;
}

// ============================================================================
// Search and Filter Types
// ============================================================================

export interface FileSearchQuery {
  query: string;
  filters: FileFilters;
  sortBy: FileSortField;
  sortOrder: 'asc' | 'desc';
  page: number;
  pageSize: number;
}

export interface FileFilters {
  types?: string[];
  extensions?: string[];
  tags?: string[];
  folderId?: string;
  uploadedBy?: string;
  dateRange?: {
    from: Date;
    to: Date;
  };
  sizeRange?: {
    min: number;
    max: number;
  };
  status?: FileStatus[];
}

export type FileSortField =
  | 'filename'
  | 'size'
  | 'uploadedAt'
  | 'updatedAt'
  | 'type';

export interface FileSearchResult {
  files: FileItem[];
  totalCount: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// ============================================================================
// Storage Types
// ============================================================================

export interface StorageQuota {
  used: number;
  total: number;
  available: number;
  percentage: number;
  
  // Breakdown
  byType: Record<string, number>;
  byFolder: Record<string, number>;
  
  // Limits
  maxFileSize: number;
  maxTotalSize: number;
}

export interface StorageStats {
  totalFiles: number;
  totalFolders: number;
  totalSize: number;
  
  // By type
  filesByType: Record<string, number>;
  sizeByType: Record<string, number>;
  
  // By date
  uploadsByDate: Record<string, number>;
  
  // Recent activity
  recentUploads: FileItem[];
  recentlyModified: FileItem[];
}

// ============================================================================
// Sharing Types
// ============================================================================

export interface ShareLink {
  id: string;
  fileId: string;
  url: string;
  token: string;
  createdAt: Date;
  expiresAt?: Date;
  accessCount: number;
  maxAccessCount?: number;
  password?: boolean;
  permissions: SharePermissions;
}

export interface SharePermissions {
  canView: boolean;
  canDownload: boolean;
  canEdit: boolean;
  canComment: boolean;
}

export interface ShareRequest {
  fileIds: string[];
  users?: string[];
  permissions: SharePermissions;
  expiresAt?: Date;
  message?: string;
}

// ============================================================================
// Version Types
// ============================================================================

export interface FileVersion {
  id: string;
  fileId: string;
  version: number;
  filename: string;
  size: number;
  uploadedAt: Date;
  uploadedBy: string;
  changes?: string;
  url: string;
}

export interface VersionHistory {
  fileId: string;
  currentVersion: number;
  versions: FileVersion[];
}

// ============================================================================
// Bulk Operations
// ============================================================================

export interface BulkOperation {
  id: string;
  type: BulkOperationType;
  fileIds: string[];
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  completedCount: number;
  failedCount: number;
  errors: Array<{ fileId: string; error: string }>;
  startedAt: Date;
  completedAt?: Date;
}

export type BulkOperationType =
  | 'delete'
  | 'move'
  | 'copy'
  | 'tag'
  | 'untag'
  | 'download'
  | 'share';

export interface BulkOperationRequest {
  type: BulkOperationType;
  fileIds: string[];
  params?: Record<string, unknown>;
}

// ============================================================================
// Preview Types
// ============================================================================

export interface FilePreviewData {
  type: PreviewType;
  data: unknown;
  metadata?: Record<string, unknown>;
}

export type PreviewType =
  | 'text'
  | 'csv'
  | 'json'
  | 'image'
  | 'pdf'
  | 'markdown'
  | 'code'
  | 'none';

export interface DataPreview {
  headers: string[];
  rows: unknown[][];
  totalRows: number;
  previewRows: number;
  dataTypes: Record<string, string>;
  statistics?: Record<string, StatsSummary>;
}

export interface StatsSummary {
  count: number;
  unique?: number;
  missing?: number;
  mean?: number;
  min?: number;
  max?: number;
  std?: number;
}

// ============================================================================
// Component Props
// ============================================================================

export interface FileUploadZoneProps {
  onFilesSelected: (files: File[]) => void;
  onUploadComplete?: (files: FileItem[]) => void;
  config?: Partial<UploadConfig>;
  accept?: string;
  multiple?: boolean;
  disabled?: boolean;
  className?: string;
}

export interface FileListProps {
  files: FileItem[];
  view: 'grid' | 'list';
  onFileSelect?: (file: FileItem) => void;
  onFileAction?: (action: FileAction, file: FileItem) => void;
  onBulkAction?: (action: BulkOperationType, fileIds: string[]) => void;
  selectedFileIds?: string[];
  sortBy?: FileSortField;
  sortOrder?: 'asc' | 'desc';
  loading?: boolean;
  className?: string;
}

export interface FilePreviewModalProps {
  file: FileItem;
  open: boolean;
  onClose: () => void;
  onDownload?: () => void;
  onDelete?: () => void;
  onShare?: () => void;
}

export interface ProgressTrackerProps {
  tasks: UploadTask[];
  onCancel?: (taskId: string) => void;
  onRetry?: (taskId: string) => void;
  onClear?: (taskId: string) => void;
  compact?: boolean;
  className?: string;
}

export interface FileMetadataProps {
  file: FileItem;
  editable?: boolean;
  onUpdate?: (metadata: Partial<FileItem>) => void;
  className?: string;
}

export interface StorageIndicatorProps {
  quota: StorageQuota;
  detailed?: boolean;
  onClick?: () => void;
  className?: string;
}

export interface FileActionsProps {
  file: FileItem;
  actions: FileAction[];
  onAction: (action: FileAction) => void;
  disabled?: boolean;
}

export type FileAction =
  | 'view'
  | 'download'
  | 'rename'
  | 'move'
  | 'copy'
  | 'share'
  | 'tag'
  | 'delete'
  | 'versions';

export interface FileSearchBarProps {
  onSearch: (query: FileSearchQuery) => void;
  filters?: FileFilters;
  placeholder?: string;
  className?: string;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface UploadInitRequest {
  filename: string;
  size: number;
  type: string;
  chunks?: number;
  folderId?: string;
}

export interface UploadInitResponse {
  uploadId: string;
  uploadUrl: string;
  chunkSize?: number;
}

export interface ChunkUploadRequest {
  uploadId: string;
  chunkIndex: number;
  chunk: Blob;
}

export interface UploadCompleteRequest {
  uploadId: string;
  filename: string;
  metadata?: Partial<FileMetadata>;
}

export interface FileUpdateRequest {
  filename?: string;
  description?: string;
  tags?: string[];
  folderId?: string;
  isPublic?: boolean;
}

// ============================================================================
// Validation Types
// ============================================================================

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// ============================================================================
// Event Types
// ============================================================================

export interface FileEvent {
  type: FileEventType;
  fileId: string;
  userId: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

export type FileEventType =
  | 'uploaded'
  | 'downloaded'
  | 'viewed'
  | 'modified'
  | 'deleted'
  | 'shared'
  | 'renamed'
  | 'moved';

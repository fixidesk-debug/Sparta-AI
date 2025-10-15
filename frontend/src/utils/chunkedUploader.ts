/**
 * Chunked File Uploader
 * 
 * Handles large file uploads with chunking, progress tracking, retry logic,
 * and pause/resume capabilities.
 */

import { 
  UploadTask, 
  UploadConfig, 
  ChunkInfo, 
  UploadError,
  UploadStatus,
  UploadInitRequest,
  UploadInitResponse,
  UploadCompleteRequest,
  FileItem
} from '../types/fileManagement';

// Default upload configuration
const DEFAULT_CONFIG: UploadConfig = {
  maxFileSize: 5 * 1024 * 1024 * 1024, // 5GB
  allowedTypes: ['*'],
  allowedExtensions: ['*'],
  chunkSize: 5 * 1024 * 1024, // 5MB chunks
  enableChunking: true,
  chunkingThreshold: 50 * 1024 * 1024, // 50MB
  maxConcurrentUploads: 3,
  maxRetries: 3,
  retryDelay: 1000,
  timeout: 30000,
  generateThumbnails: true,
  extractMetadata: true,
  validateContent: true,
};

export class ChunkedUploader {
  private config: UploadConfig;
  private tasks: Map<string, UploadTask>;
  private activeUploads: Set<string>;
  private queue: string[];

  constructor(config?: Partial<UploadConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.tasks = new Map();
    this.activeUploads = new Set();
    this.queue = [];
  }

  /**
   * Add file to upload queue
   */
  async addFile(file: File, folderId?: string): Promise<string> {
    // Validate file
    const validation = this.validateFile(file);
    if (!validation.valid) {
      throw new Error(validation.errors.join(', '));
    }

    // Create upload task
    const task: UploadTask = {
      id: this.generateId(),
      file,
      status: 'pending',
      progress: 0,
      uploadedBytes: 0,
      totalBytes: file.size,
      speed: 0,
      timeRemaining: 0,
      startedAt: new Date(),
      retryCount: 0,
      abortController: new AbortController(),
    };

    // Add chunks if file is large enough
    if (this.shouldUseChunking(file.size)) {
      task.chunks = this.createChunks(file.size);
    }

    this.tasks.set(task.id, task);
    this.queue.push(task.id);

    // Start processing queue
    this.processQueue();

    return task.id;
  }

  /**
   * Add multiple files
   */
  async addFiles(files: File[], folderId?: string): Promise<string[]> {
    const taskIds: string[] = [];
    for (const file of files) {
      try {
        const taskId = await this.addFile(file, folderId);
        taskIds.push(taskId);
      } catch (error) {
        console.error(`Failed to add file ${file.name}:`, error);
      }
    }
    return taskIds;
  }

  /**
   * Process upload queue
   */
  private async processQueue(): Promise<void> {
    while (
      this.queue.length > 0 &&
      this.activeUploads.size < this.config.maxConcurrentUploads
    ) {
      const taskId = this.queue.shift()!;
      const task = this.tasks.get(taskId);

      if (task && task.status === 'pending') {
        this.activeUploads.add(taskId);
        this.uploadTask(task).finally(() => {
          this.activeUploads.delete(taskId);
          this.processQueue();
        });
      }
    }
  }

  /**
   * Upload a single task
   */
  private async uploadTask(task: UploadTask): Promise<void> {
    try {
      this.updateTaskStatus(task, 'validating');

      // Initialize upload
      const initResponse = await this.initializeUpload(task);

      this.updateTaskStatus(task, 'uploading');

      // Upload file (chunked or single)
      if (task.chunks && task.chunks.length > 0) {
        await this.uploadChunked(task, initResponse);
      } else {
        await this.uploadSingle(task, initResponse);
      }

      // Complete upload
      this.updateTaskStatus(task, 'processing');
      const file = await this.completeUpload(task, initResponse);

      // Update task
      task.completedAt = new Date();
      this.updateTaskStatus(task, 'completed');

      // Call completion callback
      if (this.config.onComplete) {
        this.config.onComplete(file);
      }
    } catch (error) {
      this.handleUploadError(task, error);
    }
  }

  /**
   * Initialize upload with server
   */
  private async initializeUpload(task: UploadTask): Promise<UploadInitResponse> {
    const request: UploadInitRequest = {
      filename: task.file.name,
      size: task.file.size,
      type: task.file.type,
      chunks: task.chunks?.length,
    };

    const response = await fetch('/api/v1/files/upload/init', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: task.abortController?.signal,
    });

    if (!response.ok) {
      throw new Error(`Upload initialization failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Upload file in chunks
   */
  private async uploadChunked(
    task: UploadTask,
    initResponse: UploadInitResponse
  ): Promise<void> {
    const chunks = task.chunks!;
    const startTime = Date.now();

    for (const chunk of chunks) {
      if (task.status === 'cancelled') {
        throw new Error('Upload cancelled');
      }

      await this.uploadChunk(task, chunk, initResponse);

      // Update progress
      const uploadedBytes = chunks
        .filter(c => c.uploaded)
        .reduce((sum, c) => sum + c.size, 0);

      const elapsedSeconds = (Date.now() - startTime) / 1000;
      const speed = uploadedBytes / elapsedSeconds;
      const remainingBytes = task.totalBytes - uploadedBytes;
      const timeRemaining = remainingBytes / speed;

      task.uploadedBytes = uploadedBytes;
      task.progress = (uploadedBytes / task.totalBytes) * 100;
      task.speed = speed;
      task.timeRemaining = timeRemaining;

      this.tasks.set(task.id, { ...task });

      // Call progress callback
      if (this.config.onProgress) {
        this.config.onProgress(task);
      }
    }
  }

  /**
   * Upload single chunk with retry logic
   */
  private async uploadChunk(
    task: UploadTask,
    chunk: ChunkInfo,
    initResponse: UploadInitResponse,
    retryCount = 0
  ): Promise<void> {
    try {
      const blob = task.file.slice(chunk.start, chunk.end);

      const formData = new FormData();
      formData.append('uploadId', initResponse.uploadId);
      formData.append('chunkIndex', chunk.index.toString());
      formData.append('chunk', blob);

      const response = await fetch('/api/v1/files/upload/chunk', {
        method: 'POST',
        body: formData,
        signal: task.abortController?.signal,
      });

      if (!response.ok) {
        throw new Error(`Chunk upload failed: ${response.statusText}`);
      }

      chunk.uploaded = true;
      chunk.retries = retryCount;
    } catch (error) {
      if (retryCount < this.config.maxRetries) {
        // Wait before retry
        await this.delay(this.config.retryDelay * (retryCount + 1));

        // Retry chunk
        return this.uploadChunk(task, chunk, initResponse, retryCount + 1);
      } else {
        throw error;
      }
    }
  }

  /**
   * Upload entire file at once
   */
  private async uploadSingle(
    task: UploadTask,
    initResponse: UploadInitResponse
  ): Promise<void> {
    const formData = new FormData();
    formData.append('uploadId', initResponse.uploadId);
    formData.append('file', task.file);

    const xhr = new XMLHttpRequest();

    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const elapsedSeconds = (Date.now() - task.startedAt.getTime()) / 1000;
          const speed = e.loaded / elapsedSeconds;
          const timeRemaining = (e.total - e.loaded) / speed;

          task.uploadedBytes = e.loaded;
          task.progress = (e.loaded / e.total) * 100;
          task.speed = speed;
          task.timeRemaining = timeRemaining;

          this.tasks.set(task.id, { ...task });

          if (this.config.onProgress) {
            this.config.onProgress(task);
          }
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve();
        } else {
          reject(new Error(`Upload failed: ${xhr.statusText}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed: Network error'));
      });

      xhr.addEventListener('abort', () => {
        reject(new Error('Upload cancelled'));
      });

      if (task.abortController) {
        task.abortController.signal.addEventListener('abort', () => {
          xhr.abort();
        });
      }

      xhr.open('POST', '/api/v1/files/upload/single');
      xhr.send(formData);
    });
  }

  /**
   * Complete upload and get file info
   */
  private async completeUpload(
    task: UploadTask,
    initResponse: UploadInitResponse
  ): Promise<FileItem> {
    const request: UploadCompleteRequest = {
      uploadId: initResponse.uploadId,
      filename: task.file.name,
    };

    const response = await fetch('/api/v1/files/upload/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: task.abortController?.signal,
    });

    if (!response.ok) {
      throw new Error(`Upload completion failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Cancel upload
   */
  cancelUpload(taskId: string): void {
    const task = this.tasks.get(taskId);
    if (task && task.abortController) {
      task.abortController.abort();
      this.updateTaskStatus(task, 'cancelled');
    }
  }

  /**
   * Retry failed upload
   */
  async retryUpload(taskId: string): Promise<void> {
    const task = this.tasks.get(taskId);
    if (task && task.status === 'error') {
      task.retryCount++;
      task.abortController = new AbortController();

      // Reset chunks
      if (task.chunks) {
        task.chunks.forEach(chunk => {
          chunk.uploaded = false;
          chunk.retries = 0;
        });
      }

      this.updateTaskStatus(task, 'pending');
      this.queue.push(taskId);
      this.processQueue();
    }
  }

  /**
   * Get task status
   */
  getTask(taskId: string): UploadTask | undefined {
    return this.tasks.get(taskId);
  }

  /**
   * Get all tasks
   */
  getAllTasks(): UploadTask[] {
    return Array.from(this.tasks.values());
  }

  /**
   * Clear completed/failed tasks
   */
  clearTask(taskId: string): void {
    const task = this.tasks.get(taskId);
    if (task && (task.status === 'completed' || task.status === 'error')) {
      this.tasks.delete(taskId);
    }
  }

  /**
   * Clear all completed tasks
   */
  clearCompleted(): void {
    Array.from(this.tasks.entries()).forEach(([id, task]) => {
      if (task.status === 'completed') {
        this.tasks.delete(id);
      }
    });
  }

  // ============================================================================
  // Helper Methods
  // ============================================================================

  private validateFile(file: File): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Check size
    if (file.size > this.config.maxFileSize) {
      errors.push(
        `File size exceeds maximum of ${this.formatBytes(this.config.maxFileSize)}`
      );
    }

    // Check type
    if (
      this.config.allowedTypes[0] !== '*' &&
      !this.config.allowedTypes.some(type => file.type.startsWith(type))
    ) {
      errors.push(`File type ${file.type} is not allowed`);
    }

    // Check extension
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (
      extension &&
      this.config.allowedExtensions[0] !== '*' &&
      !this.config.allowedExtensions.includes(extension)
    ) {
      errors.push(`File extension .${extension} is not allowed`);
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  private shouldUseChunking(fileSize: number): boolean {
    return this.config.enableChunking && fileSize > this.config.chunkingThreshold;
  }

  private createChunks(fileSize: number): ChunkInfo[] {
    const chunks: ChunkInfo[] = [];
    const chunkSize = this.config.chunkSize;
    let start = 0;
    let index = 0;

    while (start < fileSize) {
      const end = Math.min(start + chunkSize, fileSize);
      chunks.push({
        index,
        start,
        end,
        size: end - start,
        uploaded: false,
        retries: 0,
      });
      start = end;
      index++;
    }

    return chunks;
  }

  private updateTaskStatus(task: UploadTask, status: UploadStatus): void {
    task.status = status;
    this.tasks.set(task.id, { ...task });
  }

  private handleUploadError(task: UploadTask, error: unknown): void {
    const uploadError: UploadError = {
      code: 'UPLOAD_FAILED',
      message: error instanceof Error ? error.message : 'Unknown error',
      recoverable: task.retryCount < this.config.maxRetries,
      timestamp: new Date(),
    };

    task.error = uploadError;
    this.updateTaskStatus(task, 'error');

    if (this.config.onError) {
      this.config.onError(uploadError);
    }
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private formatBytes(bytes: number): string {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Singleton instance
export const uploader = new ChunkedUploader();

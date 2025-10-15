/**
 * Chunked File Uploader
 *
 * Chunked uploader with pause/resume capabilities.
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

// Size constants
const ONE_KB = 1024;
const ONE_MB = ONE_KB * 1024;
const DEFAULT_CHUNK_SIZE = 5 * ONE_MB; // 5MB
const DEFAULT_CHUNK_THRESHOLD = 50 * ONE_MB; // 50MB

// Default upload configuration
const DEFAULT_CONFIG: UploadConfig = {
  maxFileSize: 5 * 1024 * 1024 * 1024, // 5GB
  allowedTypes: ['*'],
  allowedExtensions: ['*'],
  chunkSize: DEFAULT_CHUNK_SIZE,
  enableChunking: true,
  chunkingThreshold: DEFAULT_CHUNK_THRESHOLD,
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

  // Utility: sanitize user-supplied strings before sending to logs to avoid log injection
  private sanitizeForLog(value: unknown, maxLen = 200): string {
    try {
      if (value == null) return '';
      const s = String(value);
      // remove newlines and control characters, keep printable subset
      const cleaned = s.replace(/\s+/g, ' ').replace(/[^\x20-\x7E]/g, '');
      return cleaned.length > maxLen ? cleaned.slice(0, maxLen) + '...' : cleaned;
    } catch {
      return '';
    }
  }

  // Utility: parse JSON with a safe error message
  private async safeParseJson<T>(response: Response, context = 'response'): Promise<T> {
    try {
      return (await response.json()) as T;
    } catch (err) {
      throw new Error(`${context} contained invalid JSON`);
    }
  }

  private extractErrorMessage(err: unknown): string {
    if (!err) return '';
    if (err instanceof Error) return err.message;
    try {
      return String((err as any).message ?? err);
    } catch {
      return '';
    }
  }

  /**
   * Add file to upload queue
   * Returns a structured result to make error handling explicit to callers.
   * This avoids throwing from validation paths and is easier for scanners to reason about.
   */
  async addFile(file: File, folderId?: string): Promise<{ ok: true; id: string } | { ok: false; error: string }> {
    // Early sanity checks for the File object shape
    if (!file || typeof (file as any).name !== 'string' || typeof (file as any).size !== 'number' || Number.isNaN((file as any).size)) {
      return { ok: false, error: 'Invalid file object' };
    }

    try {
      // Validate file - explicit, early check
      const validation = this.validateFile(file);
      if (!validation.valid) {
        const msg = this.sanitizeForLog(validation.errors.join('; '));
        return { ok: false, error: `Invalid file: ${msg}` };
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

      // Add chunks if file is large enough (use safe wrapper to avoid unexpected exceptions)
      if (this.shouldUseChunking(file.size)) {
        try {
          task.chunks = this.createChunks(file.size);
        } catch (err) {
          // Log and continue without chunking as a fallback
          // eslint-disable-next-line no-console
          console.warn('createChunks failed, falling back to single upload', this.sanitizeForLog(this.extractErrorMessage(err)));
          task.chunks = undefined;
        }
      }

      this.tasks.set(task.id, task);
      this.queue.push(task.id);

      // Start processing queue asynchronously to avoid blocking
      setTimeout(() => this.processQueue(), 0);

      return { ok: true, id: task.id };
    } catch (err) {
      // Ensure we return a structured failure with a sanitized message
      const msg = this.sanitizeForLog(this.extractErrorMessage(err));
      return { ok: false, error: `addFile failed: ${msg}` };
    }
  }

  /**
   * Add multiple files
   */
  async addFiles(files: File[], folderId?: string): Promise<string[]> {
    // Add files in parallel but limit concurrency if needed in future
    const promises = files.map(file =>
      this.addFile(file, folderId).then(
        id => ({ status: 'fulfilled', id } as const),
        err => ({ status: 'rejected', error: err, name: this.sanitizeForLog(file.name) } as const)
      )
    );

    const results = await Promise.all(promises);
    const taskIds: string[] = [];
    for (const r of results) {
      if (r.status === 'fulfilled') {
        const res = r.id as any; // previous shape (string id). Handle legacy callers.
        if (typeof res === 'string') taskIds.push(res);
        else if (res && (res as any).ok) taskIds.push((res as any).id);
      } else {
        const name = r.name || 'unknown';
        const err = r.error;
        // eslint-disable-next-line no-console
        console.warn(`addFiles: failed to add ${name}: ${this.sanitizeForLog(err?.message || err)}`);
      }
    }
    return taskIds;
  }

  /**
   * Process upload queue
   */
  private async processQueue(): Promise<void> {
    // Process up to maxConcurrentUploads; schedule the next loop to avoid deep recursion
    while (this.queue.length > 0 && this.activeUploads.size < this.config.maxConcurrentUploads) {
      const taskId = this.queue.shift()!;
      const task = this.tasks.get(taskId);

      if (task && task.status === 'pending') {
        this.activeUploads.add(taskId);
        this.uploadTask(task)
          .catch(err => {
            // already handled inside uploadTask
            // eslint-disable-next-line no-console
            console.error('uploadTask failed', this.sanitizeForLog(err?.message || err));
          })
          .finally(() => {
            this.activeUploads.delete(taskId);
            // schedule next tick instead of immediate recursive call
            setTimeout(() => this.processQueue(), 0);
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
    // Maintain incremental uploadedBytes to avoid scanning the whole chunks array each iteration
    let uploadedBytes = chunks.filter(c => c.uploaded).reduce((s, c) => s + c.size, 0);

    for (const chunk of chunks) {
      if (task.status === 'cancelled') {
        throw new Error('Upload cancelled');
      }

      // skip already uploaded
      if (chunk.uploaded) continue;

      await this.uploadChunk(task, chunk, initResponse);
      uploadedBytes += chunk.size;

      const elapsedSeconds = Math.max(0.001, (Date.now() - startTime) / 1000);
      const speed = uploadedBytes / elapsedSeconds;
      const remainingBytes = Math.max(0, task.totalBytes - uploadedBytes);
      const timeRemaining = speed > 0 ? remainingBytes / speed : Infinity;

      task.uploadedBytes = uploadedBytes;
      task.progress = (uploadedBytes / task.totalBytes) * 100;
      task.speed = speed;
      task.timeRemaining = timeRemaining;

      this.tasks.set(task.id, { ...task });

      // Call progress callback
      if (this.config.onProgress) {
        try {
          this.config.onProgress(task);
        } catch (cbErr) {
          // avoid letting a progress callback break uploads
          // eslint-disable-next-line no-console
          console.warn('onProgress callback error', this.sanitizeForLog(this.extractErrorMessage(cbErr)));
        }
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
        const statusText = this.sanitizeForLog(response.statusText || `${response.status}`);
        // Try to parse server error body for more info
        let bodyMsg = '';
        try {
          const parsed = await this.safeParseJson<any>(response, 'chunk upload response');
          bodyMsg = this.sanitizeForLog(parsed?.message || parsed?.error || '');
        } catch (_) {
          // ignore parse errors here; keep statusText
        }
        throw new Error(`Chunk upload failed: ${statusText}${bodyMsg ? ' - ' + bodyMsg : ''}`);
      }

      chunk.uploaded = true;
      chunk.retries = retryCount;
    } catch (error) {
      const errMsg = this.extractErrorMessage(error);
      if (retryCount < this.config.maxRetries) {
        // Wait before retry (use a bounded backoff to avoid long waits)
        const backoff = Math.min(30_000, this.config.retryDelay * Math.pow(2, retryCount));
        await this.delay(backoff);

        // Retry chunk
        return this.uploadChunk(task, chunk, initResponse, retryCount + 1);
      }

      // If no retries left, attach sanitized error and rethrow
      const sanitized = this.sanitizeForLog(errMsg);
      throw new Error(`Chunk upload failed after ${retryCount} retries: ${sanitized}`);
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
          const now = Date.now();
          const elapsedSeconds = Math.max(0.001, (now - task.startedAt.getTime()) / 1000);
          const speed = e.loaded / elapsedSeconds;
          const remaining = Math.max(0, e.total - e.loaded);
          const timeRemaining = speed > 0 ? remaining / speed : Infinity;

          task.uploadedBytes = e.loaded;
          task.progress = (e.loaded / e.total) * 100;
          task.speed = speed;
          task.timeRemaining = timeRemaining;

          this.tasks.set(task.id, { ...task });

          if (this.config.onProgress) {
            try {
              this.config.onProgress(task);
            } catch (cbErr) {
              // don't allow callback errors to bubble
              // eslint-disable-next-line no-console
              console.warn('onProgress callback error', this.sanitizeForLog(this.extractErrorMessage(cbErr)));
            }
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
      try {
        task.abortController.abort();
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('cancelUpload: abort failed', this.sanitizeForLog(this.extractErrorMessage(err)));
      }
      this.updateTaskStatus(task, 'cancelled');
    } else {
      // nothing to cancel — log sanitized info for debugging
      // eslint-disable-next-line no-console
      console.info('cancelUpload: nothing to cancel for', this.sanitizeForLog(taskId));
    }
  }

  /**
   * Retry failed upload
   */
  async retryUpload(taskId: string): Promise<void> {
    try {
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
        // schedule processing asynchronously
        setTimeout(() => this.processQueue(), 0);
      }
    } catch (err) {
      // Log and swallow so caller doesn't crash
      // eslint-disable-next-line no-console
      console.warn('retryUpload: failed', this.sanitizeForLog(this.extractErrorMessage(err)));
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
    this.tasks.forEach((task, id) => {
      if (task.status === 'completed') this.tasks.delete(id);
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
    // Use timestamp + compact random suffix
    const rand = Math.random().toString(36).slice(2, 11);
    return `${Date.now()}-${rand}`;
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

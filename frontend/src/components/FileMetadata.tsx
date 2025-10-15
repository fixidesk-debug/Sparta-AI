/**
 * FileMetadata Component
 * 
 * Displays and edits file metadata
 */

import React, { useState, useCallback } from 'react';
import { FileMetadataProps, FileItem } from '../types/fileManagement';

const FileMetadata: React.FC<FileMetadataProps> = ({
  file,
  editable = false,
  onUpdate,
  className = '',
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedFile, setEditedFile] = useState<Partial<FileItem>>(file);
  const [newTag, setNewTag] = useState('');

  // Handle field change
  const handleChange = useCallback(
    (field: keyof FileItem, value: unknown) => {
      setEditedFile(prev => ({ ...prev, [field]: value }));
    },
    []
  );

  // Add tag
  const addTag = useCallback(() => {
    if (newTag.trim() && editedFile.tags) {
      const tags = [...editedFile.tags, newTag.trim()];
      setEditedFile(prev => ({ ...prev, tags }));
      setNewTag('');
    }
  }, [newTag, editedFile.tags]);

  // Remove tag
  const removeTag = useCallback(
    (tag: string) => {
      if (editedFile.tags) {
        const tags = editedFile.tags.filter(t => t !== tag);
        setEditedFile(prev => ({ ...prev, tags }));
      }
    },
    [editedFile.tags]
  );

  // Save changes
  const handleSave = useCallback(() => {
    if (onUpdate) {
      onUpdate(editedFile);
    }
    setIsEditing(false);
  }, [editedFile, onUpdate]);

  // Cancel editing
  const handleCancel = useCallback(() => {
    setEditedFile(file);
    setIsEditing(false);
  }, [file]);

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

  return (
    <div className={`file-metadata ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          File Details
        </h3>
        {editable && !isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            Edit
          </button>
        )}
        {isEditing && (
          <div className="flex items-center gap-2">
            <button
              onClick={handleSave}
              className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="px-3 py-1 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 text-sm"
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      {/* Metadata fields */}
      <div className="space-y-4">
        {/* Filename */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Filename
          </label>
          {isEditing ? (
            <input
              type="text"
              value={editedFile.filename || ''}
              onChange={e => handleChange('filename', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
              aria-label="Filename"
            />
          ) : (
            <p className="text-gray-900 dark:text-gray-100">{file.filename}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          {isEditing ? (
            <textarea
              value={editedFile.description || ''}
              onChange={e => handleChange('description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
              placeholder="Add a description..."
            />
          ) : (
            <p className="text-gray-900 dark:text-gray-100">
              {file.description || 'No description'}
            </p>
          )}
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Tags
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {(isEditing ? editedFile.tags : file.tags)?.map(tag => (
              <span
                key={tag}
                className="flex items-center gap-1 px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-sm"
              >
                {tag}
                {isEditing && (
                  <button
                    onClick={() => removeTag(tag)}
                    className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                    aria-label={`Remove tag ${tag}`}
                  >
                    ×
                  </button>
                )}
              </span>
            ))}
          </div>
          {isEditing && (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={newTag}
                onChange={e => setNewTag(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && addTag()}
                placeholder="Add tag..."
                className="flex-1 px-3 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-sm"
              />
              <button
                onClick={addTag}
                className="px-3 py-1 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 text-sm"
              >
                Add
              </button>
            </div>
          )}
        </div>

        {/* Read-only fields */}
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
          <div className="flex justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Size</span>
            <span className="text-sm text-gray-900 dark:text-gray-100">
              {formatBytes(file.size)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Type</span>
            <span className="text-sm text-gray-900 dark:text-gray-100">{file.type}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Uploaded</span>
            <span className="text-sm text-gray-900 dark:text-gray-100">
              {formatDate(file.uploadedAt)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Modified</span>
            <span className="text-sm text-gray-900 dark:text-gray-100">
              {formatDate(file.updatedAt)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Version</span>
            <span className="text-sm text-gray-900 dark:text-gray-100">
              {file.version}
            </span>
          </div>
        </div>

        {/* Data file metadata */}
        {file.metadata.rows && (
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data Properties
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Rows</span>
                <span className="text-sm text-gray-900 dark:text-gray-100">
                  {file.metadata.rows.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Columns</span>
                <span className="text-sm text-gray-900 dark:text-gray-100">
                  {file.metadata.columns}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Image metadata */}
        {file.metadata.width && file.metadata.height && (
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Image Properties
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Dimensions</span>
                <span className="text-sm text-gray-900 dark:text-gray-100">
                  {file.metadata.width} × {file.metadata.height}
                </span>
              </div>
              {file.metadata.format && (
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Format</span>
                  <span className="text-sm text-gray-900 dark:text-gray-100">
                    {file.metadata.format}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileMetadata;

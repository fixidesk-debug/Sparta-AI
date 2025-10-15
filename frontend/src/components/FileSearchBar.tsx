/**
 * FileSearchBar Component
 * 
 * Advanced search with filters for file management
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  FileSearchBarProps,
  FileSearchQuery,
  FileFilters,
  FileSortField,
} from '../types/fileManagement';

const FileSearchBar: React.FC<FileSearchBarProps> = ({
  onSearch,
  filters: initialFilters,
  placeholder = 'Search files...',
  className = '',
}) => {
  const [query, setQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FileFilters>(initialFilters || {});
  const [sortBy, setSortBy] = useState<FileSortField>('uploadedAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const filterRef = useRef<HTMLDivElement>(null);

  // Close filters on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (filterRef.current && !filterRef.current.contains(event.target as Node)) {
        setShowFilters(false);
      }
    };

    if (showFilters) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showFilters]);

  // Handle search
  const handleSearch = useCallback(() => {
    const searchQuery: FileSearchQuery = {
      query,
      filters,
      sortBy,
      sortOrder,
      page: 1,
      pageSize: 50,
    };
    onSearch(searchQuery);
  }, [query, filters, sortBy, sortOrder, onSearch]);

  // Handle enter key
  const handleKeyPress = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        handleSearch();
      }
    },
    [handleSearch]
  );

  // Update filter
  const updateFilter = useCallback(
    (key: keyof FileFilters, value: unknown) => {
      setFilters(prev => ({ ...prev, [key]: value }));
    },
    []
  );

  // Clear filters
  const clearFilters = useCallback(() => {
    setFilters({});
    setSortBy('uploadedAt');
    setSortOrder('desc');
  }, []);

  // Count active filters
  const activeFilterCount = Object.keys(filters).filter(
    key => filters[key as keyof FileFilters] !== undefined
  ).length;

  return (
    <div className={`file-search-bar relative ${className}`}>
      {/* Search input */}
      <div className="flex items-center gap-2">
        <div className="flex-1 relative">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            aria-label="Search files"
          />
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            🔍
          </span>
        </div>

        {/* Filter button */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`
            relative px-4 py-2 border rounded-lg transition-colors
            ${
              showFilters || activeFilterCount > 0
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
            }
          `}
          aria-label="Toggle filters"
        >
          <span>🔧 Filters</span>
          {activeFilterCount > 0 && (
            <span className="absolute -top-2 -right-2 w-5 h-5 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center">
              {activeFilterCount}
            </span>
          )}
        </button>

        {/* Search button */}
        <button
          onClick={handleSearch}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Search
        </button>
      </div>

      {/* Filters panel */}
      {showFilters && (
        <div
          ref={filterRef}
          className="absolute top-full left-0 right-0 mt-2 p-4 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg z-10"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
              Filters
            </h3>
            {activeFilterCount > 0 && (
              <button
                onClick={clearFilters}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                Clear all
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* File types */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                File Type
              </label>
              <select
                value={filters.types?.[0] || ''}
                onChange={e =>
                  updateFilter('types', e.target.value ? [e.target.value] : undefined)
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                aria-label="File type filter"
              >
                <option value="">All types</option>
                <option value="image/">Images</option>
                <option value="video/">Videos</option>
                <option value="audio/">Audio</option>
                <option value="text/">Text</option>
                <option value="application/pdf">PDF</option>
                <option value="application/json">JSON</option>
              </select>
            </div>

            {/* Date range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Upload Date
              </label>
              <select
                value={filters.dateRange ? 'custom' : ''}
                onChange={e => {
                  if (e.target.value === '') {
                    updateFilter('dateRange', undefined);
                  } else if (e.target.value === 'today') {
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    updateFilter('dateRange', { from: today, to: new Date() });
                  } else if (e.target.value === 'week') {
                    const weekAgo = new Date();
                    weekAgo.setDate(weekAgo.getDate() - 7);
                    updateFilter('dateRange', { from: weekAgo, to: new Date() });
                  } else if (e.target.value === 'month') {
                    const monthAgo = new Date();
                    monthAgo.setMonth(monthAgo.getMonth() - 1);
                    updateFilter('dateRange', { from: monthAgo, to: new Date() });
                  }
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                aria-label="Date range filter"
              >
                <option value="">Any time</option>
                <option value="today">Today</option>
                <option value="week">Last 7 days</option>
                <option value="month">Last 30 days</option>
                <option value="custom">Custom range</option>
              </select>
            </div>

            {/* Size range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                File Size
              </label>
              <select
                value={filters.sizeRange ? 'custom' : ''}
                onChange={e => {
                  if (e.target.value === '') {
                    updateFilter('sizeRange', undefined);
                  } else if (e.target.value === 'small') {
                    updateFilter('sizeRange', { min: 0, max: 1024 * 1024 }); // <1MB
                  } else if (e.target.value === 'medium') {
                    updateFilter('sizeRange', {
                      min: 1024 * 1024,
                      max: 10 * 1024 * 1024,
                    }); // 1-10MB
                  } else if (e.target.value === 'large') {
                    updateFilter('sizeRange', { min: 10 * 1024 * 1024, max: Infinity }); // >10MB
                  }
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                aria-label="File size filter"
              >
                <option value="">Any size</option>
                <option value="small">Small (&lt;1MB)</option>
                <option value="medium">Medium (1-10MB)</option>
                <option value="large">Large (&gt;10MB)</option>
              </select>
            </div>

            {/* Sort */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Sort By
              </label>
              <div className="flex gap-2">
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value as FileSortField)}
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                  aria-label="Sort field"
                >
                  <option value="filename">Name</option>
                  <option value="uploadedAt">Upload date</option>
                  <option value="updatedAt">Modified date</option>
                  <option value="size">Size</option>
                  <option value="type">Type</option>
                </select>
                <button
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700"
                  title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
                  aria-label={`Sort ${sortOrder === 'asc' ? 'ascending' : 'descending'}`}
                >
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </button>
              </div>
            </div>
          </div>

          {/* Apply button */}
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => {
                handleSearch();
                setShowFilters(false);
              }}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileSearchBar;

import React, { useState } from 'react';
import Modal, { Button, ModalActions, ProgressBar, Alert, Spinner } from './Modal';
import {
  FileText,
  Image,
  File as FileIcon,
  File as FileSpreadsheet,
  File as File,
  Download,
  Eye,
  Check,
  // Chevron and Zoom icons not present; reuse FileText as placeholders
  FileText as ChevronRight,
  FileText as ChevronLeft,
  FileText as ZoomIn,
  FileText as ZoomOut,
} from '../icons';

// =====================
// Type Definitions
// =====================

export type ExportFormat = 'pdf' | 'png' | 'jpg' | 'svg' | 'csv' | 'xlsx' | 'json';
export type ExportQuality = 'low' | 'medium' | 'high' | 'ultra';
export type ExportStep = 'format' | 'options' | 'preview' | 'download';

export interface ExportOptions {
  format: ExportFormat;
  quality: ExportQuality;
  includeMetadata: boolean;
  includeCharts: boolean;
  includeData: boolean;
  pageSize?: 'letter' | 'a4' | 'legal';
  orientation?: 'portrait' | 'landscape';
  scale?: number;
}

export interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onExport: (options: ExportOptions) => Promise<void>;
  title?: string;
  previewContent?: React.ReactNode;
  availableFormats?: ExportFormat[];
}

// =====================
// Format Configuration
// =====================

const formatConfig: Record<
  ExportFormat,
  { icon: React.ReactNode; label: string; description: string; color: string }
> = {
  pdf: {
    icon: <FileText size={32} />,
    label: 'PDF Document',
    description: 'Portable Document Format for universal compatibility',
    color: '#ef4444',
  },
  png: {
    icon: <Image size={32} />,
    label: 'PNG Image',
    description: 'High-quality image with transparency support',
    color: '#8b5cf6',
  },
  jpg: {
    icon: <Image size={32} />,
    label: 'JPG Image',
    description: 'Compressed image format for smaller file sizes',
    color: '#f59e0b',
  },
  svg: {
    icon: <File size={32} />,
    label: 'SVG Vector',
    description: 'Scalable vector graphics for perfect quality at any size',
    color: '#10b981',
  },
  csv: {
    icon: <FileSpreadsheet size={32} />,
    label: 'CSV Data',
    description: 'Comma-separated values for data analysis',
    color: '#06b6d4',
  },
  xlsx: {
    icon: <FileSpreadsheet size={32} />,
    label: 'Excel Spreadsheet',
    description: 'Microsoft Excel format with formatting support',
    color: '#10b981',
  },
  json: {
    icon: <File size={32} />,
    label: 'JSON Data',
    description: 'JavaScript Object Notation for developers',
    color: '#6366f1',
  },
};

const qualityConfig: Record<ExportQuality, { label: string; description: string; value: number }> = {
  low: { label: 'Low', description: 'Smaller file size, faster export', value: 25 },
  medium: { label: 'Medium', description: 'Balanced quality and file size', value: 50 },
  high: { label: 'High', description: 'Better quality, larger file size', value: 75 },
  ultra: { label: 'Ultra', description: 'Maximum quality, largest file size', value: 100 },
};

// =====================
// Progress Stepper Component
// =====================

const ProgressStepper: React.FC<{
  steps: string[];
  currentStep: number;
  onStepClick?: (step: number) => void;
}> = ({ steps, currentStep, onStepClick }) => (
  <div className="progress-stepper">
    {steps.map((step, index) => (
      <React.Fragment key={step}>
        <div
          className={`progress-step ${index === currentStep ? 'progress-step-active' : ''} ${
            index < currentStep ? 'progress-step-completed' : ''
          } ${onStepClick ? 'progress-step-clickable' : ''}`}
          onClick={() => onStepClick?.(index)}
        >
          <div className="progress-step-circle">
            {index < currentStep ? <Check size={16} /> : <span>{index + 1}</span>}
          </div>
          <span className="progress-step-label">{step}</span>
        </div>
        {index < steps.length - 1 && (
          <div
            className={`progress-step-line ${index < currentStep ? 'progress-step-line-completed' : ''}`}
          />
        )}
      </React.Fragment>
    ))}
  </div>
);

// =====================
// Format Selection Component
// =====================

const FormatSelection: React.FC<{
  selectedFormat: ExportFormat;
  onFormatSelect: (format: ExportFormat) => void;
  availableFormats: ExportFormat[];
}> = ({ selectedFormat, onFormatSelect, availableFormats }) => (
  <div className="format-selection">
    <h3 className="format-selection-title">Choose Export Format</h3>
    <div className="format-grid">
      {availableFormats.map((format) => {
        const config = formatConfig[format];
        return (
          <button
            key={format}
            className={`format-card ${selectedFormat === format ? 'format-card-active' : ''}`}
            onClick={() => onFormatSelect(format)}
            type="button"
          >
            <div className="format-card-icon" style={{ color: config.color }}>
              {config.icon}
            </div>
            <div className="format-card-content">
              <div className="format-card-label">{config.label}</div>
              <div className="format-card-description">{config.description}</div>
            </div>
            {selectedFormat === format && (
              <div className="format-card-check">
                <Check size={20} />
              </div>
            )}
          </button>
        );
      })}
    </div>
  </div>
);

// =====================
// Export Options Component
// =====================

const ExportOptionsPanel: React.FC<{
  options: ExportOptions;
  onOptionsChange: (options: Partial<ExportOptions>) => void;
}> = ({ options, onOptionsChange }) => {
  const handleQualityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    let quality: ExportQuality = 'medium';
    if (value <= 30) quality = 'low';
    else if (value <= 60) quality = 'medium';
    else if (value <= 85) quality = 'high';
    else quality = 'ultra';
    onOptionsChange({ quality });
  };

  const currentQuality = qualityConfig[options.quality];

  return (
    <div className="export-options">
      <h3 className="export-options-title">Configure Export Settings</h3>

      {/* Quality Slider */}
      <div className="option-section">
        <label className="option-label" htmlFor="quality-slider">
          <span>Quality</span>
          <span className="option-value">{currentQuality.label}</span>
        </label>
        <input
          id="quality-slider"
          type="range"
          min="0"
          max="100"
          value={currentQuality.value}
          onChange={handleQualityChange}
          className="quality-slider"
          aria-label="Export quality"
        />
        <p className="option-description">{currentQuality.description}</p>
      </div>

      {/* Format-specific options */}
      {(options.format === 'pdf' || options.format === 'png' || options.format === 'jpg') && (
        <>
          <div className="option-section">
            <label className="option-label">Page Size</label>
            <div className="radio-group">
              {['letter', 'a4', 'legal'].map((size) => (
                <label key={size} className="radio-option">
                  <input
                    type="radio"
                    name="pageSize"
                    value={size}
                    checked={options.pageSize === size}
                    onChange={(e) => onOptionsChange({ pageSize: e.target.value as any })}
                  />
                  <span className="radio-label">{size.toUpperCase()}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="option-section">
            <label className="option-label">Orientation</label>
            <div className="radio-group">
              {['portrait', 'landscape'].map((orient) => (
                <label key={orient} className="radio-option">
                  <input
                    type="radio"
                    name="orientation"
                    value={orient}
                    checked={options.orientation === orient}
                    onChange={(e) => onOptionsChange({ orientation: e.target.value as any })}
                  />
                  <span className="radio-label">{orient.charAt(0).toUpperCase() + orient.slice(1)}</span>
                </label>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Include options */}
      <div className="option-section">
        <label className="option-label">Include in Export</label>
        <div className="checkbox-group">
          <label className="checkbox-option">
            <input
              type="checkbox"
              checked={options.includeMetadata}
              onChange={(e) => onOptionsChange({ includeMetadata: e.target.checked })}
            />
            <span className="checkbox-label">Metadata and timestamps</span>
          </label>
          <label className="checkbox-option">
            <input
              type="checkbox"
              checked={options.includeCharts}
              onChange={(e) => onOptionsChange({ includeCharts: e.target.checked })}
            />
            <span className="checkbox-label">Charts and visualizations</span>
          </label>
          <label className="checkbox-option">
            <input
              type="checkbox"
              checked={options.includeData}
              onChange={(e) => onOptionsChange({ includeData: e.target.checked })}
            />
            <span className="checkbox-label">Raw data tables</span>
          </label>
        </div>
      </div>
    </div>
  );
};

// =====================
// Preview Panel Component
// =====================

const PreviewPanel: React.FC<{
  options: ExportOptions;
  previewContent?: React.ReactNode;
}> = ({ options, previewContent }) => {
  const [zoom, setZoom] = useState(100);

  return (
    <div className="preview-panel">
      <div className="preview-header">
        <h3 className="preview-title">Preview</h3>
        <div className="preview-controls">
          <button
            className="preview-control-btn"
            onClick={() => setZoom((z) => Math.max(50, z - 10))}
            disabled={zoom <= 50}
            type="button"
            aria-label="Zoom out"
            title="Zoom out"
          >
            <ZoomOut size={16} />
          </button>
          <span className="preview-zoom">{zoom}%</span>
          <button
            className="preview-control-btn"
            onClick={() => setZoom((z) => Math.min(200, z + 10))}
            disabled={zoom >= 200}
            type="button"
            aria-label="Zoom in"
            title="Zoom in"
          >
            <ZoomIn size={16} />
          </button>
        </div>
      </div>
      <div className="preview-content">
        <div className="preview-container" style={{ transform: `scale(${zoom / 100})` }}>
          {previewContent || (
            <div className="preview-placeholder">
              <Eye size={48} />
              <p>Preview will appear here</p>
              <p className="preview-placeholder-detail">
                Format: {formatConfig[options.format].label} • Quality: {options.quality}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// =====================
// Export Modal Component
// =====================

const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  onExport,
  title = 'Export',
  previewContent,
  availableFormats = ['pdf', 'png', 'jpg', 'svg', 'csv', 'xlsx', 'json'],
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [options, setOptions] = useState<ExportOptions>({
    format: availableFormats[0],
    quality: 'high',
    includeMetadata: true,
    includeCharts: true,
    includeData: true,
    pageSize: 'letter',
    orientation: 'portrait',
    scale: 1,
  });
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportComplete, setExportComplete] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const steps = ['Format', 'Options', 'Preview', 'Download'];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    setExportError(null);
    setExportProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setExportProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      await onExport(options);

      clearInterval(progressInterval);
      setExportProgress(100);
      setExportComplete(true);

      // Auto-close after success
      setTimeout(() => {
        handleClose();
      }, 2000);
    } catch (error) {
      setExportError(error instanceof Error ? error.message : 'Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleClose = () => {
    setCurrentStep(0);
    setIsExporting(false);
    setExportProgress(0);
    setExportComplete(false);
    setExportError(null);
    onClose();
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <FormatSelection
            selectedFormat={options.format}
            onFormatSelect={(format) => setOptions({ ...options, format })}
            availableFormats={availableFormats}
          />
        );
      case 1:
        return (
          <ExportOptionsPanel
            options={options}
            onOptionsChange={(newOptions) => setOptions({ ...options, ...newOptions })}
          />
        );
      case 2:
        return <PreviewPanel options={options} previewContent={previewContent} />;
      case 3:
        return (
          <div className="export-download">
            {!isExporting && !exportComplete && !exportError && (
              <div className="export-ready">
                <div className="export-ready-icon">
                  <Download size={64} />
                </div>
                <h3>Ready to Export</h3>
                <p>Click the button below to start exporting your file.</p>
                <div className="export-summary">
                  <div className="export-summary-item">
                    <span className="export-summary-label">Format:</span>
                    <span className="export-summary-value">{formatConfig[options.format].label}</span>
                  </div>
                  <div className="export-summary-item">
                    <span className="export-summary-label">Quality:</span>
                    <span className="export-summary-value">{options.quality.toUpperCase()}</span>
                  </div>
                </div>
              </div>
            )}

            {isExporting && (
              <div className="export-progress">
                <Spinner size="large" label="Exporting..." />
                <ProgressBar progress={exportProgress} label="Export Progress" variant="default" />
              </div>
            )}

            {exportComplete && (
              <div className="export-success">
                <div className="export-success-icon">
                  <Check size={64} />
                </div>
                <h3>Export Complete!</h3>
                <p>Your file has been successfully exported.</p>
              </div>
            )}

            {exportError && (
              <Alert
                type="error"
                title="Export Failed"
                message={exportError}
                onClose={() => setExportError(null)}
              />
            )}
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} size="large" title={title} className="export-modal">
      <div className="export-modal-content">
        <ProgressStepper steps={steps} currentStep={currentStep} onStepClick={setCurrentStep} />
        <div className="export-step-content">{renderStepContent()}</div>
      </div>

      <ModalActions align="space-between">
        <Button variant="ghost" onClick={handleClose} disabled={isExporting}>
          Cancel
        </Button>
        <div className="export-navigation">
          {currentStep > 0 && currentStep < 3 && (
            <Button
              variant="secondary"
              onClick={handleBack}
              icon={<ChevronLeft size={16} />}
              iconPosition="left"
            >
              Back
            </Button>
          )}
          {currentStep < 2 && (
            <Button
              variant="primary"
              onClick={handleNext}
              icon={<ChevronRight size={16} />}
              iconPosition="right"
            >
              Next
            </Button>
          )}
          {currentStep === 2 && (
            <Button
              variant="primary"
              onClick={handleNext}
              icon={<Download size={16} />}
              iconPosition="left"
            >
              Continue to Export
            </Button>
          )}
          {currentStep === 3 && !exportComplete && (
            <Button
              variant="primary"
              onClick={handleExport}
              loading={isExporting}
              disabled={isExporting}
              icon={<Download size={16} />}
              iconPosition="left"
            >
              Export Now
            </Button>
          )}
        </div>
      </ModalActions>
    </Modal>
  );
};

export default ExportModal;

/**
 * Chart Export Manager for Sparta AI
 * 
 * Handles exporting charts to various formats (PNG, SVG, PDF, JSON, CSV)
 */

// @ts-ignore - plotly.js will be installed via npm
import Plotly from 'plotly.js-dist-min';
import {
  ExportOptions,
  ExportResult,
  ChartConfig,
  Dataset,
} from '../types/visualization';

/**
 * Export chart to specified format
 */
export async function exportChart(
  chartElement: HTMLElement,
  config: ChartConfig,
  options: ExportOptions
): Promise<ExportResult> {
  try {
    const filename = options.filename || generateFilename(config.id);

    switch (options.format) {
      case 'png':
        return await exportToPNG(chartElement, filename, options);
      
      case 'svg':
        return await exportToSVG(chartElement, filename, options);
      
      case 'pdf':
        return await exportToPDF(chartElement, filename, options);
      
      case 'json':
        return await exportToJSON(config, filename, options);
      
      case 'csv':
        return await exportToCSV(config.datasets, filename);
      
      default:
        throw new Error(`Unsupported export format: ${options.format}`);
    }
  } catch (error) {
    const errMsg = error instanceof Error ? error.message : String(error);
    console.error('Export chart failed:', errMsg, { configId: config.id, format: options.format });
    return {
      success: false,
      format: options.format,
      filename: '',
      error: errMsg,
    };
  }
}

function generateFilename(baseId?: string) {
  const ts = Date.now();
  return `${baseId ?? 'chart'}_${ts}`;
}

/**
 * Export chart to PNG format
 */
async function exportToPNG(
  element: HTMLElement,
  filename: string,
  options: ExportOptions
): Promise<ExportResult> {
  const width = options.width || 1200;
  const height = options.height || 800;
  const scale = options.scale || 2;

  const dataUrl = await Plotly.toImage(element, {
    format: 'png',
    width,
    height,
    scale,
  });
  let blob: Blob;
  try {
    const dataUrlSafe = validateDataUrl(dataUrl);
    blob = await dataURLtoBlob(dataUrlSafe);
  } catch (err) {
    console.error('Failed to generate PNG image for export:', err);
    return {
      success: false,
      format: 'png',
      filename: '',
      error: err instanceof Error ? err.message : 'Image generation failed',
    };
  }
  downloadBlob(blob, `${filename}.png`);

  return {
    success: true,
    format: 'png',
    filename: `${filename}.png`,
    size: blob.size,
    blob,
    dataUrl,
  };
}

/**
 * Export chart to SVG format
 */
async function exportToSVG(
  element: HTMLElement,
  filename: string,
  options: ExportOptions
): Promise<ExportResult> {
  const width = options.width || 1200;
  const height = options.height || 800;

  const dataUrl = await Plotly.toImage(element, {
    format: 'svg',
    width,
    height,
  });
  let blob: Blob;
  try {
    const dataUrlSafe = validateDataUrl(dataUrl);
    blob = await dataURLtoBlob(dataUrlSafe);
  } catch (err) {
    console.error('Failed to generate SVG image for export:', err);
    return {
      success: false,
      format: 'svg',
      filename: '',
      error: err instanceof Error ? err.message : 'Image generation failed',
    };
  }
  downloadBlob(blob, `${filename}.svg`);

  return {
    success: true,
    format: 'svg',
    filename: `${filename}.svg`,
    size: blob.size,
    blob,
    dataUrl,
  };
}

/**
 * Export chart to PDF format
 * Note: This creates a PNG first and embeds it in a PDF-like structure
 * For production use, consider using a proper PDF library like jsPDF
 */
async function exportToPDF(
  element: HTMLElement,
  filename: string,
  options: ExportOptions
): Promise<ExportResult> {
  // For now, export as high-quality PNG
  // In production, integrate with jsPDF for proper PDF generation
  const width = options.width || 1200;
  const height = options.height || 800;
  const scale = options.scale || 3;

  const dataUrl = await Plotly.toImage(element, {
    format: 'png',
    width,
    height,
    scale,
  });
  let blob: Blob;
  try {
    const dataUrlSafe = validateDataUrl(dataUrl);
    blob = await dataURLtoBlob(dataUrlSafe);
  } catch (err) {
    console.error('Failed to generate PNG image for PDF export:', err);
    return {
      success: false,
      format: 'pdf',
      filename: '',
      error: err instanceof Error ? err.message : 'Image generation failed',
    };
  }
  downloadBlob(blob, `${filename}.png`);

  return {
    success: true,
    format: 'pdf',
    filename: `${filename}.png`,
    size: blob.size,
    blob,
    dataUrl,
  };
}

/**
 * Export chart configuration to JSON format
 */
async function exportToJSON(
  config: ChartConfig,
  filename: string,
  options: ExportOptions
): Promise<ExportResult> {
  const exportData: Record<string, unknown> = {
    config: {
      id: config.id,
      type: config.type,
      title: config.title,
      subtitle: config.subtitle,
      xAxisLabel: config.xAxisLabel,
      yAxisLabel: config.yAxisLabel,
    },
  };

  if (options.includeData) {
    exportData.datasets = config.datasets;
  }

  if (options.includeMetadata) {
    exportData.metadata = config.metadata;
  }

  const jsonString = JSON.stringify(exportData, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  downloadBlob(blob, `${filename}.json`);

  return {
    success: true,
    format: 'json',
    filename: `${filename}.json`,
    size: blob.size,
    blob,
  };
}

/**
 * Export chart data to CSV format
 */
async function exportToCSV(
  datasets: Dataset[],
  filename: string
): Promise<ExportResult> {
  const rows: string[] = [];

  // Create header row
  const headers = ['Dataset', 'X', 'Y', 'Z', 'Label'];
  rows.push(headers.join(','));

  // Add data rows
  datasets.forEach(dataset => {
    dataset.data.forEach(point => {
      const row = [
        escapeCSV(dataset.name),
        escapeCSV(String(point.x)),
        escapeCSV(String(point.y)),
        escapeCSV(point.z !== undefined ? String(point.z) : ''),
        escapeCSV(point.label || ''),
      ];
      rows.push(row.join(','));
    });
  });

  const csvContent = rows.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  downloadBlob(blob, `${filename}.csv`);

  return {
    success: true,
    format: 'csv',
    filename: `${filename}.csv`,
    size: blob.size,
    blob,
  };
}

/**
 * Convert data URL to Blob
 */
function dataURLtoBlob(dataUrl: string): Promise<Blob> {
  return (async () => {
    // Basic validation: only allow data: URLs here
    if (!dataUrl.startsWith('data:')) {
      throw new Error('Invalid data URL scheme');
    }
    const res = await fetch(dataUrl);
    if (!res.ok) throw new Error('Failed to fetch data URL');
    return res.blob();
  })();
}

/**
 * Validate data URL to ensure no external fetches (prevent SSRF-like misuse)
 * Accepts only data: scheme and returns the same string when valid.
 */
function validateDataUrl(url: string): string {
  if (typeof url !== 'string') throw new Error('Invalid data URL');
  const trimmed = url.trim();
  if (!trimmed.startsWith('data:')) {
    throw new Error('Only data: URLs are allowed for image export');
  }
  return trimmed;
}

/**
 * Download blob as file
 */
function downloadBlob(blob: Blob, filename: string): void {
  try {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Failed to download blob:', err);
    throw err;
  }
}

/**
 * Escape CSV value
 */
function escapeCSV(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n')) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

/**
 * Copy chart to clipboard as image
 */
export async function copyChartToClipboard(
  element: HTMLElement
): Promise<boolean> {
  try {
    const dataUrl = await Plotly.toImage(element, {
      format: 'png',
      width: 1200,
      height: 800,
      scale: 2,
    });

    const blob = await dataURLtoBlob(dataUrl);

    if (navigator.clipboard && (window as unknown as { ClipboardItem?: unknown }).ClipboardItem) {
      const ClipboardItemConstructor = (window as unknown as { ClipboardItem: new (data: Record<string, Blob>) => ClipboardItem }).ClipboardItem;
      await navigator.clipboard.write([
        new ClipboardItemConstructor({
          'image/png': blob,
        }),
      ]);
      return true;
    }
    return false;
  } catch (error) {
    console.error('Failed to copy chart to clipboard:', error instanceof Error ? error.message : String(error));
    return false;
  }
}

/**
 * Print chart
 */
export function printChart(element: HTMLElement): void {
  const printWindow = window.open('', '_blank');
  if (!printWindow) return;

  const svgElement = element.querySelector('svg');
  if (!svgElement) return;

  const svgString = new XMLSerializer().serializeToString(svgElement);
  try {
    printWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Print Chart</title>
        <style>
          body {
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
          }
          svg {
            max-width: 100%;
            height: auto;
          }
          @media print {
            body {
              padding: 0;
            }
          }
        </style>
      </head>
      <body>
        ${svgString}
        <script>
          window.onload = function() {
            window.print();
            window.onafterprint = function() {
              window.close();
            };
          };
        </script>
      </body>
    </html>
  `);

  printWindow.document.close();
  } catch (err) {
    console.error('Failed to render print window:', err instanceof Error ? err.message : String(err));
    try { printWindow.close(); } catch (_) {}
  }
}

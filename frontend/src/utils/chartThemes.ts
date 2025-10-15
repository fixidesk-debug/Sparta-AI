/**
 * Chart Theme Configurations for Sparta AI
 * 
 * Predefined themes for light and dark modes with Plotly.js templates
 */

import { ChartTheme } from '../types/visualization';

/**
 * Light theme configuration
 */
export const lightTheme: ChartTheme = {
  name: 'light',
  backgroundColor: '#ffffff',
  textColor: '#1f2937',
  gridColor: '#e5e7eb',
  axisColor: '#6b7280',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  fontSize: 12,
  titleFontSize: 16,
  colorPalette: [
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // purple
    '#ec4899', // pink
    '#06b6d4', // cyan
    '#f97316', // orange
  ],
  borderWidth: 1,
  opacity: 0.8,
  plotlyTemplate: 'plotly_white',
};

/**
 * Dark theme configuration
 */
export const darkTheme: ChartTheme = {
  name: 'dark',
  backgroundColor: '#1f2937',
  textColor: '#f9fafb',
  gridColor: '#374151',
  axisColor: '#9ca3af',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  fontSize: 12,
  titleFontSize: 16,
  colorPalette: [
    '#60a5fa', // blue
    '#34d399', // green
    '#fbbf24', // amber
    '#f87171', // red
    '#a78bfa', // purple
    '#f472b6', // pink
    '#22d3ee', // cyan
    '#fb923c', // orange
  ],
  borderWidth: 1,
  opacity: 0.8,
  plotlyTemplate: 'plotly_dark',
};

/**
 * Get theme based on user preference
 */
export function getTheme(theme: 'light' | 'dark' | 'auto'): ChartTheme {
  if (theme === 'auto') {
    // Check system preference
    if (typeof window !== 'undefined') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      return prefersDark ? darkTheme : lightTheme;
    }
    return lightTheme;
  }
  return theme === 'dark' ? darkTheme : lightTheme;
}

/**
 * Color scheme palettes for different visualization types
 */
export const colorSchemes: Record<string, string[]> = {
  default: lightTheme.colorPalette,
  
  viridis: [
    '#440154', '#482878', '#3e4989', '#31688e',
    '#26828e', '#1f9e89', '#35b779', '#6ece58',
    '#b5de2b', '#fde724',
  ],
  
  plasma: [
    '#0d0887', '#46039f', '#7201a8', '#9c179e',
    '#bd3786', '#d8576b', '#ed7953', '#fb9f3a',
    '#fdca26', '#f0f921',
  ],
  
  inferno: [
    '#000004', '#1b0c41', '#4a0c6b', '#781c6d',
    '#a52c60', '#cf4446', '#ed6925', '#fb9b06',
    '#f7d13d', '#fcffa4',
  ],
  
  magma: [
    '#000004', '#180f3d', '#440f76', '#721f81',
    '#9e2f7f', '#cd4071', '#f1605d', '#fd9668',
    '#fec287', '#fcfdbf',
  ],
  
  blues: [
    '#f7fbff', '#deebf7', '#c6dbef', '#9ecae1',
    '#6baed6', '#4292c6', '#2171b5', '#08519c',
    '#08306b',
  ],
  
  reds: [
    '#fff5f0', '#fee0d2', '#fcbba1', '#fc9272',
    '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15',
    '#67000d',
  ],
  
  greens: [
    '#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b',
    '#74c476', '#41ab5d', '#238b45', '#006d2c',
    '#00441b',
  ],
  
  categorical: [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
    '#bcbd22', '#17becf',
  ],
  
  diverging: [
    '#d73027', '#f46d43', '#fdae61', '#fee090',
    '#ffffbf', '#e0f3f8', '#abd9e9', '#74add1',
    '#4575b4',
  ],
};

/**
 * Get color scheme palette
 */
export function getColorScheme(scheme: string): string[] {
  return colorSchemes[scheme] || colorSchemes.default;
}

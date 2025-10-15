/**
 * Chat Theme Configuration
 * Theme tokens and styled-components theme for Sparta AI chat interface
 */

export const chatTheme = {
  colors: {
    // Primary colors
    primary: {
      900: '#0a0e27',
      800: '#1a1f3a',
      700: '#2a304d',
      600: '#3a4160',
      500: '#4a5273',
    },
    // Accent colors
    accent: {
      600: '#1e40af',
      500: '#2563eb',
      400: '#3b82f6',
      300: '#60a5fa',
      200: '#93c5fd',
    },
    // Neutral colors
    neutral: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a',
    },
    // Semantic colors
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    // Message types
    query: '#3b82f6',
    analysis: '#8b5cf6',
    result: '#10b981',
    // Glass effects
    glass: {
      light: 'rgba(255, 255, 255, 0.1)',
      dark: 'rgba(10, 14, 39, 0.4)',
      accent: 'rgba(37, 99, 235, 0.15)',
    },
  },
  
  gradients: {
    userMessage: 'linear-gradient(135deg, #2563eb 0%, #1e40af 100%)',
    aiMessage: 'linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(30, 64, 175, 0.1) 100%)',
    accent: 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)',
    error: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    success: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
  },
  
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    xxl: '32px',
    xxxl: '48px',
  },
  
  borderRadius: {
    sm: '6px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    full: '9999px',
  },
  
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px rgba(0, 0, 0, 0.07)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px rgba(0, 0, 0, 0.15)',
    glass: '0 8px 32px rgba(10, 14, 39, 0.2)',
    glow: '0 0 20px rgba(37, 99, 235, 0.3)',
  },
  
  typography: {
    fonts: {
      body: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      heading: "'SF Pro Display', 'Inter', sans-serif",
      code: "'JetBrains Mono', 'Fira Code', 'Monaco', monospace",
    },
    sizes: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
    },
    weights: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeights: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  
  breakpoints: {
    xs: '320px',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    base: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: '500ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },
  
  zIndex: {
    base: 0,
    dropdown: 100,
    sticky: 200,
    fixed: 300,
    modal: 500,
    tooltip: 700,
  },
} as const;

// Styled-components type declaration
declare module 'styled-components' {
  export interface DefaultTheme {
    colors: {
      primary: { 900: string; 800: string; 700: string; 600: string; 500: string };
      accent: { 600: string; 500: string; 400: string; 300: string; 200: string };
      neutral: { 50: string; 100: string; 200: string; 300: string; 400: string; 500: string; 600: string; 700: string; 800: string; 900: string };
      success: string;
      warning: string;
      error: string;
      info: string;
      query: string;
      analysis: string;
      result: string;
      glass: { light: string; dark: string; accent: string };
    };
    gradients: {
      userMessage: string;
      aiMessage: string;
      accent: string;
      error: string;
      success: string;
    };
    spacing: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
      xxl: string;
      xxxl: string;
    };
    borderRadius: {
      sm: string;
      md: string;
      lg: string;
      xl: string;
      full: string;
    };
    shadows: {
      sm: string;
      md: string;
      lg: string;
      xl: string;
      glass: string;
      glow: string;
    };
    typography: {
      fonts: { body: string; heading: string; code: string };
      sizes: { xs: string; sm: string; base: string; lg: string; xl: string; '2xl': string; '3xl': string };
      weights: { normal: number; medium: number; semibold: number; bold: number };
      lineHeights: { tight: number; normal: number; relaxed: number };
    };
    breakpoints: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
      '2xl': string;
    };
    transitions: {
      fast: string;
      base: string;
      slow: string;
      bounce: string;
    };
    zIndex: {
      base: number;
      dropdown: number;
      sticky: number;
      fixed: number;
      modal: number;
      tooltip: number;
    };
  }
}

// Media query helpers
export const media = {
  xs: `@media (min-width: ${chatTheme.breakpoints.xs})`,
  sm: `@media (min-width: ${chatTheme.breakpoints.sm})`,
  md: `@media (min-width: ${chatTheme.breakpoints.md})`,
  lg: `@media (min-width: ${chatTheme.breakpoints.lg})`,
  xl: `@media (min-width: ${chatTheme.breakpoints.xl})`,
  '2xl': `@media (min-width: ${chatTheme.breakpoints['2xl']})`,
};

// Glass morphism mixin
export const glassMorphism = (blur = '12px', opacity = 0.1) => `
  background: rgba(255, 255, 255, ${opacity});
  backdrop-filter: blur(${blur}) saturate(150%);
  -webkit-backdrop-filter: blur(${blur}) saturate(150%);
  border: 1px solid rgba(255, 255, 255, 0.18);
`;

// Hover lift effect
export const hoverLift = `
  transition: transform 200ms cubic-bezier(0.4, 0, 0.2, 1), box-shadow 200ms cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

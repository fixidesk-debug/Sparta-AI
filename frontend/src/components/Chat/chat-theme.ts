/**
 * Chat Theme for Styled-Components
 * Bridges the CSS variables from the main design system to be used in styled-components.
 */

export const theme = {
  colors: {
    bgPrimary: 'var(--bg-primary)',
    bgGradient: 'var(--bg-gradient)',
    textPrimary: 'var(--text-primary)',
    textSecondary: 'var(--text-secondary)',
    accent: 'var(--accent)',
    glassBg: 'var(--glass-bg)',
    glassBorder: 'var(--glass-border)',
    glassShadow: 'var(--glass-shadow)',
    btnPrimaryBg: 'var(--btn-primary-bg)',
    btnPrimaryText: 'var(--btn-primary-text)',
  },
  fonts: {
    primary: 'var(--font-primary)',
  },
  spacing: {
    s1: 'var(--spacing-1)', // 8px
    s2: 'var(--spacing-2)', // 16px
    s3: 'var(--spacing-3)', // 24px
    s4: 'var(--spacing-4)', // 32px
  },
  radii: {
    md: 'var(--radius-md)', // 12px
    lg: 'var(--radius-lg)', // 16px
    xl: 'var(--radius-xl)', // 24px
  },
  transitions: {
    medium: 'var(--transition-medium)',
  },
};

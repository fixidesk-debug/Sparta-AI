import React, { useEffect, useRef, useCallback, useState } from 'react';
import { createPortal } from 'react-dom';
import { X } from '../icons';
import './Modal.scss';

// =====================
// Type Definitions
// =====================

export type ModalSize = 'small' | 'medium' | 'large' | 'full';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  size?: ModalSize;
  title?: string;
  children: React.ReactNode;
  showCloseButton?: boolean;
  closeOnBackdropClick?: boolean;
  closeOnEscape?: boolean;
  preventScroll?: boolean;
  className?: string;
  backdropClassName?: string;
  animation?: boolean;
}

// =====================
// Modal Component
// =====================

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  size = 'medium',
  title,
  children,
  showCloseButton = true,
  closeOnBackdropClick = true,
  closeOnEscape = true,
  preventScroll = true,
  className = '',
  backdropClassName = '',
  animation = true,
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  // Focus trap
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'Escape' && closeOnEscape) {
        onClose();
      }

      if (e.key === 'Tab') {
        const focusableElements = modalRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (!focusableElements || focusableElements.length === 0) return;

        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    },
    [isOpen, closeOnEscape, onClose]
  );

  // Handle backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (closeOnBackdropClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  // Manage focus and scroll
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;

      // Prevent body scroll
      if (preventScroll) {
        document.body.style.overflow = 'hidden';
      }

      // Focus first focusable element
      setTimeout(() => {
        const firstFocusable = modalRef.current?.querySelector(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        ) as HTMLElement;
        firstFocusable?.focus();
      }, 100);

      // Animation delay
      if (animation) {
        setIsAnimating(true);
        setTimeout(() => setIsAnimating(false), 300);
      }
    } else {
      // Restore scroll
      document.body.style.overflow = '';

      // Restore focus
      previousActiveElement.current?.focus();
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen, preventScroll, animation]);

  // Add keyboard listeners
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  if (!isOpen) return null;

  const modalContent = (
    <div className={`modal-backdrop ${backdropClassName} ${animation ? 'modal-fade-in' : ''}`} onClick={handleBackdropClick}>
      <div
        ref={modalRef}
        className={`modal-container modal-${size} ${className} ${animation ? 'modal-scale-in' : ''} ${isAnimating ? 'modal-animating' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
      >
        {showCloseButton && (
          <button
            className="modal-close-button"
            onClick={onClose}
            aria-label="Close modal"
            type="button"
          >
            <X size={20} />
          </button>
        )}

        {title && (
          <div className="modal-header">
            <h2 id="modal-title" className="modal-title">
              {title}
            </h2>
          </div>
        )}

        <div className="modal-body">{children}</div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

// =====================
// Modal Footer Component
// =====================

export interface ModalFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const ModalFooter: React.FC<ModalFooterProps> = ({ children, className = '' }) => (
  <div className={`modal-footer ${className}`}>{children}</div>
);

// =====================
// Modal Actions Component
// =====================

export interface ModalActionsProps {
  children: React.ReactNode;
  align?: 'left' | 'center' | 'right' | 'space-between';
  className?: string;
}

export const ModalActions: React.FC<ModalActionsProps> = ({
  children,
  align = 'right',
  className = '',
}) => <div className={`modal-actions modal-actions-${align} ${className}`}>{children}</div>;

// =====================
// Button Components
// =====================

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  children,
  className = '',
  disabled,
  ...props
}) => (
  <button
    className={`btn btn-${variant} btn-${size} ${fullWidth ? 'btn-full-width' : ''} ${loading ? 'btn-loading' : ''} ${className}`}
    disabled={disabled || loading}
    {...props}
  >
    {loading && <span className="btn-spinner" />}
    {!loading && icon && iconPosition === 'left' && <span className="btn-icon btn-icon-left">{icon}</span>}
    {children}
    {!loading && icon && iconPosition === 'right' && <span className="btn-icon btn-icon-right">{icon}</span>}
  </button>
);

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  variant = 'ghost',
  size = 'medium',
  loading = false,
  className = '',
  disabled,
  ...props
}) => (
  <button
    className={`icon-btn icon-btn-${variant} icon-btn-${size} ${loading ? 'btn-loading' : ''} ${className}`}
    disabled={disabled || loading}
    {...props}
  >
    {loading ? <span className="btn-spinner" /> : icon}
  </button>
);

// =====================
// Toggle Component
// =====================

export interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  className?: string;
}

export const Toggle: React.FC<ToggleProps> = ({
  checked,
  onChange,
  label,
  description,
  disabled = false,
  className = '',
}) => (
  <label className={`toggle-container ${disabled ? 'toggle-disabled' : ''} ${className}`}>
    <div className="toggle-content">
      {label && <span className="toggle-label">{label}</span>}
      {description && <span className="toggle-description">{description}</span>}
    </div>
    <div className="toggle-switch">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="toggle-input"
      />
      <span className="toggle-slider" />
    </div>
  </label>
);

// =====================
// Input Components
// =====================

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  className = '',
  ...props
}) => (
  <div className={`input-group ${fullWidth ? 'input-full-width' : ''} ${className}`}>
    {label && <label className="input-label">{label}</label>}
    <div className={`input-wrapper ${error ? 'input-error' : ''} ${icon ? 'input-with-icon' : ''}`}>
      {icon && iconPosition === 'left' && <span className="input-icon input-icon-left">{icon}</span>}
      <input className="input-field" {...props} />
      {icon && iconPosition === 'right' && <span className="input-icon input-icon-right">{icon}</span>}
    </div>
    {error && <span className="input-error-text">{error}</span>}
    {!error && helperText && <span className="input-helper-text">{helperText}</span>}
  </div>
);

// =====================
// Progress Bar Component
// =====================

export interface ProgressBarProps {
  progress: number;
  showLabel?: boolean;
  label?: string;
  variant?: 'default' | 'success' | 'warning' | 'error';
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  showLabel = true,
  label,
  variant = 'default',
  className = '',
}) => (
  <div className={`progress-bar-container ${className}`}>
    {(showLabel || label) && (
      <div className="progress-bar-header">
        <span className="progress-bar-label">{label || 'Progress'}</span>
        {showLabel && <span className="progress-bar-percentage">{Math.round(progress)}%</span>}
      </div>
    )}
    <div className="progress-bar-track">
      <div
        className={`progress-bar-fill progress-bar-${variant}`}
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
    </div>
  </div>
);

// =====================
// Alert Component
// =====================

export interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  onClose?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  type,
  title,
  message,
  onClose,
  className = '',
}) => (
  <div className={`alert alert-${type} ${className}`} role="alert">
    <div className="alert-content">
      {title && <div className="alert-title">{title}</div>}
      <div className="alert-message">{message}</div>
    </div>
    {onClose && (
      <button className="alert-close" onClick={onClose} aria-label="Close alert">
        <X size={16} />
      </button>
    )}
  </div>
);

// =====================
// Loading Spinner Component
// =====================

export interface SpinnerProps {
  size?: 'small' | 'medium' | 'large';
  label?: string;
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'medium',
  label,
  className = '',
}) => (
  <div className={`spinner-container ${className}`}>
    <div className={`spinner spinner-${size}`} />
    {label && <span className="spinner-label">{label}</span>}
  </div>
);

export default Modal;

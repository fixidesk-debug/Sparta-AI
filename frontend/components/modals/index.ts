/**
 * Modal Components
 * 
 * A comprehensive modal component library with glass morphism design,
 * portal rendering, focus management, and accessibility features.
 * 
 * @module components/modals
 */

// Base Modal Components
export { default as Modal } from './Modal';
export type { ModalProps, ModalFooterProps, ModalActionsProps } from './Modal';

// UI Components
export { Button, IconButton, Toggle, Input, ProgressBar, Alert, Spinner } from './Modal';
export type {
  ButtonProps,
  IconButtonProps,
  ToggleProps,
  InputProps,
  ProgressBarProps,
  AlertProps,
  SpinnerProps,
} from './Modal';

// Export Modal
export { default as ExportModal } from './ExportModal';
export type {
  ExportModalProps,
  ExportFormat,
  ExportQuality,
  ExportStep,
  ExportOptions,
} from './ExportModal';

// Share Modal
export { default as ShareModal } from './ShareModal';
export type {
  ShareModalProps,
  AccessLevel,
  SocialPlatform,
  ShareSettings,
} from './ShareModal';

// Example Component
export { default as ModalExample } from './ModalExample';

// SCSS Styles (import this in your main App or component)
import './Modal.scss';

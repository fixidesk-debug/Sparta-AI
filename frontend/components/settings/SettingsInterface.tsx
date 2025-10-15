import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Palette,
  Zap,
  Database,
  Download,
  Code,
  Shield,
  HelpCircle,
  Search,
  Save,
  RotateCcw,
  Moon,
  Sun,
  Monitor,
  Bell,
  Lock,
  Globe,
  Sliders,
  Upload,
  CheckCircle,
  XCircle,
  AlertCircle,
  X,
  ChevronRight,
  ChevronDown,
  Menu,
  Eye,
  EyeOff,
} from '../icons';
import './SettingsInterface.scss';

// Types
export interface SettingsCategory {
  id: string;
  label: string;
  icon: React.ReactNode;
  color: string;
}

export interface SettingItem {
  id: string;
  label: string;
  type: 'toggle' | 'select' | 'input' | 'slider' | 'color' | 'file' | 'radio' | 'checkbox';
  value: any;
  options?: Array<{ value: string; label: string }>;
  helperText?: string;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  required?: boolean;
  disabled?: boolean;
  warning?: string;
  validation?: (value: any) => string | null;
}

export interface SettingsSection {
  id: string;
  title: string;
  description?: string;
  items: SettingItem[];
  collapsible?: boolean;
  defaultCollapsed?: boolean;
}

export interface SettingsCategoryData {
  category: string;
  sections: SettingsSection[];
}

interface SettingsInterfaceProps {
  categories?: SettingsCategory[];
  settingsData?: SettingsCategoryData[];
  onSave?: (settings: Record<string, any>) => void;
  onReset?: () => void;
  onExport?: () => void;
  onImport?: (data: any) => void;
  searchEnabled?: boolean;
  autoSave?: boolean;
  showResetButton?: boolean;
}

const defaultCategories: SettingsCategory[] = [
  { id: 'general', label: 'General', icon: <SettingsIcon size={20} />, color: '#2563eb' },
  { id: 'appearance', label: 'Appearance', icon: <Palette size={20} />, color: '#8b5cf6' },
  { id: 'performance', label: 'Performance', icon: <Zap size={20} />, color: '#10b981' },
  { id: 'data', label: 'Data', icon: <Database size={20} />, color: '#f59e0b' },
  { id: 'export', label: 'Export', icon: <Download size={20} />, color: '#06b6d4' },
  { id: 'advanced', label: 'Advanced', icon: <Code size={20} />, color: '#64748b' },
  { id: 'privacy', label: 'Privacy', icon: <Shield size={20} />, color: '#ef4444' },
  { id: 'help', label: 'Help & Support', icon: <HelpCircle size={20} />, color: '#6366f1' },
];

const SettingsInterface: React.FC<SettingsInterfaceProps> = ({
  categories = defaultCategories,
  settingsData = [],
  onSave,
  onReset,
  onExport,
  onImport,
  searchEnabled = true,
  autoSave = false,
  showResetButton = true,
}) => {
  const [activeCategory, setActiveCategory] = useState(categories[0]?.id || 'general');
  const [searchQuery, setSearchQuery] = useState('');
  const [settings, setSettings] = useState<Record<string, any>>({});
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [showPassword, setShowPassword] = useState<Record<string, boolean>>({});

  // Initialize settings from data
  useEffect(() => {
    const initialSettings: Record<string, any> = {};
    settingsData.forEach(categoryData => {
      categoryData.sections.forEach(section => {
        section.items.forEach(item => {
          initialSettings[item.id] = item.value;
        });
      });
    });
    setSettings(initialSettings);
  }, [settingsData]);

  // Auto-save functionality
  useEffect(() => {
    if (autoSave && hasChanges && !isSaving) {
      const timer = setTimeout(() => {
        handleSave();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [settings, hasChanges, autoSave]);

  const handleSettingChange = (itemId: string, value: any, validation?: (value: any) => string | null) => {
    // Validate if validation function exists
    if (validation) {
      const error = validation(value);
      if (error) {
        setValidationErrors(prev => ({ ...prev, [itemId]: error }));
        return;
      } else {
        setValidationErrors(prev => {
          const newErrors = { ...prev };
          delete newErrors[itemId];
          return newErrors;
        });
      }
    }

    setSettings(prev => ({ ...prev, [itemId]: value }));
    setHasChanges(true);
    setSaveSuccess(false);
    setSaveError(null);
  };

  const handleSave = async () => {
    // Check for validation errors
    if (Object.keys(validationErrors).length > 0) {
      setSaveError('Please fix validation errors before saving');
      return;
    }

    setIsSaving(true);
    setSaveError(null);

    try {
      await onSave?.(settings);
      setSaveSuccess(true);
      setHasChanges(false);
      
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all settings to default?')) {
      onReset?.();
      setHasChanges(false);
      setSaveSuccess(false);
      setSaveError(null);
      setValidationErrors({});
    }
  };

  const handleExport = () => {
    onExport?.();
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string);
          onImport?.(data);
          setHasChanges(true);
        } catch (error) {
          setSaveError('Invalid settings file');
        }
      };
      reader.readAsText(file);
    }
  };

  const toggleSection = (sectionId: string) => {
    setCollapsedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };

  const getCurrentCategoryData = () => {
    return settingsData.find(data => data.category === activeCategory);
  };

  const filterSections = (sections: SettingsSection[]) => {
    if (!searchQuery) return sections;
    
    return sections
      .map(section => ({
        ...section,
        items: section.items.filter(item =>
          item.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.helperText?.toLowerCase().includes(searchQuery.toLowerCase())
        ),
      }))
      .filter(section => section.items.length > 0);
  };

  const renderSettingItem = (item: SettingItem) => {
    const value = settings[item.id] ?? item.value;
    const error = validationErrors[item.id];

    switch (item.type) {
      case 'toggle':
        return (
          <div className={`setting-item setting-item--toggle ${item.disabled ? 'setting-item--disabled' : ''}`}>
            <div className="setting-item__info">
              <label className="setting-item__label" htmlFor={item.id}>
                {item.label}
                {item.required && <span className="setting-item__required">*</span>}
              </label>
              {item.helperText && <p className="setting-item__helper">{item.helperText}</p>}
              {item.warning && <p className="setting-item__warning">{item.warning}</p>}
              {error && <p className="setting-item__error">{error}</p>}
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                id={item.id}
                checked={value}
                onChange={(e) => handleSettingChange(item.id, e.target.checked, item.validation)}
                disabled={item.disabled}
              />
              <span className="toggle-switch__slider"></span>
            </label>
          </div>
        );

      case 'select':
        return (
          <div className={`setting-item setting-item--select ${item.disabled ? 'setting-item--disabled' : ''}`}>
            <div className="setting-item__info">
              <label className="setting-item__label" htmlFor={item.id}>
                {item.label}
                {item.required && <span className="setting-item__required">*</span>}
              </label>
              {item.helperText && <p className="setting-item__helper">{item.helperText}</p>}
              {item.warning && <p className="setting-item__warning">{item.warning}</p>}
              {error && <p className="setting-item__error">{error}</p>}
            </div>
            <select
              id={item.id}
              className="select-input"
              value={value}
              onChange={(e) => handleSettingChange(item.id, e.target.value, item.validation)}
              disabled={item.disabled}
            >
              {item.options?.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        );

      case 'input':
        const isPassword = item.id.toLowerCase().includes('password');
        return (
          <div className={`setting-item setting-item--input ${item.disabled ? 'setting-item--disabled' : ''}`}>
            <div className="setting-item__info">
              <label className="setting-item__label" htmlFor={item.id}>
                {item.label}
                {item.required && <span className="setting-item__required">*</span>}
              </label>
              {item.helperText && <p className="setting-item__helper">{item.helperText}</p>}
              {item.warning && <p className="setting-item__warning">{item.warning}</p>}
              {error && <p className="setting-item__error">{error}</p>}
            </div>
            <div className="input-wrapper">
              <input
                type={isPassword && !showPassword[item.id] ? 'password' : 'text'}
                id={item.id}
                className={`text-input ${error ? 'text-input--error' : ''}`}
                value={value || ''}
                placeholder={item.placeholder}
                onChange={(e) => handleSettingChange(item.id, e.target.value, item.validation)}
                disabled={item.disabled}
              />
              {isPassword && (
                <button
                  type="button"
                  className="input-toggle-button"
                  onClick={() => setShowPassword(prev => ({ ...prev, [item.id]: !prev[item.id] }))}
                >
                  {showPassword[item.id] ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              )}
            </div>
          </div>
        );

      case 'slider':
        return (
          <div className={`setting-item setting-item--slider ${item.disabled ? 'setting-item--disabled' : ''}`}>
            <div className="setting-item__info">
              <label className="setting-item__label" htmlFor={item.id}>
                {item.label}
                {item.required && <span className="setting-item__required">*</span>}
                <span className="setting-item__value">{value}</span>
              </label>
              {item.helperText && <p className="setting-item__helper">{item.helperText}</p>}
              {item.warning && <p className="setting-item__warning">{item.warning}</p>}
              {error && <p className="setting-item__error">{error}</p>}
            </div>
            <input
              type="range"
              id={item.id}
              className="range-input"
              value={value}
              min={item.min ?? 0}
              max={item.max ?? 100}
              step={item.step ?? 1}
              onChange={(e) => handleSettingChange(item.id, Number(e.target.value), item.validation)}
              disabled={item.disabled}
            />
          </div>
        );

      case 'color':
        return (
          <div className={`setting-item setting-item--color ${item.disabled ? 'setting-item--disabled' : ''}`}>
            <div className="setting-item__info">
              <label className="setting-item__label" htmlFor={item.id}>
                {item.label}
                {item.required && <span className="setting-item__required">*</span>}
              </label>
              {item.helperText && <p className="setting-item__helper">{item.helperText}</p>}
              {item.warning && <p className="setting-item__warning">{item.warning}</p>}
              {error && <p className="setting-item__error">{error}</p>}
            </div>
            <div className="color-picker">
              <input
                type="color"
                id={item.id}
                className="color-input"
                value={value}
                onChange={(e) => handleSettingChange(item.id, e.target.value, item.validation)}
                disabled={item.disabled}
              />
              <span className="color-value">{value}</span>
            </div>
          </div>
        );

      case 'radio':
        return (
          <div className={`setting-item setting-item--radio ${item.disabled ? 'setting-item--disabled' : ''}`}>
            <div className="setting-item__info">
              <label className="setting-item__label">
                {item.label}
                {item.required && <span className="setting-item__required">*</span>}
              </label>
              {item.helperText && <p className="setting-item__helper">{item.helperText}</p>}
              {item.warning && <p className="setting-item__warning">{item.warning}</p>}
              {error && <p className="setting-item__error">{error}</p>}
            </div>
            <div className="radio-group">
              {item.options?.map(option => (
                <label key={option.value} className="radio-label">
                  <input
                    type="radio"
                    name={item.id}
                    value={option.value}
                    checked={value === option.value}
                    onChange={(e) => handleSettingChange(item.id, e.target.value, item.validation)}
                    disabled={item.disabled}
                  />
                  <span className="radio-custom"></span>
                  <span className="radio-text">{option.label}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'checkbox':
        return (
          <div className={`setting-item setting-item--checkbox ${item.disabled ? 'setting-item--disabled' : ''}`}>
            <label className="checkbox-label">
              <input
                type="checkbox"
                id={item.id}
                checked={value}
                onChange={(e) => handleSettingChange(item.id, e.target.checked, item.validation)}
                disabled={item.disabled}
              />
              <span className="checkbox-custom">
                <CheckCircle size={16} className="checkbox-icon" />
              </span>
              <span className="checkbox-content">
                <span className="checkbox-text">
                  {item.label}
                  {item.required && <span className="setting-item__required">*</span>}
                </span>
                {item.helperText && <span className="checkbox-helper">{item.helperText}</span>}
              </span>
            </label>
            {item.warning && <p className="setting-item__warning">{item.warning}</p>}
            {error && <p className="setting-item__error">{error}</p>}
          </div>
        );

      case 'file':
        return (
          <div className={`setting-item setting-item--file ${item.disabled ? 'setting-item--disabled' : ''}`}>
            <div className="setting-item__info">
              <label className="setting-item__label">
                {item.label}
                {item.required && <span className="setting-item__required">*</span>}
              </label>
              {item.helperText && <p className="setting-item__helper">{item.helperText}</p>}
              {item.warning && <p className="setting-item__warning">{item.warning}</p>}
              {error && <p className="setting-item__error">{error}</p>}
            </div>
            <label className="file-upload">
              <input
                type="file"
                id={item.id}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    handleSettingChange(item.id, file.name, item.validation);
                  }
                }}
                disabled={item.disabled}
              />
              <Upload size={20} />
              <span>{value || 'Choose file...'}</span>
            </label>
          </div>
        );

      default:
        return null;
    }
  };

  const categoryData = getCurrentCategoryData();
  const filteredSections = categoryData ? filterSections(categoryData.sections) : [];

  return (
    <div className="settings-interface">
      {/* Mobile Menu Button */}
      <button
        className="settings-mobile-menu"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        <Menu size={24} />
      </button>

      {/* Sidebar */}
      <aside className={`settings-sidebar ${sidebarOpen ? 'settings-sidebar--open' : ''}`}>
        <div className="settings-sidebar__header">
          <h2 className="settings-sidebar__title">Settings</h2>
          <button
            className="settings-sidebar__close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>
        <nav className="settings-nav">
          {categories.map(category => (
            <button
              key={category.id}
              className={`settings-nav__item ${activeCategory === category.id ? 'settings-nav__item--active' : ''}`}
              onClick={() => {
                setActiveCategory(category.id);
                setSidebarOpen(false);
              }}
              style={{ '--category-color': category.color } as React.CSSProperties}
            >
              <span className="settings-nav__icon">{category.icon}</span>
              <span className="settings-nav__label">{category.label}</span>
              <ChevronRight size={16} className="settings-nav__arrow" />
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="settings-main">
        {/* Header */}
        <header className="settings-header">
          <div className="settings-header__title">
            <h1>{categories.find(c => c.id === activeCategory)?.label}</h1>
            {hasChanges && !autoSave && (
              <span className="settings-header__badge">Unsaved changes</span>
            )}
          </div>
          {searchEnabled && (
            <div className="settings-search">
              <Search size={18} className="settings-search__icon" />
              <input
                type="text"
                className="settings-search__input"
                placeholder="Search settings..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button
                  className="settings-search__clear"
                  onClick={() => setSearchQuery('')}
                  aria-label="Clear search"
                >
                  <X size={16} />
                </button>
              )}
            </div>
          )}
        </header>

        {/* Content */}
        <div className="settings-content">
          {filteredSections.length === 0 ? (
            <div className="settings-empty">
              <AlertCircle size={48} />
              <p>No settings found matching your search.</p>
            </div>
          ) : (
            filteredSections.map(section => {
              const isCollapsed = collapsedSections.has(section.id);
              return (
                <div key={section.id} className="settings-section">
                  <div className="settings-card">
                    <div
                      className={`settings-card__header ${section.collapsible ? 'settings-card__header--collapsible' : ''}`}
                      onClick={() => section.collapsible && toggleSection(section.id)}
                    >
                      <div>
                        <h3 className="settings-card__title">{section.title}</h3>
                        {section.description && (
                          <p className="settings-card__description">{section.description}</p>
                        )}
                      </div>
                      {section.collapsible && (
                        <ChevronDown
                          size={20}
                          className={`settings-card__toggle ${isCollapsed ? 'settings-card__toggle--collapsed' : ''}`}
                        />
                      )}
                    </div>
                    <div className={`settings-card__body ${isCollapsed ? 'settings-card__body--collapsed' : ''}`}>
                      {section.items.map(item => (
                        <div key={item.id}>{renderSettingItem(item)}</div>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Action Bar */}
        <div className="settings-actions">
          <div className="settings-actions__left">
            {showResetButton && (
              <button
                className="settings-button settings-button--secondary"
                onClick={handleReset}
                disabled={isSaving}
              >
                <RotateCcw size={18} />
                Reset to Default
              </button>
            )}
            {onExport && (
              <button
                className="settings-button settings-button--secondary"
                onClick={handleExport}
                disabled={isSaving}
              >
                <Download size={18} />
                Export Settings
              </button>
            )}
            {onImport && (
              <label className="settings-button settings-button--secondary">
                <Upload size={18} />
                Import Settings
                <input
                  type="file"
                  accept=".json"
                  onChange={handleImport}
                  style={{ display: 'none' }}
                  disabled={isSaving}
                />
              </label>
            )}
          </div>
          <div className="settings-actions__right">
            {saveError && (
              <span className="settings-feedback settings-feedback--error">
                <XCircle size={16} />
                {saveError}
              </span>
            )}
            {saveSuccess && (
              <span className="settings-feedback settings-feedback--success">
                <CheckCircle size={16} />
                Settings saved successfully
              </span>
            )}
            {!autoSave && (
              <button
                className="settings-button settings-button--primary"
                onClick={handleSave}
                disabled={isSaving || !hasChanges || Object.keys(validationErrors).length > 0}
              >
                {isSaving ? (
                  <>
                    <span className="settings-button__spinner"></span>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save size={18} />
                    Save Changes
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </main>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="settings-overlay"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
};

export default SettingsInterface;

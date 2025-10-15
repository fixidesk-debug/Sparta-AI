import React, { useState } from 'react';
import SettingsInterface, { SettingsCategory, SettingsCategoryData } from './SettingsInterface';
import {
  Settings as SettingsIcon,
  Palette,
  Zap,
  Database,
  Download,
  Code,
  Shield,
  HelpCircle,
} from '../icons';

const SettingsInterfaceExample: React.FC = () => {
  const [settings, setSettings] = useState<Record<string, any>>({});

  // Sample settings data for all categories
  const settingsData: SettingsCategoryData[] = [
    {
      category: 'general',
      sections: [
        {
          id: 'preferences',
          title: 'General Preferences',
          description: 'Configure your basic application preferences',
          items: [
            {
              id: 'language',
              label: 'Language',
              type: 'select',
              value: 'en',
              options: [
                { value: 'en', label: 'English' },
                { value: 'es', label: 'Spanish' },
                { value: 'fr', label: 'French' },
                { value: 'de', label: 'German' },
                { value: 'zh', label: 'Chinese' },
              ],
              helperText: 'Select your preferred language for the interface',
            },
            {
              id: 'timezone',
              label: 'Timezone',
              type: 'select',
              value: 'UTC',
              options: [
                { value: 'UTC', label: 'UTC' },
                { value: 'America/New_York', label: 'Eastern Time' },
                { value: 'America/Los_Angeles', label: 'Pacific Time' },
                { value: 'Europe/London', label: 'GMT' },
                { value: 'Asia/Tokyo', label: 'Japan Standard Time' },
              ],
              helperText: 'Select your timezone for date and time display',
            },
            {
              id: 'autoSave',
              label: 'Auto-save',
              type: 'toggle',
              value: true,
              helperText: 'Automatically save changes without confirmation',
            },
            {
              id: 'confirmations',
              label: 'Show confirmations',
              type: 'toggle',
              value: true,
              helperText: 'Display confirmation dialogs for destructive actions',
            },
          ],
        },
        {
          id: 'notifications',
          title: 'Notifications',
          description: 'Manage how you receive notifications',
          items: [
            {
              id: 'emailNotifications',
              label: 'Email notifications',
              type: 'toggle',
              value: true,
              helperText: 'Receive notifications via email',
            },
            {
              id: 'pushNotifications',
              label: 'Push notifications',
              type: 'toggle',
              value: false,
              helperText: 'Receive push notifications in your browser',
            },
            {
              id: 'soundEnabled',
              label: 'Sound effects',
              type: 'toggle',
              value: true,
              helperText: 'Play sound for notifications and alerts',
            },
            {
              id: 'notificationFrequency',
              label: 'Notification frequency',
              type: 'radio',
              value: 'instant',
              options: [
                { value: 'instant', label: 'Instant' },
                { value: 'hourly', label: 'Hourly digest' },
                { value: 'daily', label: 'Daily digest' },
                { value: 'never', label: 'Never' },
              ],
              helperText: 'Choose how often you want to receive notifications',
            },
          ],
          collapsible: true,
        },
      ],
    },
    {
      category: 'appearance',
      sections: [
        {
          id: 'theme',
          title: 'Theme Settings',
          description: 'Customize the visual appearance of your application',
          items: [
            {
              id: 'themeMode',
              label: 'Theme mode',
              type: 'radio',
              value: 'auto',
              options: [
                { value: 'light', label: 'Light' },
                { value: 'dark', label: 'Dark' },
                { value: 'auto', label: 'Auto (system)' },
              ],
              helperText: 'Choose your preferred color theme',
            },
            {
              id: 'accentColor',
              label: 'Accent color',
              type: 'color',
              value: '#2563eb',
              helperText: 'Pick your primary accent color',
            },
            {
              id: 'fontSize',
              label: 'Font size',
              type: 'slider',
              value: 14,
              min: 12,
              max: 20,
              step: 1,
              helperText: 'Adjust the base font size (12-20px)',
            },
            {
              id: 'compactMode',
              label: 'Compact mode',
              type: 'toggle',
              value: false,
              helperText: 'Reduce spacing for a more compact interface',
            },
          ],
        },
        {
          id: 'layout',
          title: 'Layout Options',
          description: 'Configure the layout and spacing',
          items: [
            {
              id: 'sidebarPosition',
              label: 'Sidebar position',
              type: 'radio',
              value: 'left',
              options: [
                { value: 'left', label: 'Left' },
                { value: 'right', label: 'Right' },
              ],
              helperText: 'Choose where the sidebar appears',
            },
            {
              id: 'showBreadcrumbs',
              label: 'Show breadcrumbs',
              type: 'checkbox',
              value: true,
              helperText: 'Display breadcrumb navigation',
            },
            {
              id: 'showMinimap',
              label: 'Show minimap',
              type: 'checkbox',
              value: false,
              helperText: 'Display code minimap for navigation',
            },
          ],
          collapsible: true,
        },
      ],
    },
    {
      category: 'performance',
      sections: [
        {
          id: 'optimization',
          title: 'Performance Optimization',
          description: 'Configure performance and resource usage settings',
          items: [
            {
              id: 'enableCaching',
              label: 'Enable caching',
              type: 'toggle',
              value: true,
              helperText: 'Cache data for faster loading times',
            },
            {
              id: 'maxCacheSize',
              label: 'Maximum cache size (MB)',
              type: 'slider',
              value: 100,
              min: 50,
              max: 500,
              step: 50,
              helperText: 'Set the maximum cache storage size',
            },
            {
              id: 'lazyLoading',
              label: 'Lazy load images',
              type: 'toggle',
              value: true,
              helperText: 'Load images only when they appear in viewport',
            },
            {
              id: 'animationsEnabled',
              label: 'Enable animations',
              type: 'toggle',
              value: true,
              helperText: 'Enable UI animations and transitions',
              warning: 'Disabling animations may improve performance on slower devices',
            },
          ],
        },
        {
          id: 'limits',
          title: 'Resource Limits',
          description: 'Set limits for resource consumption',
          items: [
            {
              id: 'maxConcurrentRequests',
              label: 'Max concurrent requests',
              type: 'slider',
              value: 6,
              min: 1,
              max: 10,
              step: 1,
              helperText: 'Maximum number of simultaneous API requests',
            },
            {
              id: 'requestTimeout',
              label: 'Request timeout (seconds)',
              type: 'input',
              value: '30',
              placeholder: 'Enter timeout in seconds',
              helperText: 'Time before a request is considered timed out',
              validation: (value: string) => {
                const num = parseInt(value);
                if (isNaN(num) || num < 5 || num > 120) {
                  return 'Timeout must be between 5 and 120 seconds';
                }
                return null;
              },
            },
          ],
          collapsible: true,
          defaultCollapsed: true,
        },
      ],
    },
    {
      category: 'data',
      sections: [
        {
          id: 'storage',
          title: 'Data Storage',
          description: 'Manage how your data is stored',
          items: [
            {
              id: 'storageLocation',
              label: 'Storage location',
              type: 'radio',
              value: 'local',
              options: [
                { value: 'local', label: 'Local storage' },
                { value: 'session', label: 'Session storage' },
                { value: 'indexeddb', label: 'IndexedDB' },
              ],
              helperText: 'Choose where to store application data',
            },
            {
              id: 'clearOnExit',
              label: 'Clear data on exit',
              type: 'toggle',
              value: false,
              helperText: 'Automatically clear stored data when closing the app',
              warning: 'This will remove all saved preferences and data',
            },
            {
              id: 'backupFrequency',
              label: 'Backup frequency',
              type: 'select',
              value: 'daily',
              options: [
                { value: 'never', label: 'Never' },
                { value: 'daily', label: 'Daily' },
                { value: 'weekly', label: 'Weekly' },
                { value: 'monthly', label: 'Monthly' },
              ],
              helperText: 'How often to create automatic backups',
            },
          ],
        },
        {
          id: 'sync',
          title: 'Data Synchronization',
          description: 'Configure data sync settings',
          items: [
            {
              id: 'enableSync',
              label: 'Enable sync',
              type: 'toggle',
              value: false,
              helperText: 'Synchronize data across devices',
            },
            {
              id: 'syncOnMobile',
              label: 'Sync on mobile',
              type: 'checkbox',
              value: false,
              helperText: 'Enable sync when using mobile data',
              warning: 'This may consume mobile data',
            },
          ],
          collapsible: true,
        },
      ],
    },
    {
      category: 'export',
      sections: [
        {
          id: 'exportOptions',
          title: 'Export Options',
          description: 'Configure export and download settings',
          items: [
            {
              id: 'exportFormat',
              label: 'Default export format',
              type: 'select',
              value: 'json',
              options: [
                { value: 'json', label: 'JSON' },
                { value: 'csv', label: 'CSV' },
                { value: 'xml', label: 'XML' },
                { value: 'pdf', label: 'PDF' },
              ],
              helperText: 'Choose the default format for exports',
            },
            {
              id: 'includeMetadata',
              label: 'Include metadata',
              type: 'checkbox',
              value: true,
              helperText: 'Include timestamps and user information in exports',
            },
            {
              id: 'compressExports',
              label: 'Compress exports',
              type: 'checkbox',
              value: false,
              helperText: 'Create compressed ZIP files for exports',
            },
            {
              id: 'autoDownload',
              label: 'Auto-download after export',
              type: 'toggle',
              value: true,
              helperText: 'Automatically download files after export completes',
            },
          ],
        },
      ],
    },
    {
      category: 'advanced',
      sections: [
        {
          id: 'developer',
          title: 'Developer Options',
          description: 'Advanced settings for developers',
          items: [
            {
              id: 'developerMode',
              label: 'Developer mode',
              type: 'toggle',
              value: false,
              helperText: 'Enable developer tools and debugging features',
              warning: 'Only enable if you know what you are doing',
            },
            {
              id: 'apiEndpoint',
              label: 'API endpoint',
              type: 'input',
              value: 'https://api.sparta-ai.com',
              placeholder: 'Enter API endpoint URL',
              helperText: 'Custom API endpoint for advanced users',
              required: true,
              validation: (value: string) => {
                if (!value.startsWith('http://') && !value.startsWith('https://')) {
                  return 'URL must start with http:// or https://';
                }
                return null;
              },
            },
            {
              id: 'debugLevel',
              label: 'Debug level',
              type: 'select',
              value: 'error',
              options: [
                { value: 'none', label: 'None' },
                { value: 'error', label: 'Errors only' },
                { value: 'warning', label: 'Warnings & Errors' },
                { value: 'info', label: 'Info, Warnings & Errors' },
                { value: 'debug', label: 'All debug info' },
              ],
              helperText: 'Set the level of debug logging',
            },
          ],
        },
        {
          id: 'experimental',
          title: 'Experimental Features',
          description: 'Try out new features before official release',
          items: [
            {
              id: 'betaFeatures',
              label: 'Enable beta features',
              type: 'toggle',
              value: false,
              helperText: 'Access experimental features in beta',
              warning: 'Beta features may be unstable',
            },
            {
              id: 'telemetry',
              label: 'Send usage data',
              type: 'toggle',
              value: true,
              helperText: 'Help improve the app by sending anonymous usage data',
            },
          ],
          collapsible: true,
          defaultCollapsed: true,
        },
      ],
    },
    {
      category: 'privacy',
      sections: [
        {
          id: 'security',
          title: 'Security Settings',
          description: 'Configure security and privacy options',
          items: [
            {
              id: 'twoFactorAuth',
              label: 'Two-factor authentication',
              type: 'toggle',
              value: false,
              helperText: 'Require additional verification when logging in',
            },
            {
              id: 'sessionTimeout',
              label: 'Session timeout (minutes)',
              type: 'slider',
              value: 30,
              min: 5,
              max: 120,
              step: 5,
              helperText: 'Automatically log out after period of inactivity',
            },
            {
              id: 'password',
              label: 'Change password',
              type: 'input',
              value: '',
              placeholder: 'Enter new password',
              helperText: 'Leave blank to keep current password',
            },
          ],
        },
        {
          id: 'privacy',
          title: 'Privacy Options',
          description: 'Control your privacy settings',
          items: [
            {
              id: 'analyticsEnabled',
              label: 'Enable analytics',
              type: 'toggle',
              value: true,
              helperText: 'Allow collection of anonymous analytics data',
            },
            {
              id: 'shareData',
              label: 'Share data with partners',
              type: 'toggle',
              value: false,
              helperText: 'Share anonymized data with trusted partners',
            },
            {
              id: 'cookieConsent',
              label: 'Cookie consent',
              type: 'radio',
              value: 'essential',
              options: [
                { value: 'all', label: 'Accept all cookies' },
                { value: 'essential', label: 'Essential cookies only' },
                { value: 'none', label: 'Decline all cookies' },
              ],
              helperText: 'Manage cookie preferences',
            },
          ],
          collapsible: true,
        },
      ],
    },
    {
      category: 'help',
      sections: [
        {
          id: 'support',
          title: 'Support & Documentation',
          description: 'Get help and access resources',
          items: [
            {
              id: 'showTutorials',
              label: 'Show tutorials',
              type: 'toggle',
              value: true,
              helperText: 'Display helpful tutorials for new features',
            },
            {
              id: 'helpTooltips',
              label: 'Enable help tooltips',
              type: 'toggle',
              value: true,
              helperText: 'Show tooltips when hovering over UI elements',
            },
            {
              id: 'keyboardShortcuts',
              label: 'Show keyboard shortcuts',
              type: 'toggle',
              value: true,
              helperText: 'Display keyboard shortcuts in menus',
            },
          ],
        },
        {
          id: 'feedback',
          title: 'Feedback',
          description: 'Help us improve',
          items: [
            {
              id: 'feedbackEnabled',
              label: 'Enable feedback widget',
              type: 'toggle',
              value: true,
              helperText: 'Show feedback button to report issues or suggestions',
            },
            {
              id: 'crashReports',
              label: 'Send crash reports',
              type: 'toggle',
              value: true,
              helperText: 'Automatically send crash reports to help us fix issues',
            },
          ],
          collapsible: true,
        },
      ],
    },
  ];

  const handleSave = async (newSettings: Record<string, any>) => {
    console.log('Saving settings:', newSettings);
    setSettings(newSettings);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // In real app, would save to backend
    localStorage.setItem('sparta-settings', JSON.stringify(newSettings));
  };

  const handleReset = () => {
    console.log('Resetting settings to default');
    setSettings({});
    localStorage.removeItem('sparta-settings');
    window.location.reload();
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(settings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'sparta-settings.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = (data: any) => {
    console.log('Importing settings:', data);
    setSettings(data);
  };

  return (
    <div style={{ height: '100vh', width: '100vw' }}>
      <SettingsInterface
        settingsData={settingsData}
        onSave={handleSave}
        onReset={handleReset}
        onExport={handleExport}
        onImport={handleImport}
        searchEnabled={true}
        autoSave={false}
        showResetButton={true}
      />
    </div>
  );
};

export default SettingsInterfaceExample;

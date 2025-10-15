import React, { useState, useCallback } from 'react';
import Modal, { Button, Toggle, Input, Alert, IconButton, ModalActions } from './Modal';
import {
  FileText as Link2,
  FileText as Copy,
  Check,
  FileText as Mail,
  FileText as Facebook,
  FileText as Twitter,
  FileText as Linkedin,
  FileText as MessageCircle,
  FileText as QrCode,
  Download,
  FileText as Calendar,
  FileText as Lock,
  FileText as Users,
  Eye,
  FileText as Edit,
  FileText as Shield,
  X,
} from '../icons';

// =====================
// Type Definitions
// =====================

export type AccessLevel = 'view' | 'comment' | 'edit' | 'admin';
export type SocialPlatform = 'facebook' | 'twitter' | 'linkedin' | 'whatsapp' | 'email';

export interface ShareSettings {
  isPublic: boolean;
  accessLevel: AccessLevel;
  allowDownload: boolean;
  requirePassword: boolean;
  password?: string;
  expirationDate?: Date;
  allowedEmails: string[];
  generateQRCode: boolean;
}

export interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  onShare: (settings: ShareSettings) => Promise<string>; // Returns share URL
  title?: string;
  shareUrl?: string;
  itemName?: string;
}

// =====================
// Social Platform Config
// =====================

const socialPlatforms: Record<
  SocialPlatform,
  { icon: React.ReactNode; label: string; color: string; getShareUrl: (url: string, text: string) => string }
> = {
  facebook: {
    icon: <Facebook size={20} />,
    label: 'Facebook',
    color: '#1877f2',
    getShareUrl: (url, text) => `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
  },
  twitter: {
    icon: <Twitter size={20} />,
    label: 'Twitter',
    color: '#1da1f2',
    getShareUrl: (url, text) =>
      `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`,
  },
  linkedin: {
    icon: <Linkedin size={20} />,
    label: 'LinkedIn',
    color: '#0a66c2',
    getShareUrl: (url, text) => `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
  },
  whatsapp: {
    icon: <MessageCircle size={20} />,
    label: 'WhatsApp',
    color: '#25d366',
    getShareUrl: (url, text) =>
      `https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`,
  },
  email: {
    icon: <Mail size={20} />,
    label: 'Email',
    color: '#6366f1',
    getShareUrl: (url, text) =>
      `mailto:?subject=${encodeURIComponent(text)}&body=${encodeURIComponent(url)}`,
  },
};

const accessLevelConfig: Record<
  AccessLevel,
  { icon: React.ReactNode; label: string; description: string }
> = {
  view: {
    icon: <Eye size={20} />,
    label: 'View Only',
    description: 'Can view but not edit or download',
  },
  comment: {
    icon: <MessageCircle size={20} />,
    label: 'Can Comment',
    description: 'Can view and leave comments',
  },
  edit: {
    icon: <Edit size={20} />,
    label: 'Can Edit',
    description: 'Can view, comment, and edit',
  },
  admin: {
    icon: <Shield size={20} />,
    label: 'Admin',
    description: 'Full access including sharing',
  },
};

// =====================
// Link Section Component
// =====================

const LinkSection: React.FC<{
  shareUrl: string;
  onCopy: () => void;
  copied: boolean;
  onGenerate: () => void;
  isGenerating: boolean;
}> = ({ shareUrl, onCopy, copied, onGenerate, isGenerating }) => (
  <div className="share-section">
    <h3 className="share-section-title">
      <Link2 size={20} />
      Share Link
    </h3>
    {shareUrl ? (
      <div className="link-input-group">
        <Input
          value={shareUrl}
          readOnly
          fullWidth
          icon={<Link2 size={16} />}
          iconPosition="left"
        />
        <Button
          variant={copied ? 'primary' : 'secondary'}
          onClick={onCopy}
          icon={copied ? <Check size={16} /> : <Copy size={16} />}
          iconPosition="left"
        >
          {copied ? 'Copied!' : 'Copy'}
        </Button>
      </div>
    ) : (
      <Button
        variant="primary"
        onClick={onGenerate}
        loading={isGenerating}
        icon={<Link2 size={16} />}
        iconPosition="left"
        fullWidth
      >
        Generate Share Link
      </Button>
    )}
  </div>
);

// =====================
// Social Share Component
// =====================

const SocialShareSection: React.FC<{
  shareUrl: string;
  itemName: string;
}> = ({ shareUrl, itemName }) => {
  const handleSocialShare = (platform: SocialPlatform) => {
    const config = socialPlatforms[platform];
    const shareText = `Check out: ${itemName}`;
    const url = config.getShareUrl(shareUrl, shareText);
    window.open(url, '_blank', 'width=600,height=400');
  };

  return (
    <div className="share-section">
      <h3 className="share-section-title">
        <Users size={20} />
        Share to Social Media
      </h3>
      <div className="social-buttons">
        {(Object.keys(socialPlatforms) as SocialPlatform[]).map((platform) => {
          const config = socialPlatforms[platform];
          return (
            <button
              key={platform}
              className="social-button"
              onClick={() => handleSocialShare(platform)}
              style={{ backgroundColor: config.color }}
              type="button"
              aria-label={`Share on ${config.label}`}
            >
              {config.icon}
              <span>{config.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

// =====================
// Access Control Component
// =====================

const AccessControlSection: React.FC<{
  settings: ShareSettings;
  onSettingsChange: (settings: Partial<ShareSettings>) => void;
}> = ({ settings, onSettingsChange }) => (
  <div className="share-section">
    <h3 className="share-section-title">
      <Shield size={20} />
      Access Control
    </h3>

    {/* Access Level */}
    <div className="access-level-group">
      <label className="form-label">Access Level</label>
      <div className="access-level-options">
        {(Object.keys(accessLevelConfig) as AccessLevel[]).map((level) => {
          const config = accessLevelConfig[level];
          return (
            <label key={level} className="access-level-option">
              <input
                type="radio"
                name="accessLevel"
                value={level}
                checked={settings.accessLevel === level}
                onChange={() => onSettingsChange({ accessLevel: level })}
              />
              <div className="access-level-content">
                <div className="access-level-icon">{config.icon}</div>
                <div className="access-level-text">
                  <div className="access-level-label">{config.label}</div>
                  <div className="access-level-description">{config.description}</div>
                </div>
              </div>
            </label>
          );
        })}
      </div>
    </div>

    {/* Toggles */}
    <div className="access-toggles">
      <Toggle
        checked={settings.isPublic}
        onChange={(checked) => onSettingsChange({ isPublic: checked })}
        label="Public Access"
        description="Anyone with the link can access"
      />
      <Toggle
        checked={settings.allowDownload}
        onChange={(checked) => onSettingsChange({ allowDownload: checked })}
        label="Allow Downloads"
        description="Users can download the content"
      />
      <Toggle
        checked={settings.requirePassword}
        onChange={(checked) => onSettingsChange({ requirePassword: checked })}
        label="Password Protection"
        description="Require password to access"
      />
      <Toggle
        checked={settings.generateQRCode}
        onChange={(checked) => onSettingsChange({ generateQRCode: checked })}
        label="Generate QR Code"
        description="Create scannable QR code for easy sharing"
      />
    </div>
  </div>
);

// =====================
// Advanced Settings Component
// =====================

const AdvancedSettingsSection: React.FC<{
  settings: ShareSettings;
  onSettingsChange: (settings: Partial<ShareSettings>) => void;
}> = ({ settings, onSettingsChange }) => {
  const [emailInput, setEmailInput] = useState('');

  const handleAddEmail = () => {
    if (emailInput && emailInput.includes('@')) {
      onSettingsChange({
        allowedEmails: [...settings.allowedEmails, emailInput],
      });
      setEmailInput('');
    }
  };

  const handleRemoveEmail = (email: string) => {
    onSettingsChange({
      allowedEmails: settings.allowedEmails.filter((e) => e !== email),
    });
  };

  return (
    <div className="share-section">
      <h3 className="share-section-title">
        <Lock size={20} />
        Advanced Settings
      </h3>

      {/* Password Input */}
      {settings.requirePassword && (
        <div className="form-group">
          <Input
            type="password"
            label="Password"
            value={settings.password || ''}
            onChange={(e) => onSettingsChange({ password: e.target.value })}
            icon={<Lock size={16} />}
            iconPosition="left"
            fullWidth
            helperText="Enter a strong password to protect your shared content"
          />
        </div>
      )}

      {/* Expiration Date */}
      <div className="form-group">
        <label className="form-label" htmlFor="expiration-date">
          <Calendar size={16} />
          Expiration Date (Optional)
        </label>
        <input
          id="expiration-date"
          type="date"
          className="date-input"
          value={settings.expirationDate ? settings.expirationDate.toISOString().split('T')[0] : ''}
          onChange={(e) =>
            onSettingsChange({
              expirationDate: e.target.value ? new Date(e.target.value) : undefined,
            })
          }
          min={new Date().toISOString().split('T')[0]}
          aria-label="Expiration date"
        />
        <p className="form-helper">Link will automatically expire on this date</p>
      </div>

      {/* Email Whitelist */}
      {!settings.isPublic && (
        <div className="form-group">
          <label className="form-label">
            <Mail size={16} />
            Allowed Email Addresses
          </label>
          <div className="email-input-group">
            <Input
              type="email"
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              placeholder="Enter email address"
              icon={<Mail size={16} />}
              iconPosition="left"
              fullWidth
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddEmail();
                }
              }}
            />
            <Button variant="secondary" onClick={handleAddEmail}>
              Add
            </Button>
          </div>
          {settings.allowedEmails.length > 0 && (
            <div className="email-list">
              {settings.allowedEmails.map((email) => (
                <div key={email} className="email-tag">
                  <span>{email}</span>
                  <IconButton
                    icon={<X size={14} />}
                    variant="ghost"
                    size="small"
                    onClick={() => handleRemoveEmail(email)}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// =====================
// QR Code Component
// =====================

const QRCodeSection: React.FC<{
  shareUrl: string;
}> = ({ shareUrl }) => {
  const [qrCodeUrl, setQrCodeUrl] = useState<string>('');

  // Generate QR code (placeholder - would use actual QR library)
  React.useEffect(() => {
    if (shareUrl) {
      // In production, use a QR code library like qrcode.react or qrcode
      // For now, using a QR code API
      const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
        shareUrl
      )}`;
      setQrCodeUrl(qrUrl);
    }
  }, [shareUrl]);

  const handleDownloadQR = () => {
    const link = document.createElement('a');
    link.href = qrCodeUrl;
    link.download = 'share-qr-code.png';
    link.click();
  };

  if (!shareUrl) return null;

  return (
    <div className="share-section">
      <h3 className="share-section-title">
        <QrCode size={20} />
        QR Code
      </h3>
      <div className="qr-code-container">
        <div className="qr-code-image">
          <img src={qrCodeUrl} alt="QR Code" />
        </div>
        <Button
          variant="secondary"
          onClick={handleDownloadQR}
          icon={<Download size={16} />}
          iconPosition="left"
          fullWidth
        >
          Download QR Code
        </Button>
      </div>
    </div>
  );
};

// =====================
// Share Modal Component
// =====================

const ShareModal: React.FC<ShareModalProps> = ({
  isOpen,
  onClose,
  onShare,
  title = 'Share',
  shareUrl: initialShareUrl,
  itemName = 'this item',
}) => {
  const [settings, setSettings] = useState<ShareSettings>({
    isPublic: true,
    accessLevel: 'view',
    allowDownload: true,
    requirePassword: false,
    password: '',
    expirationDate: undefined,
    allowedEmails: [],
    generateQRCode: false,
  });
  const [shareUrl, setShareUrl] = useState<string>(initialShareUrl || '');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [shareSuccess, setShareSuccess] = useState(false);
  const [shareError, setShareError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setShareError(null);

    try {
      const url = await onShare(settings);
      setShareUrl(url);
      setShareSuccess(true);
      setTimeout(() => setShareSuccess(false), 3000);
    } catch (error) {
      setShareError(error instanceof Error ? error.message : 'Failed to generate share link');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [shareUrl]);

  const handleSettingsChange = (newSettings: Partial<ShareSettings>) => {
    setSettings({ ...settings, ...newSettings });
  };

  const handleClose = () => {
    setShareUrl(initialShareUrl || '');
    setCopied(false);
    setShareSuccess(false);
    setShareError(null);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} size="large" title={title} className="share-modal">
      <div className="share-modal-content">
        {shareSuccess && (
          <Alert
            type="success"
            title="Share Link Generated"
            message="Your share link has been created successfully!"
          />
        )}

        {shareError && (
          <Alert type="error" title="Share Failed" message={shareError} onClose={() => setShareError(null)} />
        )}

        <LinkSection
          shareUrl={shareUrl}
          onCopy={handleCopy}
          copied={copied}
          onGenerate={handleGenerate}
          isGenerating={isGenerating}
        />

        {shareUrl && <SocialShareSection shareUrl={shareUrl} itemName={itemName} />}

        <AccessControlSection settings={settings} onSettingsChange={handleSettingsChange} />

        <AdvancedSettingsSection settings={settings} onSettingsChange={handleSettingsChange} />

        {shareUrl && settings.generateQRCode && <QRCodeSection shareUrl={shareUrl} />}
      </div>

      <ModalActions align="space-between">
        <Button variant="ghost" onClick={handleClose}>
          Close
        </Button>
        {shareUrl && (
          <Button
            variant="primary"
            onClick={handleCopy}
            icon={copied ? <Check size={16} /> : <Copy size={16} />}
            iconPosition="left"
          >
            {copied ? 'Copied!' : 'Copy Link'}
          </Button>
        )}
      </ModalActions>
    </Modal>
  );
};

export default ShareModal;

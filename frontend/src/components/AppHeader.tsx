import React from 'react';
import './AppHeader.css';

const AppHeader: React.FC = () => {
  return (
    <header className="app-header glass-container">
      <div className="app-header__left">
        <img src="/assets/sparta-logo.png" alt="Sparta AI" className="app-logo app-logo--lg" />
        <div className="app-header__title">Sparta AI</div>
      </div>
      <div className="app-header__right">
        {/* Placeholder for user actions */}
      </div>
    </header>
  );
};

export default AppHeader;

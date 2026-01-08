import React from 'react';

export const Header: React.FC = () => {
  return (
    <header style={{
      borderBottom: '1px solid var(--color-border)',
      padding: '1rem 0',
      background: 'rgba(15, 23, 42, 0.8)',
      backdropFilter: 'blur(8px)',
      position: 'sticky',
      top: 0,
      zIndex: 10
    }}>
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem', background: 'linear-gradient(to right, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          システムプロンプト診断
        </h1>
        <nav>
          {/* Future nav items */}
          <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>v0.1.0</span>
        </nav>
      </div>
    </header>
  );
};

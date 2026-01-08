import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer style={{
      marginTop: 'auto',
      padding: '2rem 0',
      borderTop: '1px solid var(--color-border)',
      textAlign: 'center',
      color: 'var(--color-text-secondary)',
      fontSize: '0.875rem'
    }}>
      <div className="container">
        <p>&copy; {new Date().getFullYear()} システムプロンプト診断. All rights reserved.</p>
      </div>
    </footer>
  );
};

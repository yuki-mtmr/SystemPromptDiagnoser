import React from 'react';

export const Questionnaire: React.FC = () => {
  return (
    <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '2rem auto' }}>
      <h2 style={{ marginTop: 0, marginBottom: '1.5rem', textAlign: 'center' }}>Diagnosis Questionnaire</h2>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem', textAlign: 'center' }}>
        Answer a few questions to generate your optimal system prompt.
      </p>
      
      <form onSubmit={(e) => e.preventDefault()}>
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            Question 1: How strict do you want the AI to be?
          </label>
          <select style={{ 
            width: '100%', 
            padding: '0.75rem', 
            borderRadius: '0.5rem',
            background: 'var(--color-bg-secondary)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-primary)',
            outline: 'none'
          }}>
            <option>Somewhat flexible</option>
            <option>Very strict</option>
            <option>Creative/Loose</option>
          </select>
        </div>

        <button type="submit" className="btn-primary" style={{ width: '100%' }}>
          Start Diagnosis
        </button>
      </form>
    </div>
  );
};

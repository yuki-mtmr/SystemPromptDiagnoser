import React from 'react';

interface ResultsDisplayProps {
  onReset: () => void;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ onReset }) => {
  return (
    <div className="glass-panel" style={{ padding: '2rem', maxWidth: '800px', margin: '2rem auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>診断完了</h2>
        <p style={{ color: 'var(--color-text-secondary)' }}>回答に基づいて、最適なシステムプロンプトを生成しました。</p>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
          推奨スタイル: <span style={{ color: 'var(--color-accent)' }}>厳格なエキスパート (Strict Expert)</span>
        </h3>
        
        <div style={{ 
          background: 'var(--color-bg-secondary)', 
          padding: '1.5rem', 
          borderRadius: '0.5rem', 
          fontFamily: 'monospace',
          lineHeight: 1.6,
          border: '1px solid var(--color-border)',
          whiteSpace: 'pre-wrap'
        }}>
          {`You are an expert system designed to provide precise, technically accurate, and concise answers.
1. Do not apologize or use filler words.
2. Focus strictly on the user's question.
3. Provide code snippets where relevant without extensive preamble.
4. If a request is ambiguous, ask clarifying questions before proceeding.`}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
        <button className="btn-primary" onClick={() => navigator.clipboard.writeText("Copied prompt!")}>
          クリップボードにコピー
        </button>
        <button 
          onClick={onReset}
          style={{ 
            background: 'transparent', 
            border: '1px solid var(--color-border)', 
            color: 'var(--color-text-primary)', 
            padding: '0.75rem 1.5rem', 
            borderRadius: '0.5rem', 
            cursor: 'pointer' 
          }}
        >
          最初からやり直す
        </button>
      </div>
    </div>
  );
};

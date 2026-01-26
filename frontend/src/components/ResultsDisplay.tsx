import React, { useState } from 'react';

interface PromptVariant {
  style: string;
  name: string;
  prompt: string;
  description: string;
}

export interface DiagnoseResult {
  recommended_style: string;
  variants: PromptVariant[];
}

interface ResultsDisplayProps {
  results: DiagnoseResult;
  onReset: () => void;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, onReset }) => {
  const [selectedStyle, setSelectedStyle] = useState<string>(results.recommended_style);
  const [copied, setCopied] = useState(false);

  const selectedVariant = results.variants.find(v => v.style === selectedStyle) || results.variants[0];

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(selectedVariant.prompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = selectedVariant.prompt;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem', maxWidth: '900px', margin: '2rem auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>診断完了</h2>
        <p style={{ color: 'var(--color-text-secondary)' }}>
          回答に基づいて、3種類のシステムプロンプトを生成しました。
        </p>
      </div>

      {/* Style selector tabs */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1.5rem',
        flexWrap: 'wrap',
        justifyContent: 'center'
      }}>
        {results.variants.map(variant => (
          <button
            key={variant.style}
            onClick={() => setSelectedStyle(variant.style)}
            style={{
              padding: '0.75rem 1.25rem',
              borderRadius: '0.5rem',
              border: selectedStyle === variant.style
                ? '2px solid var(--color-accent)'
                : '1px solid var(--color-border)',
              background: selectedStyle === variant.style
                ? 'var(--color-accent)'
                : 'var(--color-bg-secondary)',
              color: selectedStyle === variant.style
                ? '#fff'
                : 'var(--color-text-primary)',
              cursor: 'pointer',
              fontWeight: 500,
              transition: 'all 0.2s ease',
              position: 'relative'
            }}
          >
            {variant.name}
            {results.recommended_style === variant.style && (
              <span style={{
                position: 'absolute',
                top: '-8px',
                right: '-8px',
                background: '#4ade80',
                color: '#000',
                fontSize: '0.625rem',
                padding: '2px 6px',
                borderRadius: '4px',
                fontWeight: 600
              }}>
                推奨
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Selected prompt display */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '0.75rem'
        }}>
          <h3 style={{ margin: 0 }}>
            {selectedVariant.name}
          </h3>
          <span style={{
            fontSize: '0.875rem',
            color: 'var(--color-text-secondary)'
          }}>
            {selectedVariant.description}
          </span>
        </div>

        <div style={{
          background: 'var(--color-bg-secondary)',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          fontFamily: 'monospace',
          lineHeight: 1.6,
          border: '1px solid var(--color-border)',
          whiteSpace: 'pre-wrap',
          position: 'relative',
          maxHeight: '400px',
          overflowY: 'auto'
        }}>
          {selectedVariant.prompt}
        </div>
      </div>

      {/* Character count */}
      <div style={{
        textAlign: 'right',
        marginBottom: '1.5rem',
        color: 'var(--color-text-secondary)',
        fontSize: '0.875rem'
      }}>
        文字数: {selectedVariant.prompt.length}
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
        <button
          className="btn-primary"
          onClick={handleCopy}
          style={{
            minWidth: '200px',
            background: copied ? '#4ade80' : undefined
          }}
        >
          {copied ? 'コピーしました!' : 'クリップボードにコピー'}
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

      {/* All prompts comparison (collapsible) */}
      <details style={{ marginTop: '2rem' }}>
        <summary style={{
          cursor: 'pointer',
          color: 'var(--color-text-secondary)',
          padding: '1rem 0',
          borderTop: '1px solid var(--color-border)'
        }}>
          すべてのプロンプトを比較
        </summary>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '1rem' }}>
          {results.variants.map(variant => (
            <div key={variant.style}>
              <h4 style={{ marginBottom: '0.5rem' }}>{variant.name}</h4>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                {variant.description}
              </p>
              <div style={{
                background: 'var(--color-bg-secondary)',
                padding: '1rem',
                borderRadius: '0.5rem',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                lineHeight: 1.5,
                border: '1px solid var(--color-border)',
                whiteSpace: 'pre-wrap',
                maxHeight: '200px',
                overflowY: 'auto'
              }}>
                {variant.prompt}
              </div>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
};

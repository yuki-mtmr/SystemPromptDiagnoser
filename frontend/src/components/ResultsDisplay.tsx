import React, { useState } from 'react';

interface PromptVariant {
  style: string;
  name: string;
  prompt: string;
  description: string;
}

// v2用のユーザープロファイル
export interface UserProfile {
  primary_use_case: string;
  autonomy_preference: string;
  communication_style: string;
  key_traits: string[];
  detected_needs: string[];
}

export interface DiagnoseResult {
  recommended_style: string;
  variants: PromptVariant[];
  source?: 'llm' | 'mock';
  // v2で追加
  user_profile?: UserProfile;
  recommendation_reason?: string;
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
        {results.source && (
          <span
            style={{
              display: 'inline-block',
              marginTop: '0.5rem',
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              fontSize: '0.75rem',
              fontWeight: 600,
              background: results.source === 'llm' ? 'rgba(74, 222, 128, 0.2)' : 'rgba(234, 179, 8, 0.2)',
              color: results.source === 'llm' ? '#4ade80' : '#eab308',
              border: `1px solid ${results.source === 'llm' ? 'rgba(74, 222, 128, 0.4)' : 'rgba(234, 179, 8, 0.4)'}`,
            }}
          >
            {results.source === 'llm' ? '🤖 LLM生成' : '📋 モック'}
          </span>
        )}
      </div>

      {/* v2: ユーザープロファイル表示 */}
      {results.user_profile && (
        <div style={{
          background: 'var(--color-bg-secondary)',
          borderRadius: '0.75rem',
          padding: '1.5rem',
          marginBottom: '2rem',
          border: '1px solid var(--color-border)',
        }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem' }}>
            あなたのプロファイル
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
          }}>
            <div>
              <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                主な用途
              </p>
              <p style={{ margin: '0.25rem 0 0', fontWeight: 500 }}>
                {results.user_profile.primary_use_case}
              </p>
            </div>
            <div>
              <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                自律性の好み
              </p>
              <p style={{ margin: '0.25rem 0 0', fontWeight: 500 }}>
                {results.user_profile.autonomy_preference}
              </p>
            </div>
            <div>
              <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                コミュニケーションスタイル
              </p>
              <p style={{ margin: '0.25rem 0 0', fontWeight: 500 }}>
                {results.user_profile.communication_style}
              </p>
            </div>
          </div>
          {results.user_profile.key_traits.length > 0 && (
            <div style={{ marginTop: '1rem' }}>
              <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                特性
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                {results.user_profile.key_traits.map((trait, i) => (
                  <span key={i} style={{
                    padding: '0.25rem 0.75rem',
                    background: 'var(--color-bg-tertiary)',
                    borderRadius: '9999px',
                    fontSize: '0.875rem',
                  }}>
                    {trait}
                  </span>
                ))}
              </div>
            </div>
          )}
          {results.recommendation_reason && (
            <div style={{
              marginTop: '1rem',
              padding: '0.75rem',
              background: 'rgba(99, 102, 241, 0.1)',
              borderRadius: '0.5rem',
              borderLeft: '3px solid var(--color-accent)',
            }}>
              <p style={{ margin: 0, fontSize: '0.875rem' }}>
                <strong>推奨理由:</strong> {results.recommendation_reason}
              </p>
            </div>
          )}
        </div>
      )}

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

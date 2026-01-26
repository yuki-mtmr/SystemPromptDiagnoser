import { useState, useEffect } from 'react';

const API_KEY_STORAGE_KEY = 'llm_api_key';

interface ApiKeyInputProps {
  onApiKeyChange: (hasKey: boolean) => void;
}

export function ApiKeyInput({ onApiKeyChange }: ApiKeyInputProps) {
  const [apiKey, setApiKey] = useState<string>('');
  const [showInput, setShowInput] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);

  useEffect(() => {
    const savedKey = sessionStorage.getItem(API_KEY_STORAGE_KEY);
    if (savedKey) {
      setApiKey(savedKey);
      onApiKeyChange(true);
    }
  }, [onApiKeyChange]);

  const maskApiKey = (key: string): string => {
    if (key.length <= 8) return '****';
    return `${key.slice(0, 4)}...${key.slice(-4)}`;
  };

  const handleSaveKey = () => {
    if (apiKey.trim()) {
      sessionStorage.setItem(API_KEY_STORAGE_KEY, apiKey.trim());
      onApiKeyChange(true);
      setIsEditing(false);
      setShowInput(false);
    }
  };

  const handleClearKey = () => {
    sessionStorage.removeItem(API_KEY_STORAGE_KEY);
    setApiKey('');
    onApiKeyChange(false);
    setIsEditing(false);
    setShowInput(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setApiKey(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSaveKey();
    }
  };

  const hasStoredKey = sessionStorage.getItem(API_KEY_STORAGE_KEY);

  return (
    <div style={{ marginBottom: '1.5rem' }}>
      <div
        className="glass-panel"
        style={{
          padding: '1rem 1.5rem',
          maxWidth: '600px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            style={{ color: hasStoredKey ? 'var(--color-accent)' : 'var(--color-text-secondary)' }}
          >
            <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
          </svg>
          <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
            Groq API Key:
          </span>
        </div>

        {hasStoredKey && !isEditing ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <code style={{
              background: 'rgba(56, 189, 248, 0.1)',
              padding: '0.25rem 0.5rem',
              borderRadius: '0.25rem',
              color: 'var(--color-accent)',
              fontSize: '0.875rem'
            }}>
              {maskApiKey(apiKey)}
            </code>
            <button
              onClick={() => setIsEditing(true)}
              style={{
                background: 'transparent',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-secondary)',
                padding: '0.35rem 0.75rem',
                borderRadius: '0.25rem',
                cursor: 'pointer',
                fontSize: '0.75rem',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--color-accent)'}
              onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--color-border)'}
            >
              変更
            </button>
            <button
              onClick={handleClearKey}
              style={{
                background: 'transparent',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#ef4444',
                padding: '0.35rem 0.75rem',
                borderRadius: '0.25rem',
                cursor: 'pointer',
                fontSize: '0.75rem',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.borderColor = '#ef4444'}
              onMouseOut={(e) => e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.3)'}
            >
              クリア
            </button>
          </div>
        ) : showInput || isEditing ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1, minWidth: '280px' }}>
            <input
              type="password"
              value={apiKey}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="gsk_..."
              autoFocus
              style={{
                flex: 1,
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--color-border)',
                borderRadius: '0.375rem',
                padding: '0.5rem 0.75rem',
                color: 'var(--color-text-primary)',
                fontSize: '0.875rem',
                outline: 'none'
              }}
              onFocus={(e) => e.target.style.borderColor = 'var(--color-accent)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--color-border)'}
            />
            <button
              onClick={handleSaveKey}
              disabled={!apiKey.trim()}
              style={{
                background: apiKey.trim() ? 'var(--color-accent)' : 'var(--color-border)',
                border: 'none',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                cursor: apiKey.trim() ? 'pointer' : 'not-allowed',
                fontSize: '0.875rem',
                fontWeight: 500,
                transition: 'all 0.2s'
              }}
            >
              保存
            </button>
            {isEditing && (
              <button
                onClick={() => {
                  setIsEditing(false);
                  const savedKey = sessionStorage.getItem(API_KEY_STORAGE_KEY);
                  if (savedKey) setApiKey(savedKey);
                }}
                style={{
                  background: 'transparent',
                  border: '1px solid var(--color-border)',
                  color: 'var(--color-text-secondary)',
                  padding: '0.5rem 0.75rem',
                  borderRadius: '0.375rem',
                  cursor: 'pointer',
                  fontSize: '0.875rem'
                }}
              >
                キャンセル
              </button>
            )}
          </div>
        ) : (
          <button
            onClick={() => setShowInput(true)}
            style={{
              background: 'linear-gradient(135deg, var(--color-accent), #0ea5e9)',
              border: 'none',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: 500,
              boxShadow: '0 0 10px var(--color-accent-glow)',
              transition: 'all 0.2s'
            }}
          >
            APIキーを設定
          </button>
        )}
      </div>

      {!hasStoredKey && (
        <div style={{
          textAlign: 'center',
          color: 'var(--color-text-secondary)',
          fontSize: '0.75rem',
          marginTop: '0.5rem',
          maxWidth: '600px',
          margin: '0.5rem auto 0'
        }}>
          <p style={{ margin: '0 0 0.25rem' }}>
            <a
              href="https://console.groq.com/keys"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--color-accent)' }}
            >
              Groq Console
            </a>
            {' '}で無料のAPIキーを取得できます（クレジットカード不要）
          </p>
          <p style={{ margin: 0, opacity: 0.8 }}>
            手順: アカウント作成 → API Keys → Create API Key
          </p>
        </div>
      )}
    </div>
  );
}

export function getStoredApiKey(): string | null {
  return sessionStorage.getItem(API_KEY_STORAGE_KEY);
}

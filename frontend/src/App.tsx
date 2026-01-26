import { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Questionnaire, type DiagnoseAnswers } from './components/Questionnaire';
import { ResultsDisplay, type DiagnoseResult } from './components/ResultsDisplay';
import { ApiKeyInput, getStoredApiKey } from './components/ApiKeyInput';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

function App() {
  const [view, setView] = useState<'questionnaire' | 'loading' | 'results' | 'error'>('questionnaire');
  const [results, setResults] = useState<DiagnoseResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hasApiKey, setHasApiKey] = useState<boolean>(!!getStoredApiKey());

  const handleApiKeyChange = useCallback((hasKey: boolean) => {
    setHasApiKey(hasKey);
  }, []);

  const handleDiagnose = async (answers: DiagnoseAnswers) => {
    setView('loading');
    setError(null);

    const apiKey = getStoredApiKey();

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (apiKey) {
        headers['X-API-Key'] = apiKey;
      }

      const response = await fetch(`${API_BASE_URL}/api/diagnose`, {
        method: 'POST',
        headers,
        body: JSON.stringify(answers),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `診断に失敗しました: ${response.status}`);
      }

      const data: DiagnoseResult = await response.json();
      setResults(data);
      setView('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期しないエラーが発生しました');
      setView('error');
    }
  };

  const handleReset = () => {
    setView('questionnaire');
    setResults(null);
    setError(null);
  };

  return (
    <>
      <Header />
      <main className="container" style={{ flex: 1, padding: '2rem 1rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
            あなたに最適な <span style={{ color: 'var(--color-accent)' }}>システムプロンプト</span> を発見しよう
          </h2>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
            汎用的なプロンプトに悩むのはもう終わりです。あなたのスタイルに合わせた、最適なシステムプロンプトを生成します。
          </p>
        </div>

        <ApiKeyInput onApiKeyChange={handleApiKeyChange} />

        {!hasApiKey && (
          <div style={{
            background: 'rgba(234, 179, 8, 0.1)',
            border: '1px solid rgba(234, 179, 8, 0.3)',
            borderRadius: '0.5rem',
            padding: '0.75rem 1rem',
            maxWidth: '600px',
            margin: '0 auto 1.5rem',
            textAlign: 'center'
          }}>
            <p style={{ color: '#eab308', fontSize: '0.875rem', margin: 0 }}>
              APIキーが未設定のため、モックモードで動作します。LLMによる高品質な生成を利用するにはAPIキーを設定してください。
            </p>
          </div>
        )}

        {view === 'questionnaire' && (
          <Questionnaire onComplete={handleDiagnose} />
        )}

        {view === 'loading' && (
          <div className="glass-panel" style={{ padding: '3rem', maxWidth: '600px', margin: '2rem auto', textAlign: 'center' }}>
            <div style={{ marginBottom: '1rem' }}>
              <div className="spinner" style={{
                width: '48px',
                height: '48px',
                border: '3px solid var(--color-border)',
                borderTopColor: 'var(--color-accent)',
                borderRadius: '50%',
                margin: '0 auto',
                animation: 'spin 1s linear infinite'
              }} />
            </div>
            <p style={{ color: 'var(--color-text-secondary)' }}>診断中...</p>
            <style>{`
              @keyframes spin {
                to { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        )}

        {view === 'results' && results && (
          <ResultsDisplay results={results} onReset={handleReset} />
        )}

        {view === 'error' && (
          <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '2rem auto', textAlign: 'center' }}>
            <h3 style={{ color: '#ff6b6b', marginBottom: '1rem' }}>エラーが発生しました</h3>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: '1.5rem' }}>{error}</p>
            <button className="btn-primary" onClick={handleReset}>
              最初からやり直す
            </button>
          </div>
        )}
      </main>
      <Footer />
    </>
  );
}

export default App;

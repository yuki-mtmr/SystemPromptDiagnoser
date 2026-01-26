import { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Questionnaire, type DiagnoseAnswers } from './components/Questionnaire';
import { ResultsDisplay, type DiagnoseResult } from './components/ResultsDisplay';
import { ApiKeyInput, getStoredApiKey, getStoredProvider } from './components/ApiKeyInput';
import type { Provider } from './components/ApiKeyInput';
import { DiagnoseFlow } from './components/DiagnoseFlow';
import type { DiagnoseV2Result } from './hooks/useDiagnoseSession';
import { useLoadingProgress } from './hooks/useLoadingProgress';
import { useFetchWithTimeout } from './hooks/useFetchWithTimeout';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
const REQUEST_TIMEOUT = 60000; // 60秒

// v2結果をv1形式に変換
function convertV2ToV1Result(v2Result: DiagnoseV2Result): DiagnoseResult {
  return {
    recommended_style: v2Result.recommended_style,
    variants: v2Result.variants,
    source: v2Result.source,
    user_profile: v2Result.user_profile,
    recommendation_reason: v2Result.recommendation_reason,
  };
}

type ViewType = 'questionnaire' | 'questionnaire-v2' | 'loading' | 'results' | 'error';

function App() {
  // v2を優先、エラー時はv1にフォールバック
  const [useV2, setUseV2] = useState(true);
  const [view, setView] = useState<ViewType>('questionnaire-v2');
  const [results, setResults] = useState<DiagnoseResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hasApiKey, setHasApiKey] = useState<boolean>(!!getStoredApiKey());
  const [provider, setProvider] = useState<Provider>(getStoredProvider() || 'groq');

  // プログレス表示フック
  const { message: loadingMessage } = useLoadingProgress(view === 'loading');

  // タイムアウト付きfetchフック（v1用）
  const { fetchWithTimeout } = useFetchWithTimeout<DiagnoseResult>({
    timeout: REQUEST_TIMEOUT,
  });

  const handleApiKeyChange = useCallback((hasKey: boolean) => {
    setHasApiKey(hasKey);
  }, []);

  const handleProviderChange = useCallback((newProvider: Provider) => {
    setProvider(newProvider);
  }, []);

  // v2完了ハンドラ
  const handleV2Complete = useCallback((v2Result: DiagnoseV2Result) => {
    setResults(convertV2ToV1Result(v2Result));
    setView('results');
  }, []);

  // v2エラーハンドラ - v1にフォールバック
  const handleV2Error = useCallback((err: Error) => {
    console.warn('v2診断でエラーが発生しました。v1にフォールバックします:', err.message);
    setUseV2(false);
    setView('questionnaire');
  }, []);

  // v1の診断処理
  const handleDiagnose = async (answers: DiagnoseAnswers) => {
    setView('loading');
    setError(null);

    const apiKey = getStoredApiKey();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }

    if (provider) {
      headers['X-Provider'] = provider;
    }

    const data = await fetchWithTimeout(`${API_BASE_URL}/api/diagnose`, {
      method: 'POST',
      headers,
      body: JSON.stringify(answers),
    });

    if (data) {
      setResults(data);
      setView('results');
    } else {
      setError('診断に失敗しました。しばらく経ってから再度お試しください。');
      setView('error');
    }
  };

  const handleReset = () => {
    // v2を再度試行
    setUseV2(true);
    setView('questionnaire-v2');
    setResults(null);
    setError(null);
  };

  // v1に切り替え
  const switchToV1 = useCallback(() => {
    setUseV2(false);
    setView('questionnaire');
  }, []);

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

        <ApiKeyInput onApiKeyChange={handleApiKeyChange} onProviderChange={handleProviderChange} />

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

        {/* v2診断フロー */}
        {view === 'questionnaire-v2' && useV2 && (
          <div className="glass-panel" style={{ padding: '2rem', maxWidth: '700px', margin: '2rem auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem' }}>診断を開始</h3>
              <button
                onClick={switchToV1}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--color-text-secondary)',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  textDecoration: 'underline',
                }}
              >
                旧バージョンを使用
              </button>
            </div>
            <DiagnoseFlow
              onComplete={handleV2Complete}
              onError={handleV2Error}
              baseUrl={API_BASE_URL}
              apiKey={getStoredApiKey() || undefined}
              provider={provider}
            />
          </div>
        )}

        {/* v1アンケート */}
        {view === 'questionnaire' && !useV2 && (
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
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '1.125rem', marginBottom: '0.5rem' }}>
              {loadingMessage}
            </p>
            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', opacity: 0.7 }}>
              初回アクセス時はサーバー起動に時間がかかる場合があります
            </p>
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

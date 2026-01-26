/**
 * DiagnoseFlow コンポーネント
 *
 * v2診断フローの全体管理
 * Phase 1: 初期質問 → Phase 2: 動的質問 → Phase 3: 結果
 */
import { useCallback, useEffect } from 'react'
import { useDiagnoseSession } from '../hooks/useDiagnoseSession'
import type { InitialAnswers, FollowupAnswer, DiagnoseV2Result, Provider } from '../hooks/useDiagnoseSession'
import { InitialQuestions } from './InitialQuestions'
import { DynamicQuestions } from './DynamicQuestions'

interface DiagnoseFlowProps {
  onComplete: (result: DiagnoseV2Result) => void
  onError?: (error: Error) => void
  baseUrl?: string
  apiKey?: string
  provider?: Provider
}

type FlowPhase = 'initial' | 'followup' | 'loading' | 'complete' | 'error'

export const DiagnoseFlow: React.FC<DiagnoseFlowProps> = ({
  onComplete,
  onError,
  baseUrl = '',
  apiKey,
  provider,
}) => {
  const {
    sessionId,
    phase: apiPhase,
    isLoading,
    error,
    followupQuestions,
    result,
    startSession,
    continueSession,
    reset,
  } = useDiagnoseSession({ baseUrl, apiKey, provider })

  // 現在のフェーズを決定
  const getCurrentPhase = useCallback((): FlowPhase => {
    if (error) return 'error'
    if (isLoading) return 'loading'
    if (result) return 'complete'
    if (apiPhase === 'followup' && followupQuestions.length > 0) return 'followup'
    if (sessionId && apiPhase === 'followup') return 'followup'
    return 'initial'
  }, [error, isLoading, result, apiPhase, followupQuestions, sessionId])

  const currentPhase = getCurrentPhase()

  // 完了時にコールバックを呼ぶ
  useEffect(() => {
    if (result) {
      onComplete(result)
    }
  }, [result, onComplete])

  // エラー時にコールバックを呼ぶ
  useEffect(() => {
    if (error && onError) {
      onError(error)
    }
  }, [error, onError])

  // 初期質問の送信
  const handleInitialSubmit = useCallback(async (answers: InitialAnswers) => {
    await startSession(answers)
  }, [startSession])

  // フォローアップ質問の送信
  const handleFollowupSubmit = useCallback(async (answers: FollowupAnswer[]) => {
    await continueSession(answers)
  }, [continueSession])

  // リセット
  const handleReset = useCallback(() => {
    reset()
  }, [reset])

  // ステップ番号を取得
  const getStepNumber = useCallback((): number => {
    switch (currentPhase) {
      case 'initial':
        return 1
      case 'followup':
      case 'loading':
        return 2
      case 'complete':
        return 3
      default:
        return 1
    }
  }, [currentPhase])

  return (
    <div className="diagnose-flow">
      {/* フェーズインジケーター */}
      <div className="phase-indicator">
        <span className="step-label">ステップ {getStepNumber()} / 3</span>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${(getStepNumber() / 3) * 100}%` }}
          />
        </div>
      </div>

      {/* フェーズコンテンツ */}
      <div className="phase-content">
        {currentPhase === 'initial' && (
          <InitialQuestions
            onSubmit={handleInitialSubmit}
            isLoading={isLoading}
          />
        )}

        {currentPhase === 'followup' && (
          <DynamicQuestions
            questions={followupQuestions}
            onSubmit={handleFollowupSubmit}
            isLoading={isLoading}
            allowSkip={true}
          />
        )}

        {currentPhase === 'loading' && (
          <div className="loading-state">
            <div className="spinner" />
            <p>分析中...</p>
          </div>
        )}

        {currentPhase === 'error' && (
          <div className="error-state">
            <p className="error-title">エラーが発生しました</p>
            <p className="error-message">{error?.message}</p>
            <button
              type="button"
              className="reset-button"
              onClick={handleReset}
            >
              最初からやり直す
            </button>
          </div>
        )}
      </div>

      <style>{`
        .diagnose-flow {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .phase-indicator {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .step-label {
          font-size: 0.875rem;
          color: var(--color-text-secondary, #aaa);
        }

        .progress-bar {
          height: 4px;
          background: var(--color-bg-tertiary, #252538);
          border-radius: 2px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: var(--color-accent, #6366f1);
          transition: width 0.3s ease;
        }

        .phase-content {
          min-height: 300px;
        }

        .loading-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          padding: 3rem;
          color: var(--color-text-secondary, #aaa);
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 3px solid var(--color-bg-tertiary, #252538);
          border-top-color: var(--color-accent, #6366f1);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        .error-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
          padding: 3rem;
          text-align: center;
        }

        .error-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--color-error, #ef4444);
        }

        .error-message {
          color: var(--color-text-secondary, #aaa);
        }

        .reset-button {
          padding: 0.75rem 1.5rem;
          border: 1px solid var(--color-border, #444);
          border-radius: 8px;
          background: transparent;
          color: var(--color-text, #fff);
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .reset-button:hover {
          border-color: var(--color-accent, #6366f1);
          background: var(--color-bg-tertiary, #252538);
        }
      `}</style>
    </div>
  )
}

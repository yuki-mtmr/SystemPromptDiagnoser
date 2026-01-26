/**
 * InitialQuestions コンポーネント
 *
 * v2診断フローの初期質問UI
 * 自由記述（目的）+ サジェストチップ + 選択式（自律性レベル）
 */
import { useState, useCallback } from 'react'
import type { InitialAnswers } from '../hooks/useDiagnoseSession'

interface InitialQuestionsProps {
  onSubmit: (answers: InitialAnswers) => void
  isLoading?: boolean
}

type AutonomyLevel = 'obedient' | 'collaborative' | 'autonomous'

const suggestions = [
  'コーディングのサポート',
  '文章作成・編集',
  '情報のリサーチ',
  'アイデアのブレインストーミング',
  '学習・教育サポート',
]

const autonomyOptions: {
  value: AutonomyLevel
  label: string
  description: string
}[] = [
  {
    value: 'obedient',
    label: '指示に忠実',
    description: '私の指示通りに動いてほしい',
  },
  {
    value: 'collaborative',
    label: '一緒に考える',
    description: '提案しながら一緒に進めてほしい',
  },
  {
    value: 'autonomous',
    label: '自律的',
    description: '自分で判断して積極的に動いてほしい',
  },
]

export const InitialQuestions: React.FC<InitialQuestionsProps> = ({
  onSubmit,
  isLoading = false,
}) => {
  const [purpose, setPurpose] = useState('')
  const [autonomy, setAutonomy] = useState<AutonomyLevel | null>(null)

  const handleSuggestionClick = useCallback((suggestion: string) => {
    setPurpose(prev => {
      if (prev.trim()) {
        return `${prev}, ${suggestion}`
      }
      return suggestion
    })
  }, [])

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()

    if (!purpose.trim() || !autonomy) {
      return
    }

    onSubmit({
      purpose: purpose.trim(),
      autonomy,
    })
  }, [purpose, autonomy, onSubmit])

  const isValid = purpose.trim() && autonomy

  return (
    <form onSubmit={handleSubmit} className="initial-questions">
      <div className="question-section">
        <label htmlFor="purpose" className="question-label">
          AIに何をしてもらいたいですか？
        </label>
        <textarea
          id="purpose"
          value={purpose}
          onChange={e => setPurpose(e.target.value)}
          placeholder="例: コードレビュー、文章の校正、アイデア出し..."
          className="purpose-input"
          rows={3}
          disabled={isLoading}
        />
        <div className="suggestions">
          {suggestions.map(suggestion => (
            <button
              key={suggestion}
              type="button"
              className="suggestion-chip"
              onClick={() => handleSuggestionClick(suggestion)}
              disabled={isLoading}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      <div className="question-section">
        <fieldset className="autonomy-fieldset">
          <legend className="question-label">
            AIにどの程度主導権を持ってほしいですか？
          </legend>
          <div className="autonomy-options">
            {autonomyOptions.map(option => (
              <label
                key={option.value}
                className={`autonomy-option ${autonomy === option.value ? 'selected' : ''}`}
              >
                <input
                  type="radio"
                  name="autonomy"
                  value={option.value}
                  checked={autonomy === option.value}
                  onChange={() => setAutonomy(option.value)}
                  disabled={isLoading}
                />
                <span className="option-content">
                  <span className="option-label">{option.label}</span>
                  <span className="option-description">{option.description}</span>
                </span>
              </label>
            ))}
          </div>
        </fieldset>
      </div>

      <div className="submit-section">
        <button
          type="submit"
          className="submit-button"
          disabled={!isValid || isLoading}
        >
          {isLoading ? '処理中...' : '次へ'}
        </button>
      </div>

      <style>{`
        .initial-questions {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .question-section {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .question-label {
          font-size: 1.1rem;
          font-weight: 600;
          color: var(--color-text, #fff);
        }

        .purpose-input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid var(--color-border, #444);
          border-radius: 8px;
          background: var(--color-bg-secondary, #1a1a2e);
          color: var(--color-text, #fff);
          font-size: 1rem;
          resize: vertical;
        }

        .purpose-input:focus {
          outline: none;
          border-color: var(--color-accent, #6366f1);
          box-shadow: 0 0 0 2px var(--color-accent-alpha, rgba(99, 102, 241, 0.2));
        }

        .suggestions {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .suggestion-chip {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--color-border, #444);
          border-radius: 9999px;
          background: transparent;
          color: var(--color-text-secondary, #aaa);
          font-size: 0.875rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .suggestion-chip:hover:not(:disabled) {
          background: var(--color-bg-tertiary, #252538);
          border-color: var(--color-accent, #6366f1);
          color: var(--color-text, #fff);
        }

        .suggestion-chip:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .autonomy-fieldset {
          border: none;
          padding: 0;
          margin: 0;
        }

        .autonomy-options {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          margin-top: 0.5rem;
        }

        .autonomy-option {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          padding: 1rem;
          border: 1px solid var(--color-border, #444);
          border-radius: 8px;
          background: var(--color-bg-secondary, #1a1a2e);
          cursor: pointer;
          transition: all 0.2s;
        }

        .autonomy-option:hover:not(:has(input:disabled)) {
          border-color: var(--color-accent, #6366f1);
        }

        .autonomy-option.selected {
          border-color: var(--color-accent, #6366f1);
          background: var(--color-bg-tertiary, #252538);
        }

        .autonomy-option input[type="radio"] {
          margin-top: 0.25rem;
          accent-color: var(--color-accent, #6366f1);
        }

        .option-content {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .option-label {
          font-weight: 600;
          color: var(--color-text, #fff);
        }

        .option-description {
          font-size: 0.875rem;
          color: var(--color-text-secondary, #aaa);
        }

        .submit-section {
          display: flex;
          justify-content: flex-end;
        }

        .submit-button {
          padding: 0.75rem 2rem;
          border: none;
          border-radius: 8px;
          background: var(--color-accent, #6366f1);
          color: #fff;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .submit-button:hover:not(:disabled) {
          background: var(--color-accent-hover, #4f46e5);
        }

        .submit-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </form>
  )
}

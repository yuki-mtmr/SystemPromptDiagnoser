/**
 * DynamicQuestions コンポーネント
 *
 * LLM生成の動的質問を表示・回答するUI
 */
import { useState, useCallback, useEffect } from 'react'
import type { Question, FollowupAnswer } from '../hooks/useDiagnoseSession'

interface DynamicQuestionsProps {
  questions: Question[]
  onSubmit: (answers: FollowupAnswer[]) => void
  isLoading?: boolean
  allowSkip?: boolean
}

export const DynamicQuestions: React.FC<DynamicQuestionsProps> = ({
  questions,
  onSubmit,
  isLoading = false,
  allowSkip = false,
}) => {
  // 各質問の回答を管理
  const [answers, setAnswers] = useState<Record<string, string>>({})

  // 質問が変わったら回答をリセット
  useEffect(() => {
    setAnswers({})
  }, [questions])

  const handleFreeformChange = useCallback((questionId: string, value: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value,
    }))
  }, [])

  const handleChoiceSelect = useCallback((questionId: string, value: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value,
    }))
  }, [])

  const handleMultiChoiceToggle = useCallback((questionId: string, value: string) => {
    setAnswers(prev => {
      const currentValues = prev[questionId] ? prev[questionId].split(',') : []
      const index = currentValues.indexOf(value)

      if (index === -1) {
        // 追加
        return {
          ...prev,
          [questionId]: [...currentValues, value].join(','),
        }
      } else {
        // 削除
        currentValues.splice(index, 1)
        return {
          ...prev,
          [questionId]: currentValues.join(','),
        }
      }
    })
  }, [])

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()

    const formattedAnswers: FollowupAnswer[] = questions.map(q => ({
      question_id: q.id,
      answer: answers[q.id] || '',
    })).filter(a => a.answer.trim() !== '')

    onSubmit(formattedAnswers)
  }, [questions, answers, onSubmit])

  const handleSkip = useCallback(() => {
    onSubmit([])
  }, [onSubmit])

  if (questions.length === 0) {
    return (
      <div className="dynamic-questions empty">
        <p>質問がありません</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="dynamic-questions">
      {questions.map(question => (
        <div key={question.id} className="question-item">
          <label className="question-text">
            {question.question}
          </label>

          {question.type === 'freeform' ? (
            <input
              type="text"
              value={answers[question.id] || ''}
              onChange={e => handleFreeformChange(question.id, e.target.value)}
              placeholder={question.placeholder || '回答を入力...'}
              className="freeform-input"
              disabled={isLoading}
            />
          ) : question.type === 'multi_choice' ? (
            <div className="choice-options multi-choice">
              {question.choices?.map(choice => {
                const selectedValues = answers[question.id]?.split(',') || []
                const isSelected = selectedValues.includes(choice.value)
                return (
                  <label
                    key={choice.value}
                    className={`choice-option ${isSelected ? 'selected' : ''}`}
                  >
                    <input
                      type="checkbox"
                      name={question.id}
                      value={choice.value}
                      checked={isSelected}
                      onChange={() => handleMultiChoiceToggle(question.id, choice.value)}
                      disabled={isLoading}
                    />
                    <span className="choice-content">
                      <span className="choice-label">{choice.label}</span>
                      {choice.description && (
                        <span className="choice-description">{choice.description}</span>
                      )}
                    </span>
                  </label>
                )
              })}
            </div>
          ) : (
            <div className="choice-options">
              {question.choices?.map(choice => (
                <label
                  key={choice.value}
                  className={`choice-option ${answers[question.id] === choice.value ? 'selected' : ''}`}
                >
                  <input
                    type="radio"
                    name={question.id}
                    value={choice.value}
                    checked={answers[question.id] === choice.value}
                    onChange={() => handleChoiceSelect(question.id, choice.value)}
                    disabled={isLoading}
                  />
                  <span className="choice-content">
                    <span className="choice-label">{choice.label}</span>
                    {choice.description && (
                      <span className="choice-description">{choice.description}</span>
                    )}
                  </span>
                </label>
              ))}
            </div>
          )}
        </div>
      ))}

      <div className="actions">
        {allowSkip && (
          <button
            type="button"
            className="skip-button"
            onClick={handleSkip}
            disabled={isLoading}
          >
            スキップ
          </button>
        )}
        <button
          type="submit"
          className="submit-button"
          disabled={isLoading}
        >
          {isLoading ? '処理中...' : '回答する'}
        </button>
      </div>

      <style>{`
        .dynamic-questions {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .dynamic-questions.empty {
          text-align: center;
          color: var(--color-text-secondary, #aaa);
          padding: 2rem;
        }

        .question-item {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .question-text {
          font-size: 1rem;
          font-weight: 600;
          color: var(--color-text, #fff);
        }

        .freeform-input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid var(--color-border, #444);
          border-radius: 8px;
          background: var(--color-bg-secondary, #1a1a2e);
          color: var(--color-text, #fff);
          font-size: 1rem;
        }

        .freeform-input:focus {
          outline: none;
          border-color: var(--color-accent, #6366f1);
          box-shadow: 0 0 0 2px var(--color-accent-alpha, rgba(99, 102, 241, 0.2));
        }

        .choice-options {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .choice-option {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          padding: 0.75rem;
          border: 1px solid var(--color-border, #444);
          border-radius: 8px;
          background: var(--color-bg-secondary, #1a1a2e);
          cursor: pointer;
          transition: all 0.2s;
        }

        .choice-option:hover:not(:has(input:disabled)) {
          border-color: var(--color-accent, #6366f1);
        }

        .choice-option.selected {
          border-color: var(--color-accent, #6366f1);
          background: var(--color-bg-tertiary, #252538);
        }

        .choice-option input[type="radio"],
        .choice-option input[type="checkbox"] {
          margin-top: 0.25rem;
          accent-color: var(--color-accent, #6366f1);
        }

        .multi-choice .choice-option {
          cursor: pointer;
        }

        .choice-content {
          display: flex;
          flex-direction: column;
          gap: 0.125rem;
        }

        .choice-label {
          font-weight: 500;
          color: var(--color-text, #fff);
        }

        .choice-description {
          font-size: 0.875rem;
          color: var(--color-text-secondary, #aaa);
        }

        .actions {
          display: flex;
          justify-content: flex-end;
          gap: 0.75rem;
          margin-top: 0.5rem;
        }

        .skip-button {
          padding: 0.75rem 1.5rem;
          border: 1px solid var(--color-border, #444);
          border-radius: 8px;
          background: transparent;
          color: var(--color-text-secondary, #aaa);
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .skip-button:hover:not(:disabled) {
          border-color: var(--color-text-secondary, #aaa);
          color: var(--color-text, #fff);
        }

        .skip-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
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

import React, { useState } from 'react';

// DiagnoseAnswers を先に定義（ESMモジュールでの参照順序問題を回避）
export interface DiagnoseAnswers {
  strictness: string;
  response_length: string;
  tone: string;
  use_case: string;
  additional_notes: string;
}

interface QuestionnaireProps {
  onComplete: (answers: DiagnoseAnswers) => void;
}

interface Question {
  id: keyof Omit<DiagnoseAnswers, 'additional_notes'>;
  label: string;
  options: { value: string; label: string }[];
}

const questions: Question[] = [
  {
    id: 'strictness',
    label: 'AIにはどの程度厳格に振る舞ってほしいですか？',
    options: [
      { value: 'flexible', label: 'ある程度柔軟に (Flexible)' },
      { value: 'strict', label: '非常に厳格に (Very strict)' },
      { value: 'creative', label: 'クリエイティブ/自由に (Creative)' }
    ]
  },
  {
    id: 'response_length',
    label: '回答の長さはどの程度を好みますか？',
    options: [
      { value: 'short', label: '短く簡潔に (Short & concise)' },
      { value: 'standard', label: '標準的な長さ (Standard)' },
      { value: 'detailed', label: '詳細に説明 (Detailed)' }
    ]
  },
  {
    id: 'tone',
    label: 'どのようなトーンで会話したいですか？',
    options: [
      { value: 'formal', label: 'フォーマル/ビジネス (Formal)' },
      { value: 'casual', label: 'カジュアル/フレンドリー (Casual)' },
      { value: 'technical', label: '技術的/専門的 (Technical)' }
    ]
  },
  {
    id: 'use_case',
    label: '主な用途は何ですか？',
    options: [
      { value: 'coding', label: 'プログラミング・開発 (Coding)' },
      { value: 'writing', label: '文章作成・ライティング (Writing)' },
      { value: 'research', label: 'リサーチ・調査 (Research)' },
      { value: 'general', label: '汎用・その他 (General)' }
    ]
  }
];

const selectStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.75rem',
  borderRadius: '0.5rem',
  background: 'var(--color-bg-secondary)',
  border: '1px solid var(--color-border)',
  color: 'var(--color-text-primary)',
  outline: 'none',
  fontSize: '1rem',
  cursor: 'pointer'
};

const textareaStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.75rem',
  borderRadius: '0.5rem',
  background: 'var(--color-bg-secondary)',
  border: '1px solid var(--color-border)',
  color: 'var(--color-text-primary)',
  outline: 'none',
  fontSize: '1rem',
  minHeight: '100px',
  resize: 'vertical',
  fontFamily: 'inherit'
};

export const Questionnaire: React.FC<QuestionnaireProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<DiagnoseAnswers>({
    strictness: 'flexible',
    response_length: 'standard',
    tone: 'formal',
    use_case: 'general',
    additional_notes: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const totalSteps = questions.length + 1; // +1 for additional notes
  const progress = ((currentStep + 1) / totalSteps) * 100;

  const handleSelectChange = (questionId: keyof DiagnoseAnswers, value: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const handleNext = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    // Simulate a brief delay for UX
    await new Promise(resolve => setTimeout(resolve, 300));
    onComplete(answers);
  };

  const currentQuestion = questions[currentStep];
  const isLastStep = currentStep === totalSteps - 1;

  return (
    <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '2rem auto' }}>
      <h2 style={{ marginTop: 0, marginBottom: '1rem', textAlign: 'center' }}>診断アンケート</h2>

      {/* Progress bar */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '0.5rem',
          fontSize: '0.875rem',
          color: 'var(--color-text-secondary)'
        }}>
          <span>進捗</span>
          <span>{currentStep + 1} / {totalSteps}</span>
        </div>
        <div style={{
          height: '4px',
          background: 'var(--color-bg-secondary)',
          borderRadius: '2px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${progress}%`,
            height: '100%',
            background: 'var(--color-accent)',
            transition: 'width 0.3s ease'
          }} />
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        {!isLastStep && currentQuestion && (
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{
              display: 'block',
              marginBottom: '0.75rem',
              fontWeight: 500,
              fontSize: '1.125rem'
            }}>
              Q{currentStep + 1}. {currentQuestion.label}
            </label>
            <select
              value={answers[currentQuestion.id]}
              onChange={(e) => handleSelectChange(currentQuestion.id, e.target.value)}
              style={selectStyle}
            >
              {currentQuestion.options.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        )}

        {isLastStep && (
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{
              display: 'block',
              marginBottom: '0.75rem',
              fontWeight: 500,
              fontSize: '1.125rem'
            }}>
              追加の要望があれば教えてください（任意）
            </label>
            <p style={{
              color: 'var(--color-text-secondary)',
              marginBottom: '1rem',
              fontSize: '0.875rem'
            }}>
              特定のルールや制約、好みのスタイルなど、AIに伝えたいことがあればご記入ください。
            </p>
            <textarea
              value={answers.additional_notes}
              onChange={(e) => handleSelectChange('additional_notes', e.target.value)}
              placeholder="例: コードには必ずコメントを付けてほしい、日本語で回答してほしい など"
              style={textareaStyle}
            />
          </div>
        )}

        <div style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'space-between',
          marginTop: '2rem'
        }}>
          <button
            type="button"
            onClick={handlePrev}
            disabled={currentStep === 0}
            style={{
              background: 'transparent',
              border: '1px solid var(--color-border)',
              color: currentStep === 0 ? 'var(--color-text-secondary)' : 'var(--color-text-primary)',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.5rem',
              cursor: currentStep === 0 ? 'not-allowed' : 'pointer',
              opacity: currentStep === 0 ? 0.5 : 1
            }}
          >
            戻る
          </button>

          {!isLastStep ? (
            <button
              type="button"
              onClick={handleNext}
              className="btn-primary"
            >
              次へ
            </button>
          ) : (
            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? '診断中...' : '診断を開始する'}
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

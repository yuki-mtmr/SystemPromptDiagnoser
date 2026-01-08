import React from 'react';

interface QuestionnaireProps {
  onComplete: () => void;
}

export const Questionnaire: React.FC<QuestionnaireProps> = ({ onComplete }) => {
  return (
    <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '2rem auto' }}>
      <h2 style={{ marginTop: 0, marginBottom: '1.5rem', textAlign: 'center' }}>診断アンケート</h2>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem', textAlign: 'center' }}>
        いくつかの質問に答えて、最適なシステムプロンプトを生成しましょう。
      </p>
      
      <form onSubmit={(e) => { e.preventDefault(); onComplete(); }}>
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            質問 1: AIにはどの程度厳格に振る舞ってほしいですか？
          </label>
          <select style={{ 
            width: '100%', 
            padding: '0.75rem', 
            borderRadius: '0.5rem',
            background: 'var(--color-bg-secondary)',
            border: '1px solid var(--color-border)',
            color: 'var(--color-text-primary)',
            outline: 'none'
          }}>
            <option>ある程度柔軟に (Somewhat flexible)</option>
            <option>非常に厳格に (Very strict)</option>
            <option>クリエイティブ/自由に (Creative/Loose)</option>
          </select>
        </div>

        <button type="submit" className="btn-primary" style={{ width: '100%' }}>
          診断を開始する
        </button>
      </form>
    </div>
  );
};

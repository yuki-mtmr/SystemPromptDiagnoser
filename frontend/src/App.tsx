import { useState } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Questionnaire } from './components/Questionnaire';
import { ResultsDisplay } from './components/ResultsDisplay';
import './App.css'; 

function App() {
  const [view, setView] = useState<'questionnaire' | 'results'>('questionnaire');

  return (
    <>
      <Header />
      <main className="container" style={{ flex: 1, padding: '2rem 1rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
            あなたに最適な <span style={{ color: 'var(--color-accent)' }}>システムプロンプト</span> を発見しよう
          </h2>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
            汎用的なプロンプトに悩むのはもう終わりです。あなたのスタイルに合わせた、最適なシステムプロンプトを生成します。
          </p>
        </div>
        
        {view === 'questionnaire' ? (
          <Questionnaire onComplete={() => setView('results')} />
        ) : (
          <ResultsDisplay onReset={() => setView('questionnaire')} />
        )}
      </main>
      <Footer />
    </>
  );
}

export default App;

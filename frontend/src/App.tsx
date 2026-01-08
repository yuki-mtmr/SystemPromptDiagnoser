import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Questionnaire } from './components/Questionnaire';
import './App.css'; 

function App() {
  return (
    <>
      <Header />
      <main className="container" style={{ flex: 1, padding: '2rem 1rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
            Uncover Your Ideal <span style={{ color: 'var(--color-accent)' }}>System Prompt</span>
          </h2>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
            Stop wrestling with generic prompts. Get a scientifically personalized system prompt tailored to your communication style.
          </p>
        </div>
        
        <Questionnaire />
      </main>
      <Footer />
    </>
  );
}

export default App;

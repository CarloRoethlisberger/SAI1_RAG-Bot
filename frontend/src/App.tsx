// src/App.tsx
import "./App.css";
import SummarySection from "./components/SummarySection";
import BookQASection from "./components/BookQASection";
import QuizSection from "./components/QuizSection";
import UploadSection from "./components/UploadSection";

function App() {
  return (
    <div className="app-root">
      <header className="app-header">
        <h1>AI Reading Assistant</h1>
        <p>Zusammenfassen, Fragen stellen, Quiz erstellen & Bücher hochladen</p>
      </header>

      <main className="app-main">
        <section className="card">
          <h2>Freie Zusammenfassung</h2>
          <SummarySection />
        </section>

        <section className="card">
          <h2>Fragen zum Buch</h2>
          <BookQASection />
        </section>

        <section className="card">
          <h2>Quiz erstellen</h2>
          <QuizSection />
        </section>

        <section className="card">
          <h2>Buch hochladen (.txt)</h2>
          <UploadSection />
        </section>
      </main>
    </div>
  );
}

export default App;

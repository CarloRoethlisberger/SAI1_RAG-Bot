// src/App.tsx
import "./App.css";
import SummarySection from "./components/SummarySection";
import BookQASection from "./components/BookQASection";
import QuizSection from "./components/QuizSection";
import UploadSection from "./components/UploadSection";
import GutenbergSection from "./components/Gutenberg";



function App() {
  return (
    <div className="layout">
      {/* LEFT SIDEBAR */}
      <aside className="sidebar">
        <div className="sidebar-inner">
          <h2>So funktioniert’s</h2>
          <p>
            Das Projekt Gutenberg ist eine der ältesten und grössten freien digitalen Bibliotheken der Welt.
            <br />
            <br />
            Das Projekt stellt gemeinfreie Bücher kostenlos als digitale Volltexte zur Verfügung. Die Werke dürfen frei gelesen, gespeichert, weitergegeben und weiterverarbeitet werden.
            <br />
            <br />
            1) Lade manuell ein Buch (.txt) hoch oder nutze die Import-Funktion, um Bücher direkt in der Gutenberg-Datenbank zu suchen.
            <br />
            <br />
            2) Stelle Fragen zum Buch oder erstelle ein Quiz.
            <br />
            <br />
            3) Optional: Nutze „Gezielte Fragen mit Kontext“ für präzisere Antworten.
          </p>

          <div className="sidebar-box">
            <strong>Tipp:</strong>
            <div>
              Wenn du Informationen ausserhalb des Kontexts bzw. der Gutenberg-Datenbank benötigst, kannst du die Freie Zusammenfassung verwenden.
            </div>
          </div>
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
        <br />
          Info: 
          <br />
          https://www.projekt-gutenberg.org/
        </div>
      </aside>

      {/* RIGHT CONTENT */}
      <div className="content">
        <div className="app-root">
          <header className="app-header">
            <h1>AI Reading Assistant</h1>
            <p>Projekt Gutenberg neu gedacht – mit KI zum Verständnis.</p>
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

              <section className="card"> 
              <h2>Project Gutenberg (Import)</h2> 
              <GutenbergSection />
            </section>
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;

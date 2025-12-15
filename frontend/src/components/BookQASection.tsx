// src/components/BookQASection.tsx
import { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

interface BookAnswerResponse {
  answer: string;
  context: string[];
}

const BookQASection = () => {
  const [books, setBooks] = useState<string[]>([]);
  const [selectedBook, setSelectedBook] = useState<string>("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [context, setContext] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Bücherliste vom Backend holen
 
  
  useEffect(() => {
  async function fetchBooks() {
    try {
      const res = await fetch(`${API_BASE}/books`);
      if (!res.ok) throw new Error("Fehler beim Laden der Bücherliste");
      const data: string[] = await res.json();
      setBooks(data);

      // keep current selection if it still exists, else pick first
      setSelectedBook((prev) => (prev && data.includes(prev) ? prev : (data[0] ?? "")));
    } catch (err: any) {
      setError(err.message ?? "Fehler beim Laden der Bücherliste");
    }
  }

  fetchBooks(); // initial load

  const onBooksUpdated = () => fetchBooks();
  window.addEventListener("books-updated", onBooksUpdated);

  return () => window.removeEventListener("books-updated", onBooksUpdated);
}, []);

  async function handleAsk() {
    if (!selectedBook) {
      setError("Bitte zuerst ein Buch auswählen.");
      return;
    }
    if (!question.trim()) {
      setError("Bitte eine Frage eingeben.");
      return;
    }

    setLoading(true);
    setError(null);
    setAnswer(null);
    setContext([]);

    try {
      const res = await fetch(`${API_BASE}/ask_book`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          book_id: selectedBook,
          question: question,
        }),
      });

      if (!res.ok) {
        throw new Error("Fehler beim Beantworten der Frage");
      }

      const data: BookAnswerResponse = await res.json();
      setAnswer(data.answer);
      setContext(data.context ?? []);
    } catch (err: any) {
      setError(err.message ?? "Unbekannter Fehler");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {/* Buch-Auswahl */}
      <div className="field-row">
        <label className="field-label">
          Buch auswählen:
          <select
            className="select-input"
            value={selectedBook}
            onChange={(e) => setSelectedBook(e.target.value)}
          >
            {books.length === 0 && <option value="">(Keine Bücher gefunden)</option>}
            {books.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </label>
      </div>

      <textarea
        className="text-input"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={3}
        placeholder="Stelle eine Frage zum ausgewählten Buch..."
      />

      <button className="primary-button" onClick={handleAsk} disabled={loading}>
        {loading ? "Antwort wird generiert..." : "Frage stellen"}
      </button>

      {error && <p className="error-text">{error}</p>}

      {answer && (
        <div className="output-box">
          <h3>Antwort</h3>
          <p className="output-text">{answer}</p>

          {context.length > 0 && (
            <>
              <h4>Verwendete Textausschnitte</h4>
              <ul className="context-list">
                {context.map((chunk, idx) => (
                  <li key={idx}>
                    <pre className="context-chunk">{chunk}</pre>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default BookQASection;

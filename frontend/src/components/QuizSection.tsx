// src/components/QuizSection.tsx
import { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

interface QuizCard {
  question: string;
  answer: string;
}

interface QuizResponse {
  cards: QuizCard[];
}

const QuizSection = () => {
  const [books, setBooks] = useState<string[]>([]);
  const [selectedBook, setSelectedBook] = useState<string>("");
  const [numQuestions, setNumQuestions] = useState<number>(5);
  const [cards, setCards] = useState<QuizCard[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Bücher laden
  useEffect(() => {
    async function fetchBooks() {
      try {
        const res = await fetch(`${API_BASE}/books`);
        if (!res.ok) {
          throw new Error("Fehler beim Laden der Bücherliste");
        }
        const data: string[] = await res.json();
        setBooks(data);
        if (data.length > 0) {
          setSelectedBook(data[0]);
        }
      } catch (err: any) {
        setError(err.message ?? "Fehler beim Laden der Bücherliste");
      }
    }

    fetchBooks();
  }, []);

  async function handleGenerateQuiz() {
    if (!selectedBook) {
      setError("Bitte zuerst ein Buch auswählen.");
      return;
    }

    setLoading(true);
    setError(null);
    setCards([]);

    try {
      const res = await fetch(`${API_BASE}/quiz`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          book_id: selectedBook,
          num_questions: numQuestions,
        }),
      });

      if (!res.ok) {
        throw new Error("Fehler beim Erzeugen des Quiz");
      }

      const data: QuizResponse = await res.json();
      setCards(data.cards ?? []);
    } catch (err: any) {
      setError(err.message ?? "Unbekannter Fehler");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {/* Buch-Auswahl + Anzahl Fragen */}
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

        <label className="field-label">
          Anzahl Fragen:
          <input
            className="number-input"
            type="number"
            min={1}
            max={20}
            value={numQuestions}
            onChange={(e) => setNumQuestions(Number(e.target.value) || 1)}
          />
        </label>
      </div>

      <button className="primary-button" onClick={handleGenerateQuiz} disabled={loading}>
        {loading ? "Quiz wird erstellt..." : "Quiz erstellen"}
      </button>

      {error && <p className="error-text">{error}</p>}

      {cards.length > 0 && (
        <div className="output-box">
          <h3>Quizkarten</h3>
          <ul className="quiz-list">
            {cards.map((card, idx) => (
              <li key={idx} className="quiz-card">
                <p className="quiz-question">
                  <strong>Frage {idx + 1}:</strong> {card.question}
                </p>
                <p className="quiz-answer">
                  <strong>Antwort:</strong> {card.answer}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default QuizSection;

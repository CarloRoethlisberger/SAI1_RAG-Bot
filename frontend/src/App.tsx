import { useState } from "react";
import "./App.css";

function App() {
  // === SUMMARY-STATE ===
  const [input, setInput] = useState("");
  const [summary, setSummary] = useState("");

  async function handleSummary() {
    const response = await fetch("http://localhost:8000/summary", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: input }),
    });

    const data = await response.json();
    setSummary(data.summary);
  }

  // === BOOK / RAG STATE ===
  const [bookId, setBookId] = useState("faust");
  const [question, setQuestion] = useState("");
  const [bookAnswer, setBookAnswer] = useState("");
  const [bookContext, setBookContext] = useState<string[]>([]);
  const [isLoadingBook, setIsLoadingBook] = useState(false);
  const [bookError, setBookError] = useState("");

  async function handleAskBook() {
    setIsLoadingBook(true);
    setBookError("");
    setBookAnswer("");
    setBookContext([]);

    try {
      const response = await fetch("http://localhost:8000/ask_book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          book_id: bookId,
          question: question,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setBookAnswer(data.answer);
      setBookContext(data.context);
    } catch (err) {
      console.error(err);
      setBookError("Es ist ein Fehler aufgetreten.");
    } finally {
      setIsLoadingBook(false);
    }
  }

  return (
    <div className="container">
      <h1>AI Reading Assistant MVP</h1>

      {/* === SUMMARY === */}
      <section className="card">
        <h2>1. Text zusammenfassen</h2>

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="textarea"
          placeholder="Gib deinen Text ein..."
        />

        <button onClick={handleSummary} className="button">
          Zusammenfassung erzeugen
        </button>

        {summary && (
          <div className="output">
            <h3>Summary:</h3>
            <p>{summary}</p>
          </div>
        )}
      </section>

      {/* === BOOK ASK (RAG) === */}
      <section className="card">
        <h2>2. Fragen zum Buch (Faust)</h2>

        <label className="label">
          Buch-ID:
          <input
            value={bookId}
            onChange={(e) => setBookId(e.target.value)}
            className="input"
          />
        </label>

        <label className="label">
          Frage:
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="textarea"
            placeholder='z.B. "Wer ist Mephisto?"'
          />
        </label>

        <button
          onClick={handleAskBook}
          className="button"
          disabled={isLoadingBook || !question.trim()}
        >
          {isLoadingBook ? "Frage wird beantwortet..." : "Buch fragen"}
        </button>

        {bookError && <p className="error">{bookError}</p>}

        {bookAnswer && (
          <div className="output">
            <h3>Antwort:</h3>
            <p>{bookAnswer}</p>

            <h4>Kontextstellen:</h4>
            <ol>
              {bookContext.map((chunk, i) => (
                <li key={i} className="chunk">
                  {chunk}
                </li>
              ))}
            </ol>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;

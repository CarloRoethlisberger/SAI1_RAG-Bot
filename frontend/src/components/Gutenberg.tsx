// src/components/GutenbergSection.tsx
import { useState } from "react";

type GutenbergBook = {
  id: number;
  title: string;
  authors: string[];
  text_url?: string | null;
};

type GutenbergSearchResponse = {
  books: GutenbergBook[];
};

type GutenbergImportResponse = {
  book_id: string;
  title: string;
  authors: string[];
  char_count: number;
  message: string;
};

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function GutenbergSection() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<GutenbergBook[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [customBookId, setCustomBookId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");

  async function search() {
    setError("");
    setSuccess("");
    setResults([]);
    setSelectedId(null);

    if (!query.trim()) {
      setError("Bitte einen Suchbegriff eingeben.");
      return;
    }

    try {
      setLoading(true);
      const res = await fetch(
        `${API_BASE}/gutenberg/search?query=${encodeURIComponent(query.trim())}`
      );
      if (!res.ok) throw new Error(`Search failed (${res.status})`);
      const data = (await res.json()) as GutenbergSearchResponse;
      setResults(data.books || []);
    } catch (e: any) {
      setError(e?.message ?? "Fehler bei der Gutenberg-Suche.");
    } finally {
      setLoading(false);
    }
  }

  async function importBook() {
    setError("");
    setSuccess("");

    if (!selectedId) {
      setError("Bitte zuerst ein Buch auswählen.");
      return;
    }

    try {
      setLoading(true);
      const payload: { gutenberg_id: number; book_id?: string } = {
        gutenberg_id: selectedId,
      };
      if (customBookId.trim()) payload.book_id = customBookId.trim();

      const res = await fetch(`${API_BASE}/gutenberg/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Import failed (${res.status})`);
      }

      const data = (await res.json()) as GutenbergImportResponse;
      setSuccess(data.message || `Importiert als ${data.book_id}`);

      // Optional: trigger a global "books changed" event so other components can reload /books
      window.dispatchEvent(new Event("books-updated"));
    } catch (e: any) {
      setError(e?.message ?? "Fehler beim Import.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <label className="field-label">
        Suche (Titel/Autor)
        <input
          className="text-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="z.B. Faust, Shakespeare, Austen..."
        />
      </label>

      <button className="primary-button" onClick={search} disabled={loading}>
        {loading ? "Suche..." : "Suchen"}
      </button>

      {results.length > 0 && (
        <div className="output-box">
          <div className="output-text" style={{ fontWeight: 600, marginBottom: "0.5rem" }}>
            Ergebnisse (eins auswählen)
          </div>

          <div className="gutenberg-results">
            {results.map((b) => (
              <label key={b.id} className="gutenberg-result">
                <input
                  type="radio"
                  name="gutenbergPick"
                  checked={selectedId === b.id}
                  onChange={() => setSelectedId(b.id)}
                />
                <div className="gutenberg-meta">
                  <div className="gutenberg-title">{b.title}</div>
                  <div className="gutenberg-authors">{(b.authors || []).join(", ")}</div>
                  {!b.text_url && (
                    <div className="error-text" style={{ marginTop: "0.35rem" }}>
                      Kein Plain-Text-Link erkannt (Import kann fehlschlagen).
                    </div>
                  )}
                </div>
              </label>
            ))}
          </div>

          <label className="field-label" style={{ marginTop: "1rem" }}>
            Optional: eigener book_id (sonst: gutenberg_&lt;id&gt;)
            <input
              className="text-input"
              value={customBookId}
              onChange={(e) => setCustomBookId(e.target.value)}
              placeholder="z.B. faust_de oder pride_and_prejudice"
            />
          </label>

          <button className="primary-button" onClick={importBook} disabled={loading}>
            {loading ? "Import..." : "In RAG importieren"}
          </button>
        </div>
      )}

      {success && <div className="success-text">{success}</div>}
      {error && <div className="error-text">{error}</div>}
    </div>
  );
}
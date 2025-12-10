// src/components/SummarySection.tsx
import { useState } from "react";

const API_BASE = "http://localhost:8000";

const SummarySection = () => {
  const [input, setInput] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSummary() {
    setLoading(true);
    setError(null);
    setSummary("");

    try {
      const response = await fetch(`${API_BASE}/summary`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: input }),
      });

      if (!response.ok) {
        throw new Error("Fehler beim Abrufen der Zusammenfassung");
      }

      const data = await response.json();
      setSummary(data.summary ?? "");
    } catch (err: any) {
      setError(err.message ?? "Unbekannter Fehler");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <textarea
        className="text-input"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        rows={4}
        placeholder="Gib deinen Text ein..."
      />

      <button className="primary-button" onClick={handleSummary} disabled={loading}>
        {loading ? "Wird zusammengefasst..." : "Zusammenfassung erzeugen"}
      </button>

      {error && <p className="error-text">{error}</p>}

      {summary && (
        <div className="output-box">
          <h3>Zusammenfassung</h3>
          <p className="output-text">{summary}</p>
        </div>
      )}
    </div>
  );
};

export default SummarySection;

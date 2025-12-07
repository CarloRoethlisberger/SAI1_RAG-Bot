import { useState } from "react";

function App() {
  const [input, setInput] = useState("");
  const [summary, setSummary] = useState("");

  async function handleSummary() {
    const response = await fetch("http://localhost:8000/summary", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: input })
    });

    const data = await response.json();
    setSummary(data.summary);
  }

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>AI Reading Assistant MVP</h1>

      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        rows={4}
        cols={50}
        placeholder="Gib deinen Text ein..."
      />

      <br />

      <button onClick={handleSummary} style={{ marginTop: "1rem" }}>
        Generate Summary
      </button>

      {summary && (
        <div style={{ marginTop: "2rem", padding: "1rem", border: "1px solid grey" }}>
          <h3>Summary:</h3>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}

export default App;

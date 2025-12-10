// src/components/UploadSection.tsx
import { useState } from "react";

const API_BASE = "http://localhost:8000";

const UploadSection = () => {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null;
    setFile(f);
    setMessage(null);
    setError(null);
  }

  async function handleUpload() {
    if (!file) {
      setError("Bitte zuerst eine .txt-Datei auswählen.");
      return;
    }

    if (!file.name.toLowerCase().endsWith(".txt")) {
      setError("Nur .txt-Dateien sind erlaubt.");
      return;
    }

    setLoading(true);
    setMessage(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/upload_book`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Fehler beim Hochladen");
      }

      const data = await res.json();
      setMessage(data.message ?? "Buch erfolgreich hochgeladen.");
    } catch (err: any) {
      setError(err.message ?? "Unbekannter Fehler");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <input
        type="file"
        accept=".txt"
        onChange={handleFileChange}
        className="file-input"
      />

      <button className="primary-button" onClick={handleUpload} disabled={loading}>
        {loading ? "Wird hochgeladen..." : "Buch hochladen"}
      </button>

      {message && <p className="success-text">{message}</p>}
      {error && <p className="error-text">{error}</p>}
    </div>
  );
};

export default UploadSection;

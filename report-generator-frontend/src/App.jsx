import { useState } from "react";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function generateReport() {
    if (!input.trim()) {
      setError("Please enter your accomplishment details.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/generate-docx", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: input }),
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.detail || "Failed to generate report.");
      }

      // Receive the DOCX file as a Blob
      const blob = await response.blob();

      // Create temporary download URL
      const url = window.URL.createObjectURL(blob);

      // Create download link
      const link = document.createElement("a");
      link.href = url;
      link.download = "Accomplishment_Report.docx";

      document.body.appendChild(link);
      link.click();
      link.remove();

      // Clean up temporary URL
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <div className="container">
        <h1>AI Accomplishment Report Generator</h1>

        <p className="subtitle">
          Enter your accomplishments and let AI generate a Word document.
        </p>

        <label htmlFor="accomplishments">Your Accomplishments</label>

        <textarea
          id="accomplishments"
          placeholder="Example: Discussed linked list insertion and deletion. Students performed a laboratory exercise..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />

        {error && <p className="error">{error}</p>}

        <button onClick={generateReport} disabled={loading}>
          {loading ? "Generating Document..." : "Generate Word Report"}
        </button>
      </div>
    </div>
  );
}

export default App;

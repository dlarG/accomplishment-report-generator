import { useEffect, useState } from "react";
import "./App.css";

const API = "http://localhost:8000";

function App() {
  const [page, setPage] = useState("generator");

  // Report Generator states
  const [input, setInput] = useState("");
  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState("");

  // Knowledge Base states
  const [reports, setReports] = useState([]);
  const [loadingReports, setLoadingReports] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [kbError, setKbError] = useState("");
  const [kbMessage, setKbMessage] = useState("");
  const [selectedReport, setSelectedReport] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Load reports when the Knowledge Base page is opened
  useEffect(() => {
    if (page === "knowledge") {
      loadReports();
    }
  }, [page]);

  // ==============================
  // REPORT GENERATOR
  // ==============================

  async function generateReport() {
    if (!input.trim()) {
      setGenerateError("Please enter your accomplishment details.");
      return;
    }

    setGenerating(true);
    setGenerateError("");

    try {
      const response = await fetch(`${API}/api/generate-docx`, {
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

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = "Accomplishment_Report.docx";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (err) {
      setGenerateError(err.message);
    } finally {
      setGenerating(false);
    }
  }

  // ==============================
  // KNOWLEDGE BASE
  // ==============================

  async function loadReports() {
    setLoadingReports(true);
    setKbError("");

    try {
      const response = await fetch(`${API}/api/knowledge`);

      if (!response.ok) {
        throw new Error("Failed to load Knowledge Base.");
      }

      const data = await response.json();
      setReports(data);
    } catch (err) {
      setKbError(err.message);
    } finally {
      setLoadingReports(false);
    }
  }

  async function uploadReports(event) {
    const files = Array.from(event.target.files || []);

    if (files.length === 0) return;

    setUploading(true);
    setKbError("");
    setKbMessage("");

    let successful = 0;
    let failed = 0;

    for (const file of files) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch(`${API}/api/knowledge/upload`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const result = await response.json();
          throw new Error(result.detail || "Upload failed.");
        }

        successful++;
      } catch (err) {
        failed++;
        setKbError(`${file.name}: ${err.message}`);
      }
    }

    if (successful > 0) {
      setKbMessage(
        `${successful} report${
          successful > 1 ? "s" : ""
        } uploaded successfully.`
      );
    }

    if (failed > 0) {
      setKbError(`${failed} file(s) failed to upload.`);
    }

    await loadReports();

    setUploading(false);

    // Reset file picker so the same file can be uploaded again if needed
    event.target.value = "";
  }

  async function previewReport(reportId) {
    setPreviewLoading(true);
    setKbError("");
    setSelectedReport(null);

    try {
      const response = await fetch(`${API}/api/knowledge/${reportId}`);

      if (!response.ok) {
        throw new Error("Failed to load report preview.");
      }

      const data = await response.json();
      setSelectedReport(data);
    } catch (err) {
      setKbError(err.message);
    } finally {
      setPreviewLoading(false);
    }
  }

  async function deleteReport(reportId, filename) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) return;

    setKbError("");
    setKbMessage("");

    try {
      const response = await fetch(`${API}/api/knowledge/${reportId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.detail || "Failed to delete report.");
      }

      setKbMessage("Report deleted successfully.");

      if (selectedReport?.id === reportId) {
        setSelectedReport(null);
      }

      await loadReports();
    } catch (err) {
      setKbError(err.message);
    }
  }

  // ==============================
  // UI
  // ==============================

  return (
    <div className="app">
      <div className="workspace">
        {/* SIDEBAR */}
        <aside className="sidebar">
          <div className="brand">
            <div className="brand-icon">AI</div>
            <div>
              <h2>Report Assistant</h2>
              <span>Faculty Workspace</span>
            </div>
          </div>

          <p className="nav-label">WORKSPACE</p>

          <button
            className={`nav-button ${page === "generator" ? "active" : ""}`}
            onClick={() => setPage("generator")}
          >
            <span>✎</span> Report Generator
          </button>

          <button
            className={`nav-button ${page === "knowledge" ? "active" : ""}`}
            onClick={() => setPage("knowledge")}
          >
            <span>▤</span> Knowledge Base
          </button>

          <div className="sidebar-bottom">
            <div className="local-badge">
              <span className="status-dot"></span>
              Local AI · Ollama
            </div>
          </div>
        </aside>

        {/* MAIN CONTENT */}
        <main className="main-content">
          {/* ================= GENERATOR PAGE ================= */}
          {page === "generator" && (
            <div className="page-container">
              <div className="page-header">
                <div>
                  <p className="eyebrow">AI WRITING ASSISTANT</p>
                  <h1>Accomplishment Report Generator</h1>
                  <p className="page-description">
                    Transform your raw notes into professional accomplishment
                    statements.
                  </p>
                </div>
              </div>

              <section className="panel generator-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Your Accomplishments</h2>
                    <p>Enter your activities in English, Taglish, or Bisaya.</p>
                  </div>
                </div>

                <textarea
                  className="report-input"
                  placeholder="Example: nag continue sa pag discuss sa linked list sa DSA and nag introduce sa number system sa Introduction to Computing..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />

                <div className="input-footer">
                  <span>{input.length} characters</span>
                  <button
                    className="generate-button"
                    onClick={generateReport}
                    disabled={generating}
                  >
                    {generating
                      ? "Generating document..."
                      : "Generate Word Report  →"}
                  </button>
                </div>

                {generateError && (
                  <div className="alert error-alert">{generateError}</div>
                )}
              </section>

              <div className="info-panel">
                <span className="info-icon">✦</span>
                <div>
                  <strong>AI-powered writing</strong>
                  <p>
                    Your input will be processed by your local Ollama model.
                    Historical reports in your Knowledge Base will be used as
                    references during generation.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* ================= KNOWLEDGE BASE PAGE ================= */}
          {page === "knowledge" && (
            <div className="page-container">
              <div className="page-header">
                <div>
                  <p className="eyebrow">REFERENCE LIBRARY</p>
                  <h1>Knowledge Base</h1>
                  <p className="page-description">
                    Manage your previous accomplishment reports used as AI
                    writing references.
                  </p>
                </div>
              </div>

              {/* UPLOAD PANEL */}
              <section className="panel upload-panel">
                <div className="upload-icon">↑</div>

                <h2>Upload Previous Reports</h2>
                <p>
                  Upload your past accomplishment reports in DOCX format. Their
                  text will be extracted and stored for AI reference.
                </p>

                <label className="upload-button">
                  {uploading ? "Uploading files..." : "Select DOCX Files"}
                  <input
                    type="file"
                    accept=".docx"
                    multiple
                    onChange={uploadReports}
                    disabled={uploading}
                  />
                </label>

                <span className="upload-hint">
                  DOCX format · Multiple files supported
                </span>
              </section>

              {/* FEEDBACK */}
              {kbMessage && (
                <div className="alert success-alert">{kbMessage}</div>
              )}

              {kbError && <div className="alert error-alert">{kbError}</div>}

              {/* REPORT LIST */}
              <section className="panel library-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Your Reference Documents</h2>
                    <p>
                      {reports.length} document{reports.length !== 1 ? "s" : ""}{" "}
                      stored in your Knowledge Base
                    </p>
                  </div>

                  <button
                    className="refresh-button"
                    onClick={loadReports}
                    disabled={loadingReports}
                  >
                    ↻ Refresh
                  </button>
                </div>

                {loadingReports ? (
                  <div className="empty-state">
                    <p>Loading your reports...</p>
                  </div>
                ) : reports.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">▤</div>
                    <h3>No reports uploaded yet</h3>
                    <p>
                      Upload previous accomplishment reports to start building
                      your knowledge base.
                    </p>
                  </div>
                ) : (
                  <div className="report-list">
                    {reports.map((report) => (
                      <div className="report-item" key={report.id}>
                        <div className="doc-icon">DOC</div>

                        <div className="report-info">
                          <h3>{report.filename}</h3>
                          <p>
                            Uploaded:{" "}
                            {new Date(
                              report.uploaded_at + "Z"
                            ).toLocaleString()}
                          </p>
                          <p className="report-preview">
                            {report.text_preview || "No preview available"}
                          </p>
                        </div>

                        <div className="report-actions">
                          <button
                            className="preview-button"
                            onClick={() => previewReport(report.id)}
                          >
                            Preview
                          </button>

                          <button
                            className="delete-button"
                            onClick={() =>
                              deleteReport(report.id, report.filename)
                            }
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>

              {/* PREVIEW */}
              {previewLoading && (
                <section className="panel preview-panel">
                  <p>Loading document preview...</p>
                </section>
              )}

              {selectedReport && (
                <section className="panel preview-panel">
                  <div className="panel-heading">
                    <div>
                      <p className="eyebrow">DOCUMENT PREVIEW</p>
                      <h2>{selectedReport.filename}</h2>
                    </div>

                    <button
                      className="close-preview"
                      onClick={() => setSelectedReport(null)}
                    >
                      ✕
                    </button>
                  </div>

                  <pre className="preview-text">
                    {selectedReport.extracted_text}
                  </pre>
                </section>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;

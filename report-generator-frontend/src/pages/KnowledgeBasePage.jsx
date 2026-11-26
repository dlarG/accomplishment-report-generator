/* eslint-disable react-hooks/set-state-in-effect */
import { useCallback, useEffect, useState } from "react";

import KnowledgeUpload from "../components/KnowledgeUpload";
import KnowledgeList from "../components/KnowledgeList";
import KnowledgePreview from "../components/KnowledgePreview";

import {
  getKnowledgeDocuments,
  getKnowledgeDocument,
  uploadKnowledgeDocument,
  deleteKnowledgeDocument,
} from "../api/knowledgeApi";

function KnowledgeBasePage() {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);

  const [loadingReports, setLoadingReports] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadReports = useCallback(async () => {
    setLoadingReports(true);
    setError("");

    try {
      const data = await getKnowledgeDocuments();
      setReports(data);
    } catch (err) {
      setError(err.message || "Failed to load Knowledge Base.");
    } finally {
      setLoadingReports(false);
    }
  }, []);

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  async function handleUpload(files) {
    setUploading(true);
    setError("");
    setMessage("");

    let successful = 0;
    const failures = [];

    for (const file of files) {
      try {
        await uploadKnowledgeDocument(file);
        successful++;
      } catch (err) {
        failures.push(`${file.name}: ${err.message}`);
      }
    }

    if (successful > 0) {
      setMessage(
        `${successful} report${
          successful !== 1 ? "s" : ""
        } uploaded successfully.`
      );
    }

    await loadReports();
    setUploading(false);
  }

  async function handlePreview(reportId) {
    setPreviewLoading(true);
    setError("");
    setSelectedReport(null);

    try {
      const data = await getKnowledgeDocument(reportId);
      setSelectedReport(data);
    } catch (err) {
      setError(err.message || "Failed to load report preview.");
    } finally {
      setPreviewLoading(false);
    }
  }

  async function handleDelete(report) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${report.filename}"?`
    );

    if (!confirmed) return;

    setError("");
    setMessage("");

    try {
      await deleteKnowledgeDocument(report.id);

      setMessage("Report deleted successfully.");

      if (selectedReport?.id === report.id) {
        setSelectedReport(null);
      }

      await loadReports();
    } catch (err) {
      setError(err.message || "Failed to delete report.");
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <header>
        <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
          Reference Library
        </p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
          Knowledge Base
        </h1>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          Manage your previous accomplishment reports used as AI writing
          references. These documents help guide the writing style and
          terminology of generated statements.
        </p>
      </header>

      {error && (
        <div className="whitespace-pre-line rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {message && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {message}
        </div>
      )}

      <KnowledgeUpload onUpload={handleUpload} uploading={uploading} />

      <KnowledgeList
        reports={reports}
        loading={loadingReports}
        onRefresh={loadReports}
        onPreview={handlePreview}
        onDelete={handleDelete}
        previewLoading={previewLoading}
      />

      {previewLoading && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm">
          Loading document preview...
        </section>
      )}

      {selectedReport && (
        <KnowledgePreview
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
        />
      )}
    </div>
  );
}

export default KnowledgeBasePage;

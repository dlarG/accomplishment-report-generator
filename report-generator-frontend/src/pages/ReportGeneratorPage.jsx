import { useState } from "react";

import ReportInformation from "../components/ReportInformation";
import AccomplishmentList from "../components/AccomplishmentList";

import { generateAccomplishment, generateReportDocx } from "../api/reportApi";

const createEntry = () => ({
  id: crypto.randomUUID(),
  raw_text: "",
  accomplishment: "",
  remarks: "",
});

const initialReportInformation = {
  faculty_name: "",
  program_head_name: "",
  program_head_designation: "Program Head, BSIT",
  reporting_period: "",
  instruction_subjects: "",
};

function ReportGeneratorPage() {
  const [reportInfo, setReportInfo] = useState(initialReportInformation);
  const [entries, setEntries] = useState([createEntry()]);

  const [generatingIds, setGeneratingIds] = useState([]);
  const [generatingDocument, setGeneratingDocument] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  function updateReportInfo(field, value) {
    setReportInfo((previous) => ({
      ...previous,
      [field]: value,
    }));
  }

  function addEntry() {
    setEntries((previous) => [...previous, createEntry()]);
  }

  function updateEntry(entryId, field, value) {
    setEntries((previous) =>
      previous.map((entry) =>
        entry.id === entryId ? { ...entry, [field]: value } : entry
      )
    );
  }

  function removeEntry(entryId) {
    setEntries((previous) => previous.filter((entry) => entry.id !== entryId));
  }

  async function handleGenerateAccomplishment(entry) {
    setError("");
    setMessage("");

    setGeneratingIds((previous) => [...previous, entry.id]);

    try {
      const result = await generateAccomplishment(entry.raw_text);

      updateEntry(entry.id, "accomplishment", result.accomplishment || "");
      updateEntry(entry.id, "remarks", result.remarks || "");

      setMessage(
        `Accomplishment ${
          entries.findIndex((item) => item.id === entry.id) + 1
        } generated successfully.`
      );
    } catch (err) {
      setError(err.message || "Failed to generate accomplishment.");
    } finally {
      setGeneratingIds((previous) => previous.filter((id) => id !== entry.id));
    }
  }

  async function handleGenerateDocument() {
    setError("");
    setMessage("");

    if (
      !reportInfo.faculty_name.trim() ||
      !reportInfo.program_head_name.trim() ||
      !reportInfo.program_head_designation.trim() ||
      !reportInfo.reporting_period.trim() ||
      !reportInfo.instruction_subjects.trim()
    ) {
      setError("Please complete all report information fields.");
      return;
    }

    if (entries.length === 0) {
      setError("Please add at least one accomplishment.");
      return;
    }

    const incompleteEntry = entries.find(
      (entry) => !entry.raw_text.trim() || !entry.accomplishment.trim()
    );

    if (incompleteEntry) {
      setError(
        "Every activity must have raw notes and an accomplishment statement. Generate it with AI or enter it manually."
      );
      return;
    }

    if (generatingIds.length > 0) {
      setError("Please wait for the AI generation to finish.");
      return;
    }

    setGeneratingDocument(true);

    try {
      const reportData = {
        ...reportInfo,
        entries: entries.map((entry) => ({
          raw_text: entry.raw_text,
          accomplishment: entry.accomplishment,
          remarks: entry.remarks,
        })),
      };

      const blob = await generateReportDocx(reportData);

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = "Monthly_Accomplishment_Report.docx";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);

      setMessage("Your accomplishment report was generated successfully.");
    } catch (err) {
      setError(err.message || "Failed to generate Word document.");
    } finally {
      setGeneratingDocument(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <header>
        <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
          AI Writing Assistant
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
          Accomplishment Report Generator
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          Transform your raw activity notes into professional accomplishment
          statements and generate your SLSU monthly accomplishment report.
        </p>
      </header>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {message && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {message}
        </div>
      )}

      <ReportInformation values={reportInfo} onChange={updateReportInfo} />

      <AccomplishmentList
        entries={entries}
        onAdd={addEntry}
        onUpdate={updateEntry}
        onRemove={removeEntry}
        onGenerate={handleGenerateAccomplishment}
        generatingIds={generatingIds}
      />

      <section className="flex flex-col items-start justify-between gap-4 rounded-2xl border border-blue-100 bg-blue-50/70 p-6 sm:flex-row sm:items-center">
        <div>
          <h2 className="font-bold text-slate-800">
            Ready to generate your report?
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Review your entries before downloading the completed Word document.
          </p>
        </div>

        <button
          type="button"
          onClick={handleGenerateDocument}
          disabled={generatingDocument || generatingIds.length > 0}
          className="w-full rounded-xl bg-blue-600 px-6 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
        >
          {generatingDocument
            ? "Generating Word Document..."
            : "Generate Word Report →"}
        </button>
      </section>
    </div>
  );
}

export default ReportGeneratorPage;

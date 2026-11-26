function KnowledgePreview({ report, onClose }) {
  if (!report) return null;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-xs font-bold uppercase tracking-wider text-blue-600">
            Document Preview
          </p>

          <h2 className="mt-1 break-words text-lg font-bold text-slate-800">
            {report.filename}
          </h2>

          <p className="mt-1 text-xs text-slate-400">
            Extracted document content
          </p>
        </div>

        <button
          type="button"
          onClick={onClose}
          aria-label="Close preview"
          className="shrink-0 rounded-lg px-3 py-2 text-sm text-slate-500 transition hover:bg-slate-100"
        >
          ✕
        </button>
      </div>

      <pre className="max-h-[500px] overflow-auto whitespace-pre-wrap break-words rounded-xl bg-slate-50 p-5 text-sm leading-7 text-slate-700">
        {report.extracted_text || "No extracted text is available."}
      </pre>
    </section>
  );
}

export default KnowledgePreview;

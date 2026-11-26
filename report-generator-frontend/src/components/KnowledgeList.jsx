function KnowledgeList({
  reports,
  loading,
  onRefresh,
  onPreview,
  onDelete,
  previewLoading,
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-lg font-bold text-slate-800">
            Your Reference Documents
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            {reports.length} document{reports.length !== 1 ? "s" : ""} stored in
            your Knowledge Base
          </p>
        </div>

        <button
          type="button"
          onClick={onRefresh}
          disabled={loading}
          className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 disabled:opacity-50"
        >
          {loading ? "Refreshing..." : "↻ Refresh"}
        </button>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-slate-500">
          Loading your reports...
        </div>
      ) : reports.length === 0 ? (
        <div className="rounded-xl bg-slate-50 px-5 py-12 text-center">
          <div className="text-3xl text-slate-300">▤</div>
          <h3 className="mt-3 font-semibold text-slate-700">
            No reports uploaded yet
          </h3>
          <p className="mx-auto mt-2 max-w-sm text-sm text-slate-500">
            Upload previous accomplishment reports to start building your
            Knowledge Base.
          </p>
        </div>
      ) : (
        <div className="divide-y divide-slate-100">
          {reports.map((report) => (
            <div
              key={report.id}
              className="flex flex-col gap-4 py-5 first:pt-0 last:pb-0 sm:flex-row sm:items-start"
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-xs font-bold text-blue-700">
                DOCX
              </div>

              <div className="min-w-0 flex-1">
                <h3 className="break-words font-semibold text-slate-800">
                  {report.filename}
                </h3>

                <p className="mt-1 text-xs text-slate-400">
                  Uploaded:{" "}
                  {new Date(report.uploaded_at + "Z").toLocaleString()}
                </p>

                <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-500">
                  {report.text_preview || "No preview available."}
                </p>
              </div>

              <div className="flex shrink-0 gap-2 sm:justify-end">
                <button
                  type="button"
                  onClick={() => onPreview(report.id)}
                  disabled={previewLoading}
                  className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:opacity-50"
                >
                  Preview
                </button>

                <button
                  type="button"
                  onClick={() => onDelete(report)}
                  className="rounded-lg border border-red-100 px-3 py-2 text-xs font-semibold text-red-600 transition hover:bg-red-50"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default KnowledgeList;

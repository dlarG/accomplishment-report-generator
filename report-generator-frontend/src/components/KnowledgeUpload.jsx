function KnowledgeUpload({ onUpload, uploading }) {
  function handleFileChange(event) {
    const files = Array.from(event.target.files || []);

    if (files.length > 0) {
      onUpload(files);
    }

    // Allows selecting the same files again later.
    event.target.value = "";
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-7 text-center shadow-sm">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-2xl text-blue-600">
        ↑
      </div>

      <h2 className="mt-4 text-lg font-bold text-slate-800">
        Upload Previous Reports
      </h2>

      <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-500">
        Upload your previous accomplishment reports in DOCX format. Their
        extracted text will be stored and used as writing references.
      </p>

      <label
        className={`mt-5 inline-flex cursor-pointer items-center justify-center rounded-xl px-5 py-3 text-sm font-semibold text-white transition ${
          uploading
            ? "cursor-not-allowed bg-blue-400"
            : "bg-blue-600 hover:bg-blue-700"
        }`}
      >
        {uploading ? "Uploading files..." : "Select DOCX Files"}

        <input
          type="file"
          accept=".docx"
          multiple
          disabled={uploading}
          onChange={handleFileChange}
          className="hidden"
        />
      </label>

      <p className="mt-3 text-xs text-slate-400">
        DOCX format · Multiple files supported
      </p>
    </section>
  );
}

export default KnowledgeUpload;

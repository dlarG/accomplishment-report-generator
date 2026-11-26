function AccomplishmentEntry({
  entry,
  index,
  onChange,
  onGenerate,
  onRemove,
  generating,
}) {
  const textareaClass =
    "w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10";

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-sm font-bold text-blue-700">
            {String(index + 1).padStart(2, "0")}
          </div>
          <div>
            <h3 className="font-bold text-slate-800">
              Accomplishment Entry {index + 1}
            </h3>
            <p className="text-xs text-slate-400">
              Enter notes and generate a professional statement.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onRemove}
          className="rounded-lg px-3 py-2 text-xs font-semibold text-red-500 transition hover:bg-red-50"
        >
          Remove
        </button>
      </div>

      <div className="space-y-5">
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-700">
            Raw Activity Notes
          </label>
          <textarea
            rows={3}
            value={entry.raw_text}
            onChange={(event) => onChange("raw_text", event.target.value)}
            placeholder="Write your activities in English, Taglish, or Bisaya..."
            className={`${textareaClass} resize-y`}
          />
        </div>

        <div className="flex justify-end">
          <button
            type="button"
            onClick={onGenerate}
            disabled={generating || !entry.raw_text.trim()}
            className="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {generating ? "Generating..." : "✦ Generate with AI"}
          </button>
        </div>

        <div className="border-t border-slate-100 pt-5">
          <label className="mb-2 block text-sm font-semibold text-slate-700">
            Accomplishment Statement
          </label>
          <textarea
            rows={3}
            value={entry.accomplishment}
            onChange={(event) => onChange("accomplishment", event.target.value)}
            placeholder="Your professional accomplishment statement will appear here..."
            className={`${textareaClass} resize-y`}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-700">
            Remarks
            <span className="ml-2 font-normal text-slate-400">(Optional)</span>
          </label>
          <textarea
            rows={2}
            value={entry.remarks}
            onChange={(event) => onChange("remarks", event.target.value)}
            placeholder="Enter or edit the suggested remarks..."
            className={`${textareaClass} resize-y`}
          />
        </div>
      </div>
    </div>
  );
}

export default AccomplishmentEntry;

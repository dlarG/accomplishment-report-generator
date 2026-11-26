import AccomplishmentEntry from "./AccomplishmentEntry";

function AccomplishmentList({
  entries,
  onAdd,
  onUpdate,
  onRemove,
  onGenerate,
  generatingIds,
}) {
  return (
    <section className="space-y-5">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-blue-600">
            Activities
          </p>
          <h2 className="mt-1 text-xl font-bold text-slate-800">
            Your Accomplishments
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Add each activity separately. You can edit the AI results before
            generating your report.
          </p>
        </div>

        <button
          type="button"
          onClick={onAdd}
          className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-2.5 text-sm font-semibold text-blue-700 transition hover:bg-blue-100"
        >
          + Add Activity
        </button>
      </div>

      {entries.map((entry, index) => (
        <AccomplishmentEntry
          key={entry.id}
          entry={entry}
          index={index}
          onChange={(field, value) => onUpdate(entry.id, field, value)}
          onGenerate={() => onGenerate(entry)}
          onRemove={() => onRemove(entry.id)}
          generating={generatingIds.includes(entry.id)}
        />
      ))}

      <button
        type="button"
        onClick={onAdd}
        className="w-full rounded-xl border-2 border-dashed border-slate-200 py-4 text-sm font-semibold text-slate-500 transition hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700"
      >
        + Add Another Accomplishment
      </button>
    </section>
  );
}

export default AccomplishmentList;

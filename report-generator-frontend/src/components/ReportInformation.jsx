const inputClass =
  "w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10";

const labelClass = "mb-2 block text-sm font-semibold text-slate-700";

function ReportInformation({ values, onChange }) {
  function handleChange(event) {
    const { name, value } = event.target;
    onChange(name, value);
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-6">
        <p className="text-xs font-bold uppercase tracking-wider text-blue-600">
          Report Details
        </p>
        <h2 className="mt-1 text-xl font-bold text-slate-800">
          General Information
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Provide the information that will appear in your accomplishment
          report.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <div>
          <label className={labelClass} htmlFor="faculty_name">
            Faculty Name
          </label>
          <input
            id="faculty_name"
            name="faculty_name"
            value={values.faculty_name}
            onChange={handleChange}
            placeholder="Enter your complete name"
            className={inputClass}
          />
        </div>

        <div>
          <label className={labelClass} htmlFor="reporting_period">
            Reporting Period
          </label>
          <input
            id="reporting_period"
            name="reporting_period"
            value={values.reporting_period}
            onChange={handleChange}
            placeholder="e.g. November 1-15, 2026"
            className={inputClass}
          />
        </div>

        <div>
          <label className={labelClass} htmlFor="program_head_name">
            Program Head Name
          </label>
          <input
            id="program_head_name"
            name="program_head_name"
            value={values.program_head_name}
            onChange={handleChange}
            placeholder="Enter Program Head's name"
            className={inputClass}
          />
        </div>

        <div>
          <label className={labelClass} htmlFor="program_head_designation">
            Program Head Designation
          </label>
          <input
            id="program_head_designation"
            name="program_head_designation"
            value={values.program_head_designation}
            onChange={handleChange}
            placeholder="e.g. Program Head, BSIT - Programming"
            className={inputClass}
          />
        </div>

        <div className="md:col-span-2">
          <label className={labelClass} htmlFor="instruction_subjects">
            Instruction Subjects
          </label>
          <textarea
            id="instruction_subjects"
            name="instruction_subjects"
            rows={3}
            value={values.instruction_subjects}
            onChange={handleChange}
            placeholder="e.g. Data Structures and Algorithms; Introduction to Computing"
            className={`${inputClass} resize-y`}
          />
          <p className="mt-2 text-xs text-slate-400">
            Enter the subjects handled during this reporting period.
          </p>
        </div>
      </div>
    </section>
  );
}

export default ReportInformation;

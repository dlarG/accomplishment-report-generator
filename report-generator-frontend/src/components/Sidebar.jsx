function Sidebar({ page, setPage }) {
  const navigation = [
    {
      id: "generator",
      label: "Report Generator",
      icon: "✎",
      description: "Create reports",
    },
    {
      id: "knowledge",
      label: "Knowledge Base",
      icon: "▤",
      description: "Manage references",
    },
  ];

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden min-h-screen w-72 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
        <div className="flex items-center gap-3 border-b border-slate-100 px-6 py-7">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-sm font-bold text-white shadow-sm">
            AI
          </div>

          <div>
            <h2 className="font-bold text-slate-900">Report Assistant</h2>
            <p className="text-xs text-slate-400">Faculty Workspace</p>
          </div>
        </div>

        <div className="flex-1 px-4 py-7">
          <p className="mb-4 px-3 text-xs font-bold tracking-widest text-slate-400">
            WORKSPACE
          </p>

          <nav className="space-y-2">
            {navigation.map((item) => {
              const active = page === item.id;

              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setPage(item.id)}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left transition ${
                    active
                      ? "bg-blue-50 text-blue-700"
                      : "text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  <span
                    className={`flex h-10 w-10 items-center justify-center rounded-lg text-lg ${
                      active
                        ? "bg-white text-blue-600 shadow-sm"
                        : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {item.icon}
                  </span>

                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-semibold">
                      {item.label}
                    </span>
                    <span className="mt-0.5 block text-xs text-slate-400">
                      {item.description}
                    </span>
                  </span>

                  {active && (
                    <span className="h-2 w-2 rounded-full bg-blue-600" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="border-t border-slate-100 p-5">
          <div className="flex items-center gap-3 rounded-xl bg-slate-50 p-3">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
            </span>

            <div>
              <p className="text-xs font-semibold text-slate-700">
                Local AI · Ollama
              </p>
              <p className="text-xs text-slate-400">Local processing</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile navigation */}
      <div className="border-b border-slate-200 bg-white px-4 py-3 md:hidden">
        <div className="mb-3 flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-xs font-bold text-white">
            AI
          </div>

          <div>
            <h2 className="text-sm font-bold text-slate-900">
              Report Assistant
            </h2>
            <p className="text-xs text-slate-400">Faculty Workspace</p>
          </div>
        </div>

        <nav className="grid grid-cols-2 gap-2">
          {navigation.map((item) => {
            const active = page === item.id;

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setPage(item.id)}
                className={`rounded-xl px-3 py-2.5 text-sm font-semibold transition ${
                  active
                    ? "bg-blue-50 text-blue-700"
                    : "bg-slate-50 text-slate-600"
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>
    </>
  );
}

export default Sidebar;

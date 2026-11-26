import { useState } from "react";

import Sidebar from "./components/Sidebar";
import ReportGeneratorPage from "./pages/ReportGeneratorPage";
import KnowledgeBasePage from "./pages/KnowledgeBasePage";

function App() {
  const [page, setPage] = useState("generator");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 md:flex">
      <Sidebar page={page} setPage={setPage} />

      <main className="min-w-0 flex-1">
        <div className="mx-auto min-h-screen max-w-[1600px] px-4 py-7 sm:px-6 sm:py-9 lg:px-10">
          {page === "generator" && <ReportGeneratorPage />}

          {page === "knowledge" && <KnowledgeBasePage />}
        </div>
      </main>
    </div>
  );
}

export default App;

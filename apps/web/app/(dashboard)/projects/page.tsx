import Link from "next/link";
import { Plus } from "lucide-react";

export default function ProjectsPage() {
  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-white">Projekte</h1>
        <Link
          href="/projects/new"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg font-medium transition-colors"
        >
          <Plus size={18} />
          Neues Projekt
        </Link>
      </div>
      {/* ProjectList will be a client component fetching from API */}
      <div className="text-slate-400 text-center py-16">
        Lade Projekte…
      </div>
    </div>
  );
}

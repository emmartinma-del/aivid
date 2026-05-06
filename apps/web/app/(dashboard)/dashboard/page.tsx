import Link from "next/link";
import { Plus } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400 mt-1">Willkommen bei AIvid</p>
        </div>
        <Link
          href="/projects/new"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg font-medium transition-colors"
        >
          <Plus size={18} />
          Neues Projekt
        </Link>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        {[
          { label: "Videos generiert", value: "0" },
          { label: "Aktueller Plan", value: "Free" },
          { label: "Videos diesen Monat", value: "0 / 1" },
        ].map((stat) => (
          <div key={stat.label} className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <p className="text-slate-400 text-sm">{stat.label}</p>
            <p className="text-3xl font-bold text-white mt-2">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* CTA when no projects */}
      <div className="bg-slate-900 border border-slate-800 border-dashed rounded-2xl p-16 text-center">
        <div className="text-6xl mb-4">🎬</div>
        <h2 className="text-xl font-bold text-white mb-2">Noch keine Projekte</h2>
        <p className="text-slate-400 mb-6">Erstelle dein erstes App-Previewvideo in wenigen Minuten.</p>
        <Link
          href="/projects/new"
          className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          <Plus size={18} />
          Erstes Projekt erstellen
        </Link>
      </div>
    </div>
  );
}

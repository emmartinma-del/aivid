"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import Link from "next/link";
import { Plus, FileVideo, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

const STATUS_ICON: Record<string, React.ReactNode> = {
  draft: <FileVideo size={16} className="text-slate-400" />,
  generating: <Loader2 size={16} className="text-yellow-400 animate-spin" />,
  completed: <CheckCircle size={16} className="text-green-400" />,
  failed: <AlertCircle size={16} className="text-red-400" />,
};

const STATUS_LABEL: Record<string, string> = {
  draft: "Entwurf",
  generating: "Wird generiert…",
  completed: "Abgeschlossen",
  failed: "Fehler",
};

export default function ProjectsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: () => api.listProjects(),
  });

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

      {isLoading && (
        <div className="flex items-center gap-3 text-slate-400 py-16 justify-center">
          <Loader2 size={20} className="animate-spin" />
          Lade Projekte…
        </div>
      )}

      {!isLoading && data?.items?.length === 0 && (
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
      )}

      {!isLoading && data?.items && data.items.length > 0 && (
        <div className="grid gap-4">
          {data.items.map((project) => (
            <Link
              key={project.id}
              href={`/projects/${project.id}`}
              className="bg-slate-900 border border-slate-800 hover:border-slate-600 rounded-xl p-5 flex items-center gap-4 transition-colors group"
            >
              <div className="w-10 h-10 bg-indigo-600/20 rounded-lg flex items-center justify-center text-indigo-400 shrink-0">
                <FileVideo size={20} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-semibold truncate group-hover:text-indigo-300 transition-colors">
                  {project.app_name}
                </p>
                <p className="text-slate-400 text-sm truncate mt-0.5">
                  {project.target_store.toUpperCase()} · {project.style_theme} · {project.app_category ?? "App"}
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-400 shrink-0">
                {STATUS_ICON[project.status] ?? STATUS_ICON.draft}
                {STATUS_LABEL[project.status] ?? project.status}
              </div>
              <div className="text-slate-600 text-xs shrink-0">
                {new Date(project.created_at).toLocaleDateString("de-CH")}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

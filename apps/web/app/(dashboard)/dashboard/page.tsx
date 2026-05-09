"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import Link from "next/link";
import { Plus, FileVideo, CheckCircle, Loader2 } from "lucide-react";

const TIER_LABEL: Record<string, string> = {
  free: "Free",
  starter: "Starter",
  pro: "Pro",
  agency: "Agency",
};

const STATUS_LABEL: Record<string, string> = {
  draft: "Entwurf",
  generating: "Wird generiert…",
  completed: "Abgeschlossen",
  failed: "Fehler",
};

export default function DashboardPage() {
  const { data: sub } = useQuery({
    queryKey: ["subscription"],
    queryFn: () => api.getSubscription(),
  });

  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: () => api.listProjects(),
  });

  const completedCount = projects?.items?.filter((p) => p.status === "completed").length ?? 0;

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

      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <p className="text-slate-400 text-sm">Videos generiert</p>
          <p className="text-3xl font-bold text-white mt-2">{completedCount}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <p className="text-slate-400 text-sm">Aktueller Plan</p>
          <p className="text-3xl font-bold text-white mt-2">{sub ? TIER_LABEL[sub.tier] ?? sub.tier : "…"}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <p className="text-slate-400 text-sm">Videos diesen Monat</p>
          <p className="text-3xl font-bold text-white mt-2">
            {sub ? `${sub.videos_used} / ${sub.videos_limit}` : "…"}
          </p>
        </div>
      </div>

      {projects?.items && projects.items.length > 0 ? (
        <div>
          <h2 className="text-lg font-bold text-white mb-4">Letzte Projekte</h2>
          <div className="grid gap-3">
            {projects.items.slice(0, 5).map((project) => (
              <Link
                key={project.id}
                href={`/projects/${project.id}`}
                className="bg-slate-900 border border-slate-800 hover:border-slate-600 rounded-xl p-4 flex items-center gap-4 transition-colors group"
              >
                <div className="w-9 h-9 bg-indigo-600/20 rounded-lg flex items-center justify-center text-indigo-400 shrink-0">
                  {project.status === "completed" ? (
                    <CheckCircle size={18} className="text-green-400" />
                  ) : project.status === "generating" ? (
                    <Loader2 size={18} className="text-yellow-400 animate-spin" />
                  ) : (
                    <FileVideo size={18} />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium truncate group-hover:text-indigo-300 transition-colors">
                    {project.app_name}
                  </p>
                  <p className="text-slate-500 text-xs truncate">
                    {STATUS_LABEL[project.status] ?? project.status}
                  </p>
                </div>
                <p className="text-slate-600 text-xs shrink-0">
                  {new Date(project.created_at).toLocaleDateString("de-CH")}
                </p>
              </Link>
            ))}
          </div>
          {projects.items.length > 5 && (
            <Link href="/projects" className="text-indigo-400 hover:text-indigo-300 text-sm mt-4 inline-block">
              Alle {projects.total} Projekte anzeigen →
            </Link>
          )}
        </div>
      ) : (
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
    </div>
  );
}

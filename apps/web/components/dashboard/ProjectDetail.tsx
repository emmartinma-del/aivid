"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { Download, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { formatDuration, formatBytes } from "@/lib/utils";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const STATUS_BADGE: Record<string, string> = {
  draft: "bg-slate-700 text-slate-300",
  generating: "bg-yellow-500/20 text-yellow-300",
  completed: "bg-green-500/20 text-green-300",
  failed: "bg-red-500/20 text-red-300",
};

export function ProjectDetail({ projectId }: { projectId: string }) {
  const { data: project } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => api.getProject(projectId),
  });

  const { data: videosData } = useQuery({
    queryKey: ["videos", projectId],
    queryFn: () => api.listVideos(projectId),
    enabled: project?.status === "completed",
  });

  if (!project) return <div className="p-8 text-slate-400">Lade…</div>;

  return (
    <div className="p-8 max-w-4xl">
      <Link href="/projects" className="flex items-center gap-2 text-slate-400 hover:text-white mb-6 text-sm">
        <ArrowLeft size={16} /> Zurück zu Projekten
      </Link>

      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">{project.app_name}</h1>
          <p className="text-slate-400 mt-1">{project.app_category}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${STATUS_BADGE[project.status] ?? STATUS_BADGE.draft}`}>
          {project.status}
        </span>
      </div>

      {/* Project info */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: "Store", value: project.target_store.toUpperCase() },
          { label: "Style", value: project.style_theme },
          { label: "Keywords", value: project.keywords?.join(", ") || "—" },
        ].map((item) => (
          <div key={item.label} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <p className="text-slate-400 text-xs mb-1">{item.label}</p>
            <p className="text-white font-medium text-sm">{item.value}</p>
          </div>
        ))}
      </div>

      {/* Videos */}
      {videosData?.items && videosData.items.length > 0 && (
        <div>
          <h2 className="text-lg font-bold text-white mb-4">Generierte Videos</h2>
          <div className="space-y-4">
            {videosData.items.map((video) => (
              <div key={video.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <div className="flex items-center gap-4">
                  {video.cdn_url && (
                    <video
                      src={video.cdn_url}
                      className="w-24 rounded-lg"
                      controls={false}
                      muted
                    />
                  )}
                  <div className="flex-1">
                    <p className="text-white font-medium">
                      {video.target_store.toUpperCase()} · {video.orientation} · {video.resolution}
                    </p>
                    <p className="text-slate-400 text-sm mt-1">
                      {formatDuration(video.duration_seconds)}
                      {video.file_size_bytes && ` · ${formatBytes(video.file_size_bytes)}`}
                      {video.watermarked && " · Wasserzeichen (Free Plan)"}
                    </p>
                    {video.expires_at && (
                      <p className="text-yellow-400 text-xs mt-1">
                        Abläuft: {new Date(video.expires_at).toLocaleDateString("de-CH")}
                      </p>
                    )}
                  </div>
                  <a
                    href={`${API_URL}/api/v1/videos/${video.id}/download`}
                    download
                    className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    <Download size={16} />
                    Download
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

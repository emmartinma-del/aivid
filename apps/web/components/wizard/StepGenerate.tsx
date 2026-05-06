"use client";

import { useState } from "react";
import { api } from "@/lib/api-client";
import { useJobProgress } from "@/lib/ws-client";
import { Sparkles, CheckCircle, XCircle } from "lucide-react";

type Props = {
  projectId: string;
  onBack: () => void;
  onDone: (videoId: string) => void;
};

const STEP_LABELS: Record<string, string> = {
  preflight: "Vorbereitung…",
  script_gen: "KI schreibt Skript…",
  asset_prep: "Assets werden vorbereitet…",
  voiceover: "Voiceover wird generiert…",
  music_fetch: "Hintergrundmusik wird geladen…",
  composition: "Video wird komponiert…",
  quality_check: "Qualitätsprüfung…",
  finalize: "Video wird hochgeladen…",
};

export function StepGenerate({ projectId, onBack, onDone }: Props) {
  const [jobId, setJobId] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [videoId, setVideoId] = useState<string | null>(null);

  const { progress, step, status } = useJobProgress(jobId, {
    onCompleted: (e) => { setVideoId(e.video_id); },
    onFailed: (e) => { setErrorMsg(e.error); },
  });

  async function startGeneration() {
    setGenerating(true);
    setErrorMsg(null);
    try {
      const job = await api.generateVideo(projectId);
      setJobId(job.id);
    } catch (e: any) {
      setErrorMsg(e.message);
      setGenerating(false);
    }
  }

  return (
    <div className="space-y-6 text-center">
      <h2 className="text-xl font-bold text-white">Video generieren</h2>

      {!jobId && !generating && (
        <>
          <p className="text-slate-400">
            KI generiert dein App-Store-Video vollautomatisch:
            Skript, Voiceover, Musik und Videokomposition.
          </p>
          <div className="grid grid-cols-2 gap-3 text-left max-w-sm mx-auto text-sm text-slate-300">
            {["📝 KI-Skript via Claude", "🎙 Professioneller Voiceover", "🎵 Lizenzfreie Musik", "🎬 FFmpeg Videokomposition"].map((item) => (
              <div key={item} className="flex items-center gap-2">{item}</div>
            ))}
          </div>

          <div className="flex justify-between pt-4">
            <button onClick={onBack} className="text-slate-400 hover:text-white px-6 py-3 rounded-lg transition-colors">
              ← Zurück
            </button>
            <button
              onClick={startGeneration}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-3 rounded-lg font-semibold transition-all hover:scale-105"
            >
              <Sparkles size={18} />
              Video generieren
            </button>
          </div>
        </>
      )}

      {(jobId || generating) && status !== "completed" && status !== "failed" && (
        <div className="py-8">
          <div className="w-16 h-16 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin mx-auto mb-6" />
          <p className="text-white font-medium mb-2">
            {step ? STEP_LABELS[step] ?? "Verarbeitung…" : "Starte Pipeline…"}
          </p>
          <p className="text-slate-400 text-sm mb-6">{progress}% abgeschlossen</p>
          <div className="w-full bg-slate-800 rounded-full h-2.5 max-w-sm mx-auto">
            <div
              className="bg-indigo-500 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {status === "completed" && videoId && (
        <div className="py-8">
          <CheckCircle className="mx-auto text-green-400 mb-4" size={64} />
          <h3 className="text-2xl font-bold text-white mb-2">Video fertig! 🎉</h3>
          <p className="text-slate-400 mb-6">Dein App-Store-Video ist bereit zum Download.</p>
          <button
            onClick={() => onDone(videoId)}
            className="bg-green-600 hover:bg-green-500 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
          >
            Video ansehen & herunterladen →
          </button>
        </div>
      )}

      {(status === "failed" || errorMsg) && (
        <div className="py-8">
          <XCircle className="mx-auto text-red-400 mb-4" size={64} />
          <h3 className="text-xl font-bold text-white mb-2">Generierung fehlgeschlagen</h3>
          <p className="text-red-400 text-sm mb-6">{errorMsg}</p>
          <button
            onClick={() => { setJobId(null); setGenerating(false); setErrorMsg(null); }}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-lg font-medium"
          >
            Erneut versuchen
          </button>
        </div>
      )}
    </div>
  );
}

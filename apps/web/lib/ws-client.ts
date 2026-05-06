"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { getSession } from "next-auth/react";

const WS_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
  .replace(/^http/, "ws");

export type JobProgressEvent =
  | { type: "progress"; job_id: string; step: string; progress_pct: number; status: string }
  | { type: "completed"; job_id: string; video_id: string; cdn_url?: string }
  | { type: "failed"; job_id: string; error: string };

interface UseJobProgressOptions {
  onCompleted?: (event: Extract<JobProgressEvent, { type: "completed" }>) => void;
  onFailed?: (event: Extract<JobProgressEvent, { type: "failed" }>) => void;
}

export function useJobProgress(jobId: string | null, options: UseJobProgressOptions = {}) {
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "running" | "completed" | "failed">("idle");
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(async () => {
    if (!jobId) return;
    const session = await getSession();
    const token = (session as any)?.accessToken;
    if (!token) return;

    wsRef.current?.close();
    const ws = new WebSocket(`${WS_URL}/ws/jobs/${jobId}?token=${token}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data: JobProgressEvent = JSON.parse(event.data);
      if (data.type === "progress") {
        setProgress(data.progress_pct);
        setStep(data.step);
        setStatus("running");
      } else if (data.type === "completed") {
        setProgress(100);
        setStatus("completed");
        options.onCompleted?.(data);
        ws.close();
      } else if (data.type === "failed") {
        setStatus("failed");
        options.onFailed?.(data);
        ws.close();
      }
    };

    ws.onerror = () => setStatus("failed");
    setStatus("running");
  }, [jobId]);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return { progress, step, status };
}

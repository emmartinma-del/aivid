"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X, ImageIcon, Video } from "lucide-react";
import { api } from "@/lib/api-client";
import { formatBytes } from "@/lib/utils";

type Props = {
  projectId: string;
  onNext: () => void;
  onBack: () => void;
};

type UploadedFile = {
  id: string;
  name: string;
  size: number;
  assetType: string;
  preview?: string;
  status: "uploading" | "done" | "error";
};

function detectAssetType(file: File): string {
  if (file.type.startsWith("video/")) return "gameplay_clip";
  const name = file.name.toLowerCase();
  if (name.includes("icon") || (file.type === "image/png" && file.size < 200 * 1024)) return "icon";
  return "screenshot_iphone";
}

export function StepAssetUpload({ projectId, onNext, onBack }: Props) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);

  const uploadFile = useCallback(async (file: File) => {
    const assetType = detectAssetType(file);
    const tempId = crypto.randomUUID();

    setFiles((prev) => [...prev, {
      id: tempId, name: file.name, size: file.size,
      assetType, status: "uploading",
      preview: file.type.startsWith("image/") ? URL.createObjectURL(file) : undefined,
    }]);

    try {
      const { upload_url, s3_key, s3_bucket } = await api.getUploadUrl(projectId, {
        filename: file.name,
        mime_type: file.type,
        asset_type: assetType,
        file_size_bytes: file.size,
      });

      await fetch(upload_url, { method: "PUT", body: file, headers: { "Content-Type": file.type } });

      await api.registerAsset(projectId, {
        s3_key, s3_bucket, filename: file.name, mime_type: file.type,
        asset_type: assetType, file_size_bytes: file.size,
      });

      setFiles((prev) => prev.map((f) => f.id === tempId ? { ...f, status: "done" } : f));
    } catch {
      setFiles((prev) => prev.map((f) => f.id === tempId ? { ...f, status: "error" } : f));
    }
  }, [projectId]);

  const onDrop = useCallback((accepted: File[]) => {
    accepted.forEach(uploadFile);
  }, [uploadFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".png", ".jpg", ".jpeg", ".webp"],
      "video/*": [".mp4", ".mov"],
    },
    maxFiles: 8,
  });

  const removeFile = (id: string) =>
    setFiles((prev) => prev.filter((f) => f.id !== id));

  const doneCount = files.filter((f) => f.status === "done").length;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white mb-2">Assets hochladen</h2>
        <p className="text-slate-400 text-sm">
          Screenshots (iPhone/Android), App-Icon und optional ein Gameplay-Clip.
          Mindestens 1 Screenshot erforderlich.
        </p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
          isDragActive ? "border-indigo-500 bg-indigo-500/10" : "border-slate-700 hover:border-slate-500"
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto text-slate-500 mb-4" size={36} />
        <p className="text-slate-300 font-medium mb-1">
          {isDragActive ? "Loslassen zum Hochladen" : "Dateien hierher ziehen oder klicken"}
        </p>
        <p className="text-slate-500 text-sm">PNG, JPG, WebP, MP4, MOV · max. 8 Dateien</p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((f) => (
            <div key={f.id} className="flex items-center gap-3 bg-slate-800 rounded-lg p-3">
              {f.preview ? (
                <img src={f.preview} alt="" className="w-12 h-12 rounded object-cover" />
              ) : (
                <div className="w-12 h-12 bg-slate-700 rounded flex items-center justify-center">
                  <Video size={20} className="text-slate-400" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium truncate">{f.name}</p>
                <p className="text-slate-400 text-xs">{formatBytes(f.size)} · {f.assetType.replace("_", " ")}</p>
              </div>
              <div className="flex items-center gap-2">
                {f.status === "uploading" && (
                  <span className="text-indigo-400 text-xs animate-pulse">Hochladen…</span>
                )}
                {f.status === "done" && <span className="text-green-400 text-xs">✓ Hochgeladen</span>}
                {f.status === "error" && <span className="text-red-400 text-xs">Fehler</span>}
                <button onClick={() => removeFile(f.id)} className="text-slate-500 hover:text-red-400">
                  <X size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex justify-between pt-2">
        <button onClick={onBack} className="text-slate-400 hover:text-white px-6 py-3 rounded-lg transition-colors">
          ← Zurück
        </button>
        <button
          onClick={onNext}
          disabled={doneCount === 0}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-8 py-3 rounded-lg font-medium transition-colors"
        >
          Weiter → ({doneCount} hochgeladen)
        </button>
      </div>
    </div>
  );
}

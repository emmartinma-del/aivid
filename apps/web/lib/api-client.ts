import { getSession } from "next-auth/react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getAuthHeaders(): Promise<Record<string, string>> {
  const session = await getSession();
  const token = (session as any)?.accessToken;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const authHeaders = await getAuthHeaders();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...(init.headers as Record<string, string> | undefined),
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Projects
  createProject: (data: CreateProjectInput) =>
    request<Project>("/api/v1/projects", { method: "POST", body: JSON.stringify(data) }),
  listProjects: (page = 1) =>
    request<ProjectList>(`/api/v1/projects?page=${page}`),
  getProject: (id: string) =>
    request<Project>(`/api/v1/projects/${id}`),
  updateProject: (id: string, data: Partial<CreateProjectInput>) =>
    request<Project>(`/api/v1/projects/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteProject: (id: string) =>
    request<void>(`/api/v1/projects/${id}`, { method: "DELETE" }),
  generateVideo: (id: string) =>
    request<Job>(`/api/v1/projects/${id}/generate`, { method: "POST" }),

  // Assets
  getUploadUrl: (projectId: string, data: UploadUrlInput) =>
    request<UploadUrl>(`/api/v1/projects/${projectId}/assets/upload-url`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  registerAsset: (projectId: string, data: RegisterAssetInput) =>
    request<Asset>(`/api/v1/projects/${projectId}/assets`, { method: "POST", body: JSON.stringify(data) }),
  listAssets: (projectId: string) =>
    request<Asset[]>(`/api/v1/projects/${projectId}/assets`),
  deleteAsset: (projectId: string, assetId: string) =>
    request<void>(`/api/v1/projects/${projectId}/assets/${assetId}`, { method: "DELETE" }),

  // Jobs
  getJob: (jobId: string) => request<Job>(`/api/v1/jobs/${jobId}`),

  // Videos
  listVideos: (projectId: string) =>
    request<VideoList>(`/api/v1/projects/${projectId}/videos`),
  getVideo: (videoId: string) => request<Video>(`/api/v1/videos/${videoId}`),

  // Subscription
  getSubscription: () => request<Subscription>("/api/v1/subscriptions/me"),
};

// Types
export interface CreateProjectInput {
  name: string;
  app_name: string;
  app_description?: string;
  keywords?: string[];
  app_category?: string;
  target_store: "ios" | "android" | "both";
  style_theme: "modern" | "gaming" | "corporate" | "fun";
}

export interface Project {
  id: string;
  name: string;
  app_name: string;
  app_description?: string;
  keywords?: string[];
  app_category?: string;
  target_store: string;
  style_theme: string;
  status: string;
  organization_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectList {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
}

export interface UploadUrlInput {
  filename: string;
  mime_type: string;
  asset_type: string;
  file_size_bytes?: number;
}

export interface UploadUrl {
  upload_url: string;
  s3_key: string;
  s3_bucket: string;
  expires_in: number;
}

export interface RegisterAssetInput {
  s3_key: string;
  s3_bucket: string;
  filename: string;
  mime_type: string;
  asset_type: string;
  device_type?: string;
  file_size_bytes?: number;
  width_px?: number;
  height_px?: number;
  sort_order?: number;
}

export interface Asset {
  id: string;
  project_id: string;
  asset_type: string;
  device_type?: string;
  filename: string;
  mime_type: string;
  file_size_bytes?: number;
  width_px?: number;
  height_px?: number;
  sort_order: number;
  url?: string;
  created_at: string;
}

export interface Job {
  id: string;
  project_id: string;
  status: string;
  current_step?: string;
  progress_pct: number;
  error_message?: string;
  retry_count: number;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface Video {
  id: string;
  project_id: string;
  job_id: string;
  target_store: string;
  orientation: string;
  resolution: string;
  duration_seconds: number;
  file_size_bytes?: number;
  cdn_url?: string;
  watermarked: boolean;
  expires_at?: string;
  created_at: string;
}

export interface VideoList {
  items: Video[];
}

export interface Subscription {
  tier: string;
  status: string;
  videos_used: number;
  videos_limit: number;
  period_end?: string;
}

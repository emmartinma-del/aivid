"use client";

import { useState } from "react";
import type { CreateProjectInput } from "@/lib/api-client";

type Props = {
  initialValues: Partial<CreateProjectInput>;
  onSubmit: (data: Pick<CreateProjectInput, "name" | "app_name" | "app_description" | "keywords" | "app_category">) => Promise<void>;
};

const CATEGORIES = ["Games", "Productivity", "Social", "Health & Fitness", "Education", "Finance", "Photo & Video", "Music", "Travel", "Food & Drink", "Shopping", "Utilities"];

export function StepAppInfo({ initialValues, onSubmit }: Props) {
  const [form, setForm] = useState({
    name: initialValues.name ?? "",
    app_name: initialValues.app_name ?? "",
    app_description: initialValues.app_description ?? "",
    keywords: initialValues.keywords?.join(", ") ?? "",
    app_category: initialValues.app_category ?? "",
  });
  const [loading, setLoading] = useState(false);

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    await onSubmit({
      name: form.name || form.app_name,
      app_name: form.app_name,
      app_description: form.app_description || undefined,
      keywords: form.keywords ? form.keywords.split(",").map((k) => k.trim()).filter(Boolean) : undefined,
      app_category: form.app_category || undefined,
    });
    setLoading(false);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h2 className="text-xl font-bold text-white mb-6">App-Informationen</h2>

      <div>
        <label className="text-sm font-medium text-slate-300 block mb-1.5">App-Name *</label>
        <input
          type="text"
          value={form.app_name}
          onChange={set("app_name")}
          placeholder="z.B. MyFitness Pro"
          className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label className="text-sm font-medium text-slate-300 block mb-1.5">Kategorie</label>
        <select
          value={form.app_category}
          onChange={set("app_category")}
          className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">Kategorie wählen…</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      <div>
        <label className="text-sm font-medium text-slate-300 block mb-1.5">Beschreibung</label>
        <textarea
          value={form.app_description}
          onChange={set("app_description")}
          placeholder="Was macht deine App einzigartig? Was sind die Hauptfeatures?"
          rows={4}
          className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
        />
      </div>

      <div>
        <label className="text-sm font-medium text-slate-300 block mb-1.5">Keywords (kommagetrennt)</label>
        <input
          type="text"
          value={form.keywords}
          onChange={set("keywords")}
          placeholder="z.B. fitness, workout, gesundheit, training"
          className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <div className="flex justify-end pt-2">
        <button
          type="submit"
          disabled={loading || !form.app_name}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-8 py-3 rounded-lg font-medium transition-colors"
        >
          {loading ? "Speichern…" : "Weiter →"}
        </button>
      </div>
    </form>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, type CreateProjectInput } from "@/lib/api-client";
import { StepAppInfo } from "./StepAppInfo";
import { StepAssetUpload } from "./StepAssetUpload";
import { StepStyleSelect } from "./StepStyleSelect";
import { StepStoreSelect } from "./StepStoreSelect";
import { StepGenerate } from "./StepGenerate";

const STEPS = ["App-Infos", "Assets", "Style", "Store", "Generieren"];

export function ProjectWizard() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [form, setForm] = useState<Partial<CreateProjectInput>>({
    target_store: "ios",
    style_theme: "modern",
  });

  const next = () => setStep((s) => Math.min(s + 1, STEPS.length - 1));
  const back = () => setStep((s) => Math.max(s - 1, 0));

  async function handleAppInfoSubmit(data: Pick<CreateProjectInput, "name" | "app_name" | "app_description" | "keywords" | "app_category">) {
    const merged = { ...form, ...data } as CreateProjectInput;
    setForm(merged);

    if (!projectId) {
      const project = await api.createProject(merged);
      setProjectId(project.id);
    } else {
      await api.updateProject(projectId, data);
    }
    next();
  }

  return (
    <div>
      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-10">
        {STEPS.map((label, idx) => (
          <div key={label} className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                idx < step
                  ? "bg-indigo-600 text-white"
                  : idx === step
                  ? "bg-indigo-500 text-white ring-4 ring-indigo-500/30"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              {idx < step ? "✓" : idx + 1}
            </div>
            <span className={`text-sm font-medium hidden sm:block ${idx === step ? "text-white" : "text-slate-500"}`}>
              {label}
            </span>
            {idx < STEPS.length - 1 && <div className="w-8 h-0.5 bg-slate-800 mx-1" />}
          </div>
        ))}
      </div>

      {/* Step content */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
        {step === 0 && (
          <StepAppInfo initialValues={form} onSubmit={handleAppInfoSubmit} />
        )}
        {step === 1 && projectId && (
          <StepAssetUpload projectId={projectId} onNext={next} onBack={back} />
        )}
        {step === 2 && (
          <StepStyleSelect
            value={form.style_theme ?? "modern"}
            onChange={(v) => setForm((f) => ({ ...f, style_theme: v }))}
            onNext={next}
            onBack={back}
          />
        )}
        {step === 3 && (
          <StepStoreSelect
            value={form.target_store ?? "ios"}
            onChange={(v) => setForm((f) => ({ ...f, target_store: v }))}
            onNext={next}
            onBack={back}
          />
        )}
        {step === 4 && projectId && (
          <StepGenerate
            projectId={projectId}
            onBack={back}
            onDone={(videoId) => router.push(`/projects/${projectId}`)}
          />
        )}
      </div>
    </div>
  );
}

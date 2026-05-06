import { ProjectWizard } from "@/components/wizard/ProjectWizard";

export default function NewProjectPage() {
  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-2xl font-bold text-white mb-2">Neues Projekt</h1>
      <p className="text-slate-400 mb-8">Erstelle dein App-Store-Previewvideo in 5 Schritten.</p>
      <ProjectWizard />
    </div>
  );
}

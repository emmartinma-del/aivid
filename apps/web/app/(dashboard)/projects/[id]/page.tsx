import { ProjectDetail } from "@/components/dashboard/ProjectDetail";

export default function ProjectPage({ params }: { params: { id: string } }) {
  return <ProjectDetail projectId={params.id} />;
}

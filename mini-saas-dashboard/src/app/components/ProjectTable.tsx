// src/app/components/ProjectTable.tsx

import type { Project } from "@/app/types/project";

interface ProjectTableProps {
  projects: Project[];
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  onEdit: (project: Project) => void;
  onDelete: (project: Project) => void;
}

export function ProjectTable({
  projects,
  loading,
  error,
  onRetry,
  onEdit,
  onDelete,
}: ProjectTableProps) {
  if (loading) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4 backdrop-blur">
        <div className="flex h-32 items-center justify-center text-sm text-slate-300">
          Loading projects...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4 backdrop-blur">
        <div className="flex h-32 flex-col items-center justify-center gap-2 text-center text-sm">
          <p className="text-red-400">{error}</p>
          <button
            onClick={onRetry}
            className="text-xs font-medium text-indigo-400 hover:text-indigo-300 underline-offset-2 hover:underline"
          >
            Retry
          </button>
        </div>
      </section>
    );
  }

  if (projects.length === 0) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4 backdrop-blur">
        <div className="flex h-32 flex-col items-center justify-center gap-2 text-center text-sm text-slate-300">
          <p>No projects found.</p>
          <p className="text-xs text-slate-400">
            Try adjusting filters or create a new project.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4 backdrop-blur">
      <div className="overflow-x-auto">
        <table className="min-w-full table-auto text-left text-sm">
          <thead>
            <tr className="border-b border-slate-800 text-xs uppercase tracking-wide text-slate-400">
              <th className="px-3 py-2">Name</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Deadline</th>
              <th className="px-3 py-2">Assignee</th>
              <th className="px-3 py-2">Budget</th>
              <th className="px-3 py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr
                key={project.id}
                className="border-b border-slate-800/60 last:border-none hover:bg-slate-900/70"
              >
                <td className="px-3 py-2">
                  <div className="flex flex-col">
                    <span className="font-medium text-slate-100">
                      {project.name}
                    </span>
                    <span className="text-xs text-slate-400">
                      ID: {project.id.slice(0, 8)}…
                    </span>
                  </div>
                </td>
                <td className="px-3 py-2">
                  <span
                    className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
                      project.status === "ACTIVE"
                        ? "bg-emerald-500/15 text-emerald-300"
                        : project.status === "ON_HOLD"
                        ? "bg-amber-500/15 text-amber-300"
                        : "bg-slate-500/20 text-slate-200"
                    }`}
                  >
                    {project.status === "ACTIVE"
                      ? "Active"
                      : project.status === "ON_HOLD"
                      ? "On hold"
                      : "Completed"}
                  </span>
                </td>
                <td className="px-3 py-2 text-slate-200">
                  {new Date(project.deadline).toLocaleDateString()}
                </td>
                <td className="px-3 py-2 text-slate-200">
                  {project.assignedTo}
                </td>
                <td className="px-3 py-2 text-slate-200">
                  ${project.budget.toLocaleString()}
                </td>
                <td className="px-3 py-2 text-right">
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => onEdit(project)}
                      className="rounded-lg border border-slate-700 px-2.5 py-1 text-xs font-medium text-slate-100 hover:bg-slate-800"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => onDelete(project)}
                      className="rounded-lg bg-red-500/80 px-2.5 py-1 text-xs font-medium text-white hover:bg-red-500"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

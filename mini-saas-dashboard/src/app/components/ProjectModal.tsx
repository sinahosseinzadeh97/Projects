// src/app/components/ProjectModal.tsx

import type {
  ModalMode,
  ProjectFormState,
  ProjectStatus,
} from "@/app/types/project";
import type { FormEvent } from "react";

interface ProjectModalProps {
  isOpen: boolean;
  mode: ModalMode;
  formState: ProjectFormState;
  formError: string | null;
  saving: boolean;
  onClose: () => void;
  onChange: (field: keyof ProjectFormState, value: string | ProjectStatus) => void;
  onSubmit: (event: FormEvent) => void;
}

export function ProjectModal({
  isOpen,
  mode,
  formState,
  formError,
  saving,
  onClose,
  onChange,
  onSubmit,
}: ProjectModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 backdrop-blur">
      <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-2xl">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-50">
              {mode === "create" ? "Create new project" : "Edit project"}
            </h2>
            <p className="mt-1 text-xs text-slate-400">
              Fill in the details below and save your changes.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-1 text-slate-400 hover:bg-slate-800 hover:text-slate-100"
            disabled={saving}
          >
            ✕
          </button>
        </div>

        {formError && (
          <div className="mb-3 rounded-xl border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-200">
            {formError}
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-3">
          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-200">
              Project name
            </label>
            <input
              type="text"
              value={formState.name}
              onChange={(e) => onChange("name", e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="CRM Dashboard, Billing service..."
            />
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-200">
                Status
              </label>
              <select
                value={formState.status}
                onChange={(e) =>
                  onChange("status", e.target.value as ProjectStatus)
                }
                className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="ACTIVE">Active</option>
                <option value="ON_HOLD">On hold</option>
                <option value="COMPLETED">Completed</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-200">
                Deadline
              </label>
              <input
                type="date"
                value={formState.deadline}
                onChange={(e) => onChange("deadline", e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-200">
                Assigned to
              </label>
              <input
                type="text"
                value={formState.assignedTo}
                onChange={(e) => onChange("assignedTo", e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Ali, Sara..."
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-200">
                Budget (USD)
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={formState.budget}
                onChange={(e) => onChange("budget", e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="mt-4 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800"
              disabled={saving}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-xl bg-indigo-500 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-indigo-500/40 transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={saving}
            >
              {saving
                ? mode === "create"
                  ? "Creating..."
                  : "Saving..."
                : mode === "create"
                ? "Create project"
                : "Save changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

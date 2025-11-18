// src/app/components/ProjectFilters.tsx

import type { ProjectStatus } from "@/app/types/project";

interface ProjectFiltersProps {
  statusFilter: "ALL" | ProjectStatus;
  onStatusFilterChange: (status: "ALL" | ProjectStatus) => void;
  searchQuery: string;
  onSearchQueryChange: (value: string) => void;
}

export function ProjectFilters({
  statusFilter,
  onStatusFilterChange,
  searchQuery,
  onSearchQueryChange,
}: ProjectFiltersProps) {
  return (
    <section className="flex flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-900/40 p-4 backdrop-blur">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        {/* Status filter */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Status
          </span>
          <div className="flex flex-wrap gap-2">
            {["ALL", "ACTIVE", "ON_HOLD", "COMPLETED"].map((status) => (
              <button
                key={status}
                type="button"
                onClick={() =>
                  onStatusFilterChange(status as "ALL" | ProjectStatus)
                }
                className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                  statusFilter === status
                    ? "bg-indigo-500 text-white"
                    : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                }`}
              >
                {status === "ALL"
                  ? "All"
                  : status === "ACTIVE"
                  ? "Active"
                  : status === "ON_HOLD"
                  ? "On hold"
                  : "Completed"}
              </button>
            ))}
          </div>
        </div>

        {/* Search */}
        <div className="flex w-full items-center gap-2 sm:w-auto">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchQueryChange(e.target.value)}
            placeholder="Search by name or assignee..."
            className="w-full rounded-xl border border-slate-700 bg-slate-900/70 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:w-64"
          />
        </div>
      </div>
    </section>
  );
}

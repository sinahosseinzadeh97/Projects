// src/app/dashboard/page.tsx
"use client";

import { useEffect, useMemo, useState, FormEvent } from "react";
import type {
  ModalMode,
  Project,
  ProjectFormState,
  ProjectStatus,
} from "../types/project";
import { ProjectFilters } from "../components/ProjectFilters";
import { ProjectTable } from "../components/ProjectTable";
import { ProjectModal } from "../components/ProjectModal";
import { SignedIn, SignedOut, RedirectToSignIn } from "@clerk/nextjs";

export default function DashboardPage() {
  return (
    <>
      <SignedIn>
        <DashboardContent />
      </SignedIn>

      <SignedOut>
        <RedirectToSignIn redirectUrl="/dashboard" />
      </SignedOut>
    </>
  );
}

function DashboardContent() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [statusFilter, setStatusFilter] = useState<"ALL" | ProjectStatus>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);

  const [formState, setFormState] = useState<ProjectFormState>({
    name: "",
    status: "ACTIVE",
    deadline: "",
    assignedTo: "",
    budget: "",
  });

  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  // Fetch all projects from the API
  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);

      const res = await fetch("/api/projects");
      if (!res.ok) {
        throw new Error("Failed to fetch projects");
      }

      const data = await res.json();
      setProjects(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load projects. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  // Client-side filtering & search
  const filteredProjects = useMemo(() => {
    return projects
      .filter((project) => {
        if (statusFilter === "ALL") return true;
        return project.status === statusFilter;
      })
      .filter((project) => {
        if (!searchQuery.trim()) return true;
        const q = searchQuery.toLowerCase();
        return (
          project.name.toLowerCase().includes(q) ||
          project.assignedTo.toLowerCase().includes(q)
        );
      });
  }, [projects, statusFilter, searchQuery]);

  // Modal handlers
  const openCreateModal = () => {
    setModalMode("create");
    setActiveProjectId(null);
    setFormError(null);
    setFormState({
      name: "",
      status: "ACTIVE",
      deadline: "",
      assignedTo: "",
      budget: "",
    });
    setIsModalOpen(true);
  };

  const openEditModal = (project: Project) => {
    setModalMode("edit");
    setActiveProjectId(project.id);
    setFormError(null);

    const deadlineDate = new Date(project.deadline);
    const deadlineValue = isNaN(deadlineDate.getTime())
      ? ""
      : deadlineDate.toISOString().slice(0, 10);

    setFormState({
      name: project.name,
      status: project.status,
      deadline: deadlineValue,
      assignedTo: project.assignedTo,
      budget: String(project.budget ?? ""),
    });

    setIsModalOpen(true);
  };

  const closeModal = () => {
    if (saving) return;
    setIsModalOpen(false);
  };

  // Form state change
  const handleFormChange = (
    field: keyof ProjectFormState,
    value: string | ProjectStatus
  ) => {
    setFormState((prev) => ({
      ...prev,
      [field]: value as string,
    }));
  };

  // Basic client-side validation
  const validateForm = (): boolean => {
    if (!formState.name.trim()) {
      setFormError("Project name is required.");
      return false;
    }
    if (!formState.deadline) {
      setFormError("Deadline is required.");
      return false;
    }
    if (!formState.assignedTo.trim()) {
      setFormError("Assigned team member is required.");
      return false;
    }
    if (!formState.budget.trim() || isNaN(Number(formState.budget))) {
      setFormError("Budget must be a valid number.");
      return false;
    }

    setFormError(null);
    return true;
  };

  // Create or update project
  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();

    if (!validateForm()) return;

    try {
      setSaving(true);

      const payload = {
        name: formState.name.trim(),
        status: formState.status,
        deadline: formState.deadline,
        assignedTo: formState.assignedTo.trim(),
        budget: Number(formState.budget),
      };

      let res: Response;

      if (modalMode === "create") {
        res = await fetch("/api/projects", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });
      } else {
        if (!activeProjectId) {
          setFormError("No project selected for editing.");
          return;
        }
        res = await fetch(`/api/projects/${activeProjectId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });
      }

      if (!res.ok) {
        const errorBody = await res.json().catch(() => null);
        const message =
          errorBody?.message || "Failed to save project. Please try again.";
        setFormError(message);
        return;
      }

      await fetchProjects();
      setIsModalOpen(false);
    } catch (err) {
      console.error(err);
      setFormError("Unexpected error occurred. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  // Delete project
  const handleDelete = async (project: Project) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete project "${project.name}"?`
    );
    if (!confirmed) return;

    try {
      const res = await fetch(`/api/projects/${project.id}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const body = await res.json().catch(() => null);
        const message =
          body?.message || "Failed to delete project. Please try again.";
        alert(message);
        return;
      }

      setProjects((prev) => prev.filter((p) => p.id !== project.id));
    } catch (err) {
      console.error(err);
      alert("Unexpected error occurred while deleting project.");
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8">
        {/* Header */}
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Mini SaaS Projects Dashboard
            </h1>
            <p className="mt-1 text-sm text-slate-300">
              Manage project status, deadlines, owners, and budgets in one
              place.
            </p>
          </div>

          <button
            onClick={openCreateModal}
            className="inline-flex items-center justify-center rounded-xl bg-indigo-500 px-4 py-2 text-sm font-medium shadow-md shadow-indigo-500/30 transition hover:bg-indigo-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"
          >
            + New Project
          </button>
        </header>

        {/* Filters */}
        <ProjectFilters
          statusFilter={statusFilter}
          onStatusFilterChange={setStatusFilter}
          searchQuery={searchQuery}
          onSearchQueryChange={setSearchQuery}
        />

        {/* Table */}
        <ProjectTable
          projects={filteredProjects}
          loading={loading}
          error={error}
          onRetry={fetchProjects}
          onEdit={openEditModal}
          onDelete={handleDelete}
        />

        {/* Modal */}
        <ProjectModal
          isOpen={isModalOpen}
          mode={modalMode}
          formState={formState}
          formError={formError}
          saving={saving}
          onClose={closeModal}
          onChange={handleFormChange}
          onSubmit={handleSubmit}
        />
      </div>
    </main>
  );
}

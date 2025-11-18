// src/app/types/project.ts

// Union type for supported project statuses
export type ProjectStatus = "ACTIVE" | "ON_HOLD" | "COMPLETED";

// Entity returned from the backend
export interface Project {
  id: string;
  name: string;
  status: ProjectStatus;
  deadline: string; // ISO string from the backend
  assignedTo: string;
  budget: number;
  createdAt: string;
  updatedAt: string;
}

// Local state shape for the project form in the modal
export interface ProjectFormState {
  name: string;
  status: ProjectStatus;
  deadline: string; // yyyy-mm-dd (for <input type="date" />)
  assignedTo: string;
  budget: string; // kept as string in the form, converted to number on submit
}

// Modal mode (create vs edit)
export type ModalMode = "create" | "edit";

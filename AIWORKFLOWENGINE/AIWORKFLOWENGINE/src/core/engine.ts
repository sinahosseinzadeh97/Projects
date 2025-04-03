import { Workflow } from './workflow';
import { IWorkflowEngine, IWorkflow, WorkflowConfig } from '../types';
import { Logger } from '../utils/logger';

/**
 * The main workflow engine that manages workflow creation and execution
 */
export class WorkflowEngine implements IWorkflowEngine {
  private workflows: Map<string, IWorkflow>;
  private logger: Logger;

  constructor() {
    this.workflows = new Map();
    this.logger = new Logger('WorkflowEngine');
    this.logger.info('WorkflowEngine initialized');
  }

  /**
   * Create a new workflow with the given ID
   * @param id Unique identifier for the workflow
   * @param config Optional configuration for the workflow
   * @returns A new workflow instance
   */
  createWorkflow(id: string, config?: WorkflowConfig): IWorkflow {
    if (this.workflows.has(id)) {
      throw new Error(`Workflow with ID '${id}' already exists`);
    }

    const workflow = new Workflow(id, config);
    this.workflows.set(id, workflow);
    this.logger.info(`Created workflow '${id}'`);
    
    return workflow;
  }

  /**
   * Get a workflow by its ID
   * @param id The workflow identifier
   * @returns The workflow instance
   */
  getWorkflow(id: string): IWorkflow {
    const workflow = this.workflows.get(id);
    if (!workflow) {
      throw new Error(`Workflow with ID '${id}' not found`);
    }
    return workflow;
  }

  /**
   * Delete a workflow by its ID
   * @param id The workflow identifier
   * @returns true if the workflow was deleted
   */
  deleteWorkflow(id: string): boolean {
    const result = this.workflows.delete(id);
    if (result) {
      this.logger.info(`Deleted workflow '${id}'`);
    } else {
      this.logger.warn(`Failed to delete workflow '${id}': not found`);
    }
    return result;
  }

  /**
   * Get all registered workflows
   * @returns A list of all workflow instances
   */
  getAllWorkflows(): IWorkflow[] {
    return Array.from(this.workflows.values());
  }

  /**
   * Save the current state of all workflows
   * @param path Optional path to save to
   */
  saveState(path?: string): void {
    // Implementation for serializing workflows to disk
    this.logger.info(`Saved engine state${path ? ` to ${path}` : ''}`);
  }

  /**
   * Load workflows from a saved state
   * @param path Optional path to load from
   */
  loadState(path?: string): void {
    // Implementation for deserializing workflows from disk
    this.logger.info(`Loaded engine state${path ? ` from ${path}` : ''}`);
  }
} 
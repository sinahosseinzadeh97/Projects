import { IAgent } from './agent';

/**
 * Configuration options for a workflow
 */
export interface WorkflowConfig {
  /**
   * Maximum number of steps allowed in this workflow
   */
  maxSteps?: number;
  
  /**
   * Whether to automatically validate the workflow before execution
   */
  autoValidate?: boolean;
  
  /**
   * Custom metadata for this workflow
   */
  metadata?: Record<string, any>;
}

/**
 * Status of a workflow step execution
 */
export type WorkflowStepStatus = 'pending' | 'running' | 'success' | 'error';

/**
 * Result of a workflow step execution
 */
export interface WorkflowStepResult {
  /**
   * The output data from the step
   */
  output: any;
  
  /**
   * When the step started executing
   */
  startTime: Date;
  
  /**
   * When the step finished executing
   */
  endTime: Date;
  
  /**
   * The execution status of the step
   */
  status: WorkflowStepStatus;
  
  /**
   * Any error that occurred during execution
   */
  error?: Error;
}

/**
 * Context for workflow execution
 */
export interface WorkflowExecutionContext {
  /**
   * The ID of the workflow being executed
   */
  workflowId: string;
  
  /**
   * The input data provided to the workflow
   */
  input: any;
  
  /**
   * Results of each step that has been executed
   */
  stepResults: Record<string, WorkflowStepResult>;
  
  /**
   * When the workflow execution started
   */
  startTime: Date;
  
  /**
   * When the workflow execution completed
   */
  endTime?: Date;
  
  /**
   * Any error that occurred during workflow execution
   */
  error?: Error;
}

/**
 * A step in a workflow
 */
export interface WorkflowStep {
  /**
   * Unique identifier for this step
   */
  id: string;
  
  /**
   * The agent that will execute this step
   */
  agent: IAgent;
  
  /**
   * Input data for this step
   * 
   * Can include:
   * - Direct values
   * - References to workflow input: "workflow.input.someProperty"
   * - References to previous step outputs: "workflow.steps.stepId.output.someProperty"
   */
  input?: Record<string, any>;
  
  /**
   * Custom metadata for this step
   */
  metadata?: Record<string, any>;
}

/**
 * Interface for a workflow
 */
export interface IWorkflow {
  /**
   * The unique identifier of this workflow
   */
  readonly id: string;
  
  /**
   * Add a step to this workflow
   */
  addStep(step: WorkflowStep): IWorkflow;
  
  /**
   * Execute this workflow with the provided input
   */
  execute(input: any): Promise<any>;
  
  /**
   * Get a step by its ID
   */
  getStep(id: string): WorkflowStep | undefined;
  
  /**
   * Get all steps in this workflow
   */
  getSteps(): WorkflowStep[];
  
  /**
   * Remove a step by its ID
   */
  removeStep(id: string): boolean;
}

/**
 * Interface for the workflow engine
 */
export interface IWorkflowEngine {
  /**
   * Create a new workflow with the given ID
   */
  createWorkflow(id: string, config?: WorkflowConfig): IWorkflow;
  
  /**
   * Get a workflow by its ID
   */
  getWorkflow(id: string): IWorkflow;
  
  /**
   * Delete a workflow by its ID
   */
  deleteWorkflow(id: string): boolean;
  
  /**
   * Get all registered workflows
   */
  getAllWorkflows(): IWorkflow[];
  
  /**
   * Save the current state of all workflows
   */
  saveState(path?: string): void;
  
  /**
   * Load workflows from a saved state
   */
  loadState(path?: string): void;
} 
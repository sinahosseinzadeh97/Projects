import { IWorkflow, WorkflowConfig, WorkflowStep, WorkflowStepResult, WorkflowExecutionContext } from '../types';
import { Logger } from '../utils/logger';
import { WorkflowError } from '../utils/errors';

/**
 * Represents a sequence of steps that can be executed to process data
 */
export class Workflow implements IWorkflow {
  private steps: WorkflowStep[] = [];
  private logger: Logger;
  
  /**
   * The unique identifier of this workflow
   */
  public readonly id: string;

  /**
   * Creates a new workflow
   * @param id Unique identifier for this workflow
   * @param config Optional workflow configuration
   */
  constructor(id: string, private config?: WorkflowConfig) {
    this.id = id;
    this.logger = new Logger(`Workflow[${id}]`);
    this.logger.info('Workflow created');
  }

  /**
   * Add a step to this workflow
   * @param step The step configuration to add
   * @returns This workflow, for chaining
   */
  addStep(step: WorkflowStep): IWorkflow {
    // Validate the step
    if (!step.id) {
      throw new WorkflowError('Step must have an id', 'INVALID_STEP');
    }
    
    if (!step.agent) {
      throw new WorkflowError('Step must have an agent', 'INVALID_STEP');
    }

    // Check for duplicate step IDs
    const existingStep = this.steps.find(s => s.id === step.id);
    if (existingStep) {
      throw new WorkflowError(`Step with ID '${step.id}' already exists in this workflow`, 'DUPLICATE_STEP');
    }

    this.steps.push(step);
    this.logger.info(`Added step '${step.id}' to workflow`);
    
    return this;
  }

  /**
   * Execute this workflow with the provided input
   * @param input The input data for the workflow
   * @returns The result of the workflow execution
   */
  async execute(input: any): Promise<any> {
    if (this.steps.length === 0) {
      throw new WorkflowError('Cannot execute workflow with no steps', 'EMPTY_WORKFLOW');
    }

    this.logger.info(`Executing workflow with ${this.steps.length} steps`);
    
    // Create execution context
    const context: WorkflowExecutionContext = {
      workflowId: this.id,
      input,
      stepResults: {},
      startTime: new Date(),
      endTime: undefined
    };

    let finalResult = null;

    try {
      // Execute steps in sequence
      for (const step of this.steps) {
        this.logger.info(`Executing step '${step.id}'`);
        
        // Process input for this step (resolving references to previous steps)
        const stepInput = this.resolveStepInput(step, context);
        
        // Execute the step
        const stepResult = await step.agent.execute(stepInput);
        
        // Store the result in the context
        const stepResultWithMeta: WorkflowStepResult = {
          output: stepResult,
          startTime: new Date(), // Should be captured at start of execution
          endTime: new Date(),
          status: 'success'
        };
        
        context.stepResults[step.id] = stepResultWithMeta;
        finalResult = stepResult;
        
        this.logger.info(`Completed step '${step.id}'`);
      }

      context.endTime = new Date();
      this.logger.info(`Workflow execution completed successfully`);
      
      return finalResult;
    } catch (error) {
      context.endTime = new Date();
      context.error = error;
      
      this.logger.error(`Workflow execution failed: ${error.message}`);
      throw new WorkflowError(`Workflow execution failed: ${error.message}`, 'EXECUTION_ERROR', error);
    }
  }

  /**
   * Process input for a step, resolving references to workflow input or previous step outputs
   * @param step The step to process input for
   * @param context The execution context
   * @returns The processed input for the step
   */
  private resolveStepInput(step: WorkflowStep, context: WorkflowExecutionContext): any {
    if (!step.input) {
      return {};
    }

    const resolvedInput: any = {};

    for (const [key, value] of Object.entries(step.input)) {
      if (typeof value === 'string' && value.startsWith('workflow.')) {
        // This is a reference to a workflow value
        const path = value.split('.');
        
        if (path[1] === 'input') {
          // Reference to workflow input
          resolvedInput[key] = this.getNestedValue(context.input, path.slice(2));
        } else if (path[1] === 'steps') {
          // Reference to a previous step's output
          const stepId = path[2];
          const stepResult = context.stepResults[stepId];
          
          if (!stepResult) {
            throw new WorkflowError(`Referenced step '${stepId}' not found or has not been executed`, 'INVALID_REFERENCE');
          }
          
          resolvedInput[key] = this.getNestedValue(stepResult.output, path.slice(3));
        } else {
          throw new WorkflowError(`Invalid reference: ${value}`, 'INVALID_REFERENCE');
        }
      } else {
        // Direct value
        resolvedInput[key] = value;
      }
    }

    return resolvedInput;
  }

  /**
   * Get a nested value from an object using a path array
   * @param obj The object to get the value from
   * @param path The path to the value
   * @returns The value at the path, or undefined if not found
   */
  private getNestedValue(obj: any, path: string[]): any {
    let current = obj;
    
    for (const key of path) {
      if (current === undefined || current === null) {
        return undefined;
      }
      
      current = current[key];
    }
    
    return current;
  }

  /**
   * Get a step by its ID
   * @param id The step ID
   * @returns The step, or undefined if not found
   */
  getStep(id: string): WorkflowStep | undefined {
    return this.steps.find(step => step.id === id);
  }

  /**
   * Get all steps in this workflow
   * @returns Array of workflow steps
   */
  getSteps(): WorkflowStep[] {
    return [...this.steps];
  }

  /**
   * Remove a step by its ID
   * @param id The step ID to remove
   * @returns true if the step was removed
   */
  removeStep(id: string): boolean {
    const initialLength = this.steps.length;
    this.steps = this.steps.filter(step => step.id !== id);
    const removed = this.steps.length < initialLength;
    
    if (removed) {
      this.logger.info(`Removed step '${id}' from workflow`);
    }
    
    return removed;
  }
} 
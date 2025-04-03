/**
 * Configuration for an agent
 */
export interface AgentConfig {
  /**
   * Unique name for the agent
   */
  name: string;
  
  /**
   * Optional description of what the agent does
   */
  description?: string;
  
  /**
   * Custom configuration options for this agent
   */
  options?: Record<string, any>;
}

/**
 * Interface for an agent that can perform tasks in a workflow
 */
export interface IAgent {
  /**
   * Unique name for this agent
   */
  readonly name: string;
  
  /**
   * Execute the agent's task with the given input
   * @param input The input data for the agent
   * @returns The result of the agent's execution
   */
  execute(input: any): Promise<any>;
  
  /**
   * Get configuration information about this agent
   * @returns The agent's configuration
   */
  getConfig(): AgentConfig;
} 
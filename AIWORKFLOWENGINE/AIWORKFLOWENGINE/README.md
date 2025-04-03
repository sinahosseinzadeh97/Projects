# AI Workflow Engine

A flexible and powerful TypeScript-based engine for creating, managing, and executing AI workflows. This engine allows you to orchestrate complex AI-driven processes by connecting different components into cohesive workflows.

## Features

- **Modular Architecture**: Create reusable components that can be connected in various ways
- **Multiple AI Integrations**: Built-in support for various AI providers (OpenAI, etc.)
- **Workflow Management**: Define, save, load, and execute workflows
- **Extensible**: Easy to add new components, connectors, and integrations
- **Typed Interfaces**: Strong typing for reliable workflow creation
- **Error Handling**: Robust error management for AI operations
- **Observability**: Built-in logging and monitoring

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-workflow-engine.git

# Navigate to the project directory
cd ai-workflow-engine

# Install dependencies
npm install

# Build the project
npm run build
```

## Quick Start

```typescript
import { WorkflowEngine, OpenAIConnector, TextProcessingAgent } from 'ai-workflow-engine';

// Initialize the engine
const engine = new WorkflowEngine();

// Create connectors
const openai = new OpenAIConnector({
  apiKey: process.env.OPENAI_API_KEY,
});

// Create agents
const textSummarizer = new TextProcessingAgent({
  name: 'text-summarizer',
  modelName: 'gpt-3.5-turbo',
  connector: openai,
});

// Create a workflow
const workflow = engine.createWorkflow('document-processor');

// Add a step to the workflow
workflow.addStep({
  id: 'summarize-text',
  agent: textSummarizer,
  input: {
    text: 'workflow.input.text',
    maxLength: 100,
  },
});

// Execute the workflow
const result = await workflow.execute({
  text: 'Your long text to summarize goes here...'
});

console.log(result);
```

## Core Components

### Agents

Agents are the core processing units in the workflow engine. Each agent specializes in a specific task:

- **TextProcessingAgent**: Handles text-based operations like summarization, classification, etc.
- **ImageProcessingAgent**: Works with image data for analysis, generation, etc.
- **DataProcessingAgent**: Transforms and processes structured data
- **IntegrationAgent**: Connects to external services and APIs

### Connectors

Connectors provide standardized interfaces to various AI providers:

- **OpenAIConnector**: Interface to OpenAI APIs
- **LocalModelConnector**: Interface to locally hosted models
- **CustomConnector**: Build your own connector for any service

### Workflows

Workflows connect agents together to create complex processes:

- Define multi-step operations
- Handle data transformations between steps
- Manage error handling and retry logic
- Conditional branching based on intermediate results

## Documentation

For detailed documentation, see the [docs](./docs) directory or visit our [documentation site](https://example.com/docs).

## Examples

Check out the [examples](./examples) directory for complete workflow examples:

- Text processing pipelines
- Content generation workflows
- Data extraction systems
- Multi-modal processing flows

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
# ADR-3: AI Agent Architecture for Natural Language Processing and Tool Orchestration

## Status
Accepted

## Date
2026-01-14

## Context
We need to implement an AI agent that interprets natural language messages from users and orchestrates MCP tool calls to manage todos. The solution must use the OpenAI Agents SDK to map natural language intents to MCP tool calls, fetch conversation history from the database each turn, handle confirmations and errors for all CRUD actions, support tool chaining for complex user commands, and ensure the agent operates in a stateless backend environment. This architecture will form the foundation of the AI chatbot's ability to understand and act on user requests through intelligent tool orchestration.

## Decision
We will implement an AI agent using the OpenAI Agents SDK that:
- Maps natural language intents to MCP tool calls using OpenAI's function calling capabilities
- Fetches conversation history from the database each turn to maintain context
- Handles confirmations and errors for all CRUD actions through the agent's response mechanism
- Supports tool chaining for complex user commands using OpenAI's built-in chaining
- Operates in a stateless backend environment by storing conversation context in the database

The system will maintain conversation state using database-stored context while leveraging OpenAI's thread management for continuity.

## Consequences

### Positive
- Enables sophisticated natural language understanding through OpenAI's advanced models
- Provides reliable tool orchestration with OpenAI's native function calling
- Maintains conversation context across server restarts through database persistence
- Supports complex multi-step operations through tool chaining
- Ensures scalability and reliability with stateless operation

### Negative
- Dependency on external OpenAI services creates potential availability and cost concerns
- Limited control over the underlying NLP algorithms
- Potential latency from external API calls
- Possible vendor lock-in with OpenAI's ecosystem

## Alternatives
- Custom NLP implementation: Would require extensive development and maintenance effort but provide full control
- Rule-based system: Would be more predictable but less flexible for varied user expressions
- Third-party NLP services (e.g., Dialogflow, AWS Lex): Would create external dependencies but potentially more cost-effective

## References
- specs/3-ai-agent-logic/plan.md
- specs/3-ai-agent-logic/spec.md
- specs/3-ai-agent-logic/data-model.md
- specs/3-ai-agent-logic/contracts/api-contract.md
# ADR-1: MCP Tools Architecture for AI Agent Task Management

## Status
Accepted

## Date
2026-01-14

## Context
We need to enable an AI agent to perform CRUD operations on tasks stored in a PostgreSQL database using Model Context Protocol (MCP). The solution must ensure tools are stateless and rely only on database state, with standardized input/output schemas for consistent agent behavior. This architecture will form the foundation of the AI chatbot's ability to manage tasks.

## Decision
We will implement 5 specific MCP tools with strict input/output schemas:
- add_task: Creates new tasks in the database
- list_tasks: Retrieves tasks from the database
- complete_task: Updates task status to completed
- delete_task: Removes tasks from the database
- update_task: Modifies task properties

Each tool will connect to the PostgreSQL database on demand, perform its operation, and disconnect, ensuring complete statelessness. We'll use JSON Schema validation for all inputs and consistent error handling patterns.

## Consequences

### Positive
- Enables AI agents to reliably manage tasks through standardized interfaces
- Stateless design ensures scalability and eliminates server-side session state concerns
- Strict schemas provide predictability and validation for AI agent interactions
- Direct database operations ensure data consistency
- Clear separation of concerns with each tool having a single responsibility

### Negative
- Potential performance overhead from establishing database connections for each operation
- Need for robust error handling when database connectivity issues occur
- Increased complexity in managing database connection lifecycle per tool call
- Possible limitations in transactional operations across multiple tools

## Alternatives
- REST API with traditional HTTP endpoints: Would require additional infrastructure and authentication, but might offer better performance through connection pooling
- Message queue pattern: Could provide better decoupling and async processing, but adds complexity and potential state management issues
- Direct database access from AI agent: Would violate security principles and create tight coupling between AI and database

## References
- specs/1-todo-mcp-tools/plan.md
- specs/1-todo-mcp-tools/spec.md
- specs/1-todo-mcp-tools/data-model.md
- specs/1-todo-mcp-tools/contracts/api-contract.md
# Todo App - Hackathon II Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-14

## Active Technologies

- Model Context Protocol (MCP) SDK for Python
- PostgreSQL database for task storage
- JSON Schema validation for tool inputs/outputs
- Statelessness pattern for MCP tools
- REST-style API patterns for tool interactions

## Project Structure

```text
specs/
└── 1-todo-mcp-tools/
    ├── spec.md
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── quickstart.md
    └── contracts/
        └── api-contract.md
```

## Commands

- Install MCP SDK: `pip install ai-mcp-sdk`
- Install database dependencies: `pip install psycopg2-binary sqlmodel`
- Start MCP server: `python mcp_server.py`
- Set database connection: `export DATABASE_URL="postgresql://..."`

## Code Style

- Use strict JSON schema validation for all tool inputs
- Implement stateless operations that rely only on database state
- Return consistent error responses with appropriate status codes
- Follow consistent naming conventions for MCP tools

## Recent Changes

- Added 5 MCP tools for task management: add_task, list_tasks, complete_task, delete_task, update_task
- Defined strict input/output schemas for all tools
- Established database connection patterns for stateless operations
- Created comprehensive API contracts for tool interactions

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
# Todo App - MCP Server Architecture Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-014

## Active Technologies

- Model Context Protocol (MCP) SDK for Python
- PostgreSQL database for task storage
- JSON Schema validation for tool inputs/outputs
- Stateless server architecture patterns
- Standardized response formatting for MCP tools

## Project Structure

```text
specs/
└── 2-mcp-server-arch/
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
- Return consistent response formats with success/data/message structure
- Follow consistent naming conventions for MCP tools

## Recent Changes

- Added stateless MCP server architecture with 5 task management tools
- Defined strict input/output schemas for all tools
- Established database connection patterns for stateless operations
- Created comprehensive API contracts for tool interactions

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
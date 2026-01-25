# Implementation Plan: Todo AI Chatbot — MCP Tools Specification

**Feature**: 1-todo-mcp-tools
**Branch**: 1-todo-mcp-tools
**Created**: 2026-01-14
**Status**: Draft

## Technical Context

This feature implements Model Context Protocol (MCP) tools for a Todo AI Chatbot that will allow the AI agent to perform CRUD operations on tasks stored in a PostgreSQL database. The tools must be stateless and rely only on database state.

The implementation will include 5 specific tools:
- add_task: Creates a new task in the database
- list_tasks: Retrieves all tasks from the database
- complete_task: Marks a task as completed in the database
- delete_task: Removes a task from the database
- update_task: Modifies task properties in the database

Each tool will have strict input/output schemas and consistent error handling.

**Unknowns requiring research:**
- MCP SDK installation and setup process
- Specific database connection patterns for stateless operations
- Error handling best practices for MCP tools

## Constitution Check

**Verify adherence to project principles from constitution.md:**

- ✅ Minimal Viable Change: Implementation focuses on core MCP tools without unnecessary additions
- ✅ Testable Components: Each tool will have verifiable input/output behavior
- ✅ Clear Boundaries: Tools will have well-defined responsibilities
- ✅ Fail Fast: Proper error handling will be implemented for invalid inputs
- ✅ Stateless Design: Tools will rely only on database state, not in-memory state

## Gates

**All gates must pass before implementation begins:**

- [x] Research complete for MCP SDK usage
- [x] Database schema confirmed for task entity
- [x] Input/output schemas defined for all 5 tools
- [x] Error handling patterns established

**Gates that require justification if not passed:**
- If any tool maintains internal state (violates statelessness requirement)
- If tools don't use consistent error handling
- If input/output schemas are not strict

---

## Phase 0: Outline & Research

### Research Tasks

1. **MCP SDK Installation and Setup**
   - Investigate how to install and configure the MCP SDK
   - Understand the basic structure for creating MCP tools
   - Learn how to register tools with the MCP server

2. **Database Connection Patterns for Stateless Tools**
   - Research best practices for connecting to PostgreSQL from MCP tools
   - Understand how to ensure tools remain stateless
   - Learn about connection pooling and cleanup patterns

3. **Error Handling Best Practices for MCP Tools**
   - Identify standard error types and responses for MCP tools
   - Understand how to provide meaningful error messages to AI agents
   - Learn about logging and debugging patterns

### Expected Outcomes from Research
- Clear understanding of MCP SDK tool creation process
- Verified database connection approach that maintains statelessness
- Standardized error handling approach for all tools

---

## Phase 1: Design & Contracts

### Data Model: task entity

**Entity: Task**
- id: UUID (primary key, auto-generated)
- title: String (required, max 255 chars)
- description: Text (optional)
- status: Enum ('pending', 'completed') (default: 'pending')
- created_at: Timestamp (auto-generated)
- updated_at: Timestamp (auto-generated, updates on change)

**Validation Rules:**
- Title must not be empty
- Status must be one of allowed values
- ID must be unique

### API Contracts: MCP Tools

#### Tool 1: add_task
**Description**: Creates a new task in the database

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string", "minLength": 1, "maxLength": 255},
    "description": {"type": "string", "maxLength": 1000},
    "status": {"type": "string", "enum": ["pending", "completed"], "default": "pending"}
  },
  "required": ["title"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "task": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "status": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    },
    "message": {"type": "string"}
  }
}
```

#### Tool 2: list_tasks
**Description**: Retrieves all tasks from the database

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "status_filter": {"type": "string", "enum": ["pending", "completed"]}
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "title": {"type": "string"},
          "description": {"type": "string"},
          "status": {"type": "string"},
          "created_at": {"type": "string", "format": "date-time"},
          "updated_at": {"type": "string", "format": "date-time"}
        }
      }
    },
    "count": {"type": "number"}
  }
}
```

#### Tool 3: complete_task
**Description**: Marks a task as completed in the database

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string", "format": "uuid"}
  },
  "required": ["task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "task": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "status": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    },
    "message": {"type": "string"}
  }
}
```

#### Tool 4: delete_task
**Description**: Removes a task from the database

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string", "format": "uuid"}
  },
  "required": ["task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "deleted_task_id": {"type": "string"},
    "message": {"type": "string"}
  }
}
```

#### Tool 5: update_task
**Description**: Modifies task properties in the database

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string", "format": "uuid"},
    "title": {"type": "string", "minLength": 1, "maxLength": 255},
    "description": {"type": "string", "maxLength": 1000},
    "status": {"type": "string", "enum": ["pending", "completed"]}
  },
  "required": ["task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "task": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "status": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    },
    "message": {"type": "string"}
  }
}
```

### Quickstart Guide

1. Install MCP SDK and dependencies
2. Set up PostgreSQL connection
3. Implement each of the 5 tools with strict schemas
4. Test each tool individually
5. Verify statelessness of all tools
6. Test error handling scenarios

### Agent Context Update

The following technologies and patterns will be added to the agent context:
- MCP SDK tool creation patterns
- PostgreSQL connection for stateless operations
- Strict JSON schema validation
- Consistent error handling approaches
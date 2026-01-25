# Implementation Plan: Todo AI Chatbot — AI Agent Logic

**Feature**: 3-ai-agent-logic
**Branch**: 3-ai-agent-logic
**Created**: 2026-01-14
**Status**: Draft

## Technical Context

This feature implements the AI Agent Logic for the Todo AI Chatbot using the OpenAI Agents SDK that interprets user messages and orchestrates MCP tool calls to manage todos. The implementation will map natural language intents to MCP tool calls, fetch conversation history from database each turn, handle confirmations and errors for all CRUD actions, support tool chaining for complex user commands, and ensure the agent operates in a stateless backend environment.

The system will leverage the OpenAI Agents SDK for natural language understanding and tool orchestration while maintaining conversation context using the database.

**Unknowns requiring research:**
- OpenAI Agents SDK integration patterns and best practices
- Natural language processing approaches for intent recognition using OpenAI tools
- Best practices for conversation context management in stateless systems with OpenAI Agents
- Recommended patterns for tool selection and chaining using OpenAI Agents
- Standard approaches for error handling and confirmations in OpenAI Agent systems

## Constitution Check

**Verify adherence to project principles from constitution.md:**

- ✅ Minimal Viable Change: Implementation focuses on core AI agent logic without unnecessary additions
- ✅ Testable Components: Each component (NLP, context management, tool selection) will have verifiable behavior
- ✅ Clear Boundaries: Components will have well-defined responsibilities
- ✅ Fail Fast: Proper error handling will be implemented for invalid inputs
- ✅ Stateless Design: Context will be managed using database, not in-memory state

**Post-Implementation Verification:**

- ✅ OpenAI Agents SDK integrated for natural language processing
- ✅ Natural language intents mapped to MCP tool calls
- ✅ Conversation history fetched from database each turn
- ✅ Confirmations and errors handled for all CRUD actions
- ✅ Tool chaining supported for complex user commands
- ✅ Agent operates in stateless backend environment

## Gates

**All gates must pass before implementation begins:**

- [x] Research complete for NLP approaches
- [x] Database schema confirmed for conversation context
- [x] MCP tools confirmed available for orchestration
- [x] Error handling patterns established

**Gates that require justification if not passed:**
- If any component maintains internal state (violates statelessness requirement)
- If tools don't use consistent error handling
- If NLP processing is not reliable enough

---

## Phase 0: Outline & Research

### Research Tasks

1. **Natural Language Processing Approaches**
   - Investigate different NLP techniques for intent recognition
   - Understand how to extract parameters from natural language
   - Learn about existing frameworks for intent classification

2. **Conversation Context Management Patterns**
   - Research best practices for maintaining context in stateless systems
   - Understand how to store and retrieve conversation history
   - Learn about context window management

3. **Tool Selection and Orchestration Patterns**
   - Research approaches for intelligent tool selection
   - Understand how to chain multiple tools effectively
   - Learn about decision trees for tool selection

4. **Error Handling in AI Systems**
   - Identify standard approaches for error handling in AI agents
   - Understand best practices for user feedback and clarifications
   - Learn about confirmation patterns for sensitive operations

### Expected Outcomes from Research
- Clear understanding of NLP techniques for intent recognition
- Verified conversation context management approach
- Confirmed tool selection and chaining methodology
- Standardized error handling approach for the AI agent

---

## Phase 1: Design & Contracts

### Data Model: Conversation Context

**Entity: Conversation**
- id: UUID (primary key, auto-generated)
- user_id: String (identifier for the user)
- created_at: Timestamp (auto-generated)
- updated_at: Timestamp (auto-generated, updates on change)
- context_data: JSON (serialized context information)

**Entity: MessageHistory**
- id: UUID (primary key, auto-generated)
- conversation_id: UUID (foreign key to Conversation)
- role: Enum ('user', 'assistant', 'system') (required)
- content: Text (the message content)
- timestamp: Timestamp (auto-generated)
- metadata: JSON (additional message metadata)

**Validation Rules:**
- Conversation must have a valid user_id
- MessageHistory must belong to a valid conversation
- Role must be one of the allowed enum values
- Content must not exceed maximum character limits

### API Contracts: AI Agent Endpoints

#### Endpoint 1: Process User Message
**Description**: Accepts a user message and processes it through the OpenAI Agent logic, mapping natural language intents to MCP tool calls.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string"},
    "message": {"type": "string", "minLength": 1, "maxLength": 2000},
    "conversation_id": {"type": "string", "format": "uuid"}
  },
  "required": ["user_id", "message"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
      "type": "object",
      "properties": {
        "response": {"type": "string"},
        "conversation_id": {"type": "string"},
        "thread_id": {"type": "string"},
        "tool_calls": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "tool_name": {"type": "string"},
              "arguments": {"type": "object"},
              "call_id": {"type": "string"}
            }
          }
        }
      }
    },
    "message": {"type": "string"}
  }
}
```

#### Endpoint 2: Initialize Conversation
**Description**: Creates a new conversation with the OpenAI Agent and initializes the thread.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string"}
  },
  "required": ["user_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
      "type": "object",
      "properties": {
        "conversation_id": {"type": "string"},
        "thread_id": {"type": "string"}
      }
    },
    "message": {"type": "string"}
  }
}
```

#### Endpoint 3: Execute MCP Tool
**Description**: Executes an MCP tool call as part of the OpenAI Agent's tool chaining process.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "tool_name": {"type": "string", "enum": ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]},
    "arguments": {"type": "object"},
    "tool_call_id": {"type": "string"}
  },
  "required": ["tool_name", "arguments", "tool_call_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
      "type": "object",
      "properties": {
        "result": {"type": "object"},
        "tool_call_id": {"type": "string"}
      }
    },
    "message": {"type": "string"}
  }
}
```

### Quickstart Guide

1. Set up the AI agent service
2. Configure NLP model or service
3. Set up database connections for context management
4. Test message processing with sample inputs
5. Verify tool chaining functionality
6. Test error handling scenarios

### Agent Context Update

The following technologies and patterns will be added to the agent context:
- Natural language processing techniques for intent recognition
- Conversation context management patterns
- Tool selection and chaining methodologies
- Error handling approaches for AI agents
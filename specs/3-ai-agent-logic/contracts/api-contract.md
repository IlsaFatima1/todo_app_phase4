# OpenAPI Contract: Todo AI Chatbot with OpenAI Agents

## process_user_message Endpoint

### Description
Accepts a user message and processes it through the OpenAI Agent logic, mapping natural language intents to MCP tool calls.

### Request Schema
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

### Response Schema
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

## initialize_conversation Endpoint

### Description
Creates a new conversation with the OpenAI Agent and initializes the thread.

### Request Schema
```json
{
  "type": "object",
  "properties": {
    "user_id": {"type": "string"}
  },
  "required": ["user_id"]
}
```

### Response Schema
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

## execute_mcp_tool Endpoint

### Description
Executes an MCP tool call as part of the OpenAI Agent's tool chaining process.

### Request Schema
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

### Response Schema
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
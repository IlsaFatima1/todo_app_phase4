# Quickstart Guide: Todo AI Chatbot with OpenAI Agents

## Prerequisites

- Python 3.8 or higher
- OpenAI Python SDK installed
- PostgreSQL database instance
- OpenAI API key
- Existing MCP tools available for integration

## Installation

1. Install the OpenAI SDK:
```bash
pip install openai
```

2. Install additional dependencies:
```bash
pip install python-dotenv
```

## Configuration

Set the following environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export DATABASE_URL="postgresql://username:password@localhost:5432/todo_ai_db"
```

## Running the Service

1. Start the AI agent service:
```bash
python ai_agent_service.py
```

2. The service will provide the following endpoints:
   - `POST /api/ai/process_message`: Process user messages through the OpenAI Agent
   - `POST /api/ai/init_conversation`: Initialize a new conversation
   - `POST /api/ai/execute_tool`: Execute MCP tools as part of tool chaining

## Testing the Service

Example to process a user message:
```json
{
  "user_id": "user123",
  "message": "Add a task to buy groceries tomorrow",
  "conversation_id": "conv456"
}
```

## Integration with MCP Tools

The AI Agent will automatically map natural language intents to the following MCP tools:
- `add_task`: For creating new tasks
- `list_tasks`: For retrieving existing tasks
- `complete_task`: For marking tasks as completed
- `delete_task`: For removing tasks
- `update_task`: For modifying existing tasks

## Troubleshooting

- If OpenAI API calls fail, verify your API key is correct
- If conversations aren't persisting, check database connection settings
- For tool execution errors, verify MCP tools are properly configured
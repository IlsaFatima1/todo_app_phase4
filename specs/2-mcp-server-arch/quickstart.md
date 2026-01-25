# Quickstart Guide: Todo AI Chatbot MCP Server Architecture

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database instance
- MCP SDK for Python installed
- Environment variables configured for database connection

## Installation

1. Install the MCP SDK:
```bash
pip install ai-mcp-sdk
```

2. Install database dependencies:
```bash
pip install psycopg2-binary sqlmodel
```

## Configuration

Set the following environment variables:
```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/todo_mcp_db"
```

## Running the Server

1. Start the MCP server:
```bash
python mcp_server.py
```

2. The server will register the following tools:
   - `add_task`: Create new tasks
   - `list_tasks`: Retrieve all tasks
   - `complete_task`: Mark tasks as completed
   - `delete_task`: Remove tasks
   - `update_task`: Modify task properties

## Testing the Tools

Use an MCP client to call any of the registered tools with the appropriate parameters.

Example to add a task:
```json
{
  "tool_name": "add_task",
  "arguments": {
    "title": "Sample task",
    "description": "This is a sample task"
  }
}
```

## Troubleshooting

- If database connection fails, verify DATABASE_URL is correct
- If tools are not recognized, ensure the MCP server started successfully
- For validation errors, check that input parameters match the required schemas
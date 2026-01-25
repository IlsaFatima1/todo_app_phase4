# OpenAPI Contract: Todo AI Chatbot MCP Tools

## add_task Tool

### Description
Creates a new task in the database with the provided properties.

### Request Schema
```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string", "minLength": 1, "maxLength": 255},
    "description": {"type": "string", "maxLength": 1000, "default": ""},
    "status": {"type": "string", "enum": ["pending", "completed"], "default": "pending"}
  },
  "required": ["title"]
}
```

### Response Schema
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
  },
  "required": ["success", "task", "message"]
}
```

## list_tasks Tool

### Description
Retrieves all tasks from the database, optionally filtered by status.

### Request Schema
```json
{
  "type": "object",
  "properties": {
    "status_filter": {"type": "string", "enum": ["pending", "completed"]}
  }
}
```

### Response Schema
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
  },
  "required": ["success", "tasks", "count"]
}
```

## complete_task Tool

### Description
Marks a task as completed in the database.

### Request Schema
```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string", "format": "uuid"}
  },
  "required": ["task_id"]
}
```

### Response Schema
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
  },
  "required": ["success", "task", "message"]
}
```

## delete_task Tool

### Description
Removes a task from the database.

### Request Schema
```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string", "format": "uuid"}
  },
  "required": ["task_id"]
}
```

### Response Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "deleted_task_id": {"type": "string"},
    "message": {"type": "string"}
  },
  "required": ["success", "deleted_task_id", "message"]
}
```

## update_task Tool

### Description
Modifies task properties in the database.

### Request Schema
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

### Response Schema
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
  },
  "required": ["success", "task", "message"]
}
```
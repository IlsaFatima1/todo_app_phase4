# API Contract: Todo AI Chatbot MCP Tools

## add_task Tool

### Description
Creates a new task in the database with the provided properties.

### Input Schema
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

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
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

## list_tasks Tool

### Description
Retrieves all tasks from the database, optionally filtered by status.

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "status_filter": {"type": "string", "enum": ["pending", "completed"]}
  }
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
      "type": "object",
      "properties": {
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
    },
    "message": {"type": "string"}
  }
}
```

## complete_task Tool

### Description
Marks a task as completed in the database.

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string", "format": "uuid"}
  },
  "required": ["task_id"]
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
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

## delete_task Tool

### Description
Removes a task from the database.

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "task_id": {"type": "string", "format": "uuid"}
  },
  "required": ["task_id"]
}
```

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
      "type": "object",
      "properties": {
        "deleted_task_id": {"type": "string"}
      }
    },
    "message": {"type": "string"}
  }
}
```

## update_task Tool

### Description
Modifies task properties in the database.

### Input Schema
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

### Output Schema
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "data": {
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
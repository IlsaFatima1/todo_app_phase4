# Data Model: Task Entity for Todo AI Chatbot

## Entity: Task

### Fields
- **id** (UUID)
  - Type: Universally Unique Identifier
  - Constraints: Primary Key, Auto-generated
  - Description: Unique identifier for each task

- **title** (String)
  - Type: Variable character string
  - Constraints: Required, Max length 255 characters
  - Description: Brief title or summary of the task

- **description** (Text)
  - Type: Text field
  - Constraints: Optional, Max length 1000 characters
  - Description: Detailed description of the task

- **status** (Enum)
  - Type: Enumeration
  - Values: 'pending', 'completed'
  - Constraints: Required, Default value 'pending'
  - Description: Current status of the task

- **created_at** (Timestamp)
  - Type: DateTime
  - Constraints: Auto-generated on creation
  - Description: Timestamp when the task was created

- **updated_at** (Timestamp)
  - Type: DateTime
  - Constraints: Auto-generated, Updates on modification
  - Description: Timestamp when the task was last updated

### Relationships
- None (standalone entity)

### Validation Rules
1. **Title Validation**: Title field must not be empty or consist only of whitespace
2. **Status Validation**: Status field must be one of the allowed enum values ('pending', 'completed')
3. **ID Uniqueness**: ID field must be unique across all tasks
4. **Field Length**: Title and description must not exceed maximum character lengths

### State Transitions
- **Creation**: New tasks are created with status='pending' by default
- **Update**: Tasks can transition from 'pending' to 'completed' or have other properties modified
- **Deletion**: Tasks can be permanently removed from the system

### Indexes
- Primary Index: id (automatically created)
- Additional Indexes: None required for initial implementation
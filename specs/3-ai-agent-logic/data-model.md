# Data Model: Conversation Context for Todo AI Chatbot with OpenAI Agents

## Entity: Conversation

### Fields
- **id** (UUID)
  - Type: Universally Unique Identifier
  - Constraints: Primary Key, Auto-generated
  - Description: Unique identifier for each conversation

- **user_id** (String)
  - Type: Variable character string
  - Constraints: Required, Max length 255 characters
  - Description: Identifier for the user participating in the conversation

- **created_at** (Timestamp)
  - Type: DateTime
  - Constraints: Auto-generated on creation
  - Description: Timestamp when the conversation was started

- **updated_at** (Timestamp)
  - Type: DateTime
  - Constraints: Auto-generated, Updates on modification
  - Description: Timestamp when the conversation was last updated

- **context_data** (JSON)
  - Type: JSON/JSONB field
  - Constraints: Optional
  - Description: Serialized context information for the conversation, including OpenAI thread references

- **thread_id** (String)
  - Type: String
  - Constraints: Optional
  - Description: Reference to OpenAI thread ID for maintaining continuity with OpenAI Agents

### Relationships
- One-to-many: Conversation to MessageHistory

### Validation Rules
1. **User ID Validation**: user_id field must not be empty or consist only of whitespace
2. **ID Uniqueness**: ID field must be unique across all conversations
3. **Context Data Format**: If present, context_data must be valid JSON
4. **Thread ID Format**: If present, thread_id must be a valid OpenAI thread identifier format

### State Transitions
- **Creation**: New conversation initiated when user starts interaction
- **Update**: Conversation updated when new messages are added
- **Closure**: Conversation may be archived after period of inactivity

### Indexes
- Primary Index: id (automatically created)
- Secondary Index: user_id (for efficient user-based queries)
- Additional Index: thread_id (for OpenAI thread reference lookup)

## Entity: MessageHistory

### Fields
- **id** (UUID)
  - Type: Universally Unique Identifier
  - Constraints: Primary Key, Auto-generated
  - Description: Unique identifier for each message

- **conversation_id** (UUID)
  - Type: Universally Unique Identifier
  - Constraints: Foreign Key, Required
  - Description: Reference to the parent conversation

- **role** (Enum)
  - Type: Enumeration
  - Values: 'user', 'assistant', 'system', 'tool'
  - Constraints: Required
  - Description: Defines the role of the message author

- **content** (Text)
  - Type: Text field
  - Constraints: Required, Max length 10000 characters
  - Description: The actual content of the message

- **timestamp** (Timestamp)
  - Type: DateTime
  - Constraints: Auto-generated
  - Description: When the message was recorded

- **metadata** (JSON)
  - Type: JSON/JSONB field
  - Constraints: Optional
  - Description: Additional metadata about the message, including tool call information

- **tool_call_id** (String)
  - Type: String
  - Constraints: Optional
  - Description: ID of the tool call if this message is a tool response

- **tool_name** (String)
  - Type: String
  - Constraints: Optional
  - Description: Name of the tool that was called (for tool role messages)

### Relationships
- Many-to-one: MessageHistory to Conversation (via conversation_id)

### Validation Rules
1. **Role Validation**: Role field must be one of the allowed enum values ('user', 'assistant', 'system', 'tool')
2. **Content Validation**: Content field must not be empty or consist only of whitespace
3. **Foreign Key Validation**: conversation_id must reference an existing conversation
4. **Content Length**: Content must not exceed maximum character limits
5. **Tool Role Consistency**: If role is 'tool', tool_name and tool_call_id should be present

### State Transitions
- **Creation**: New message added to conversation history
- **Metadata Update**: Additional information may be added to metadata field after creation

### Indexes
- Primary Index: id (automatically created)
- Foreign Key Index: conversation_id (for efficient conversation-based queries)
- Timestamp Index: timestamp (for chronological ordering)
- Tool Call Index: tool_call_id (for tool call tracking)
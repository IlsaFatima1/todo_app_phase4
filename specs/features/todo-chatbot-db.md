# Todo AI Chatbot - Database Models Specification

## Overview
This specification defines the database models for the Todo AI Chatbot system using SQLModel. The models will persist tasks, conversations, and messages to a Neon Serverless PostgreSQL database, supporting stateless conversation workflows for backend and agent systems.

## Target Audience
- Backend developers implementing the API
- Agent systems that persist tasks, conversations, and messages
- MCP tools that interact with the database
- Database administrators managing the Neon PostgreSQL instance

## Scope

### In Scope
- Todo items with status, priority, and metadata
- Conversation threads between users and AI
- Message history with content and metadata
- User profiles and session management
- Relationship mapping between todos and conversations
- Audit trails and timestamps for all entities

### Out of Scope
- Frontend UI components
- Real-time messaging protocols
- AI model training data
- File storage for attachments (future extension)
- Third-party service integrations

## Data Model Design

### Core Entities

#### 1. User Model
```sql
users
├── id (UUID, Primary Key)
├── email (String, Unique, Not Null)
├── username (String, Unique)
├── full_name (String)
├── is_active (Boolean, Default: True)
├── created_at (DateTime, Not Null)
└── updated_at (DateTime, Not Null)
```

#### 2. Todo Model
```sql
todos
├── id (UUID, Primary Key)
├── title (String, Not Null)
├── description (Text)
├── status (String: pending, in_progress, completed, archived)
├── priority (String: low, medium, high, urgent)
├── due_date (DateTime)
├── created_by (UUID, Foreign Key -> users.id)
├── assigned_to (UUID, Foreign Key -> users.id)
├── completed_at (DateTime)
├── created_at (DateTime, Not Null)
├── updated_at (DateTime, Not Null)
└── metadata (JSON)
```

#### 3. Conversation Model
```sql
conversations
├── id (UUID, Primary Key)
├── title (String)
├── user_id (UUID, Foreign Key -> users.id)
├── created_at (DateTime, Not Null)
├── updated_at (DateTime, Not Null)
└── metadata (JSON)
```

#### 4. Message Model
```sql
messages
├── id (UUID, Primary Key)
├── conversation_id (UUID, Foreign Key -> conversations.id)
├── sender_type (String: user, ai, system)
├── sender_id (UUID, Foreign Key -> users.id)
├── content (Text, Not Null)
├── message_type (String: text, command, response, error)
├── created_at (DateTime, Not Null)
└── metadata (JSON)
```

#### 5. Todo-Conversation Link Model
```sql
todo_conversation_links
├── id (UUID, Primary Key)
├── todo_id (UUID, Foreign Key -> todos.id)
├── conversation_id (UUID, Foreign Key -> conversations.id)
├── created_at (DateTime, Not Null)
└── relationship_type (String: discussion, update, creation)
```

## SQLModel Definitions

### Base Model
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def __setattr__(self, name, value):
        if name == "updated_at":
            super().__setattr__("updated_at", datetime.utcnow())
        super().__setattr__(name, value)

class UUIDPrimaryKey(SQLModel):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )
```

### User Model
```python
class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)
    username: Optional[str] = Field(unique=True)
    full_name: Optional[str]

class User(UUIDPrimaryKey, UserBase, TimestampMixin, table=True):
    __tablename__ = "users"

    email: str = Field(unique=True, nullable=False)
    username: Optional[str] = Field(unique=True)
    full_name: Optional[str]
    is_active: bool = Field(default=True)

    # Relationships
    todos_created: List["Todo"] = Relationship(back_populates="creator")
    todos_assigned: List["Todo"] = Relationship(back_populates="assignee")
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages_sent: List["Message"] = Relationship(back_populates="sender")

class UserRead(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserCreate(UserBase):
    password: str  # Will be hashed before storing

class UserUpdate(SQLModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
```

### Todo Model
```python
from enum import Enum

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class TodoPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TodoBase(SQLModel):
    title: str = Field(nullable=False)
    description: Optional[str] = None
    status: TodoStatus = Field(default=TodoStatus.PENDING)
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = Field(default={})

class Todo(UUIDPrimaryKey, TodoBase, TimestampMixin, table=True):
    __tablename__ = "todos"

    # Foreign Keys
    created_by: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    assigned_to: Optional[uuid.UUID] = Field(foreign_key="users.id")

    # Relationships
    creator: "User" = Relationship(back_populates="todos_created")
    assignee: Optional["User"] = Relationship(back_populates="todos_assigned")
    conversation_links: List["TodoConversationLink"] = Relationship(back_populates="todo")

class TodoRead(TodoBase):
    id: uuid.UUID
    created_by: uuid.UUID
    assigned_to: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

class TodoCreate(TodoBase):
    created_by: uuid.UUID
    assigned_to: Optional[uuid.UUID] = None

class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None
```

### Conversation Model
```python
class ConversationBase(SQLModel):
    title: Optional[str] = None
    metadata: Optional[dict] = Field(default={})

class Conversation(UUIDPrimaryKey, ConversationBase, TimestampMixin, table=True):
    __tablename__ = "conversations"

    # Foreign Key
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
    todo_links: List["TodoConversationLink"] = Relationship(back_populates="conversation")

class ConversationRead(ConversationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class ConversationCreate(ConversationBase):
    user_id: uuid.UUID

class ConversationUpdate(SQLModel):
    title: Optional[str] = None
    metadata: Optional[dict] = None
```

### Message Model
```python
class SenderType(str, Enum):
    USER = "user"
    AI = "ai"
    SYSTEM = "system"

class MessageType(str, Enum):
    TEXT = "text"
    COMMAND = "command"
    RESPONSE = "response"
    ERROR = "error"

class MessageBase(SQLModel):
    sender_type: SenderType = Field(nullable=False)
    content: str = Field(nullable=False)
    message_type: MessageType = Field(default=MessageType.TEXT)
    metadata: Optional[dict] = Field(default={})

class Message(UUIDPrimaryKey, MessageBase, TimestampMixin, table=True):
    __tablename__ = "messages"

    # Foreign Keys
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False)
    sender_id: Optional[uuid.UUID] = Field(foreign_key="users.id")  # Optional for system messages

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    sender: Optional["User"] = Relationship(back_populates="messages_sent")

class MessageRead(MessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: Optional[uuid.UUID]
    created_at: datetime

class MessageCreate(MessageBase):
    conversation_id: uuid.UUID
    sender_id: Optional[uuid.UUID] = None

class MessageUpdate(SQLModel):
    content: Optional[str] = None
    message_type: Optional[MessageType] = None
    metadata: Optional[dict] = None
```

### Todo-Conversation Link Model
```python
class RelationshipType(str, Enum):
    DISCUSSION = "discussion"
    UPDATE = "update"
    CREATION = "creation"

class TodoConversationLinkBase(SQLModel):
    relationship_type: RelationshipType = Field(default=RelationshipType.DISCUSSION)

class TodoConversationLink(UUIDPrimaryKey, TodoConversationLinkBase, TimestampMixin, table=True):
    __tablename__ = "todo_conversation_links"

    # Foreign Keys
    todo_id: uuid.UUID = Field(foreign_key="todos.id", nullable=False)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False)

    # Relationships
    todo: "Todo" = Relationship(back_populates="conversation_links")
    conversation: "Conversation" = Relationship(back_populates="todo_links")

class TodoConversationLinkRead(TodoConversationLinkBase):
    id: uuid.UUID
    todo_id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime

class TodoConversationLinkCreate(TodoConversationLinkBase):
    todo_id: uuid.UUID
    conversation_id: uuid.UUID
```

## Indexes and Constraints

### Primary Indexes
- All tables have UUID primary keys
- Auto-generated indexes on primary keys

### Secondary Indexes
```sql
-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Todos
CREATE INDEX idx_todos_status ON todos(status);
CREATE INDEX idx_todos_priority ON todos(priority);
CREATE INDEX idx_todos_due_date ON todos(due_date);
CREATE INDEX idx_todos_created_by ON todos(created_by);
CREATE INDEX idx_todos_assigned_to ON todos(assigned_to);
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);

-- Conversations
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- Messages
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_sender_type ON messages(sender_type);

-- Todo-Conversation Links
CREATE INDEX idx_todo_conv_links_todo_id ON todo_conversation_links(todo_id);
CREATE INDEX idx_todo_conv_links_conversation_id ON todo_conversation_links(conversation_id);
```

### Foreign Key Constraints
- Enforce referential integrity between related tables
- Cascade delete for messages when conversation is deleted
- Prevent deletion of users with existing records

## Data Validation Rules

### User Model
- Email must be valid format
- Username must be unique and alphanumeric + underscore/hyphen
- Cannot deactivate user with active todos assigned

### Todo Model
- Title must not be empty
- Due date cannot be in the past for completed todos
- Status transition validation (e.g., cannot complete an archived task)

### Message Model
- Content length limits (max 10,000 characters)
- Cannot have sender_id for system messages
- Conversation must exist before creating messages

## Statelessness Considerations

### Session Management
- No server-side session state stored
- Authentication handled via JWT tokens
- All conversation state derived from stored messages

### Query Optimization
- Efficient indexing for common query patterns
- Pagination support for large datasets
- Batch operations for bulk operations

## Migration Strategy

### Initial Migration
- Create all tables in dependency order
- Populate with initial seed data if needed
- Set up proper constraints and indexes

### Future Migrations
- Follow semantic versioning for schema changes
- Provide backward-compatible migration paths
- Include rollback procedures for each migration

## Security Considerations

### Data Protection
- Encrypt sensitive data at rest
- Secure connections to Neon PostgreSQL
- Audit trail for all data modifications

### Access Control
- Row-level security for user data isolation
- Proper validation of foreign key relationships
- Prevent unauthorized cross-user data access

## Performance Requirements

### Query Performance
- Sub-100ms response times for common operations
- Support for concurrent access patterns
- Efficient pagination for large result sets

### Scalability
- Support for millions of messages and conversations
- Horizontal scaling readiness
- Efficient storage utilization

## Acceptance Criteria

### Functional Requirements
- [ ] All models can be created, read, updated, and deleted
- [ ] Foreign key relationships enforce data integrity
- [ ] Indexes support required query patterns
- [ ] Validation rules prevent invalid data insertion
- [ ] Timestamps are properly maintained

### Non-Functional Requirements
- [ ] Models support concurrent access
- [ ] Performance benchmarks are met
- [ ] Security requirements are satisfied
- [ ] Migration scripts are properly tested
- [ ] Documentation is complete